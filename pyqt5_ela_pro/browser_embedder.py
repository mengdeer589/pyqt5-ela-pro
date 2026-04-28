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

import json
import time
import weakref
from pathlib import Path
from typing import Optional, Any, Callable

from PyQt5.QtCore import pyqtSignal, QTimer, QObject, QUrl, QProcess
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt5.QtWebSockets import QWebSocket
from PyQt5.QtWidgets import QWidget

from .window_embedder import ElaWindowEmbedder

try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None
try:
    import win32process
except ImportError:
    win32process = None


class _BrowserController(QObject):
    """CDP WebSocket 客户端（内部类）- 信号驱动版本"""

    cdpReady = pyqtSignal()
    errorOccurred = pyqtSignal(str)
    consoleMessage = pyqtSignal(str, str)

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
        self.cdpReady.emit()

    def _on_connect_timeout(self) -> None:
        self._log("CDP WebSocket 连接超时", 30)
        self.errorOccurred.emit("WebSocket 连接超时")
        self._running = False
        if self._ws:
            self._ws.close()
            self._ws = None

    def _on_error(self, error) -> None:
        self._log(f"WebSocket 错误: {error}", 30)
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
            if method and not method.startswith("Debugger"):
                self._log(f"[CDP Event] {method}: {params}", 10)
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

    def set_loadStarted_callback(self, callback: Callable) -> None:
        self._loadStarted_callback = callback

    def set_loadFinished_callback(self, callback: Callable) -> None:
        self._loadFinished_callback = callback

    def sendCommand(
        self, method: str, params: Optional[dict] = None, callback: Optional[Callable[[Any], None]] = None
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

    def runJS(self, script: str, callback: Optional[Callable[[Any], None]] = None) -> int:
        """执行 JavaScript 代码（非阻塞）

        :param script: JavaScript 代码
        :param callback: 可选回调
        :returns: 消息 ID
        """
        return self.sendCommand(
            "Runtime.evaluate", {"expression": script, "returnByValue": True}, callback=callback
        )

    def navigate(self, url: str, callback: Optional[Callable[[Any], None]] = None) -> int:
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
    logMessage = pyqtSignal(str, int)
    embedCompleted = pyqtSignal(bool)
    consoleMessage = pyqtSignal(str, str)

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
        ElaBrowserEmbedder._instances.add(self)

        self._webview_path = webview_path
        self._debug_port = debug_port or self._alloc_debug_port()
        self._browser_args = browser_args or []
        self._browser_process: Optional[QProcess] = None
        self._controller: Optional[_BrowserController] = None
        self._target_hwnd: Optional[int] = None
        self._original_parent: Optional[int] = None
        self._original_style: Optional[int] = None
        self._original_exstyle: Optional[int] = None
        self._original_rect: Optional[tuple] = None
        self._pending_window_title: Optional[str] = None
        self._pending_connect_cdp: bool = False
        self._browser_embedTimer: Optional[QTimer] = None
        self._network_mgr: Optional[QNetworkAccessManager] = None
        self._debug_url_timer: Optional[QTimer] = None
        self._debug_url_retries: int = 0
        self._debug_url_max_retries: int = 0
        self._debug_url_callback: Optional[Callable] = None

    def embed(self, url: str, window_title: str, connect_cdp: bool = True) -> None:
        """嵌入浏览器并导航到指定 URL（非阻塞）

        :param url: 目标 URL
        :param window_title: 浏览器窗口标题（必须指定，用于查找窗口）
        :param connect_cdp: 是否连接 CDP（用于页面加载监控）
            CDP 连接会在窗口嵌入成功后自动启动，完成后触发 embedCompleted 信号

        使用示例:
            browser.embed("http://example.com", window_title="MyBrowser")
            browser.embedCompleted.connect(lambda ok: print("嵌入完成" if ok else "失败"))
        """
        if self._embeddedInfo is not None:
            self._log("已有嵌入窗口，请先调用 release()", 30)
            return

        if self._browser_process is not None and self._browser_process.state() != QProcess.NotRunning:
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
            f"--window-position=-9999,-9999",
            f"--remote-debugging-port={self._debug_port}",
            "--remote-allow-origins=*",
        ]
        args.extend(self._browser_args)

        self._browser_process = QProcess(self)
        self._browser_process.setProgram(str(self._webview_path))
        self._browser_process.setArguments(args)
        self._browser_process.readyReadStandardOutput.connect(
            self._on_browser_stdout
        )
        self._browser_process.readyReadStandardError.connect(
            self._on_browser_stderr
        )
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

    def _startEmbedTimer(self, window_title: str, timeout: float = 30) -> None:
        self._embedTimeout = timeout
        self._embed_start_time = time.time()
        self._browser_embedTimer = QTimer(self)
        self._browser_embedTimer.timeout.connect(self._onEmbedTimerTimeout)
        self._browser_embedTimer.start(500)

    def _onEmbedTimerTimeout(self) -> None:
        if not self._pending_window_title:
            if self._browser_embedTimer:
                self._browser_embedTimer.stop()
            return

        elapsed = time.time() - self._embed_start_time
        if elapsed > self._embedTimeout:
            if self._browser_embedTimer:
                self._browser_embedTimer.stop()
            self.windowNotFound.emit(f"等待窗口 '{self._pending_window_title}' 超时")
            self._pending_window_title = None
            self._cleanup_browser()
            return

        hwnd = self.findWindowByTitle(self._pending_window_title)
        if hwnd:
            if (
                win32process
                and self._browser_process
                and self._browser_process.state() == QProcess.Running
            ):
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if pid != self._browser_process.processId():
                        hwnd = 0
                except Exception:
                    hwnd = 0
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
        self._original_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
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
        self._controller.set_loadFinished_callback(
            lambda: self.loadFinished.emit()
        )
        self._controller.cdpReady.connect(self._on_cdpReady)
        self._controller.errorOccurred.connect(self._onCdpError)
        self._controller.consoleMessage.connect(self.consoleMessage)
        self._controller.connect()

    def _on_cdpReady(self) -> None:
        self._log("CDP 连接就绪", 20)
        self.embedCompleted.emit(True)

    def _onCdpError(self, error: str) -> None:
        self._log(f"CDP 连接失败: {error}", 40)
        self.embedCompleted.emit(False)

    def reload(self, callback: Optional[Callable[[Any], None]] = None) -> None:
        """刷新当前页面（非阻塞）

        :param callback: 可选回调，刷新完成时调用
        """
        if self._controller:
            self._controller.reload(callback=callback)

    def navigate(self, url: str, callback: Optional[Callable[[Any], None]] = None) -> None:
        """导航到指定 URL（非阻塞）

        :param url: 目标 URL
        :param callback: 可选回调，导航完成时调用
        """
        if self._controller:
            self._controller.navigate(url, callback=callback)

    def runJS(self, script: str, callback: Optional[Callable[[Any], None]] = None) -> Optional[int]:
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
                if self._original_exstyle is not None:
                    win32gui.SetWindowLong(
                        self._target_hwnd, win32con.GWL_EXSTYLE, self._original_exstyle
                    )
                if self._original_rect:
                    win32gui.SetWindowPos(
                        self._target_hwnd,
                        0,
                        self._original_rect[0],
                        self._original_rect[1],
                        self._original_rect[2] - self._original_rect[0],
                        self._original_rect[3] - self._original_rect[1],
                        win32con.SWP_HIDEWINDOW | win32con.SWP_NOACTIVATE | win32con.SWP_NOZORDER,
                    )
            except Exception as e:
                self._log(f"还原窗口状态失败: {e}", 30)

        self._target_hwnd = None
        self._original_parent = None
        self._original_style = None
        self._original_exstyle = None
        self._original_rect = None

        ElaWindowEmbedder.release(self, destroy=True)

        self._cleanup_browser()
        if hasattr(self, '_debug_port') and self._debug_port:
            ElaBrowserEmbedder._freed_ports.add(self._debug_port)

    def deleteLater(self) -> None:
        self.release()
        super().deleteLater()
