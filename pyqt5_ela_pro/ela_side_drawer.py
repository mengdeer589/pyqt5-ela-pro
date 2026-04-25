"""
ElaDrawer SiliconUI 风格侧边抽屉组件。

支持上下左右四个方向滑出的抽屉面板，带遮罩层和动画效果。
参考 SiliconUI 的 SiLayerDrawer 设计。
"""

from __future__ import annotations

from enum import IntEnum
from typing import Optional

from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QRect, QEvent
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPaintEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsDropShadowEffect

from PyQt5ElaWidgetTools import eTheme, ElaThemeType


class ElaDrawerPosition(IntEnum):
    Left = 0
    Right = 1
    Top = 2
    Bottom = 3


class ElaDrawerPanel(QWidget):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        corner_radius: int = 12,
        position: ElaDrawerPosition = ElaDrawerPosition.Right,
    ) -> None:
        super().__init__(parent)
        self._corner_radius = corner_radius
        self._position = position
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def setBgColor(self, color: QColor) -> None:
        self._bg_color = color
        self.update()

    def setPosition(self, position: ElaDrawerPosition) -> None:
        self._position = position
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        if not hasattr(self, "_bg_color"):
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        path = QPainterPath()
        r = self._corner_radius
        w, h = self.width(), self.height()

        if self._position == ElaDrawerPosition.Left:
            path.moveTo(w, r)
            path.quadTo(w, 0, w - r, 0)
            path.lineTo(0, 0)
            path.lineTo(0, h)
            path.lineTo(w - r, h)
            path.quadTo(w, h, w, h - r)
        elif self._position == ElaDrawerPosition.Right:
            path.moveTo(0, r)
            path.quadTo(0, 0, r, 0)
            path.lineTo(w, 0)
            path.lineTo(w, h)
            path.lineTo(r, h)
            path.quadTo(0, h, 0, h - r)
        elif self._position == ElaDrawerPosition.Top:
            path.moveTo(r, h)
            path.quadTo(0, h, 0, h - r)
            path.lineTo(0, 0)
            path.lineTo(w, 0)
            path.lineTo(w, h - r)
            path.quadTo(w, h, w - r, h)
        else:  # Bottom
            path.moveTo(r, 0)
            path.quadTo(0, 0, 0, r)
            path.lineTo(0, h)
            path.lineTo(w, h)
            path.lineTo(w, r)
            path.quadTo(w, 0, w - r, 0)

        path.closeSubpath()
        painter.fillPath(path, self._bg_color)


class ElaDrawerDim(QWidget):
    clicked = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self._bg_color = QColor(0, 0, 0, 102)

    def setBgColor(self, color: QColor) -> None:
        self._bg_color = color
        palette = self.palette()
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), self._bg_color)


