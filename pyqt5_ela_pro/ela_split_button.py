"""
拆分按钮组件，风格参考 ElaWidgetTools 的 ElaSplitButton。

左侧为主要按钮区域（文字 + 可选图标），右侧为下拉箭头，
点击箭头弹出菜单。

用法::

    from pyqt5_ela_pro import ElaSplitButton

    btn = ElaSplitButton(text="保存", icon=ElaIconType.IconName.FloppyDisk, parent=self)
    btn.clicked.connect(lambda: print("保存"))

    menu = QMenu(btn)
    menu.addAction("另存为")
    btn.setMenu(menu)
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, QRectF, QSize, pyqtSignal, QPoint, QEvent
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


class ElaSplitButton(ElaThemeWidget):
    """拆分按钮。

    左侧为主操作区域（文字 + 可选图标），右侧为下拉箭头。
    点击左侧发出 ``clicked()`` 信号，点击右侧弹出菜单。

    :param text: 按钮文字
    :param icon: ElaAwesome 图标名称
    :param parent: 父控件
    """

    clicked = pyqtSignal()

    def __init__(
        self,
        text: str = "",
        icon: ElaIconType.IconName = ElaIconType.IconName.None_,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self._text = text
        self._icon = icon
        self._border_radius = 3
        self._dropdown_width = 30
        self._menu: Optional[ElaMenu] = None
        self._is_left_hovered = False
        self._is_right_hovered = False
        self._is_left_pressed = False
        self._is_right_pressed = False

        self.setObjectName("ElaSplitButton")
        self.setFixedHeight(35)
        self.setMouseTracking(True)
        self._icon_font = QFont("ElaAwesome")
        self._arrow_font = QFont("ElaAwesome")

        font = self.font()
        font.setPixelSize(15)
        self.setFont(font)

    # ── Public API ────────────────────────────────────────

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

    def setBorderRadius(self, radius: int) -> None:
        """设置圆角半径。

        :param radius: 圆角半径（像素）
        """
        self._border_radius = radius
        self.update()

    def borderRadius(self) -> int:
        """获取圆角半径。

        :returns: 圆角半径（像素）
        """
        return self._border_radius

    def setMenu(self, menu: ElaMenu) -> None:
        """设置下拉菜单（点击右侧箭头时弹出）。

        :param menu: ElaMenu 实例
        """
        self._menu = menu

    def menu(self) -> Optional[ElaMenu]:
        """获取当前下拉菜单。

        :returns: ElaMenu 实例，未设置时返回 None
        """
        return self._menu

    # ── Internal ──────────────────────────────────────────

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    # ── Events ────────────────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            split_x = self.width() - self._dropdown_width
            if event.pos().x() < split_x:
                self._is_left_pressed = True
            else:
                self._is_right_pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            split_x = self.width() - self._dropdown_width
            if self._is_left_pressed and event.pos().x() < split_x:
                self.clicked.emit()
            elif self._is_right_pressed and event.pos().x() >= split_x:
                if self._menu:
                    pos = self.mapToGlobal(QPoint(0, self.height()))
                    self._menu.popup(pos)
            self._is_left_pressed = False
            self._is_right_pressed = False
            self.update()
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        split_x = self.width() - self._dropdown_width
        left_hovered = event.pos().x() < split_x
        right_hovered = not left_hovered
        if (
            self._is_left_hovered != left_hovered
            or self._is_right_hovered != right_hovered
        ):
            self._is_left_hovered = left_hovered
            self._is_right_hovered = right_hovered
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._is_left_hovered = False
        self._is_right_hovered = False
        self._is_left_pressed = False
        self._is_right_pressed = False
        self.update()
        super().leaveEvent(event)

    # ── Paint ─────────────────────────────────────────────

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = self.width()
        h = self.height()
        br = self._border_radius
        split_x = w - self._dropdown_width

        left_rect = QRectF(0, 0, split_x, h)
        right_rect = QRectF(split_x, 0, self._dropdown_width, h)
        full_rect = QRectF(0, 0, w, h)

        base_color = eTheme.getThemeColor(
            self._theme_mode, ElaThemeType.ThemeColor.BasicBase
        )
        hover_color = eTheme.getThemeColor(
            self._theme_mode, ElaThemeType.ThemeColor.BasicHover
        )
        press_color = eTheme.getThemeColor(
            self._theme_mode, ElaThemeType.ThemeColor.BasicPress
        )
        text_color = eTheme.getThemeColor(
            self._theme_mode, ElaThemeType.ThemeColor.BasicText
        )
        border_color = eTheme.getThemeColor(
            self._theme_mode, ElaThemeType.ThemeColor.BasicBorder
        )

        left_color = (
            press_color
            if self._is_left_pressed
            else (hover_color if self._is_left_hovered else base_color)
        )
        right_color = (
            press_color
            if self._is_right_pressed
            else (hover_color if self._is_right_hovered else base_color)
        )

        path = QPainterPath()
        path.addRoundedRect(full_rect, br, br)
        painter.setClipPath(path)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(left_color)
        painter.drawRect(left_rect)

        painter.setBrush(right_color)
        painter.drawRect(right_rect)

        painter.setClipPath(path)
        if self._theme_mode == ElaThemeType.ThemeMode.Light:
            painter.setPen(QPen(border_color, 1))
        else:
            painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(full_rect, br, br)

        painter.setPen(QPen(border_color, 1))
        painter.drawLine(split_x, 4, split_x, h - 4)

        painter.setPen(text_color)
        if self._icon != ElaIconType.IconName.None_:
            self._icon_font.setPixelSize(18)
            fm_icon = QFontMetrics(self._icon_font)
            icon_w = fm_icon.horizontalAdvance(chr(int(self._icon)))

            text_font = self.font()
            text_fm = QFontMetrics(text_font)
            text_w = 0 if not self._text else text_fm.horizontalAdvance(self._text)

            spacing = 0 if not self._text else 8
            total_w = icon_w + spacing + text_w
            start_x = left_rect.x() + (left_rect.width() - total_w) // 2

            painter.setFont(self._icon_font)
            painter.drawText(
                QRectF(start_x, left_rect.y(), icon_w, left_rect.height()),
                Qt.AlignmentFlag.AlignCenter,
                chr(int(self._icon)),
            )

            if self._text:
                painter.setFont(text_font)
                painter.drawText(
                    QRectF(
                        start_x + icon_w + spacing,
                        left_rect.y(),
                        text_w,
                        left_rect.height(),
                    ),
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                    self._text,
                )
        else:
            painter.setFont(self.font())
            painter.drawText(left_rect, Qt.AlignmentFlag.AlignCenter, self._text)

        self._arrow_font.setPixelSize(14)
        painter.setFont(self._arrow_font)
        painter.setPen(text_color)
        painter.drawText(
            right_rect,
            Qt.AlignmentFlag.AlignCenter,
            chr(int(ElaIconType.IconName.AngleDown)),
        )

    def sizeHint(self) -> QSize:
        fm = QFontMetrics(self.font())
        text_w = 0 if not self._text else fm.horizontalAdvance(self._text)
        icon_w = 24 if self._icon != ElaIconType.IconName.None_ else 0
        spacing = (
            0 if (not self._text or self._icon == ElaIconType.IconName.None_) else 8
        )
        left_w = icon_w + spacing + text_w + 20
        return QSize(left_w + self._dropdown_width, 35)
