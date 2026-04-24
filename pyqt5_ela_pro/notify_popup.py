"""
右下角通知弹窗组件。

从屏幕右下角滑入的通知弹窗，支持自动超时关闭和鼠标悬停保持。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, QTimer, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPainter

from PyQt5ElaWidgetTools import (
    eTheme,
    ElaThemeType,
    ElaText,
    ElaIconButton,
    ElaIconType,
    ElaTheme,
)


class ElaNotifyPopup(QWidget):
    """右下角通知弹窗

    从屏幕右下角滑入显示，支持自动超时关闭和鼠标悬停保持。

    :param parent: 父组件
    :param title: 通知标题
    :param content: 通知内容
    :param timeout: 超时时长（毫秒），默认 5000ms，0 表示不自动关闭
    """

    closed = pyqtSignal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "",
        content: str = "",
        timeout: int = 10000,
    ) -> None:
        super().__init__(parent)

        self._title = title
        self._content = content
        self._timeout = timeout
        self._is_showing = False
        self._animation = None
        self._timer = None

        self._setup_ui()
        self._init()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        self._title_text = ElaText(self)
        self._title_text.setTextPixelSize(14)
        self._title_text.setText(self._title)
        header_layout.addWidget(self._title_text, 1)
        header_layout.addStretch()

        self._close_btn = ElaIconButton(ElaIconType.IconName.X, 20, self)
        self._close_btn.setFixedSize(24, 24)
        self._close_btn.clicked.connect(self._on_close)
        header_layout.addWidget(self._close_btn)

        layout.addLayout(header_layout)

        self._content_text = ElaText(self)
        self._content_text.setTextPixelSize(12)
        self._content_text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._content_text.setWordWrap(True)
        self._content_text.setText(self._content)
        layout.addWidget(self._content_text, 1)

    def _init(self):
        self.setWindowFlags(
            Qt.Tool
            | Qt.X11BypassWindowManagerHint
            | Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedWidth(300)
        self.resize(300, 100)

        self._animation = QPropertyAnimation(self, b"pos")
        self._animation.setDuration(300)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timeout)

    def _update_positions(self):
        screen = self._get_screen_geometry()
        self._start_pos = QPoint(
            screen.width() - self.width() - 5,
            screen.height(),
        )
        self._end_pos = QPoint(
            screen.width() - self.width() - 5,
            screen.height() - self.height() - 5,
        )

    def _get_screen_geometry(self):
        from PyQt5.QtWidgets import QApplication

        screen = QApplication.primaryScreen()
        if screen:
            return screen.availableGeometry()
        return QApplication.instance().desktop().availableGeometry()

    def show(self, title: str = "", content: str = "", timeout: int = -1) -> None:
        if title:
            self.setTitle(title)
        if content:
            self.setContent(content)
        if timeout >= 0:
            self.setTimeout(timeout)

        self._update_positions()
        self._timer.stop()
        self._is_showing = False
        self._animation.stop()
        self.move(self._start_pos)
        super().show()

        self._animation.setStartValue(self.pos())
        self._animation.setEndValue(self._end_pos)
        self._animation.start()

        if self._timeout > 0:
            self._timer.start(self._timeout)

    def _on_close(self):
        self._close_animation()

    def _close_animation(self):
        self._timer.stop()
        self._is_showing = False
        self._animation.stop()
        self._animation.setStartValue(self.pos())
        self._animation.setEndValue(self._start_pos)
        self._animation.start()
        self._animation.finished.connect(self._on_animation_end)

    def _on_animation_end(self):
        try:
            self._animation.finished.disconnect(self._on_animation_end)
        except TypeError:
            pass
        self.hide()
        self.closed.emit()

    def _on_timeout(self):
        self._close_animation()

    def enterEvent(self, event):
        self._timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._timeout > 0 and not self._is_showing:
            self._timer.start(self._timeout)
        super().leaveEvent(event)

    def setTitle(self, title: str) -> None:
        self._title = title
        self._title_text.setText(title)

    def setContent(self, content: str) -> None:
        self._content = content
        self._content_text.setText(content)

    def setTimeout(self, timeout: int) -> None:
        self._timeout = timeout

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        mode = eTheme.getThemeMode()
        bg_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBase)
        border_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBaseLine)

        painter.setPen(border_color)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)

        super().paintEvent(event)


class ElaNotifyManager:
    """通知弹窗管理器（单例）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._popups = []
        return cls._instance

    def show(self, title: str = "", content: str = "", timeout: int = 5000) -> None:
        popup = ElaNotifyPopup(title=title, content=content, timeout=timeout)
        popup.closed.connect(lambda: self._on_popup_closed(popup))
        self._popups.append(popup)
        popup.show(title, content, timeout)

    def _on_popup_closed(self, popup: ElaNotifyPopup) -> None:
        if popup in self._popups:
            self._popups.remove(popup)


show_notify = ElaNotifyManager().show