class ElaDrawer(QWidget):
    """
    SiliconUI 风格侧边抽屉组件。

    特性：
    - 支持上下左右四个方向滑入
    - 半透明遮罩层，点击可关闭
    - 平滑动画效果
    - 支持主题适配
    """

    closed = pyqtSignal()
    showed = pyqtSignal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        position: ElaDrawerPosition = ElaDrawerPosition.Right,
        drawer_size: int = 360,
    ) -> None:
        super().__init__(parent)
        self._position = position
        self._drawer_size = drawer_size
        self._is_opened = False
        self._close_on_dim_clicked = True
        self._animation_duration = 250
        self._corner_radius = 12
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.hide()

        self._dim_widget = ElaDrawerDim(self)
        self._dim_widget.clicked.connect(self._onDimClicked)
        self._dim_widget.hide()

        self._drawer_widget = ElaDrawerPanel(self, self._corner_radius, self._position)

        shadow = QGraphicsDropShadowEffect(self._drawer_widget)
        shadow.setColor(QColor(0, 0, 0, 60))
        if self._position == ElaDrawerPosition.Left:
            shadow.setOffset(4, 0)
        elif self._position == ElaDrawerPosition.Right:
            shadow.setOffset(-4, 0)
        elif self._position == ElaDrawerPosition.Top:
            shadow.setOffset(0, 4)
        else:
            shadow.setOffset(0, -4)
        shadow.setBlurRadius(16)
        self._drawer_widget.setGraphicsEffect(shadow)

        self._main_layout = QVBoxLayout(self._drawer_widget)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self._content_widget: Optional[QWidget] = None

        self._show_anim = QPropertyAnimation(self._drawer_widget, b"geometry")
        self._show_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._hide_anim = QPropertyAnimation(self._drawer_widget, b"geometry")
        self._hide_anim.setEasingCurve(QEasingCurve.InCubic)
        self._hide_anim.finished.connect(self._onHideFinished)

        self._dim_anim = QPropertyAnimation(self._dim_widget, b"windowOpacity")
        self._dim_anim.setDuration(self._animation_duration)

        if parent:
            parent.installEventFilter(self)

        self._onThemeModeChanged(eTheme.getThemeMode())
        eTheme.themeModeChanged.connect(self._onThemeModeChanged)

    def _onThemeModeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        bg_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBase)
        self._drawer_widget.setBgColor(bg_color)
        dim_color = QColor(0, 0, 0, 102)
        self._dim_widget.setBgColor(dim_color)

    def _getStartRect(self, parent: QWidget) -> QRect:
        if self._position == ElaDrawerPosition.Left:
            return QRect(-self._drawer_size, 0, self._drawer_size, parent.height())
        elif self._position == ElaDrawerPosition.Right:
            return QRect(parent.width(), 0, self._drawer_size, parent.height())
        elif self._position == ElaDrawerPosition.Top:
            return QRect(0, -self._drawer_size, parent.width(), self._drawer_size)
        else:  # Bottom
            return QRect(0, parent.height(), parent.width(), self._drawer_size)

    def _getEndRect(self, parent: QWidget) -> QRect:
        if self._position == ElaDrawerPosition.Left:
            return QRect(0, 0, self._drawer_size, parent.height())
        elif self._position == ElaDrawerPosition.Right:
            return QRect(
                parent.width() - self._drawer_size,
                0,
                self._drawer_size,
                parent.height(),
            )
        elif self._position == ElaDrawerPosition.Top:
            return QRect(0, 0, parent.width(), self._drawer_size)
        else:  # Bottom
            return QRect(
                0,
                parent.height() - self._drawer_size,
                parent.width(),
                self._drawer_size,
            )

    def setContentWidget(self, widget: QWidget) -> "ElaDrawer":
        if self._content_widget:
            self._main_layout.removeWidget(self._content_widget)
        self._content_widget = widget
        self._main_layout.addWidget(widget)
        return self

    def setDrawerSize(self, size: int) -> "ElaDrawer":
        self._drawer_size = size
        return self

    def setCornerRadius(self, radius: int) -> "ElaDrawer":
        self._corner_radius = radius
        return self

    def setCloseOnDimClicked(self, on: bool) -> "ElaDrawer":
        self._close_on_dim_clicked = on
        return self

    def setAnimationDuration(self, duration: int) -> "ElaDrawer":
        self._animation_duration = duration
        self._show_anim.setDuration(duration)
        self._hide_anim.setDuration(duration)
        self._dim_anim.setDuration(duration)
        return self

    def opened(self) -> bool:
        return self._is_opened

    def showDrawer(self) -> None:
        if self._is_opened:
            return

        if not self._content_widget:
            return

        parent = self.parentWidget()
        if not parent:
            return

        self.resize(parent.size())
        self._dim_widget.resize(self.size())

        start_rect = self._getStartRect(parent)
        end_rect = self._getEndRect(parent)

        self._drawer_widget.setGeometry(start_rect)
        self._drawer_widget.show()
        self._dim_widget.setWindowOpacity(0)
        self._dim_widget.show()
        self.show()
        self._is_opened = True

        self._show_anim.setDuration(self._animation_duration)
        self._show_anim.setStartValue(start_rect)
        self._show_anim.setEndValue(end_rect)
        self._show_anim.start()

        self._dim_anim.setStartValue(0)
        self._dim_anim.setEndValue(1)
        self._dim_anim.start()

        self.showed.emit()

    def closeDrawer(self) -> None:
        if not self._is_opened:
            return

        parent = self.parentWidget()
        if not parent:
            return

        current_rect = self._drawer_widget.geometry()
        end_rect = self._getStartRect(parent)

        self._hide_anim.setDuration(self._animation_duration)
        self._hide_anim.setStartValue(current_rect)
        self._hide_anim.setEndValue(end_rect)
        self._hide_anim.start()

        self._dim_anim.setStartValue(1)
        self._dim_anim.setEndValue(0)
        self._dim_anim.start()

    def _onDimClicked(self) -> None:
        if self._close_on_dim_clicked:
            self.closeDrawer()

    def _onHideFinished(self) -> None:
        self._dim_widget.hide()
        self._drawer_widget.hide()
        self.hide()
        self._is_opened = False
        self.closed.emit()

    def toggleDrawer(self) -> None:
        if self._is_opened:
            self.closeDrawer()
        else:
            self.showDrawer()

    def eventFilter(self, watched, event) -> bool:
        if watched == self.parentWidget() and self._is_opened:
            if event.type() == QEvent.Type.Resize:
                self.resize(event.size())
                self._dim_widget.resize(self.size())
                parent = watched
                end_rect = self._getEndRect(parent)
                self._drawer_widget.setGeometry(end_rect)
        return super().eventFilter(watched, event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._is_opened:
            self._dim_widget.resize(self.size())
            parent = self.parentWidget()
            if parent:
                end_rect = self._getEndRect(parent)
                self._drawer_widget.setGeometry(end_rect)

    def deleteLater(self) -> None:
        try:
            eTheme.themeModeChanged.disconnect(self._onThemeModeChanged)
        except (TypeError, RuntimeError):
            pass
        super().deleteLater()
