"""
外部窗口嵌入器 (Windows + PyQt5)

可将指定的外部窗口嵌入到 QWidget 中，支持窗口查找、嵌入、释放等操作。
针对 Windows 7/10/11 做了兼容性优化。

使用示例:
    embedder = ElaWindowEmbedder(parent_widget)
    embedder.embedByHwnd(hwnd)
"""

from __future__ import annotations

import logging
import ctypes
import ctypes.wintypes
from typing import Optional, Any

try:
    import win32process  # type: ignore[attr-defined]
except ImportError:
    win32process = None

try:
    import win32api  # type: ignore[attr-defined]
    import win32con  # type: ignore[attr-defined]
    import win32gui  # type: ignore[attr-defined]
except ImportError:
    win32api = None
    win32con = None
    win32gui = None
from PyQt5.QtCore import pyqtSignal, QTimer, QAbstractNativeEventFilter
from PyQt5.QtWidgets import QWidget, QApplication

from ._internal import catch_error
from PyQt5.QtGui import QWindow

logger = logging.getLogger(__name__)

# ── SetWindowSubclass 回调类型 ──────────────────────────────
_SUBCLASS_PROC = ctypes.WINFUNCTYPE(
    ctypes.c_int,
    ctypes.wintypes.HWND,
    ctypes.wintypes.UINT,
    ctypes.wintypes.WPARAM,
    ctypes.wintypes.LPARAM,
    ctypes.c_size_t,  # UINT_PTR
    ctypes.wintypes.DWORD,
)


class _ImeForwardFilter(QAbstractNativeEventFilter):
    """Qt 原生事件过滤器，转发 IME 和焦点消息到嵌入窗口。

    SetParent 后，Chrome 渲染进程的 HWND 收不到来自 Qt 线程的 IME 消息。
    此过滤器在 Qt 事件循环中拦截关键 Windows 消息并转发到嵌入的 HWND。
    同时通过 SetWindowSubclass 在嵌入窗口上拦截 IME 消息，
    阻止 Chrome 清除 IME 上下文，并在首次调用时撤销 Chrome 的 OLE 拖拽注册。
    """

    def __init__(self):
        super().__init__()
        self._target_hwnd: Optional[int] = None
        self._subclass_proc = None

    def set_target(self, hwnd: Optional[int]) -> None:
        self._target_hwnd = hwnd
        if hwnd:
            self._install_subclass()
        else:
            self._uninstall_subclass()

    # ── SetWindowSubclass ────────────────────────────────

    def _install_subclass(self) -> None:
        if self._subclass_proc is not None:
            return

        try:

            @_SUBCLASS_PROC
            def subclass_proc(hwnd, msg, wparam, lparam, uId, dwData):
                if msg == 0x0281:  # WM_IME_SETCONTEXT
                    lparam = 0
                    return ctypes.windll.comctl32.DefSubclassProc(
                        hwnd, msg, wparam, lparam
                    )
                return ctypes.windll.comctl32.DefSubclassProc(hwnd, msg, wparam, lparam)

            self._subclass_proc = subclass_proc
            ctypes.windll.comctl32.SetWindowSubclass(
                self._target_hwnd, subclass_proc, 1, 0
            )
        except Exception:
            pass

    def _uninstall_subclass(self) -> None:
        if self._subclass_proc is not None and self._target_hwnd is not None:
            try:
                ctypes.windll.comctl32.RemoveWindowSubclass(
                    self._target_hwnd, self._subclass_proc, 1
                )
            except Exception:
                pass
            self._subclass_proc = None

    def nativeEventFilter(self, eventType, message):
        if eventType != "windows_generic_MSG" or self._target_hwnd is None:
            return False, 0
        try:
            msg = ctypes.wintypes.MSG.from_address(message.__int__())
            if msg.message == 0x0007:  # WM_SETFOCUS
                ctypes.windll.user32.SetFocus(self._target_hwnd)
                return False, 0
            if msg.message in (
                0x0051,  # WM_INPUTLANGCHANGE
                0x0281,  # WM_IME_SETCONTEXT
                0x0282,  # WM_IME_NOTIFY
                0x0286,  # WM_IME_CHAR
                0x010D,  # WM_IME_STARTCOMPOSITION
                0x010E,  # WM_IME_ENDCOMPOSITION
                0x010F,  # WM_IME_COMPOSITION
            ):
                ctypes.windll.user32.PostMessageW(
                    self._target_hwnd, msg.message, msg.wParam, msg.lParam
                )
                return False, 0
        except Exception:
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


