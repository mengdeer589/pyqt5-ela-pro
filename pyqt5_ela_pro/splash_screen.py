"""
启动画面组件，风格参考 ElaWidgetTools 的 ElaSplashScreen。

全 QPainter 自定义绘制，支持主题自适应、Logo、淡入淡出动画、可拖动。

用法::

    splash = ElaSplashScreen(parent=self)
    splash.setTitle("My App")
    splash.setSubTitle("Version 1.0")
    splash.show()
    # ... loading ...
    splash.setValue(100)
    splash.finish(main_window)
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, QRect, QRectF, QPoint, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QPixmap, QPaintEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication

from PyQt5ElaWidgetTools import (
    eTheme,
    ElaThemeType,
    ElaText,
    ElaTextType,
    ElaProgressBar,
    ElaProgressRing,
)

from .widget_base import ElaThemeWidget


class ElaSplashScreen(ElaThemeWidget):
    """启动画面组件。

    全 QPainter 自定义绘制，支持 Logo、标题、副标题、状态文字、进度条/环，
    主题自适应、淡入淡出动画、鼠标拖动。

    :param parent: 父控件
    """

    closed = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._border_radius = 12
        self._minimum = 0
        self._maximum = 100
        self._value = 0
        self._is_show_progress_bar = True
        self._is_show_progress_ring = True
        self._is_closable = False
        self._logo = QPixmap()
        self._is_dragging = False
        self._drag_start = QPoint()
        self._fade_target = None
        self._fade_opacity = 1.0
        self._fade_timer = QTimer(self)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(580, 400)

        # Title
        self._title_text = ElaText(self)
        self._title_text.setTextStyle(ElaTextType.TextStyle.TitleLarge)
        self._title_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Subtitle
        self._subtitle_text = ElaText(self)
        self._subtitle_text.setTextStyle(ElaTextType.TextStyle.Subtitle)
        self._subtitle_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._subtitle_text.setWordWrap(True)
        self._subtitle_text.setMinimumWidth(400)

        # Status
        self._status_text = ElaText(self)
        self._status_text.setTextStyle(ElaTextType.TextStyle.Body)
        self._status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Progress bar
        self._progress_bar = ElaProgressBar(self)
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(100)
        self._progress_bar.setFixedHeight(24)

        # Progress ring
        self._progress_ring = ElaProgressRing(self)
        self._progress_ring.setFixedSize(48, 48)
        self._progress_ring.setIsBusying(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 50, 36, 36)
        layout.setSpacing(6)
        layout.addStretch(2)
        layout.addWidget(self._title_text, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(4)
        layout.addWidget(self._subtitle_text, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(self._progress_ring, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(8)
        layout.addWidget(self._status_text, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(12)
        layout.addWidget(self._progress_bar)
        layout.addStretch(1)

    # ── Public API ────────────────────────────────────────

    def setBorderRadius(self, r: int) -> None:
        """设置窗口圆角半径。

        :param r: 圆角半径（像素）
        """
        self._border_radius = r
        self.update()

    def borderRadius(self) -> int:
        """获取窗口圆角半径。

        :returns: 圆角半径（像素）
        """
        return self._border_radius

    def setTitle(self, title: str) -> None:
        """设置标题文字。

        :param title: 标题
        """
        self._title_text.setText(title)

    def title(self) -> str:
        """获取标题文字。

        :returns: 标题
        """
        return self._title_text.text()

    def setSubTitle(self, text: str) -> None:
        """设置副标题文字。

        :param text: 副标题
        """
        self._subtitle_text.setText(text)

    def subTitle(self) -> str:
        """获取副标题文字。

        :returns: 副标题
        """
        return self._subtitle_text.text()

    def setStatusText(self, text: str) -> None:
        """设置状态文字。

        :param text: 状态文字
        """
        self._status_text.setText(text)

    def statusText(self) -> str:
        """获取状态文字。

        :returns: 状态文字
        """
        return self._status_text.text()

    def setLogo(self, logo: QPixmap) -> None:
        """设置 Logo 图片。

        :param logo: Logo 像素图
        """
        self._logo = logo
        self.update()

    def logo(self) -> QPixmap:
        """获取 Logo 图片。

        :returns: Logo 像素图
        """
        return self._logo

    def setMinimum(self, n: int) -> None:
        """设置进度最小值。

        :param n: 最小值
        """
        self._minimum = n
        self._progress_bar.setMinimum(n)

    def minimum(self) -> int:
        """获取进度最小值。

        :returns: 最小值
        """
        return self._minimum

    def setMaximum(self, n: int) -> None:
        """设置进度最大值。

        :param n: 最大值
        """
        self._maximum = n
        self._progress_bar.setMaximum(n)

    def maximum(self) -> int:
        """获取进度最大值。

        :returns: 最大值
        """
        return self._maximum

    def setValue(self, n: int) -> None:
        """设置当前进度值。

        :param n: 进度值
        """
        self._value = n
        self._progress_bar.setValue(n)
        self._progress_ring.setValue(n)

    def value(self) -> int:
        """获取当前进度值。

        :returns: 进度值
        """
        return self._value

    def setShowProgressBar(self, show: bool) -> None:
        """设置是否显示进度条。

        :param show: 是否显示
        """
        self._is_show_progress_bar = show
        self._progress_bar.setVisible(show)

    def isShowProgressBar(self) -> bool:
        """当前是否显示进度条。

        :returns: 显示状态
        """
        return self._is_show_progress_bar

    def setShowProgressRing(self, show: bool) -> None:
        """设置是否显示进度环。

        :param show: 是否显示
        """
        self._is_show_progress_ring = show
        self._progress_ring.setVisible(show)

    def isShowProgressRing(self) -> bool:
        """当前是否显示进度环。

        :returns: 显示状态
        """
        return self._is_show_progress_ring

    def setClosable(self, closable: bool) -> None:
        """设置是否可关闭。

        :param closable: 是否可关闭
        """
        self._is_closable = closable

    def isClosable(self) -> bool:
        """当前是否可关闭。

        :returns: 可关闭状态
        """
        return self._is_closable

    def show(self) -> None:
        """显示启动画面（居中于当前屏幕）。"""
        screen = QApplication.primaryScreen()
        if screen:
            sg = screen.availableGeometry()
            self.move(
                (sg.width() - self.width()) // 2, (sg.height() - self.height()) // 2
            )
        self._progress_bar.setVisible(self._is_show_progress_bar)
        self._progress_ring.setVisible(self._is_show_progress_ring)
        self.setWindowOpacity(1.0)
        super().show()

    def close(self) -> None:
        """关闭启动画面并发射 ``closed`` 信号。"""
        super().close()
        self.closed.emit()

    def finish(self, main_window: QWidget) -> None:
        """淡出关闭并显示主窗口。

        :param main_window: 主窗口实例
        """
        self._fade_target = main_window
        self._fade_opacity = 1.0
        self._fade_timer.setInterval(20)
        self._fade_timer.timeout.connect(self._onFadeTick)
        self._fade_timer.start()

    # ── Internal ──────────────────────────────────────────

    def _onFadeTick(self) -> None:
        self._fade_opacity -= 0.05
        if self._fade_opacity <= 0:
            self._fade_timer.stop()
            target = self._fade_target
            self.setWindowOpacity(1.0)
            self.closed.emit()
            super().close()
            if target:
                target.show()
                target.raise_()
                target.activateWindow()
            return
        self.setWindowOpacity(self._fade_opacity)

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    # ── Events ────────────────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_start = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._is_dragging:
            self.move(event.globalPos() - self._drag_start)
            event.accept()

    def mouseReleaseEvent(self, _event: QMouseEvent) -> None:
        self._is_dragging = False

    # ── Paint ─────────────────────────────────────────────

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        mode = self._theme_mode
        br = self._border_radius
        sb = 6
        fg = QRect(sb, sb, self.width() - 2 * sb, self.height() - 2 * sb)

        # Shadow
        eTheme.drawEffectShadow(painter, self.rect(), sb, br)

        # Background
        path = QPainterPath()
        path.addRoundedRect(QRectF(fg), br, br)
        painter.setClipPath(path)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.DialogBase))
        painter.drawRoundedRect(QRectF(fg), br, br)

        # Logo
        if not self._logo.isNull():
            ls = min(80, min(fg.width(), fg.height()) // 3)
            lr = QRect(fg.x() + (fg.width() - ls) // 2, fg.y() + 30, ls, ls)
            painter.drawPixmap(
                lr,
                self._logo.scaled(
                    ls,
                    ls,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                ),
            )

        # Border
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(
            QPen(eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.PopupBorder), 1)
        )
        painter.drawRoundedRect(QRectF(fg), br, br)
