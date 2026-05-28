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
import subprocess
import time
import weakref
from pathlib import Path
from typing import Any, Callable, Optional, Union
from urllib.parse import unquote, urlparse

from PyQt5.QtCore import (QAbstractNativeEventFilter, QObject, QPoint,
                          QProcess, QTimer, QUrl, pyqtSignal)
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtWebSockets import QWebSocket
from PyQt5.QtWidgets import QApplication, QWidget

from .window_embedder import ElaWindowEmbedder

try:
    import win32con  # type: ignore[attr-defined]
    import win32gui  # type: ignore[attr-defined]
except ImportError:
    win32gui = None
    win32con = None
try:
    import win32process  # type: ignore[attr-defined]
except ImportError:
    win32process = None

try:
    from comtypes import (COMMETHOD, GUID,  # type: ignore[attr-defined]
                          HRESULT, COMObject, IUnknown)

    _COM_AVAILABLE = True
except ImportError:
    _COM_AVAILABLE = False


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
        elif method in (
            "Target.targetCreated",
            "Target.attachedToTarget",
            "Target.targetInfoChanged",
        ):
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
        """设置页面开始加载的回调。"""
        self._loadStarted_callback = callback

    def set_loadFinished_callback(self, callback: Callable) -> None:
        """设置页面加载完成的回调。"""
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

        if self._ws is None:
            return -1
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
        (
            "wParam",
            ctypes.c_uint64 if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_uint32,
        ),
        (
            "lParam",
            ctypes.c_uint64 if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_uint32,
        ),
        ("time", ctypes.c_uint32),
        ("pt", ctypes.c_uint64),
    ]


class _ImeForwardFilter(QAbstractNativeEventFilter):
    """Qt 原生事件过滤器，转发 IME 到嵌入的浏览器窗口。"""

    def __init__(self):
        super().__init__()
        self._last_cursor_pos: Optional[tuple[int, int]] = None
        self._last_cursor_hwnd: Optional[int] = None
        self._last_chrome_hwnd: Optional[int] = None

    def _find_at_cursor(self) -> Optional[int]:
        pt = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        pos = (pt.x, pt.y)
        if pos == self._last_cursor_pos:
            return self._last_cursor_hwnd
        self._last_cursor_pos = pos

        w = QApplication.widgetAt(QPoint(pt.x, pt.y))
        hwnd = getattr(w, "_chrome_hwnd", None)
        self._last_cursor_hwnd = hwnd
        return hwnd

    def nativeEventFilter(self, eventType, message):
        if eventType != "windows_generic_MSG":
            return False, 0
        try:
            hwnd = self._find_at_cursor() or None
            msg = _MSG.from_address(message.__int__())

            # Focus transition: Chrome ↔ Qt, only when state changes
            if hwnd != self._last_chrome_hwnd:
                if hwnd:
                    self._last_chrome_hwnd = hwnd
                    ctypes.windll.user32.SetFocus(hwnd)
                else:
                    self._last_chrome_hwnd = None
                    pt = ctypes.wintypes.POINT()
                    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
                    from PyQt5 import sip
                    w = QApplication.widgetAt(QPoint(pt.x, pt.y))
                    try:
                        if w is not None and not sip.isdeleted(w):
                            ctypes.windll.user32.SetFocus(int(w.winId()))
                    except Exception:
                        pass

            # IME forwarding: always forward when cursor is on Chrome
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


_ime_filter = _ImeForwardFilter()
_ime_installed = False


def _ensure_ime_filter() -> None:
    global _ime_installed
    if not _ime_installed:
        try:
            QApplication.instance().installNativeEventFilter(_ime_filter)
            _ime_installed = True
        except Exception:
            pass


# ── 共享 Browser 进程管理器 ─────────────────────────────────

