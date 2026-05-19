"""
下拉按钮组件，风格参考 ElaWidgetTools 的 ElaDropDownButton。

点击展开下拉菜单。

用法::

    from pyqt5_ela_pro import ElaDropDownButton

    btn = ElaDropDownButton(text="操作", icon=ElaIconType.IconName.Gear, parent=self)

    menu = ElaMenu(btn)
    menu.addAction("选项一")
    btn.setMenu(menu)
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, QRect, QRectF, QSize, QPoint, QEvent
from PyQt5.QtGui import (
    QPainter,
    QPainterPath,
    QPen,
    QFont,
    QFontMetrics,
    QPaintEvent,
    QMouseEvent,
)
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaIconType, ElaMenu

from .widget_base import ElaThemeWidget


class ElaDropDownButton(ElaThemeWidget):
    """下拉按钮。

    点击展开 ElaMenu。
    支持图标+文字居中，右侧下拉箭头。

    :param text: 按钮文字
    :param icon: ElaAwesome 图标名称
    :param parent: 父控件
    """

    def __init__(
        self,
        text: str = "",
        icon: ElaIconType.IconName = ElaIconType.IconName.None_,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self._text = text
        self._icon = icon
        self._border_radius = 6
        self._menu: Optional[ElaMenu] = None
        self._is_hover = False
        self._is_pressed = False

        self.setObjectName("ElaDropDownButton")
        self.setFixedHeight(35)
        self.setMouseTracking(True)
        self._icon_font = QFont("ElaAwesome")
        self._arrow_font = QFont("ElaAwesome")

    def setText(self, text: str) -> None:
        """设置按钮文字。

        :param text: 文字内容
        """
        self._text = text
        self.updateGeometry()
        self.update()

    def text(self) -> str:
        """获取按钮文字。

        :returns: 文字内容
        """
        return self._text

    def setElaIcon(self, icon: ElaIconType.IconName) -> None:
        """设置按钮图标。

        :param icon: ElaAwesome 图标名称
        """
        self._icon = icon
        self.updateGeometry()
        self.update()

    def elaIcon(self) -> ElaIconType.IconName:
        """获取当前图标。

        :returns: ElaAwesome 图标名称
        """
        return self._icon

    def setBorderRadius(self, r: int) -> None:
        """设置圆角半径。

        :param r: 圆角半径（像素）
        """
        self._border_radius = r
        self.update()

    def borderRadius(self) -> int:
        """获取圆角半径。

        :returns: 圆角半径（像素）
        """
        return self._border_radius

    def setMenu(self, menu: ElaMenu) -> None:
        """设置下拉菜单。

        :param menu: ElaMenu 实例
        """
        self._menu = menu

    def menu(self) -> Optional[ElaMenu]:
        """获取当前下拉菜单。

        :returns: ElaMenu 实例，未设置时返回 None
        """
        return self._menu

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    # ── Events ────────────────────────────────────────────

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.HoverEnter:
            self._is_hover = True
            self.update()
        elif event.type() == QEvent.Type.HoverLeave:
            self._is_hover = False
            self.update()
        return super().event(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = False
            self.update()
            if self._menu and self.rect().contains(event.pos()):
                self._menu.popup(self.mapToGlobal(QPoint(0, self.height())))
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._is_hover = False
        self._is_pressed = False
        self.update()
        super().leaveEvent(event)

    # ── Paint ─────────────────────────────────────────────

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        br = self._border_radius
        path = QPainterPath()
        path.addRoundedRect(
            QRectF(0.5, 0.5, self.width() - 1, self.height() - 1), br, br
        )

        if self._is_pressed:
            painter.fillPath(
                path,
                eTheme.getThemeColor(
                    self._theme_mode, ElaThemeType.ThemeColor.BasicPress
                ),
            )
        elif self._is_hover:
            painter.fillPath(
                path,
                eTheme.getThemeColor(
                    self._theme_mode, ElaThemeType.ThemeColor.BasicHover
                ),
            )
        else:
            painter.fillPath(
                path,
                eTheme.getThemeColor(
                    self._theme_mode, ElaThemeType.ThemeColor.BasicBase
                ),
            )

        if self._theme_mode == ElaThemeType.ThemeMode.Light:
            painter.setPen(
                QPen(
                    eTheme.getThemeColor(
                        self._theme_mode, ElaThemeType.ThemeColor.BasicBorder
                    ),
                    1,
                )
            )
            painter.drawPath(path)

        text_color = eTheme.getThemeColor(
            self._theme_mode, ElaThemeType.ThemeColor.BasicText
        )
        arrow_w = 20
        arrow_margin = 8
        content_left = 10
        content_right = self.width() - arrow_w

        # Calculate content size
        icon_w = 0
        if self._icon != ElaIconType.IconName.None_:
            self._icon_font.setPixelSize(16)
            icon_w = QFontMetrics(self._icon_font).horizontalAdvance(
                chr(int(self._icon))
            )

        text_w = 0
        if self._text:
            text_font = self.font()
            text_w = QFontMetrics(text_font).horizontalAdvance(self._text)

        gap = 6 if (icon_w > 0 and text_w > 0) else 0
        total_w = icon_w + gap + text_w
        dx = content_left + (content_right - content_left - total_w) // 2

        # Icon
        if self._icon != ElaIconType.IconName.None_:
            self._icon_font.setPixelSize(16)
            painter.setFont(self._icon_font)
            painter.setPen(text_color)
            painter.drawText(
                QRect(dx, 0, icon_w, self.height()),
                Qt.AlignmentFlag.AlignCenter,
                chr(int(self._icon)),
            )
            dx += icon_w + gap

        # Text
        if self._text:
            painter.setFont(self.font())
            painter.setPen(text_color)
            painter.drawText(
                QRect(dx, 0, text_w, self.height()),
                Qt.AlignmentFlag.AlignCenter,
                self._text,
            )

        # Arrow
        self._arrow_font.setPixelSize(16)
        painter.setFont(self._arrow_font)
        painter.setPen(text_color)
        painter.drawText(
            QRect(self.width() - arrow_w - arrow_margin, 0, arrow_w, self.height()),
            Qt.AlignmentFlag.AlignCenter,
            chr(int(ElaIconType.IconName.AngleDown)),
        )

    def sizeHint(self) -> QSize:
        icon_w = 0
        if self._icon != ElaIconType.IconName.None_:
            self._icon_font.setPixelSize(16)
            icon_w = QFontMetrics(self._icon_font).horizontalAdvance(
                chr(int(self._icon))
            )

        text_w = 0
        if self._text:
            text_font = QFont()
            text_font.setPixelSize(14)
            text_w = QFontMetrics(text_font).horizontalAdvance(self._text)

        gap = 6 if (icon_w > 0 and text_w > 0) else 0
        total = 10 + icon_w + gap + text_w + 20 + 8 + 10
        return QSize(int(total), 35)
