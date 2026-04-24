"""
外部窗口嵌入器 (Windows + PyQt5)

可将指定的外部窗口嵌入到 QWidget 中，支持窗口查找、嵌入、释放等操作。
针对 Windows 7/10/11 做了兼容性优化。

使用示例:
    embedder = ElaWindowEmbedder(parent_widget)
    embedder.embed_by_hwnd(hwnd)
"""

from __future__ import annotations

import logging
from typing import Optional, Any

import win32api
import win32con
import win32gui
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
        window_embedded(int): 窗口嵌入成功，参数为 hwnd
        window_released(int): 窗口释放成功，参数为原 hwnd
        window_not_found(str): 等待窗口时未找到，参数为状态消息
        embed_error(str): 嵌入出错，参数为错误信息
        embed_timeout(): 等待窗口嵌入超时

    使用示例：
        embedder = ElaWindowEmbedder(parent_widget)
        embedder.embed_by_hwnd(hwnd)
        embedder.release()
    """

    window_embedded = pyqtSignal(int)
    window_released = pyqtSignal(int)
    window_not_found = pyqtSignal(str)
    embed_error = pyqtSignal(str)
    embed_timeout = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)

        self._embedded_info: Optional[dict] = None
        self._embedded_widget: Optional[QWidget] = None
        self._is_embedded: bool = False
        self._resize_throttle_time: float = 0
        self._resize_count: int = 0

        self._embed_timer = QTimer(self)
        self._embed_timer.timeout.connect(self._on_embed_timer_timeout)
        self._find_timer = QTimer(self)
        self._find_timer.timeout.connect(self._on_find_timer_timeout)
        self._embed_pending_hwnd: Optional[int] = None
        self._embed_pending_title: Optional[str] = None
        self._embed_pending_class_name: Optional[str] = None
        self._embed_retry_count: int = 0
        self._embed_max_retries: int = 30

    def _start_embed_timer(self, hwnd: int) -> None:
        self._embed_pending_hwnd = hwnd
        self._embed_retry_count = 0
        self._embed_timer.start(1000)

    def _stop_embed_timer(self) -> None:
        self._embed_timer.stop()
        self._embed_pending_hwnd = None
        self._embed_retry_count = 0

    def _on_embed_timer_timeout(self) -> None:
        if self._embed_pending_hwnd is None:
            self._stop_embed_timer()
            return

        self._embed_retry_count += 1

        if self._embed_retry_count >= self._embed_max_retries:
            self._stop_embed_timer()
            self.embed_timeout.emit()
            return

        if self._try_embed_once(self._embed_pending_hwnd):
            self._stop_embed_timer()

    def _start_find_timer(
        self, title: Optional[str] = None, class_name: Optional[str] = None
    ) -> None:
        self._embed_pending_title = title
        self._embed_pending_class_name = class_name
        self._embed_retry_count = 0
        self._find_timer.start(1000)

    def _stop_find_timer(self) -> None:
        self._find_timer.stop()
        self._embed_pending_title = None
        self._embed_pending_class_name = None

    def _on_find_timer_timeout(self) -> None:
        self._embed_retry_count += 1

        if self._embed_retry_count >= self._embed_max_retries:
            self._stop_find_timer()
            self.embed_timeout.emit()
            return

        hwnd = 0
        if self._embed_pending_title:
            hwnd = self.find_window_by_title(
                self._embed_pending_title, self._embed_pending_class_name
            )
        elif self._embed_pending_class_name:
            hwnd = self.find_window_by_class(self._embed_pending_class_name)

        if hwnd:
            self._stop_find_timer()
            self.embed_by_hwnd(hwnd)
        else:
            self.window_not_found.emit(f"等待窗口中... ({self._embed_retry_count}s)")

    def is_window_valid(self, hwnd: int) -> bool:
        """检查窗口句柄是否有效"""
        if not hwnd:
            return False
        try:
            return bool(win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd))
        except Exception:
            return False

    def _try_embed_once(self, hwnd: int) -> bool:
        """尝试嵌入单个窗口"""
        if not self.is_window_valid(hwnd):
            return False

        window_info = self.get_window_info(hwnd)
        if not window_info:
            return False

        try:
            qwindow = QWindow.fromWinId(hwnd)
            widget = QWidget.createWindowContainer(qwindow, self)
            widget.setObjectName("embedded_window")

            widget.hwnd = hwnd
            widget.phwnd = window_info["phwnd"]
            widget.style = window_info["style"]
            widget.exstyle = window_info["exstyle"]
            widget.wrect = window_info["wrect"]

            widget.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
            win32gui.SetParent(hwnd, int(self.winId()))

            current_style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            new_style = current_style | win32con.WS_CLIPSIBLINGS
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, new_style)

            current_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            new_exstyle = current_exstyle | win32con.WS_EX_NOPARENTNOTIFY
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_exstyle)

            widget.setGeometry(0, 0, self.width(), self.height())
            widget.show()

            self._embedded_info = window_info.copy()
            self._embedded_widget = widget
            self._is_embedded = True

            self._show_embedded_window()
            self.window_embedded.emit(hwnd)
            return True

        except Exception as e:
            logger.warning(f"嵌入窗口失败: {e}")
            return False

    def _show_embedded_window(self) -> None:
        """显示已嵌入的窗口"""
        if self._embedded_info:
            hwnd = self._embedded_info.get("hwnd")
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
                        | win32con.SWP_NOMOVE
                        | win32con.SWP_NOACTIVATE,
                    )
                except Exception as e:
                    logger.warning(f"显示嵌入窗口失败: {e}")

    def find_window_by_title(self, title: str, class_name: Optional[str] = None) -> int:
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
            self.embed_error.emit(f"查找窗口时出错: {str(e)}")
            return 0

        return results[0] if results else 0

    def find_window_by_class(self, class_name: str) -> int:
        """根据窗口类名查找窗口句柄

        :param class_name: 窗口类名（精确匹配）
        :returns: 窗口句柄，未找到返回 0
        """
        if not class_name:
            return 0

        try:
            return win32gui.FindWindow(class_name, None)
        except Exception as e:
            self.embed_error.emit(f"查找窗口时出错: {str(e)}")
            return 0

    def get_window_info(self, hwnd: int) -> Optional[dict]:
        """获取窗口详细信息

        :param hwnd: 窗口句柄
        :returns: 包含 hwnd, phwnd, title, class_name, style, exstyle, wrect 的字典
        """
        if not self.is_window_valid(hwnd):
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
            self.embed_error.emit(f"获取窗口信息失败: {str(e)}")
            return None

    def embed_by_hwnd(self, hwnd: int) -> bool:
        """根据句柄嵌入窗口

        :param hwnd: 目标窗口句柄
        :returns: True 表示成功发起嵌入流程（异步嵌入会等待）
        """
        if self._embedded_info:
            self.release()

        self._stop_find_timer()

        if self._try_embed_once(hwnd):
            return True

        self._start_embed_timer(hwnd)
        return True

    def embed_by_title(self, title: str, class_name: Optional[str] = None) -> bool:
        """根据标题嵌入窗口

        :param title: 窗口标题（支持包含匹配）
        :param class_name: 可选的窗口类名
        :returns: True 表示成功发起嵌入流程
        """
        hwnd = self.find_window_by_title(title, class_name)

        if not hwnd:
            self.window_not_found.emit(f"未找到标题包含 '{title}' 的窗口，正在等待...")
            self._start_find_timer(title=title, class_name=class_name)
            return True

        return self.embed_by_hwnd(hwnd)

    def embed_by_class(self, class_name: str) -> bool:
        """根据类名嵌入窗口

        :param class_name: 窗口类名
        :returns: True 表示成功发起嵌入流程
        """
        hwnd = self.find_window_by_class(class_name)

        if not hwnd:
            self.window_not_found.emit(
                f"未找到类名为 '{class_name}' 的窗口，正在等待..."
            )
            self._start_find_timer(class_name=class_name)
            return True

        return self.embed_by_hwnd(hwnd)

    def release(self, destroy: bool = False) -> bool:
        """释放已嵌入的窗口

        :param destroy: True 则不恢复窗口原状态直接销毁
        :returns: True 表示成功
        """
        if not self._embedded_info:
            return True

        try:
            info = self._embedded_info
            hwnd = info["hwnd"]

            if self._embedded_widget:
                self._embedded_widget.close()
                self._embedded_widget.deleteLater()
                self._embedded_widget = None

            if destroy:
                released_hwnd = hwnd
                self._embedded_info = None
                self.window_released.emit(released_hwnd)
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
            self._embedded_info = None
            self._is_embedded = False

            self.window_released.emit(released_hwnd)
            return True

        except Exception as e:
            error_msg = f"释放窗口失败: {str(e)}"
            self.embed_error.emit(error_msg)
            return False

    def mousePressEvent(self, event) -> None:
        if self._embedded_widget and self._embedded_info:
            hwnd = self._embedded_info.get("hwnd")
            if hwnd:
                try:
                    win32gui.SetFocus(hwnd)
                except Exception:
                    pass
        super().mousePressEvent(event)

    def wheelEvent(self, event) -> None:
        if self._embedded_widget and self._embedded_info:
            hwnd = self._embedded_info.get("hwnd")

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

        if not self._is_embedded or not self._embedded_widget or not self._embedded_info:
            return

        import time
        current_time = time.time()
        if current_time - self._resize_throttle_time < 0.1:
            self._resize_count += 1
            if self._resize_count > 5:
                return
        else:
            self._resize_throttle_time = current_time
            self._resize_count = 0

        width = self.width()
        height = self.height()

        self._embedded_widget.setGeometry(0, 0, width, height)

        hwnd = self._embedded_info.get("hwnd")
        if hwnd:
            win32gui.SetWindowPos(
                hwnd,
                0,
                0,
                0,
                width,
                height,
                win32con.SWP_NOZORDER
                | win32con.SWP_NOACTIVATE
                | win32con.SWP_NOMOVE,
            )

    def closeEvent(self, event) -> None:
        if self._embedded_info:
            self.release()
        super().closeEvent(event)

    @property
    def embedded_window_info(self) -> Optional[dict]:
        """返回已嵌入窗口的信息副本"""
        return self._embedded_info.copy() if self._embedded_info else None

    @property
    def has_embedded_window(self) -> bool:
        """当前是否已有嵌入的窗口"""
        return self._embedded_info is not None
