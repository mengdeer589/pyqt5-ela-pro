"""
浏览器嵌入组件 (Windows + PyQt5)

继承自 ElaWindowEmbedder，添加浏览器启动和管理功能。
需要额外依赖: psutil

使用示例:
    from pyqt5_ela_pro.browser_embedder import ElaBrowserEmbedder
    browser = ElaBrowserEmbedder(
        webview_path=Path("Supermium/chrome.exe"),
        port=9023,
        debug_port=9222,
        parent=self
    )
    browser.embed("http://example.com", window_title="MyBrowser")
"""

from __future__ import annotations

import json
import multiprocessing
import time
import urllib.request
from pathlib import Path
from typing import Optional, Any, Callable

from PyQt5.QtCore import pyqtSignal, QTimer, QObject, QEventLoop, QUrl
from PyQt5.QtWebSockets import QWebSocket
from PyQt5.QtWidgets import QWidget

from .window_embedder import ElaWindowEmbedder

try:
    import win32gui
    import win32con
except ImportError:
    raise ImportError("ElaBrowserEmbedder 需要 pywin32，请运行: uv pip install pywin32")


def _run_browser_process(command: list, pid_shared) -> None:
    """在子进程中运行浏览器"""
    import subprocess

    proc = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    pid_shared.value = proc.pid


class _BrowserController(QObject):
    """CDP WebSocket 客户端（内部类）"""

    def __init__(
        self,
        debugger_url: Optional[str] = None,
        debug_port: int = 9222,
        timeout: float = 5.0,
        log_func: Optional[Callable[[str, int], None]] = None,
    ):
        super().__init__()
        self._debugger_url = debugger_url
        self._debug_port = debug_port
        self._timeout = timeout
        self._log_func = log_func
        self._ws: Optional[QWebSocket] = None
        self._message_id: int = 0
        self._callbacks: dict[int, Callable] = {}
        self._pending_results: dict[int, Any] = {}
        self._event_loop: Optional[QEventLoop] = None
        self._running: bool = False
        self._load_started_callback: Optional[Callable] = None
        self._load_finished_callback: Optional[Callable] = None

        if not debugger_url and debug_port:
            self._debugger_url = self._get_debugger_url()

    def _log(self, message: str, level: int = 30) -> None:
        if self._log_func:
            self._log_func(message, level)

    def _get_debugger_url(self, timeout: float = 10) -> str:
        start = time.time()
        while time.time() - start < timeout:
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{self._debug_port}/json", timeout=2
                ) as resp:
                    targets = json.loads(resp.read())
                    if targets:
                        return targets[0]["webSocketDebuggerUrl"]
            except Exception:
                pass
            time.sleep(0.5)
        raise RuntimeError(f"无法连接到调试端口 {self._debug_port}")

    def connect(self) -> None:
        self._ws = QWebSocket()
        self._ws.error.connect(self._on_error)
        self._ws.textMessageReceived.connect(self._on_text_message)

        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        self._ws.connected.connect(loop.quit)
        self._ws.open(QUrl(self._debugger_url))
        timer.start(10000)
        loop.exec_()
        timer.stop()

        self._running = True
        self.send_command("Page.enable")

    def _on_error(self, error):
        self._log(f"WebSocket 错误: {error}", 30)
        if self._event_loop and self._event_loop.isRunning():
            self._event_loop.quit()

    def _on_text_message(self, message: str) -> None:
        try:
            data = json.loads(message)
        except Exception as e:
            self._log(f"CDP 消息解析失败: {e}", 30)
            return

        if "id" in data:
            msg_id = data["id"]
            result = data.get("result")
            self._pending_results[msg_id] = result
            if msg_id in self._callbacks:
                self._callbacks.pop(msg_id)()
            if self._event_loop and self._event_loop.isRunning():
                self._event_loop.quit()
        else:
            method = data.get("method")
            params = data.get("params", {})
            if method and not method.startswith("Debugger"):
                self._log(f"[CDP Event] {method}: {params}", 10)
            self._handle_event(method, params)

    def _handle_event(self, method: Optional[str], params: dict) -> None:
        if method == "Page.loadEventFired":
            if self._load_started_callback:
                self._load_started_callback()
        elif method == "Page.frameStoppedLoading":
            if self._load_finished_callback:
                self._load_finished_callback()

    def set_load_started_callback(self, callback: Callable) -> None:
        self._load_started_callback = callback

    def set_load_finished_callback(self, callback: Callable) -> None:
        self._load_finished_callback = callback

    def send_command(self, method: str, params: Optional[dict] = None) -> Any:
        msg_id = self._message_id
        self._message_id += 1

        cmd: dict = {"id": msg_id, "method": method}
        if params:
            cmd["params"] = params

        self._event_loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self._event_loop.quit)
        timer.start(int(self._timeout * 1000))

        self._ws.sendTextMessage(json.dumps(cmd))
        self._event_loop.exec_()
        timer.stop()
        self._event_loop = None

        return self._pending_results.pop(msg_id, None)

    def run_js(self, script: str) -> Any:
        """执行 JavaScript 代码

        :param script: JavaScript 代码
        :returns: 执行结果
        """
        return self.send_command(
            "Runtime.evaluate", {"expression": script, "returnByValue": True}
        )

    def navigate(self, url: str) -> Any:
        """导航到指定 URL

        :param url: 目标 URL
        :returns: 执行结果
        """
        return self.send_command("Page.navigate", {"url": url})

    def reload(self) -> Any:
        """刷新页面

        :returns: 执行结果
        """
        return self.send_command("Page.reload")

    def close(self) -> None:
        self._running = False
        if self._ws:
            self._ws.close()
            self._ws = None


