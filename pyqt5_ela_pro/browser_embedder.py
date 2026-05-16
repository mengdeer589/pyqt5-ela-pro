"""
浏览器嵌入组件 (Windows + PyQt5)

继承自 ElaWindowEmbedder，添加浏览器启动和管理功能。

使用示例:
    from pyqt5_ela_pro.browser_embedder import ElaBrowserEmbedder
    browser = ElaBrowserEmbedder(
        webview_path=Path("chrome.exe"),
        port=9023,
        debug_port=9222,
        parent=self
    )
    browser.embed("http://example.com", window_title="MyBrowser")
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes
import json
import time
import weakref
from urllib.parse import unquote, urlparse
from pathlib import Path
from typing import Optional, Any, Callable, Union

from PyQt5.QtCore import pyqtSignal, QTimer, QObject, QUrl, QProcess, QAbstractNativeEventFilter
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt5.QtWebSockets import QWebSocket
from PyQt5.QtWidgets import QWidget

from .window_embedder import ElaWindowEmbedder

try:
    import win32gui  # type: ignore[attr-defined]
    import win32con  # type: ignore[attr-defined]
except ImportError:
    win32gui = None
    win32con = None
try:
    import win32process  # type: ignore[attr-defined]
except ImportError:
    win32process = None

# OLE 初始化（进程级，供 RegisterDragDrop 使用）
try:
    ctypes.windll.ole32.OleInitialize(None)
except Exception:
    pass


class _BrowserController(QObject):
    """CDP WebSocket 客户端（内部类）- 信号驱动版本"""

    cdpReady = pyqtSignal()
    errorOccurred = pyqtSignal(str)
    consoleMessage = pyqtSignal(str, str)
    domContentReady = pyqtSignal()
    pageError = pyqtSignal(str, str)
    networkRequest = pyqtSignal(str, str, str)
    networkResponse = pyqtSignal(str, int, str)

    def __init__(
        self,
        debugger_url: str,
        timeout: float = 5.0,
        log_func: Optional[Callable[[str, int], None]] = None,
    ):
        super().__init__()
        self._debugger_url = debugger_url
        self._timeout = timeout
        self._log_func = log_func
        self._ws: Optional[QWebSocket] = None
        self._message_id: int = 0
        self._callbacks: dict[int, Callable] = {}
        self._result_timers: dict[int, QTimer] = {}
        self._connect_timer: Optional[QTimer] = None
        self._running: bool = False
        self._loadStarted_callback: Optional[Callable] = None
        self._loadFinished_callback: Optional[Callable] = None
        self._dropped_file_callback: Optional[Callable[[str], None]] = None

    def _log(self, message: str, level: int = 30) -> None:
        if self._log_func:
            self._log_func(message, level)

    def connect(self) -> None:
        """启动 WebSocket 连接（非阻塞）"""
        self._ws = QWebSocket()
        self._ws.error.connect(self._on_error)
        self._ws.textMessageReceived.connect(self._on_text_message)
        self._ws.connected.connect(self._on_connected)

        self._connect_timer = QTimer(self)
        self._connect_timer.setSingleShot(True)
        self._connect_timer.timeout.connect(self._on_connect_timeout)
        self._connect_timer.start(10000)

        self._ws.open(QUrl(self._debugger_url))

    def _on_connected(self) -> None:
        self._log("CDP WebSocket 已连接", 20)
        self._connect_timer.stop()
        self._running = True
        self.sendCommand("Page.enable")
        self.sendCommand("Runtime.enable")
        self.sendCommand("Network.enable")
        self.sendCommand("Log.enable")
        self.sendCommand(
            "Browser.setDownloadBehavior",
            {
                "behavior": "deny",
            },
        )
        self.sendCommand(
            "Target.setAutoAttach",
            {
                "autoAttach": True,
                "waitForDebuggerOnStart": False,
                "flatten": True,
            },
        )
        self.cdpReady.emit()

    def _on_connect_timeout(self) -> None:
        self._log("CDP WebSocket 连接超时", 30)
        self.errorOccurred.emit("WebSocket 连接超时")
        self._running = False
        if self._ws:
            self._ws.close()
            self._ws = None

    def _on_error(self, error) -> None:
        try:
            self._log(f"WebSocket 错误: {error}", 30)
        except RuntimeError:
            return
        self.errorOccurred.emit(str(error))
        if self._connect_timer:
            self._connect_timer.stop()

    def _on_text_message(self, message: str) -> None:
        try:
            data = json.loads(message)
        except Exception as e:
            self._log(f"CDP 消息解析失败: {e}", 30)
            return

        if "id" in data:
            msg_id = data["id"]
            result = data.get("result")
            if msg_id in self._callbacks:
                cb = self._callbacks.pop(msg_id)
                cb(result)
            if msg_id in self._result_timers:
                self._result_timers[msg_id].stop()
                self._result_timers[msg_id].deleteLater()
                del self._result_timers[msg_id]
        else:
            method = data.get("method")
            params = data.get("params", {})
            self._handle_event(method, params)

    def _handle_event(self, method: Optional[str], params: dict) -> None:
        if method == "Page.frameStartedLoading":
            if self._loadStarted_callback:
                self._loadStarted_callback()
        elif method in ("Page.loadEventFired", "Page.frameStoppedLoading"):
            if self._loadFinished_callback:
                self._loadFinished_callback()
        elif method == "Runtime.consoleAPICalled":
            msg_type = params.get("type", "log")
            args = params.get("args", [])
            texts = []
            for arg in args:
                value = arg.get("value", "")
                texts.append(str(value))
            text = " ".join(texts)
            self.consoleMessage.emit(msg_type, text)
        elif method in ("Target.targetCreated", "Target.attachedToTarget", "Target.targetInfoChanged"):
            self._close_target_page(params)
        elif method == "Page.frameRequestedNavigation":
            url = params.get("url", "")
            if url.startswith("file:///"):
                path = self._parse_file_url_path(url)
                if self._dropped_file_callback:
                    self._dropped_file_callback(path)
                self.sendCommand("Page.stopLoading", {})
        elif method == "Page.downloadWillBegin":
            url = params.get("url", "")
            if url.startswith("file:///"):
                path = self._parse_file_url_path(url)
                if self._dropped_file_callback:
                    self._dropped_file_callback(path)
        elif method == "Page.domContentEventFired":
            self.domContentReady.emit()
        elif method == "Runtime.exceptionThrown":
            details = params.get("exceptionDetails", {})
            exception_text = details.get("text", "")
            url = details.get("url", "")
            self.pageError.emit(url, exception_text)
        elif method == "Network.requestWillBeSent":
            request = params.get("request", {})
            req_url = request.get("url", "")
            req_method = request.get("method", "GET")
            req_type = params.get("type", "")
            self.networkRequest.emit(req_url, req_method, req_type)
        elif method == "Network.responseReceived":
            response = params.get("response", {})
            resp_url = response.get("url", "")
            status = response.get("status", 0)
            resp_type = params.get("type", "")
            self.networkResponse.emit(resp_url, status, resp_type)
        elif method == "Inspector.targetCrashed":
            self._log("浏览器标签页崩溃", 40)
        elif method == "Log.entryAdded":
            entry = params.get("entry", {})
            log_level = entry.get("level", "log")
            log_text = entry.get("text", "")
            self.consoleMessage.emit(log_level, log_text)
        elif method == "Page.javascriptDialogOpening":
            self.sendCommand("Page.handleJavaScriptDialog", {"accept": True})

    @staticmethod
    def _parse_file_url_path(url: str) -> str:
        path = unquote(urlparse(url).path)
        if path.startswith("/") and len(path) > 2 and path[2] == ":":
            path = path[1:]
        return path

    def _close_target_page(self, params: dict) -> None:
        target = params.get("targetInfo", {})
        url = target.get("url", "")
        if url.startswith("file:///"):
            path = self._parse_file_url_path(url)
            if self._dropped_file_callback:
                self._dropped_file_callback(path)
            self.sendCommand("Target.closeTarget", {"targetId": target["targetId"]})
        elif target.get("type") == "page":
            self.sendCommand("Target.closeTarget", {"targetId": target["targetId"]})

    def set_loadStarted_callback(self, callback: Callable) -> None:
        self._loadStarted_callback = callback

    def set_loadFinished_callback(self, callback: Callable) -> None:
        self._loadFinished_callback = callback

    def sendCommand(
        self,
        method: str,
        params: Optional[dict] = None,
        callback: Optional[Callable[[Any], None]] = None,
    ) -> int:
        """发送 CDP 命令（非阻塞）

        :param method: 方法名
        :param params: 参数
        :param callback: 可选回调，收到响应时调用
        :returns: 消息 ID
        """
        msg_id = self._message_id
        self._message_id += 1

        cmd: dict = {"id": msg_id, "method": method}
        if params:
            cmd["params"] = params

        if callback:
            self._callbacks[msg_id] = callback

        if callback and self._timeout > 0:
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._on_command_timeout(msg_id))
            timer.start(int(self._timeout * 1000))
            self._result_timers[msg_id] = timer

        self._ws.sendTextMessage(json.dumps(cmd))
        return msg_id

    def _on_command_timeout(self, msg_id: int) -> None:
        self._log(f"命令 {msg_id} 超时", 30)
        self._callbacks.pop(msg_id, None)
        timer = self._result_timers.pop(msg_id, None)
        if timer:
            timer.deleteLater()

    def runJS(
        self, script: str, callback: Optional[Callable[[Any], None]] = None
    ) -> int:
        """执行 JavaScript 代码（非阻塞）

        :param script: JavaScript 代码
        :param callback: 可选回调
        :returns: 消息 ID
        """
        return self.sendCommand(
            "Runtime.evaluate",
            {"expression": script, "returnByValue": True},
            callback=callback,
        )

    def navigate(
        self, url: str, callback: Optional[Callable[[Any], None]] = None
    ) -> int:
        """导航到指定 URL（非阻塞）

        :param url: 目标 URL
        :param callback: 可选回调
        :returns: 消息 ID
        """
        return self.sendCommand("Page.navigate", {"url": url}, callback=callback)

    def reload(self, callback: Optional[Callable[[Any], None]] = None) -> int:
        """刷新页面（非阻塞）

        :param callback: 可选回调
        :returns: 消息 ID
        """
        return self.sendCommand("Page.reload", callback=callback)

    def close(self) -> None:
        self._running = False
        if self._connect_timer:
            self._connect_timer.stop()
            self._connect_timer = None
        for timer in self._result_timers.values():
            timer.stop()
            timer.deleteLater()
        self._result_timers.clear()
        self._callbacks.clear()
        if self._ws:
            self._ws.close()
            self._ws = None


# ── IME 转发过滤器（浏览器专用）──────────────────────────────

class _MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", ctypes.c_void_p),
        ("message", ctypes.c_uint32),
        ("wParam", ctypes.c_uint64 if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_uint32),
        ("lParam", ctypes.c_uint64 if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_uint32),
        ("time", ctypes.c_uint32),
        ("pt", ctypes.c_uint64),
    ]


class _ImeForwardFilter(QAbstractNativeEventFilter):
    """Qt 原生事件过滤器，转发 IME 到嵌入的浏览器窗口。"""

    def _find_at_cursor(self) -> Optional[int]:
        from PyQt5.QtCore import QPoint
        from PyQt5.QtWidgets import QApplication
        pt = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        w = QApplication.widgetAt(QPoint(pt.x, pt.y))
        # print(w.objectName())
        return getattr(w, '_chrome_hwnd', None)

    def nativeEventFilter(self, eventType, message):
        if eventType != "windows_generic_MSG":
            return False, 0
        try:
            hwnd = self._find_at_cursor() or None
            msg = _MSG.from_address(message.__int__())
            if hwnd :
                ctypes.windll.user32.SetFocus(hwnd)
                return False, 0
            else:
                ctypes.windll.user32.SetFocus(None)
            if hwnd and msg.message in (
                0x0051, 0x0281, 0x0282, 0x0286,
                0x010D, 0x010E, 0x010F,
            ):
                ctypes.windll.user32.PostMessageW(
                    hwnd, msg.message, msg.wParam, msg.lParam
                )
                return False, 0
        except Exception:  # noqa
            pass
        return False, 0
        try:
            msg = _MSG.from_address(message.__int__())
            hwnd_at = self._find_at_cursor()
            if hwnd_at:  # WM_SETFOCUS
                ctypes.windll.user32.SetFocus(hwnd_at)
                return False, 0
            if hwnd_at and msg.message in (
                0x0051, 0x0281, 0x0282, 0x0286,
                0x010D, 0x010E, 0x010F,0x0007
            ):
                ctypes.windll.user32.PostMessageW(
                    self.hwnd_at, msg.message, msg.wParam, msg.lParam
                )
                return False, 0
        except Exception:  # noqa
            pass
        return False, 0


_ime_filter = _ImeForwardFilter()
_ime_installed = False


def _ensure_ime_filter() -> None:
    global _ime_installed
    if not _ime_installed:
        try:
            from PyQt5.QtWidgets import QApplication
            QApplication.instance().installNativeEventFilter(_ime_filter)
            _ime_installed = True
        except Exception:
            pass


class ElaBrowserEmbedder(ElaWindowEmbedder):
    """浏览器嵌入组件

    继承自 ElaWindowEmbedder，添加浏览器启动和管理功能。

    信号（继承自 ElaWindowEmbedder）:
        windowEmbedded(int): 窗口嵌入成功
        windowReleased(int): 窗口释放成功
        windowNotFound(str): 等待窗口时未找到
        embedError(str): 嵌入出错
        embedTimeout(): 等待窗口嵌入超时

    新增信号:
        loadStarted(): 页面开始加载
        loadFinished(): 页面加载完成

    使用示例:
        browser = ElaBrowserEmbedder(
            webview_path=Path("chrome.exe"),
            port=9023,
            debug_port=9222,
            parent=self
        )
        browser.embed("http://example.com", window_title="MyBrowser")
    """

    loadStarted = pyqtSignal()
    loadFinished = pyqtSignal()
    domContentReady = pyqtSignal()
    pageError = pyqtSignal(str, str)
    networkRequest = pyqtSignal(str, str, str)
    networkResponse = pyqtSignal(str, int, str)
    logMessage = pyqtSignal(str, int)
    embedCompleted = pyqtSignal(bool)
    consoleMessage = pyqtSignal(str, str)
    fileDropped = pyqtSignal(str)

    _debug_port_counter = 9222
    _freed_ports: set[int] = set()
    _instances: weakref.WeakSet = weakref.WeakSet()

    @classmethod
    def _alloc_debug_port(cls) -> int:
        if cls._freed_ports:
            return cls._freed_ports.pop()
        cls._debug_port_counter += 1
        return cls._debug_port_counter

    @classmethod
    def getAllInstances(cls) -> list:
        """返回所有活跃实例"""
        return list(cls._instances)

    @classmethod
    def closeAllInstances(cls) -> None:
        """关闭所有活跃实例"""
        for instance in list(cls._instances):
            instance.release()

    @staticmethod
    def _checkDependencies() -> None:
        if win32gui is None:
            raise ImportError(
                "ElaBrowserEmbedder 需要 pywin32，请运行: uv pip install pywin32"
            )

    def __init__(
        self,
        webview_path: Path,
        debug_port: Optional[int] = None,
        browser_args: Optional[list[str]] = None,
        parent: Optional[QWidget] = None,
    ):
        self._checkDependencies()
        super().__init__(parent)
        _ensure_ime_filter()
        ElaBrowserEmbedder._instances.add(self)

        self._webview_path = webview_path
        self._debug_port = debug_port or self._alloc_debug_port()
        self._browser_args = browser_args or []
        self._browser_process: Optional[QProcess] = None
        self._controller: Optional[_BrowserController] = None
        self._target_hwnd: Optional[int] = None
        self._original_parent: Optional[int] = None
        self._original_style: Optional[int] = None
        self._original_ex_style: Optional[int] = None
        self._original_rect: Optional[tuple] = None
        self._pending_window_title: Optional[str] = None
        self._pending_connect_cdp: bool = False
        self._browser_embedTimer: Optional[QTimer] = None
        self._network_mgr: Optional[QNetworkAccessManager] = None
        self._debug_url_timer: Optional[QTimer] = None
        self._debug_url_retries: int = 0
        self._debug_url_max_retries: int = 0
        self._debug_url_callback: Optional[Callable] = None
        self._last_dropped_file_path: Optional[str] = None
        self._last_dropped_file_time: float = 0
        self._ole_drop_target: Any = None
        self._ole_target_hwnd: Optional[int] = None

    def embed(
        self,
        url: Union[str, Path],
        window_title: Optional[str] = None,
        connect_cdp: bool = True,
    ) -> None:
        """嵌入浏览器并导航到指定 URL（非阻塞）

        :param url: 目标 URL 或本地文件 Path
        :param window_title: 浏览器窗口标题。设置时按标题查找窗口，
            不设置时自动通过浏览器进程 PID 查找窗口。
        :param connect_cdp: 是否连接 CDP（用于页面加载监控）
            CDP 连接会在窗口嵌入成功后自动启动，完成后触发 embedCompleted 信号

        使用示例:
            browser.embed("http://example.com")
            browser.embed(Path("/path/to/page.html"))
            browser.embedCompleted.connect(lambda ok: print("嵌入完成" if ok else "失败"))
        """
        if isinstance(url, Path):
            url = url.as_uri()
        if self._embeddedInfo is not None:
            self._log("已有嵌入窗口，请先调用 release()", 30)
            return

        if (
            self._browser_process is not None
            and self._browser_process.state() != QProcess.NotRunning
        ):
            self._log("浏览器进程已在运行，请先调用 release()", 30)
            return

        self._pending_window_title = window_title
        self._pending_connect_cdp = connect_cdp
        self._start_browser_process(url)
        self._startEmbedTimer(window_title)

    def _start_browser_process(self, url: str) -> None:
        args = [
            f"--app={url}",
            "--incognito",
            "--no-first-run",
            "--disable-sync",
            # "--kiosk",
            "--window-position=-9999,-9999",
            f"--remote-debugging-port={self._debug_port}",
            "--remote-allow-origins=*",
        ]
        args.extend(self._browser_args)

        self._browser_process = QProcess(self)
        self._browser_process.setProgram(str(self._webview_path))
        self._browser_process.setArguments(args)
        self._browser_process.readyReadStandardOutput.connect(self._on_browser_stdout)
        self._browser_process.readyReadStandardError.connect(self._on_browser_stderr)
        self._browser_process.start()

    def _on_browser_stdout(self) -> None:
        data = bytes(self._browser_process.readAllStandardOutput()).decode(
            errors="replace"
        )
        if data.strip():
            self._log(f"[stdout] {data.strip()}", 10)

    def _on_browser_stderr(self) -> None:
        data = bytes(self._browser_process.readAllStandardError()).decode(
            errors="replace"
        )
        if data.strip():
            self._log(f"[stderr] {data.strip()}", 20)

    def _findWindowByPid(self) -> int:
        """通过进程 PID 查找属于该进程的第一个可见窗口。"""
        if not win32process or not self._browser_process:
            return 0
        pid = self._browser_process.processId()
        if not pid:
            return 0
        results: list[int] = []

        def enum_callback(hwnd: int, _) -> bool:
            if win32gui.IsWindowVisible(hwnd):
                try:
                    _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if window_pid == pid:
                        results.append(hwnd)
                except Exception:  # noqa
                    pass
            return True

        try:
            win32gui.EnumWindows(enum_callback, None)
        except Exception:  # noqa
            return 0
        return results[0] if results else 0

    def _startEmbedTimer(
        self, window_title: Optional[str] = None, timeout: float = 30
    ) -> None:
        self._embedTimeout = timeout
        self._embed_start_time = time.time()
        self._browser_embedTimer = QTimer(self)
        self._browser_embedTimer.timeout.connect(self._onEmbedTimerTimeout)
        self._browser_embedTimer.start(500)

    def _onEmbedTimerTimeout(self) -> None:
        elapsed = time.time() - self._embed_start_time
        if elapsed > self._embedTimeout:
            if self._browser_embedTimer:
                self._browser_embedTimer.stop()
            title = self._pending_window_title or "未知标题"
            self.windowNotFound.emit(f"等待窗口 '{title}' 超时")
            self._pending_window_title = None
            self._cleanup_browser()
            return

        if self._pending_window_title:
            hwnd = self.findWindowByTitle(self._pending_window_title)
            if (
                hwnd
                and win32process
                and self._browser_process
                and self._browser_process.state() == QProcess.Running
            ):
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if pid != self._browser_process.processId():
                        hwnd = 0
                except Exception:  # noqa
                    hwnd = 0
        else:
            hwnd = self._findWindowByPid()
        if hwnd:
            if self._browser_embedTimer:
                self._browser_embedTimer.stop()
            self._pending_window_title = None
            self._embedHwnd(hwnd)
            if self._pending_connect_cdp:
                self._start_cdp_connection()
            else:
                self.embedCompleted.emit(True)

    def _embedHwnd(self, hwnd: int) -> None:
        self._target_hwnd = hwnd

        self._original_parent = win32gui.GetParent(hwnd)
        self._original_style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        self._original_ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        self._original_rect = win32gui.GetWindowRect(hwnd)

        if self._embeddedInfo:
            ElaWindowEmbedder.release(self)

        self._tryEmbedOnce(hwnd)
        if self._original_rect and self._original_rect[0] < -5000:
            w = self._original_rect[2] - self._original_rect[0]
            h = self._original_rect[3] - self._original_rect[1]
            screen = win32gui.GetWindowRect(win32gui.GetDesktopWindow())
            cx = screen[0] + (screen[2] - screen[0] - w) // 2
            cy = screen[1] + (screen[3] - screen[1] - h) // 2
            self._original_rect = (cx, cy, cx + w, cy + h)
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        try:
            self._install_drop_interceptor(hwnd)
        except Exception as e:  # noqa
            print(f"[ElaBrowserEmbedder] 拖放拦截安装失败: {e}")

    def _install_drop_interceptor(self, hwnd: int) -> None:
        """通过 COM IDropTarget 在浏览器 HWND 上拦截 OLE 拖放。

        替换 Chrome 的 OLE 拖放目标为我们自己的 IDropTarget。
        在 Drop() 中提取文件路径 → 发射信号 → 返回 DROPEFFECT_NONE 拒绝。
        """
        try:
            from comtypes import IUnknown, GUID, HRESULT, COMMETHOD, COMObject
            from ctypes import (
                POINTER,
                c_uint32,
                c_void_p,
                create_unicode_buffer,
                byref,
                cast,
            )

            OLE32 = ctypes.windll.ole32
            SHELL32 = ctypes.windll.shell32

            # 定义 IDropTarget COM 接口
            class _IDropTarget(IUnknown):
                _iid_ = GUID("{00000122-0000-0000-C000-000000000046}")
                _methods_ = [
                    COMMETHOD(
                        [],
                        HRESULT,
                        "DragEnter",
                        (["in"], c_void_p, "pDataObj"),
                        (["in"], c_uint32, "grfKeyState"),
                        (["in"], c_void_p, "pt"),
                        (["in", "out"], POINTER(c_uint32), "pdwEffect"),
                    ),
                    COMMETHOD(
                        [],
                        HRESULT,
                        "DragOver",
                        (["in"], c_uint32, "grfKeyState"),
                        (["in"], c_void_p, "pt"),
                        (["in", "out"], POINTER(c_uint32), "pdwEffect"),
                    ),
                    COMMETHOD([], HRESULT, "DragLeave"),
                    COMMETHOD(
                        [],
                        HRESULT,
                        "Drop",
                        (["in"], c_void_p, "pDataObj"),
                        (["in"], c_uint32, "grfKeyState"),
                        (["in"], c_void_p, "pt"),
                        (["in", "out"], POINTER(c_uint32), "pdwEffect"),
                    ),
                ]

            class _ChromeDropTarget(COMObject):
                _com_interfaces_ = [_IDropTarget]

                def __init__(self, embedder):
                    super().__init__()
                    self._embedder = embedder
                    self._cached_path = ""

                @staticmethod
                def _normalize_drop_effect(pdwEffect):
                    allowed = pdwEffect[0]
                    if allowed & 1:
                        pdwEffect[0] = 1
                    elif allowed & 2:
                        pdwEffect[0] = 2
                    elif allowed & 4:
                        pdwEffect[0] = 4
                    else:
                        pdwEffect[0] = 0

                def DragEnter(self, pDataObj, grfKeyState, pt, pdwEffect):
                    self._normalize_drop_effect(pdwEffect)
                    self._cached_path = self._extract_h_drop(pDataObj)
                    return 0

                def DragOver(self, grfKeyState, pt, pdwEffect):
                    self._normalize_drop_effect(pdwEffect)
                    return 0

                def DragLeave(self):
                    if self._cached_path:
                        self._embedder._on_dropped_file(self._cached_path)
                    self._cached_path = ""

                def Drop(self, pDataObj, grfKeyState, pt, pdwEffect):
                    if self._cached_path:
                        self._embedder._on_dropped_file(self._cached_path)
                    else:
                        path = self._extract_h_drop(pDataObj)
                        if path:
                            self._embedder._on_dropped_file(path)
                    pdwEffect[0] = 0
                    self._cached_path = ""
                    return 0

                def _extract_h_drop(self, pDataObj) -> str:
                    try:
                        vtable = c_void_p.from_address(pDataObj).value
                        slot3_addr = vtable + 3 * ctypes.sizeof(c_void_p)
                        func_ptr = c_void_p.from_address(slot3_addr).value
                        GETDATA = ctypes.WINFUNCTYPE(
                            ctypes.c_long, c_void_p, c_void_p, c_void_p
                        )
                        GetData = GETDATA(func_ptr)

                        class _FormatEtc(ctypes.Structure):
                            _fields_ = [
                                ("cfFormat", ctypes.c_uint16),
                                ("_pad1", ctypes.c_uint16),
                                ("ptd", c_void_p),
                                ("dwAspect", c_uint32),
                                ("lindex", ctypes.c_int32),
                                ("tymed", c_uint32),
                            ]

                        class _StgMedium(ctypes.Structure):
                            _fields_ = [
                                ("tymed", c_uint32),
                                ("_pad1", c_uint32),
                                ("hGlobal", c_void_p),
                                ("pUnkForRelease", c_void_p),
                            ]

                        fmt = _FormatEtc()
                        fmt.cfFormat = 15
                        fmt.ptd = None
                        fmt.dwAspect = 1
                        fmt.lindex = -1
                        fmt.tymed = 1

                        stg = _StgMedium()
                        hr = GetData(pDataObj, byref(fmt), byref(stg))
                        if hr != 0:
                            return ""
                        if not stg.hGlobal:
                            OLE32.ReleaseStgMedium(byref(stg))
                            return ""
                        p = ctypes.windll.kernel32.GlobalLock(stg.hGlobal)
                        if not p:
                            OLE32.ReleaseStgMedium(byref(stg))
                            return ""
                        buf = create_unicode_buffer(260)
                        SHELL32.DragQueryFileW(c_void_p(p), 0, buf, 260)
                        result = buf.value
                        ctypes.windll.kernel32.GlobalUnlock(stg.hGlobal)
                        OLE32.ReleaseStgMedium(byref(stg))
                        return result
                    except Exception:  # noqa
                        return ""

            self._ole_drop_target = _ChromeDropTarget(self)
            pdt = cast(
                self._ole_drop_target._com_pointers_[_IDropTarget._iid_],
                c_void_p,
            )

            # 先注销旧的拖放注册，再注册我们的
            OLE32.RevokeDragDrop(hwnd)
            hr = OLE32.RegisterDragDrop(hwnd, pdt)
            if hr == 0:
                self._ole_target_hwnd = hwnd
            else:
                print(f"[ElaBrowserEmbedder] RegisterDragDrop 失败: {hr:#010x}")
                self._ole_drop_target = None
        except ImportError:
            print("[ElaBrowserEmbedder] comtypes 未安装，使用 CDP 后备检测")
        except Exception as e:  # noqa
            print(f"[ElaBrowserEmbedder] OLE 拖放拦截安装失败: {e}")

    def _remove_drop_interceptor(self) -> None:
        if hasattr(self, "_ole_target_hwnd") and self._ole_target_hwnd:
            try:
                ctypes.windll.ole32.RevokeDragDrop(self._ole_target_hwnd)
            except Exception:  # noqa
                pass
            self._ole_target_hwnd = None
        self._ole_drop_target = None

    def _log(self, message: str, level: int = 30) -> None:
        self.logMessage.emit(message, level)

    # ---- 异步 CDP 连接 ----

    def _start_cdp_connection(self) -> None:
        """启动 CDP 连接流程（非阻塞）"""
        self._start_debug_url_polling(self._on_debugger_url_obtained)

    def _start_debug_url_polling(
        self, callback: Callable[[str], None], timeout: float = 15
    ) -> None:
        """通过 QTimer + QNetworkAccessManager 异步轮询调试 URL"""
        self._debug_url_callback = callback
        self._debug_url_retries = 0
        self._debug_url_max_retries = int(timeout / 0.5)

        self._network_mgr = QNetworkAccessManager(self)
        self._network_mgr.finished.connect(self._on_debug_url_response)

        self._debug_url_timer = QTimer(self)
        self._debug_url_timer.setSingleShot(True)
        self._debug_url_timer.timeout.connect(self._do_debug_url_request)

        self._do_debug_url_request()

    def _do_debug_url_request(self) -> None:
        if self._debug_url_retries >= self._debug_url_max_retries:
            self._log("获取调试 URL 超时", 40)
            self.embedCompleted.emit(False)
            self._cleanup_debug_url_polling()
            return

        url = QUrl(f"http://127.0.0.1:{self._debug_port}/json")
        self._network_mgr.get(QNetworkRequest(url))
        self._debug_url_retries += 1

    def _on_debug_url_response(self, reply: QNetworkReply) -> None:
        if reply.error():
            self._log(f"CDP 调试端口尚未就绪: {reply.errorString()}", 10)
            self._debug_url_timer.start(500)
            reply.deleteLater()
            return

        try:
            data = json.loads(bytes(reply.readAll()).decode())
            if data:
                debugger_url = data[0].get("webSocketDebuggerUrl")
                if debugger_url:
                    cb = self._debug_url_callback
                    self._cleanup_debug_url_polling()
                    if cb:
                        cb(debugger_url)
                    reply.deleteLater()
                    return
        except Exception as e:
            self._log(f"CDP 调试端口响应解析失败: {e}", 20)

        self._debug_url_timer.start(500)
        reply.deleteLater()

    def _cleanup_debug_url_polling(self) -> None:
        if self._debug_url_timer:
            self._debug_url_timer.stop()
            self._debug_url_timer.deleteLater()
            self._debug_url_timer = None
        if self._network_mgr:
            try:
                self._network_mgr.finished.disconnect(self._on_debug_url_response)
            except (TypeError, RuntimeError):
                pass
            self._network_mgr.deleteLater()
            self._network_mgr = None
        self._debug_url_callback = None

    def _on_debugger_url_obtained(self, debugger_url: str) -> None:
        self._controller = _BrowserController(
            debugger_url=debugger_url, log_func=self._log
        )
        self._controller.set_loadStarted_callback(lambda: self.loadStarted.emit())
        self._controller.set_loadFinished_callback(lambda: self.loadFinished.emit())
        self._controller.cdpReady.connect(self._on_cdpReady)
        self._controller.errorOccurred.connect(self._onCdpError)
        self._controller.consoleMessage.connect(self.consoleMessage)
        self._controller.domContentReady.connect(self.domContentReady)
        self._controller.pageError.connect(self.pageError)
        self._controller.networkRequest.connect(self.networkRequest)
        self._controller.networkResponse.connect(self.networkResponse)
        self._controller.connect()

    def _on_dropped_file(self, path: str) -> None:
        now = time.time()
        if (
            path == self._last_dropped_file_path
            and now - self._last_dropped_file_time < 0.5
        ):
            return
        self._last_dropped_file_path = path
        self._last_dropped_file_time = now
        self.fileDropped.emit(path)

    def _on_cdpReady(self) -> None:
        self._log("CDP 连接就绪", 20)
        self._controller._dropped_file_callback = self._on_dropped_file
        self._inject_block_new_window()
        self.embedCompleted.emit(True)

    def _inject_block_new_window(self) -> None:
        """注入脚本，防止网站通过 window.open 或 target=_blank 创建新窗口。"""
        script = """