class ElaWindowEmbedder(QWidget):
    """外部窗口嵌入器

    功能：
    - 将指定的外部窗口嵌入到当前 QWidget 中
    - 检测目标窗口是否存在
    - 支持窗口的嵌入和释放
    - Windows 7/10/11 兼容性优化

    信号：
        windowEmbedded(int): 窗口嵌入成功，参数为 hwnd
        windowReleased(int): 窗口释放成功，参数为原 hwnd
        windowNotFound(str): 等待窗口时未找到，参数为状态消息
        embedError(str): 嵌入出错，参数为错误信息
        embedTimeout(): 等待窗口嵌入超时

    使用示例：
        embedder = ElaWindowEmbedder(parent_widget)
        embedder.embedByHwnd(hwnd)
        embedder.release()
    """

    windowEmbedded = pyqtSignal(int)
    windowReleased = pyqtSignal(int)
    windowNotFound = pyqtSignal(str)
    embedError = pyqtSignal(str)
    embedTimeout = pyqtSignal()
    fileDropped = pyqtSignal(str)

    @staticmethod
    def _checkDependencies() -> None:
        if win32gui is None:
            raise ImportError(
                "ElaWindowEmbedder 需要 pywin32，请运行: uv pip install pywin32"
            )

    def __init__(self, parent: Optional[QWidget] = None):
        self._checkDependencies()
        super().__init__(parent=parent)

        _ensure_ime_filter()
        self.setAcceptDrops(True)

        self._embeddedInfo: Optional[dict] = None
        self._embeddedWidget: Optional[QWidget] = None
        self._isEmbedded: bool = False
        self._resize_debounce: Optional[QTimer] = None

        self._embedTimer = QTimer(self)
        self._embedTimer.timeout.connect(self._onEmbedTimerTimeout)
        self._findTimer = QTimer(self)
        self._findTimer.timeout.connect(self._onFindTimerTimeout)
        self._embedPendingHwnd: Optional[int] = None
        self._embedPendingTitle: Optional[str] = None
        self._embedPendingClassName: Optional[str] = None
        self._embedRetryCount: int = 0
        self._embedMaxRetries: int = 30
        self._attached_tid: Optional[int] = None

    def _startEmbedTimer(self, hwnd: int) -> None:
        self._embedPendingHwnd = hwnd
        self._embedRetryCount = 0
        self._embedTimer.start(1000)

    def _stopEmbedTimer(self) -> None:
        self._embedTimer.stop()
        self._embedPendingHwnd = None
        self._embedRetryCount = 0

    def _onEmbedTimerTimeout(self) -> None:
        if self._embedPendingHwnd is None:
            self._stopEmbedTimer()
            return

        self._embedRetryCount += 1

        if self._embedRetryCount >= self._embedMaxRetries:
            self._stopEmbedTimer()
            self.embedTimeout.emit()
            return

        if self._tryEmbedOnce(self._embedPendingHwnd):
            self._stopEmbedTimer()

    def _startFindTimer(
        self, title: Optional[str] = None, class_name: Optional[str] = None
    ) -> None:
        self._embedPendingTitle = title
        self._embedPendingClassName = class_name
        self._embedRetryCount = 0
        self._findTimer.start(1000)

    def _stopFindTimer(self) -> None:
        self._findTimer.stop()
        self._embedPendingTitle = None
        self._embedPendingClassName = None

    def _onFindTimerTimeout(self) -> None:
        self._embedRetryCount += 1

        if self._embedRetryCount >= self._embedMaxRetries:
            self._stopFindTimer()
            self.embedTimeout.emit()
            return

        hwnd = 0
        if self._embedPendingTitle:
            hwnd = self.findWindowByTitle(
                self._embedPendingTitle, self._embedPendingClassName
            )
        elif self._embedPendingClassName:
            hwnd = self.findWindowByClass(self._embedPendingClassName)

        if hwnd:
            self._stopFindTimer()
            self.embedByHwnd(hwnd)
        else:
            self.windowNotFound.emit(f"等待窗口中... ({self._embedRetryCount}s)")

    def isWindowValid(self, hwnd: int) -> bool:
        """检查窗口句柄是否有效"""
        if not hwnd:
            return False
        try:
            return bool(win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd))
        except Exception:
            return False

    def _tryEmbedOnce(self, hwnd: int) -> bool:
        """尝试嵌入单个窗口"""
        if not self.isWindowValid(hwnd):
            return False

        window_info = self.getWindowInfo(hwnd)
        if not window_info:
            return False

        if self._embeddedInfo:
            self.release(destroy=True)

        try:
            qwindow = QWindow.fromWinId(hwnd)
            widget = QWidget.createWindowContainer(qwindow, self)
            widget.setObjectName("embedded_window")

            widget.hwnd = hwnd
            widget.phwnd = window_info["phwnd"]
            widget.style = window_info["style"]
            widget.exstyle = window_info["exstyle"]
            widget.wrect = window_info["wrect"]

            win32gui.SetParent(hwnd, int(self.winId()))

            # ── 修复 IME 输入法无法激活的问题 ──

            # SetParent 后嵌入窗口的线程与 Qt 线程的输入状态不再共享，
            # 通过 AttachThreadInput 使两线程共享 IME 上下文和焦点状态。
            try:
                target_tid, _ = win32process.GetWindowThreadProcessId(hwnd)
                current_tid = win32api.GetCurrentThreadId()
                if target_tid != current_tid:
                    win32gui.AttachThreadInput(target_tid, current_tid, True)
                    self._attached_tid = target_tid
            except Exception:
                pass

            current_style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            new_style = current_style | win32con.WS_CLIPSIBLINGS
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, new_style)

            current_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            new_exstyle = current_exstyle | win32con.WS_EX_NOPARENTNOTIFY
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_exstyle)

            widget.setGeometry(0, 0, self.width(), self.height())
            widget.show()

            self._embeddedInfo = window_info.copy()
            self._embeddedWidget = widget
            self._isEmbedded = True

            self._showEmbeddedWindow()
            _ime_filter.set_target(hwnd)
            self.windowEmbedded.emit(hwnd)
            return True

        except Exception as e:
            logger.warning(f"嵌入窗口失败: {e}")
            return False

    def _showEmbeddedWindow(self) -> None:
        """显示已嵌入的窗口"""
        if self._embeddedInfo:
            hwnd = self._embeddedInfo.get("hwnd")
            if hwnd:
                try:
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                    win32gui.SetWindowPos(
                        hwnd,
                        0,
                        0,
                        0,
                        self.width(),
                        self.height(),
                        win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE,
                    )
                except Exception as e:
                    logger.warning(f"显示嵌入窗口失败: {e}")

    def findWindowByTitle(self, title: str, class_name: Optional[str] = None) -> int:
        """根据窗口标题查找窗口句柄

        :param title: 窗口标题（支持包含匹配）
        :param class_name: 可选的窗口类名（精确匹配）
        :returns: 窗口句柄，未找到返回 0
        """
        if not title:
            return 0

        results: list[int] = []

        def enum_callback(hwnd: int, _: Any) -> bool:
            if win32gui.IsWindow(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if title in window_title:
                    if class_name:
                        if win32gui.GetClassName(hwnd) == class_name:
                            results.append(hwnd)
                    else:
                        results.append(hwnd)
            return True

        try:
            win32gui.EnumWindows(enum_callback, None)
        except Exception as e:
            self.embedError.emit(f"查找窗口时出错: {str(e)}")
            return 0

        return results[0] if results else 0

    def findWindowByClass(self, class_name: str) -> int:
        """根据窗口类名查找窗口句柄

        :param class_name: 窗口类名（精确匹配）
        :returns: 窗口句柄，未找到返回 0
        """
        if not class_name:
            return 0

        try:
            return win32gui.FindWindow(class_name, None)
        except Exception as e:
            self.embedError.emit(f"查找窗口时出错: {str(e)}")
            return 0

    def getWindowInfo(self, hwnd: int) -> Optional[dict]:
        """获取窗口详细信息

        :param hwnd: 窗口句柄
        :returns: 包含 hwnd, phwnd, title, class_name, style, exstyle, wrect 的字典
        """
        if not self.isWindowValid(hwnd):
            return None

        try:
            phwnd = win32gui.GetParent(hwnd)
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            wrect = win32gui.GetWindowRect(hwnd)[:2] + win32gui.GetClientRect(hwnd)[2:]

            return {
                "hwnd": hwnd,
                "phwnd": phwnd,
                "title": title,
                "class_name": class_name,
                "style": style,
                "exstyle": exstyle,
                "wrect": wrect,
            }
        except Exception as e:
            self.embedError.emit(f"获取窗口信息失败: {str(e)}")
            return None

    def embedByHwnd(self, hwnd: int) -> bool:
        """根据句柄嵌入窗口

        :param hwnd: 目标窗口句柄
        :returns: True 表示成功发起嵌入流程（异步嵌入会等待）
        """
        if self._embeddedInfo:
            self.release()

        self._stopFindTimer()

        if self._tryEmbedOnce(hwnd):
            return True

        self._startEmbedTimer(hwnd)
        return True

    def embedByTitle(self, title: str, class_name: Optional[str] = None) -> bool:
        """根据标题嵌入窗口

        :param title: 窗口标题（支持包含匹配）
        :param class_name: 可选的窗口类名
        :returns: True 表示成功发起嵌入流程
        """
        hwnd = self.findWindowByTitle(title, class_name)

        if not hwnd:
            self.windowNotFound.emit(f"未找到标题包含 '{title}' 的窗口，正在等待...")
            self._startFindTimer(title=title, class_name=class_name)
            return True

        return self.embedByHwnd(hwnd)

    def embedByClass(self, class_name: str) -> bool:
        """根据类名嵌入窗口

        :param class_name: 窗口类名
        :returns: True 表示成功发起嵌入流程
        """
        hwnd = self.findWindowByClass(class_name)

        if not hwnd:
            self.windowNotFound.emit(f"未找到类名为 '{class_name}' 的窗口，正在等待...")
            self._startFindTimer(class_name=class_name)
            return True

        return self.embedByHwnd(hwnd)

    def release(self, destroy: bool = False) -> bool:
        """释放已嵌入的窗口

        :param destroy: True 则不恢复窗口原状态直接销毁
        :returns: True 表示成功
        """
        _ime_filter.set_target(None)

        if not self._embeddedInfo:
            return True

        try:
            # 分离之前 AttachThreadInput 附加的线程输入状态
            if self._attached_tid:
                try:
                    current_tid = win32api.GetCurrentThreadId()
                    win32gui.AttachThreadInput(self._attached_tid, current_tid, False)
                except Exception:
                    pass
                self._attached_tid = None

            info = self._embeddedInfo
            hwnd = info["hwnd"]

            if self._embeddedWidget:
                self._embeddedWidget.close()
                self._embeddedWidget.deleteLater()
                self._embeddedWidget = None

            if destroy:
                released_hwnd = hwnd
                self._embeddedInfo = None
                self._isEmbedded = False
                self.windowReleased.emit(released_hwnd)
                return True

            phwnd = info["phwnd"]
            style = info["style"]
            exstyle = info["exstyle"]
            wrect = info["wrect"]

            win32gui.SetParent(hwnd, phwnd)

            win32gui.SetWindowLong(
                hwnd, win32con.GWL_STYLE, style | win32con.WS_VISIBLE
            )
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exstyle)

            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            win32gui.SetWindowPos(
                hwnd, 0, wrect[0], wrect[1], wrect[2], wrect[3], win32con.SWP_NOACTIVATE
            )

            released_hwnd = hwnd
            self._embeddedInfo = None
            self._isEmbedded = False

            self.windowReleased.emit(released_hwnd)
            return True

        except Exception as e:
            error_msg = f"释放窗口失败: {str(e)}"
            self.embedError.emit(error_msg)
            return False

    def mousePressEvent(self, event) -> None:
        if self._embeddedWidget and self._embeddedInfo:
            hwnd = self._embeddedInfo.get("hwnd")
            if hwnd:
                try:
                    win32gui.SetFocus(hwnd)
                except Exception:
                    pass
        super().mousePressEvent(event)

    def focusInEvent(self, event) -> None:
        """当 Qt 控件获得焦点时，将键盘焦点转发给嵌入窗口。"""
        super().focusInEvent(event)
        if self._embeddedInfo:
            hwnd = self._embeddedInfo.get("hwnd")
            if hwnd:
                try:
                    win32gui.SetFocus(hwnd)
                except Exception:
                    pass

    def wheelEvent(self, event) -> None:
        if self._embeddedWidget and self._embeddedInfo:
            hwnd = self._embeddedInfo.get("hwnd")

            if hwnd:
                try:
                    win32gui.SetFocus(hwnd)
                except Exception:
                    pass

                delta = event.angleDelta().y()
                pos = event.pos()

                wParam = (delta << 16) & 0xFFFF0000
                lParam = (pos.x() & 0xFFFF) | ((pos.y() & 0xFFFF) << 16)

                try:
                    win32api.PostMessage(hwnd, 0x020A, wParam, lParam)
                except Exception:
                    try:
                        win32gui.SendMessage(hwnd, 0x020A, wParam, lParam)
                    except Exception:
                        pass

        super().wheelEvent(event)

    def dragEnterEvent(self, event) -> None:
        """接受拖入的文件。"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        """发射拖入文件的路径。"""
        for url in event.mimeData().urls():
            if url.isLocalFile():
                self.fileDropped.emit(url.toLocalFile())

    @catch_error
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if not self._isEmbedded or not self._embeddedWidget or not self._embeddedInfo:
            return
        if self._resize_debounce is None:
            self._resize_debounce = QTimer(self)
            self._resize_debounce.setSingleShot(True)
            self._resize_debounce.timeout.connect(self._apply_debounced_resize)
        self._resize_debounce.start(150)

    def _apply_debounced_resize(self) -> None:
        if not self._embeddedInfo or not self._embeddedWidget:
            return
        width = self.width()
        height = self.height()
        self._embeddedWidget.setGeometry(0, 0, width, height)
        hwnd = self._embeddedInfo.get("hwnd")
        if hwnd:
            win32gui.SetWindowPos(
                hwnd,
                0,
                0,
                0,
                width,
                height,
                win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE,
            )

    def closeEvent(self, event) -> None:
        if self._embeddedInfo:
            self.release()
        super().closeEvent(event)

    @property
    def embeddedWindowInfo(self) -> Optional[dict]:
        """返回已嵌入窗口的信息副本"""
        return self._embeddedInfo.copy() if self._embeddedInfo else None

    @property
    def hasEmbeddedWindow(self) -> bool:
        """当前是否已有嵌入的窗口"""
        return self._embeddedInfo is not None