class _BrowserSession:
    """共享 Chrome Browser 进程单例，支持多 --app 窗口共享一个进程。"""

    _instance: Optional[Any] = None  # type: ignore[name-defined]
    _refcount: int = 0

    def __init__(self, webview_path: Path, debug_port: int, profile_dir: Path, browser_args: Optional[list[str]] = None) -> None:
        self._webview_path = webview_path
        self._debug_port = debug_port
        self._profile_dir = profile_dir
        self._process: Optional[QProcess] = None
        self._known_hwnds: set[int] = set()
        self._browser_args = browser_args or []

    @classmethod
    def acquire(cls, webview_path: Path, debug_port: int, profile_dir: Path, browser_args: Optional[list[str]] = None) -> _BrowserSession:
        if cls._instance is not None:
            cls._refcount += 1
            return cls._instance
        cls._instance = cls(webview_path, debug_port, profile_dir, browser_args)
        cls._refcount = 1
        return cls._instance

    def release(self) -> None:
        _BrowserSession._refcount -= 1
        if _BrowserSession._refcount <= 0:
            self._terminate()
            _BrowserSession._instance = None
            _BrowserSession._refcount = 0

    def launch_start(self, url: str, _window_title: str) -> None:
        args = [
            f"--app={url}",
            "--incognito", "--no-first-run", "--disable-sync",
            "--disable-session-crashed-bubble", "--suppress-message-center-popups",
            f"--user-data-dir={self._profile_dir}",
            f"--remote-debugging-port={self._debug_port}",
            "--remote-allow-origins=*",
            "--window-position=-9999,-9999",
        ]
        args.extend(self._browser_args)

        if self._process is None:
            self._process = QProcess()
            self._process.setProgram(str(self._webview_path))
            self._process.setArguments(args)
            self._process.setProcessChannelMode(QProcess.SeparateChannels)
            self._process.start()
        else:
            subprocess.Popen(
                [str(self._webview_path), *args],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.DETACHED_PROCESS,
            )

    def poll_hwnd(self) -> Optional[int]:
        browser_pid = self._process.processId() if self._process else 0
        hwnds: list[int] = []

        def _cb(hwnd, _):
            try:
                if (win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd)
                        and win32gui.GetClassName(hwnd) == "Chrome_WidgetWin_1"
                        and hwnd not in self._known_hwnds
                        and win32gui.GetWindowText(hwnd)):
                    if browser_pid:
                        _, wpid = win32process.GetWindowThreadProcessId(hwnd)
                        if wpid != browser_pid:
                            return True
                    hwnds.append(hwnd)
            except Exception:
                pass
            return True

        win32gui.EnumWindows(_cb, None)

        for hwnd in hwnds:
            self._known_hwnds.add(hwnd)
            return hwnd
        return None

    def _terminate(self) -> None:
        if self._process:
            try:
                if self._process.state() == QProcess.Running:
                    self._process.terminate()
                    self._process.waitForFinished(3000)
                    if self._process.state() == QProcess.Running:
                        self._process.kill()
            except Exception:
                pass
            self._process = None


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

    _instances: weakref.WeakSet = weakref.WeakSet()
    _default_debug_port: int = 9222

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
        if not _COM_AVAILABLE:
            raise ImportError(
                "ElaBrowserEmbedder 需要 comtypes，请运行: uv pip install comtypes"
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
        self._debug_port = debug_port or ElaBrowserEmbedder._default_debug_port
        self._session: Optional[_BrowserSession] = None
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
        self._hwnd_timer: Optional[QTimer] = None
        self._hwnd_retries: int = 0
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
        self._embedded_url: Optional[str] = None

    def _log(self, message: str, level: int = 30) -> None:
        self.logMessage.emit(message, level)

    def embed(
        self,
        url: Union[str, Path],
        window_title: Optional[str] = None,
        connect_cdp: bool = True,
    ) -> None:
        if isinstance(url, Path):
            url = url.as_uri()
        if self._embeddedInfo is not None:
            self._log("已有嵌入窗口，请先调用 release()", 30)
            return
        if self._hwnd_timer is not None:
            self._log("嵌入流程正在进行中", 30)
            return

        import tempfile

        profile_dir = Path(tempfile.gettempdir()) / "pyqt5_ela_browser_profile"
        profile_dir.mkdir(exist_ok=True)

        self._embedded_url = url
        self._session = _BrowserSession.acquire(
            self._webview_path, self._debug_port, profile_dir, self._browser_args
        )

        self._session.launch_start(url, window_title or url)
        self._pending_window_title = window_title or url
        self._pending_connect_cdp = connect_cdp
        self._start_hwnd_polling()

    def _start_hwnd_polling(self) -> None:
        self._hwnd_retries = 0
        self._hwnd_timer = QTimer(self)
        self._hwnd_timer.setSingleShot(True)
        self._hwnd_timer.timeout.connect(self._poll_hwnd)
        self._hwnd_timer.start(0)

    def _poll_hwnd(self) -> None:
        if not self._session:
            self._cleanup_hwnd_polling()
            return

        hwnd = self._session.poll_hwnd()
        if hwnd:
            self._cleanup_hwnd_polling()
            self._embedHwnd(hwnd)
            if self._pending_connect_cdp:
                self._pending_connect_cdp = False
                self._start_cdp_connection()
            return

        self._hwnd_retries += 1
        if self._hwnd_retries >= 60:
            self._cleanup_hwnd_polling()
            self._log(f"等待窗口超时: {self._pending_window_title}", 40)
            return

        self._hwnd_timer.start(500)

    def _cleanup_hwnd_polling(self) -> None:
        if self._hwnd_timer:
            self._hwnd_timer.stop()
            self._hwnd_timer.deleteLater()
            self._hwnd_timer = None
        self._hwnd_retries = 0

    def _cleanup_browser(self) -> None:
        """清理 CDP 连接"""
        if self._controller:
            try:
                self._controller.cdpReady.disconnect(self._on_cdpReady)
            except (TypeError, RuntimeError):
                pass
            try:
                self._controller.errorOccurred.disconnect(self._onCdpError)
            except (TypeError, RuntimeError):
                pass
            try:
                self._controller.consoleMessage.disconnect(self.consoleMessage)
            except (TypeError, RuntimeError):
                pass
            try:
                self._controller.domContentReady.disconnect(self.domContentReady)
            except (TypeError, RuntimeError):
                pass
            try:
                self._controller.pageError.disconnect(self.pageError)
            except (TypeError, RuntimeError):
                pass
            try:
                self._controller.networkRequest.disconnect(self.networkRequest)
            except (TypeError, RuntimeError):
                pass
            try:
                self._controller.networkResponse.disconnect(self.networkResponse)
            except (TypeError, RuntimeError):
                pass
            self._controller.close()
            self._controller = None

    # ---- 公共 API（CDP 操控） ----

    def reload(self, callback: Optional[Callable[[Any], None]] = None) -> None:
        """刷新当前页面（非阻塞）"""
        if self._controller:
            self._controller.reload(callback=callback)

    def navigate(
        self, url: str, callback: Optional[Callable[[Any], None]] = None
    ) -> None:
        """导航到指定 URL（非阻塞）"""
        if self._controller:
            self._controller.navigate(url, callback=callback)

    def load_url(
        self, url: Union[str, Path], callback: Optional[Callable[[Any], None]] = None
    ) -> Optional[int]:
        """加载指定 URL 或本地文件（非阻塞）"""
        if isinstance(url, Path):
            url = url.as_uri()
        if self._controller:
            return self._controller.navigate(url, callback=callback)
        return None

    def runJS(
        self, script: str, callback: Optional[Callable[[Any], None]] = None
    ) -> Optional[int]:
        """执行 JavaScript 代码（非阻塞）"""
        if self._controller:
            return self._controller.runJS(script, callback=callback)
        return None

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
        port = self._session._debug_port if self._session else self._debug_port
        if self._debug_url_retries >= self._debug_url_max_retries:
            self._log("获取调试 URL 超时", 40)
            self.embedCompleted.emit(False)
            self._cleanup_debug_url_polling()
            return

        url = QUrl(f"http://127.0.0.1:{port}/json")
        self._network_mgr.get(QNetworkRequest(url))
        self._debug_url_retries += 1

    def _on_debug_url_response(self, reply) -> None:
        if reply.error():
            self._log(f"CDP 调试端口尚未就绪: {reply.errorString()}", 10)
            self._debug_url_timer.start(500)
            reply.deleteLater()
            return

        try:
            data = json.loads(bytes(reply.readAll()).decode())
            if data:
                debugger_url = None
                for target in data:
                    if target.get("type") == "page":
                        turl = target.get("url", "")
                        if turl == self._embedded_url or turl == f"{self._embedded_url}/" or self._embedded_url == f"{turl}/":
                            debugger_url = target.get("webSocketDebuggerUrl")
                            break
                if not debugger_url:
                    for target in data:
                        if target.get("type") == "page":
                            debugger_url = target.get("webSocketDebuggerUrl")
                            break
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
        self._controller.set_loadStarted_callback(self.loadStarted.emit)
        self._controller.set_loadFinished_callback(self.loadFinished.emit)
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
        ctypes.windll.user32.SetFocus(hwnd)
        try:
            self._install_drop_interceptor(hwnd)
        except Exception as e:  # noqa
            pass

    def _install_drop_interceptor(self, hwnd: int) -> None:
        """通过 COM IDropTarget 在浏览器 HWND 上拦截 OLE 拖放。"""
        if not _COM_AVAILABLE:
            return
        try:
            from ctypes import (POINTER, byref, c_uint32, c_void_p, cast,
                                create_unicode_buffer)

            OLE32 = ctypes.windll.ole32
            try:
                OLE32.OleInitialize(None)
            except Exception:
                pass
            SHELL32 = ctypes.windll.shell32

            # 定义 IDropTarget COM 接口
            class _IDropTarget(IUnknown):
                _iid_ = GUID("{00000122-0000-0000-C000-000000000046}")
                _methods_ = [
                    COMMETHOD([], HRESULT, "DragEnter",
                              (["in"], c_void_p, "pDataObj"),
                              (["in"], c_uint32, "grfKeyState"),
                              (["in"], c_void_p, "pt"),
                              (["in", "out"], POINTER(c_uint32), "pdwEffect")),
                    COMMETHOD([], HRESULT, "DragOver",
                              (["in"], c_uint32, "grfKeyState"),
                              (["in"], c_void_p, "pt"),
                              (["in", "out"], POINTER(c_uint32), "pdwEffect")),
                    COMMETHOD([], HRESULT, "DragLeave"),
                    COMMETHOD([], HRESULT, "Drop",
                              (["in"], c_void_p, "pDataObj"),
                              (["in"], c_uint32, "grfKeyState"),
                              (["in"], c_void_p, "pt"),
                              (["in", "out"], POINTER(c_uint32), "pdwEffect")),
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

                def DragEnter(self, pDataObj, _grfKeyState, _pt, pdwEffect):
                    self._normalize_drop_effect(pdwEffect)
                    self._cached_path = self._extract_h_drop(pDataObj)
                    return 0

                def DragOver(self, _grfKeyState, _pt, pdwEffect):
                    self._normalize_drop_effect(pdwEffect)
                    return 0

                def DragLeave(self):
                    if self._cached_path:
                        self._embedder._on_dropped_file(self._cached_path)
                    self._cached_path = ""

                def Drop(self, pDataObj, _grfKeyState, _pt, pdwEffect):
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
                        GETDATA = ctypes.WINFUNCTYPE(ctypes.c_long, c_void_p, c_void_p, c_void_p)
                        GetData = GETDATA(func_ptr)

                        class _FormatEtc(ctypes.Structure):
                            _fields_ = [
                                ("cfFormat", ctypes.c_uint16), ("_pad1", ctypes.c_uint16),
                                ("ptd", c_void_p), ("dwAspect", c_uint32),
                                ("lindex", ctypes.c_int32), ("tymed", c_uint32),
                            ]
                        class _StgMedium(ctypes.Structure):
                            _fields_ = [
                                ("tymed", c_uint32), ("_pad1", c_uint32),
                                ("hGlobal", c_void_p), ("pUnkForRelease", c_void_p),
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
            pdt = cast(self._ole_drop_target._com_pointers_[_IDropTarget._iid_], c_void_p)
            OLE32.RevokeDragDrop(hwnd)
            hr = OLE32.RegisterDragDrop(hwnd, pdt)
            if hr == 0:
                self._ole_target_hwnd = hwnd
            else:
                self._ole_drop_target = None
        except Exception:  # noqa
            pass

    def _remove_drop_interceptor(self) -> None:
        if hasattr(self, "_ole_target_hwnd") and self._ole_target_hwnd:
            try:
                ctypes.windll.ole32.RevokeDragDrop(self._ole_target_hwnd)
            except Exception:  # noqa
                pass
            self._ole_target_hwnd = None
        self._ole_drop_target = None

    def release(self) -> None:
        """释放浏览器窗口并终止浏览器进程"""
        if self._browser_embedTimer:
            self._browser_embedTimer.stop()
            self._browser_embedTimer = None
        self._pending_window_title = None
        self._cleanup_hwnd_polling()
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
        if self._session:
            self._session.release()
            self._session = None

    def closeEvent(self, event) -> None:
        """窗口关闭时释放资源。"""
        self.release()
        super().closeEvent(event)

    def deleteLater(self) -> None:
        self.release()
        super().deleteLater()
