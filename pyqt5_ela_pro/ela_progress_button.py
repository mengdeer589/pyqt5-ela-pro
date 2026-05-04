"""
进度显示按钮组件。

继承自 ElaPushButton，支持显示进度条，进度由外部控制。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import pyqtSignal, QRect, QRectF, QSize
from PyQt5.QtGui import QColor, QPainter, QLinearGradient, QPainterPath, QPaintEvent
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaPushButton, ElaIcon, ElaIconType

from ._internal import _draw_button_content


class ElaProgressButton(ElaPushButton):
    """进度显示按钮。

    继承自 ElaPushButton，支持显示进度条。
    进度由外部通过 setProgress() 控制。

    :param text: 按钮文本
    :param getProgressColor: 进度条颜色，为 None 时使用主题色
    :param parent: 父控件

    Example::

        button = ElaProgressButton(text="下载", parent=parent)
        button.setProgress(50)  # 显示50%进度
        button.setProgress(100)  # 完成
    """

    progressChanged = pyqtSignal(int)

    def __init__(
        self,
        text: str = "",
        getProgressColor: Optional[QColor] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setText(text)

        self._border_radius = 3
        self._icon_name: Optional[ElaIconType.IconName] = None
        self._icon_size = 16
        self._progress = 0.0
        self._progress_color = QColor()
        self._custom_progress_color = getProgressColor is not None
        self.setFixedHeight(38)

        self._theme_connection = self._updateProgressColor
        self._updateProgressColor(eTheme.getThemeMode())
        eTheme.themeModeChanged.connect(self._theme_connection)

    def _updateProgressColor(self, mode: ElaThemeType.ThemeMode) -> None:
        if not self._custom_progress_color:
            self._progress_color = eTheme.getThemeColor(
                mode, ElaThemeType.ThemeColor.PrimaryNormal
            )
        self.update()

    def setBorderRadius(self, radius: int) -> None:
        """设置圆角大小。

        :param radius: 圆角半径
        """
        self._border_radius = radius
        self.update()

    def setElaIcon(self, iconName: ElaIconType.IconName, iconSize: int = 16) -> None:
        """设置图标。

        :param iconName: 图标名称
        :param iconSize: 图标大小，默认 16
        """
        self._icon_name = iconName
        self._icon_size = iconSize
        self.setIconSize(QSize(iconSize, iconSize))
        self.update()

    def setProgressColor(self, color: QColor) -> None:
        """设置进度条颜色。

        :param color: 进度条颜色
        """
        self._custom_progress_color = True
        self._progress_color = color
        self.update()

    def getProgressColor(self) -> QColor:
        """返回进度条填充颜色。

        :return: 进度条颜色
        """
        return self._progress_color

    def setProgress(self, percent: int) -> None:
        """设置进度百分比 (0-100)。

        :param percent: 进度百分比，范围 0-100
        """
        percent = max(0, min(100, percent))
        self._progress = percent / 100.0
        self.progressChanged.emit(percent)
        self.update()

    def getProgress(self) -> int:
        """获取当前进度 (0-100)。

        :return: 进度百分比
        """
        return int(self._progress * 100)

    def resetProgress(self) -> None:
        """重置进度为0。"""
        self.setProgress(0)

    def _getCurrentBgColor(self) -> QColor:
        mode = eTheme.getThemeMode()
        if not self.isEnabled():
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicDisable)
        if self.isDown():
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicPress)
        if self.underMouse():
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicHover)
        return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBase)

    def _getCurrentTextColor(self) -> QColor:
        mode = eTheme.getThemeMode()
        if not self.isEnabled():
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicTextDisable)
        return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicText)

    def _getBorderColor(self) -> QColor:
        mode = eTheme.getThemeMode()
        return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBaseLine)

    def deleteLater(self) -> None:
        if self._theme_connection is not None:
            try:
                eTheme.themeModeChanged.disconnect(self._theme_connection)
            except (TypeError, RuntimeError):
                pass
            self._theme_connection = None
        super().deleteLater()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        shadow_border = 3
        rect = QRect(
            shadow_border,
            shadow_border,
            self.width() - 2 * shadow_border,
            self.height() - 2 * shadow_border,
        )

        bg_color = self._getCurrentBgColor()
        text_color = self._getCurrentTextColor()
        border_color = self._getBorderColor()

        # Background + border (same pattern as ElaThemeToolButton)
        painter.setPen(border_color)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(rect, self._border_radius, self._border_radius)

        # Progress overlay
        if self._progress > 0:
            path = QPainterPath()
            path.addRoundedRect(QRectF(rect), self._border_radius, self._border_radius)
            painter.save()
            painter.setClipPath(path)

            if self._progress < 1.0:
                p = self._progress
                gradient = QLinearGradient(rect.topLeft(), rect.topRight())
                gradient.setColorAt(0, self._progress_color)
                gradient.setColorAt(p, self._progress_color)
                gradient.setColorAt(min(p + 0.001, 1.0), QColor(0, 0, 0, 0))
                gradient.setColorAt(1, QColor(0, 0, 0, 0))
                painter.fillRect(rect, gradient)
            else:
                painter.fillRect(rect, self._progress_color)

            painter.restore()

        # Icon + text (same pattern as ElaThemeToolButton)
        def _icon_getter(icon_name, color):
            return ElaIcon.getInstance().getElaIcon(icon_name, color)

        _draw_button_content(
            painter, self.text(), self._icon_name, self._icon_size,
            shadow_border, self.width(), self.height(), text_color, _icon_getter,
        )