(function() {
    var origOpen = window.open;
    window.open = function(url) {
        if (url) window.location.href = url;
        return window;
    };
    document.addEventListener('click', function(e) {
        var a = e.target.closest('a');
        if (a && a.target === '_blank') {
            e.preventDefault();
            if (a.href) window.location.href = a.href;
        }
    }, true);
    document.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
    }, true);
})();
"""
        self._controller.sendCommand(
            "Page.addScriptToEvaluateOnNewDocument", {"source": script}
        )
        self._controller.sendCommand(
            "Runtime.evaluate", {"expression": script, "returnByValue": False}
        )
        self._log("已注入新窗口拦截脚本", 20)

    def _onCdpError(self, error: str) -> None:
        self._log(f"CDP 连接失败: {error}", 40)
        self.embedCompleted.emit(False)

    def reload(self, callback: Optional[Callable[[Any], None]] = None) -> None:
        """刷新当前页面（非阻塞）

        :param callback: 可选回调，刷新完成时调用
        """
        if self._controller:
            self._controller.reload(callback=callback)

    def navigate(
        self, url: str, callback: Optional[Callable[[Any], None]] = None
    ) -> None:
        """导航到指定 URL（非阻塞）

        :param url: 目标 URL
        :param callback: 可选回调，导航完成时调用
        """
        if self._controller:
            self._controller.navigate(url, callback=callback)

    def load_url(
        self, url: Union[str, Path], callback: Optional[Callable[[Any], None]] = None
    ) -> Optional[int]:
        """加载指定 URL 或本地文件（非阻塞），与 QWebEnginePage.loadUrl() 行为一致。

        :param url: 目标 URL 或本地文件 Path
        :param callback: 可选回调，加载完成时调用
        :returns: 消息 ID（调试用），CDP 未就绪时返回 None
        """
        if isinstance(url, Path):
            url = url.as_uri()
        if self._controller:
            return self._controller.navigate(url, callback=callback)
        return None

    def runJS(
        self, script: str, callback: Optional[Callable[[Any], None]] = None
    ) -> Optional[int]:
        """执行 JavaScript 代码（非阻塞）

        :param script: JavaScript 代码
        :param callback: 可选回调，收到执行结果时调用
        :returns: 消息 ID（调试用），或 None（CDP未就绪）
        """
        if self._controller:
            return self._controller.runJS(script, callback=callback)
        return None

    def _cleanup_browser(self) -> None:
        """清理浏览器进程和CDP连接"""
        if self._controller:
            self._controller.close()
            self._controller = None

        if self._browser_process:
            if self._browser_process.state() == QProcess.Running:
                self._browser_process.terminate()
                if not self._browser_process.waitForFinished(2000):
                    self._browser_process.kill()
                    self._browser_process.waitForFinished(100)
            self._browser_process = None

    def release(self) -> None:
        """释放浏览器窗口并终止浏览器进程"""
        if self._browser_embedTimer:
            self._browser_embedTimer.stop()
            self._browser_embedTimer = None
        self._pending_window_title = None
        self._cleanup_debug_url_polling()

        if self._target_hwnd:
            try:
                win32gui.ShowWindow(self._target_hwnd, win32con.SW_HIDE)
                win32gui.SetParent(self._target_hwnd, self._original_parent)
                if self._original_style is not None:
                    style_no_visible = self._original_style & ~win32con.WS_VISIBLE
                    win32gui.SetWindowLong(
                        self._target_hwnd, win32con.GWL_STYLE, style_no_visible
                    )
                if self._original_ex_style is not None:
                    win32gui.SetWindowLong(
                        self._target_hwnd, win32con.GWL_EXSTYLE, self._original_ex_style
                    )
                if self._original_rect:
                    win32gui.SetWindowPos(
                        self._target_hwnd,
                        0,
                        self._original_rect[0],
                        self._original_rect[1],
                        self._original_rect[2] - self._original_rect[0],
                        self._original_rect[3] - self._original_rect[1],
                        win32con.SWP_HIDEWINDOW
                        | win32con.SWP_NOACTIVATE
                        | win32con.SWP_NOZORDER,
                    )
            except Exception as e:
                self._log(f"还原窗口状态失败: {e}", 30)

        self._target_hwnd = None
        self._original_parent = None
        self._original_style = None
        self._original_ex_style = None
        self._original_rect = None

        self._remove_drop_interceptor()
        ElaWindowEmbedder.release(self, destroy=True)

        self._cleanup_browser()
        if hasattr(self, "_debug_port") and self._debug_port:
            ElaBrowserEmbedder._freed_ports.add(self._debug_port)

    def closeEvent(self, event) -> None:
        """窗口关闭时释放资源。"""
        self.release()
        super().closeEvent(event)

    def deleteLater(self) -> None:
        self.release()
        super().deleteLater()