class ElaBrowserEmbedder(ElaWindowEmbedder):
    """浏览器嵌入组件

    继承自 ElaWindowEmbedder，添加浏览器启动和管理功能。

    依赖: psutil

    信号（继承自 ElaWindowEmbedder）:
        window_embedded(int): 窗口嵌入成功
        window_released(int): 窗口释放成功
        window_not_found(str): 等待窗口时未找到
        embed_error(str): 嵌入出错
        embed_timeout(): 等待窗口嵌入超时

    新增信号:
        load_started(): 页面开始加载
        load_finished(): 页面加载完成

    使用示例:
        browser = ElaBrowserEmbedder(
            webview_path=Path("Supermium/chrome.exe"),
            port=9023,
            debug_port=9222,
            parent=self
        )
        browser.embed("http://example.com", window_title="MyBrowser")
    """

    load_started = pyqtSignal()
    load_finished = pyqtSignal()
    log_message = pyqtSignal(str, int)

    _debug_port_counter = 9222
    _instances: set = set()

    @classmethod
    def _alloc_debug_port(cls) -> int:
        cls._debug_port_counter += 1
        return cls._debug_port_counter

    @classmethod
    def get_all_instances(cls) -> list:
        """返回所有活跃实例"""
        return list(cls._instances)

    @classmethod
    def close_all_instances(cls) -> None:
        """关闭所有活跃实例"""
        for instance in list(cls._instances):
            instance.release()
        cls._instances.clear()

    def __init__(
        self,
        webview_path: Path,
        port: int = 9023,
        debug_port: Optional[int] = None,
        parent: Optional[QWidget] = None,
    ):
        self._check_dependencies()
        super().__init__(parent)
        ElaBrowserEmbedder._instances.add(self)

        self._webview_path = webview_path
        self._port = port
        self._debug_port = debug_port or self._alloc_debug_port()
        self._browser_process: Optional[multiprocessing.Process] = None
        self._browser_pid: Optional[multiprocessing.Value] = None
        self._controller: Optional[_BrowserController] = None
        self._target_hwnd: Optional[int] = None
        self._original_parent: Optional[int] = None
        self._original_style: Optional[int] = None
        self._original_exstyle: Optional[int] = None
        self._original_rect: Optional[tuple] = None
        self._pending_window_title: Optional[str] = None
        self._browser_embed_timer: Optional[QTimer] = None

    @staticmethod
    def _check_dependencies() -> None:
        """检查可选依赖是否已安装"""
        missing = []
        try:
            import psutil
        except ImportError:
            missing.append("psutil")

        if missing:
            raise ImportError(
                f"ElaBrowserEmbedder 需要以下依赖: {', '.join(missing)}\n"
                f"请运行: uv pip install {' '.join(missing)}"
            )

    def embed(self, url: str, window_title: str, connect_cdp: bool = True) -> None:
        """嵌入浏览器并导航到指定 URL

        :param url: 目标 URL
        :param window_title: 浏览器窗口标题（必须指定，用于查找窗口）
        :param connect_cdp: 是否连接 CDP（用于页面加载监控）

        使用示例:
            browser.embed("http://example.com", window_title="MyBrowser")
        """
        if self._embedded_info is not None:
            self._log("已有嵌入窗口，请先调用 release()", 30)
            return

        if self._browser_process is not None and self._browser_process.is_alive():
            self._log("浏览器进程已在运行，请先调用 release()", 30)
            return

        self._pending_window_title = window_title
        self._start_browser_process(url)
        self._start_embed_timer(window_title)

        if connect_cdp:
            self._connect_cdp()

    def _start_browser_process(self, url: str) -> None:
        cache_dir = Path.cwd() / "runtime" / "cache" / f"browser_{self._debug_port}"
        cache_dir.mkdir(parents=True, exist_ok=True)

        command = [
            str(self._webview_path),
            f"--app={url}",
            "--incognito",
            "--disable-web-security",
            "--no-first-run",
            "--disable-sync",
            "--kiosk",
            "--start-maximized",
            f"--remote-debugging-port={self._debug_port}",
            "--remote-allow-origins=*",
            f"--user-data-dir={cache_dir}",
        ]

        self._browser_pid = multiprocessing.Value("i", 0)
        self._browser_process = multiprocessing.Process(
            target=_run_browser_process, args=(command, self._browser_pid), daemon=True
        )
        self._browser_process.start()

    def _start_embed_timer(self, window_title: str, timeout: float = 30) -> None:
        self._embed_timeout = timeout
        self._embed_start_time = time.time()
        self._browser_embed_timer = QTimer(self)
        self._browser_embed_timer.timeout.connect(self._on_embed_timer_timeout)
        self._browser_embed_timer.start(500)

    def _on_embed_timer_timeout(self) -> None:
        if not self._pending_window_title:
            if self._browser_embed_timer:
                self._browser_embed_timer.stop()
            return

        elapsed = time.time() - self._embed_start_time
        if elapsed > self._embed_timeout:
            if self._browser_embed_timer:
                self._browser_embed_timer.stop()
            self.window_not_found.emit(f"等待窗口 '{self._pending_window_title}' 超时")
            self._pending_window_title = None
            self._cleanup_browser()
            return

        hwnd = self.find_window_by_title(self._pending_window_title)
        if hwnd:
            if self._browser_embed_timer:
                self._browser_embed_timer.stop()
            self._pending_window_title = None
            self._embed_hwnd(hwnd)

    def _embed_hwnd(self, hwnd: int) -> None:
        self._target_hwnd = hwnd

        self._original_parent = win32gui.GetParent(hwnd)
        self._original_style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        self._original_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        self._original_rect = win32gui.GetWindowRect(hwnd)

        if self._embedded_info:
            ElaWindowEmbedder.release(self)

        self._try_embed_once(hwnd)

    def _get_debugger_url(self, timeout: float = 10) -> str:
        start = time.time()
        while time.time() - start < timeout:
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{self._debug_port}/json", timeout=2
                ) as resp:
                    targets = json.loads(resp.read())
                    if targets:
                        return targets[0]["webSocketDebuggerUrl"]
            except Exception:
                pass
            time.sleep(0.5)
        raise RuntimeError(f"无法连接到调试端口 {self._debug_port}")

    def _log(self, message: str, level: int = 30) -> None:
        self.log_message.emit(message, level)

    def _connect_cdp(self) -> None:
        QTimer.singleShot(0, self._do_connect_cdp)

    def _do_connect_cdp(self) -> None:
        try:
            debugger_url = self._get_debugger_url()
            self._controller = _BrowserController(debugger_url=debugger_url, log_func=self._log)
            self._controller.set_load_started_callback(lambda: self.load_started.emit())
            self._controller.set_load_finished_callback(
                lambda: self.load_finished.emit()
            )
            self._controller.connect()
        except Exception as e:
            self._log(f"CDP 连接失败: {e}", 40)

    def reload(self) -> None:
        """刷新当前页面"""
        if self._controller:
            self._controller.reload()

    def navigate(self, url: str) -> None:
        """导航到指定 URL

        :param url: 目标 URL
        """
        if self._controller:
            self._controller.navigate(url)

    def run_js(self, script: str) -> Any:
        """执行 JavaScript 代码

        :param script: JavaScript 代码
        :returns: 执行结果
        """
        if self._controller:
            return self._controller.run_js(script)
        return None

    def _cleanup_browser(self) -> None:
        """清理浏览器进程和CDP连接"""
        if self._controller:
            self._controller.close()
            self._controller = None

        if self._browser_pid and self._browser_pid.value != 0:
            self._kill_browser_by_pid(self._browser_pid.value)
        if self._browser_process:
            self._browser_process.terminate()
            self._browser_process.join(timeout=5)
            if self._browser_process.is_alive():
                self._browser_process.kill()
            self._browser_process = None

    def release(self) -> None:
        """释放浏览器窗口并终止浏览器进程"""
        if self._browser_embed_timer:
            self._browser_embed_timer.stop()
            self._browser_embed_timer = None
        self._pending_window_title = None

        if self._target_hwnd:
            try:
                win32gui.SetParent(self._target_hwnd, self._original_parent)
                if self._original_style is not None:
                    win32gui.SetWindowLong(
                        self._target_hwnd, win32con.GWL_STYLE, self._original_style
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
                        0,
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
        ElaBrowserEmbedder._instances.discard(self)

    def _kill_browser_by_pid(self, pid: int) -> None:
        import psutil

        try:
            proc = psutil.Process(pid)
            exe_path = proc.exe()
            if exe_path.lower() == str(self._webview_path).lower():
                self._log(f"杀死浏览器进程 {pid}: {exe_path}", 20)
                proc.kill()
            else:
                self._log(f"跳过进程 {pid}: {exe_path} (不是目标浏览器)", 30)
        except psutil.NoSuchProcess:
            pass
        except Exception as e:
            self._log(f"杀死进程失败: {e}", 40)
