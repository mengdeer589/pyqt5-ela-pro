"""
主要按钮组件。

使用 Primary 主题色的按钮，与 ElaToggleButton ON 状态外观一致。
继承自 ElaPushButton，支持图标、点击事件等所有功能。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, QRect, QRectF, QSize
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPen, QFont, QPaintEvent
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import (
    eTheme,
    ElaThemeType,
    ElaPushButton,
    ElaIcon,
    ElaIconType,
    ElaToolButton,
)


def _draw_button_content(
    painter: QPainter,
    text: str,
    icon_name,
    icon_size: int,
    shadow_border: int,
    widget_width: int,
    widget_height: int,
    text_color: QColor,
    icon_getter,
) -> QRect:
    """绘制按钮图标和文字布局。

    :return: 文字区域 QRect
    """
    if icon_name is not None:
        icon_sz = QSize(icon_size, icon_size)
        spacing = 8
        content_height = widget_height - 2 * shadow_border

        fm = painter.fontMetrics()
        text_width = fm.horizontalAdvance(text)
        total_content_width = icon_sz.width() + spacing + text_width
        start_x = (
            shadow_border
            + (widget_width - 2 * shadow_border - total_content_width) // 2
        )

        icon_y = shadow_border + (content_height - icon_sz.height()) // 2
        icon_rect = QRect(start_x, icon_y, icon_sz.width(), icon_sz.height())

        text_rect = QRect(
            icon_rect.right() + spacing,
            shadow_border,
            text_width,
            content_height,
        )
        icon = icon_getter(icon_name, text_color)
        painter.drawPixmap(icon_rect, icon.pixmap(icon_sz))
    else:
        rect = QRect(
            shadow_border,
            shadow_border,
            widget_width - 2 * shadow_border,
            widget_height - 2 * shadow_border,
        )
        text_rect = rect

    painter.setPen(text_color)
    painter.setFont(painter.font())
    painter.drawText(
        text_rect,
        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
        text,
    )
    return text_rect


class ElaThemeToolButton(ElaToolButton):
    """工具按钮。

    继承自 ElaThemeToolButton，支持图标和文字水平排列。
    图标支持主题切换，自动更新颜色。
    外观与 ElaPushButton 一致，支持圆角背景。

    :param text: 按钮文本
    :param icon: 图标名称
    :param iconSize: 图标大小，默认 16
    :param parent: 父控件

    Example::

        btn = ElaThemeToolButton(text="设置", icon=ElaIconType.IconName.Gear, parent=parent)
    """

    def __init__(
        self,
        text: Optional[str] = None,
        icon: Optional[ElaIconType.IconName] = None,
        iconSize: int = 16,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._border_radius = 3
        self._icon_name: Optional[ElaIconType.IconName] = None
        self._icon_size = iconSize
        self.setFixedHeight(38)
        if text:
            self.setText(text)
        if icon:
            self.setElaIcon(icon, iconSize)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._themeConnection = eTheme.themeModeChanged.connect(self._onThemeModeChanged)

    def _onThemeModeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self.update()

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
        if mode == ElaThemeType.ThemeMode.Light:
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBorder)
        return QColor(0, 0, 0, 0)

    def setElaIcon(self, iconName: ElaIconType.IconName, iconSize: int = 16) -> None:
        """设置图标。

        :param iconName: 图标名称
        :param iconSize: 图标大小，默认 16
        """
        self._icon_name = iconName
        self._icon_size = iconSize
        self.setIconSize(QSize(iconSize, iconSize))
        self._updateIconColor()
        self.update()

    def _updateIconColor(self) -> None:
        if self._icon_name is not None:
            text_color = self._getCurrentTextColor()
            icon = ElaIcon.getInstance().getElaIcon(self._icon_name, text_color)
            self.setIcon(icon)

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

        painter.setPen(border_color)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(rect, self._border_radius, self._border_radius)

        def _icon_getter(icon_name, color):
            return ElaIcon.getInstance().getElaIcon(icon_name, color)

        _draw_button_content(
            painter,
            self.text(),
            self._icon_name,
            self._icon_size,
            shadow_border,
            self.width(),
            self.height(),
            text_color,
            _icon_getter,
        )

    def deleteLater(self) -> None:
        try:
            eTheme.themeModeChanged.disconnect(self._themeConnection)
        except (TypeError, RuntimeError):
            pass
        super().deleteLater()


class ElaPrimaryButton(ElaPushButton):
    """主要按钮。

    使用 Primary 主题色的按钮，外观与 ElaToggleButton ON 状态一致。
    支持图标、点击事件等 ElaPushButton 所有功能。

    :param text: 按钮文本
    :param icon: 图标名称
    :param iconSize: 图标大小，默认 16
    :param parent: 父控件

    Example::

        btn = ElaPrimaryButton(text="提交", icon=ElaIconType.IconName.FloppyDisk, parent=parent)
        btn.clicked.connect(lambda: print("点击"))
    """

    def __init__(
        self,
        text: Optional[str] = None,
        icon: Optional[ElaIconType.IconName] = None,
        iconSize: int = 16,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self._border_radius = 3
        self._icon_name: Optional[ElaIconType.IconName] = None
        self._icon_size = iconSize

        if text is not None:
            self.setText(text)
        if icon is not None:
            self.setElaIcon(icon, iconSize)

    def setElaIcon(self, iconName: ElaIconType.IconName, iconSize: int = 16) -> None:
        """设置图标。

        :param iconName: 图标名称
        :param iconSize: 图标大小，默认 16
        """
        self._icon_name = iconName
        self._icon_size = iconSize
        self.setIconSize(QSize(iconSize, iconSize))
        self.update()

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

        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), self._border_radius, self._border_radius)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg_color)
        painter.drawPath(path)

        def _icon_getter(icon_name, color):
            return ElaIcon.getInstance().getElaIcon(icon_name, color)

        _draw_button_content(
            painter,
            self.text(),
            self._icon_name,
            self._icon_size,
            shadow_border,
            self.width(),
            self.height(),
            text_color,
            _icon_getter,
        )

    def setBorderRadius(self, radius: int) -> None:
        """设置圆角大小。

        :param radius: 圆角半径
        """
        self._border_radius = radius
        self.update()

    def borderRadius(self) -> int:
        """返回圆角大小。

        :return: 圆角半径
        """
        return self._border_radius

    def _getPrimaryColor(self) -> QColor:
        current_theme = eTheme.getThemeMode()
        return eTheme.getThemeColor(
            current_theme, ElaThemeType.ThemeColor.PrimaryNormal
        )

    def _getPrimaryHoverColor(self) -> QColor:
        current_theme = eTheme.getThemeMode()
        return eTheme.getThemeColor(current_theme, ElaThemeType.ThemeColor.PrimaryHover)

    def _getPrimaryPressColor(self) -> QColor:
        current_theme = eTheme.getThemeMode()
        return eTheme.getThemeColor(current_theme, ElaThemeType.ThemeColor.PrimaryPress)

    def _getDisableColor(self) -> QColor:
        current_theme = eTheme.getThemeMode()
        return eTheme.getThemeColor(current_theme, ElaThemeType.ThemeColor.BasicDisable)

    def _getTextColor(self) -> QColor:
        current_theme = eTheme.getThemeMode()
        return eTheme.getThemeColor(
            current_theme, ElaThemeType.ThemeColor.BasicTextInvert
        )

    def _getDisableTextColor(self) -> QColor:
        current_theme = eTheme.getThemeMode()
        return eTheme.getThemeColor(
            current_theme, ElaThemeType.ThemeColor.BasicTextDisable
        )

    def _getCurrentBgColor(self) -> QColor:
        if not self.isEnabled():
            return self._getDisableColor()
        if self.isDown():
            return self._getPrimaryPressColor()
        if self.underMouse():
            return self._getPrimaryHoverColor()
        return self._getPrimaryColor()

    def _getCurrentTextColor(self) -> QColor:
        if not self.isEnabled():
            return self._getDisableTextColor()
        return self._getTextColor()
