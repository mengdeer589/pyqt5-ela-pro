"""
主要按钮组件。

使用 Primary 主题色的按钮，与 ElaToggleButton ON 状态外观一致。
继承自 ElaPushButton，支持图标、点击事件等所有功能。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, QRect, QRectF, QSize
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPen, QFont
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import (
    eTheme,
    ElaThemeType,
    ElaPushButton,
    ElaIcon,
    ElaIconType,
    ElaToolButton,
)


class ElaToolButtonExt(ElaToolButton):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)


class ElaPrimaryButton(ElaPushButton):
    """主要按钮。

    使用 Primary 主题色的按钮，外观与 ElaToggleButton ON 状态一致。
    支持图标、点击事件等 ElaPushButton 所有功能。

    :param parent: 父控件

    Example::

        btn = PrimaryButton(parent)
        btn.setText("提交")
        btn.clicked.connect(lambda: print("点击"))
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self._border_radius = 3
        self._icon_name: Optional[ElaIconType.IconName] = None
        self._icon_size = 16

    def setElaIcon(self, iconName: ElaIconType.IconName, iconSize: int = 16) -> None:
        """设置图标。

        :param iconName: 图标名称
        :param iconSize: 图标大小，默认 16
        """
        self._icon_name = iconName
        self._icon_size = iconSize
        self.setIconSize(QSize(iconSize, iconSize))
        self.update()

    def paintEvent(self, event) -> None:
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

        if self._icon_name is not None:
            icon_size = QSize(self._icon_size, self._icon_size)
            text_rect = QRect(
                shadow_border + icon_size.width() + 8,
                shadow_border,
                self.width() - 2 * shadow_border - icon_size.width() - 8,
                self.height() - 2 * shadow_border,
            )
            icon_rect = QRect(
                shadow_border + 8,
                shadow_border
                + (self.height() - 2 * shadow_border - icon_size.height()) // 2,
                icon_size.width(),
                icon_size.height(),
            )
            icon = ElaIcon.getInstance().getElaIcon(self._icon_name, text_color)
            painter.drawPixmap(icon_rect, icon.pixmap(icon_size))
        else:
            text_rect = rect

        painter.setPen(text_color)
        painter.setFont(self.font())
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
            self.text(),
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
