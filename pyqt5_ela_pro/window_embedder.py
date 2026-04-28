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
import time
from typing import Optional, Any

try:
    import win32api
    import win32con
    import win32gui
except ImportError:
    win32api = None
    win32con = None
    win32gui = None
from PyQt5.QtCore import Qt, pyqtSignal, QTimer

from ._internal import catch_error
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QWidget

logger = logging.getLogger(__name__)


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

    @staticmethod
    def _checkDependencies() -> None:
        if win32gui is None:
            raise ImportError(
                "ElaWindowEmbedder 需要 pywin32，请运行: uv pip install pywin32"
            )

    def __init__(self, parent: Optional[QWidget] = None):
        self._checkDependencies()
        super().__init__(parent=parent)

        self._embeddedInfo: Optional[dict] = None
        self._embeddedWidget: Optional[QWidget] = None
        self._isEmbedded: bool = False
        self._resizeThrottleTime: float = 0
        self._resizeCount: int = 0

        self._embedTimer = QTimer(self)
        self._embedTimer.timeout.connect(self._onEmbedTimerTimeout)
        self._findTimer = QTimer(self)
        self._findTimer.timeout.connect(self._onFindTimerTimeout)
        self._embedPendingHwnd: Optional[int] = None
        self._embedPendingTitle: Optional[str] = None
        self._embedPendingClassName: Optional[str] = None
        self._embedRetryCount: int = 0
        self._embedMaxRetries: int = 30

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
                        win32con.SWP_NOZORDER
                        | win32con.SWP_NOACTIVATE,
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
            self.windowNotFound.emit(
                f"未找到类名为 '{class_name}' 的窗口，正在等待..."
            )
            self._startFindTimer(class_name=class_name)
            return True

        return self.embedByHwnd(hwnd)

    def release(self, destroy: bool = False) -> bool:
        """释放已嵌入的窗口

        :param destroy: True 则不恢复窗口原状态直接销毁
        :returns: True 表示成功
        """
        if not self._embeddedInfo:
            return True

        try:
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

    @catch_error
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)

        if not self._isEmbedded or not self._embeddedWidget or not self._embeddedInfo:
            return

        current_time = time.time()
        if current_time - self._resizeThrottleTime < 0.1:
            self._resizeCount += 1
            if self._resizeCount > 5:
                return
        else:
            self._resizeThrottleTime = current_time
            self._resizeCount = 0

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
                win32con.SWP_NOZORDER
                | win32con.SWP_NOACTIVATE,
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
