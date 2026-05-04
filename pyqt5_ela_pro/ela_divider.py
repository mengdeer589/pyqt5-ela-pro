"""
分割线组件，风格参考 Ant Design Divider。

支持水平/垂直方向，可带文字，支持实线/虚线样式，自动适配深浅色主题。

用法::

    from pyqt5_ela_pro import ElaDivider

    ElaDivider(parent=self)                          # 纯水平线
    ElaDivider(text="OR", parent=self)                # 居中文字
    ElaDivider(text="请登录", orientation="left")     # 左对齐文字
    ElaDivider(variant="dashed", parent=self)          # 虚线
    ElaDivider(vertical=True, parent=self)             # 垂直线
"""

from __future__ import annotations

from typing import Literal, Optional

from PyQt5.QtCore import QRect, QSize, Qt
from PyQt5.QtGui import QPainter, QPaintEvent, QPen
from PyQt5.QtWidgets import QSizePolicy, QWidget
from PyQt5ElaWidgetTools import ElaThemeType, eTheme

from ._internal import disconnect_theme_signal

ElaDividerOrientation = Literal["left", "center", "right", "top", "bottom"]
ElaDividerVariant = Literal["solid", "dashed"]


class ElaDivider(QWidget):
    """分割线组件。

    支持水平（默认）和垂直方向，可在分割线中嵌入文字，
    文字支持左/中/右（水平）或上/中/下（垂直）定位。

    :param text: 分割线中的文字，为空则不显示文字
    :param orientation: 文字位置
        - 水平模式: ``"left"`` / ``"center"`` / ``"right"``
        - 垂直模式: ``"top"`` / ``"center"`` / ``"bottom"``
    :param variant: 线条样式，``"solid"`` 实线 / ``"dashed"`` 虚线
    :param vertical: ``False`` 水平分割线 / ``True`` 垂直分割线
    :param parent: 父控件
    """

    def __init__(
        self,
        text: str = "",
        orientation: str = "center",
        variant: ElaDividerVariant = "solid",
        vertical: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self._text = text
        self._orientation = orientation
        self._variant = variant
        self._vertical = vertical

        if vertical:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._onThemeChanged(eTheme.getThemeMode())
        eTheme.themeModeChanged.connect(self._onThemeChanged)

    # ── Public API ────────────────────────────────────────

    def setText(self, text: str) -> None:
        self._text = text
        self.update()

    def text(self) -> str:
        return self._text

    def setOrientation(self, orientation: str) -> None:
        self._orientation = orientation
        self.update()

    def orientation(self) -> str:
        return self._orientation

    def setVariant(self, variant: ElaDividerVariant) -> None:
        self._variant = variant
        self.update()

    def variant(self) -> str:
        return self._variant

    def setVertical(self, vertical: bool) -> None:
        self._vertical = vertical
        if vertical:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.update()

    def isVertical(self) -> bool:
        return self._vertical

    # ── Internal ──────────────────────────────────────────

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self.update()

    def deleteLater(self) -> None:
        disconnect_theme_signal(self._onThemeChanged)
        super().deleteLater()

    def sizeHint(self) -> QSize:
        fm = self.fontMetrics()
        if self._vertical:
            text_w = fm.horizontalAdvance(self._text) if self._text else 0
            w = max(2, text_w + 24)
            return QSize(w, 100)
        else:
            text_h = fm.height() if self._text else 0
            h = max(24, text_h + 16)
            return QSize(100, h)

    # ── Paint ─────────────────────────────────────────────

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        mode = eTheme.getThemeMode()
        line_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBaseLine)
        text_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicText)

        if self._vertical:
            self._paint_vertical(painter, line_color, text_color)
        else:
            self._paint_horizontal(painter, line_color, text_color)

    def _paint_horizontal(self, painter: QPainter, line_color, text_color) -> None:
        w = self.width()
        h = self.height()
        gap = 8
        edge_pad = 24

        pen = QPen(line_color, 1)
        if self._variant == "dashed":
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setDashPattern([4, 4])
        painter.setPen(pen)

        cy = h // 2  # vertical center

        if not self._text:
            painter.drawLine(edge_pad, cy, w - edge_pad, cy)
            return

        fm = painter.fontMetrics()
        text_w = fm.horizontalAdvance(self._text)
        text_h = fm.height()

        if self._orientation == "left":
            tx = edge_pad
        elif self._orientation == "right":
            tx = w - edge_pad - text_w
        else:  # center
            tx = (w - text_w) // 2

        ty = cy - text_h // 2
        text_rect = QRect(tx, ty, text_w, text_h)

        # Draw left line segment
        if tx - gap > 0:
            painter.drawLine(0, cy, tx - gap, cy)

        # Draw right line segment
        right_start = tx + text_w + gap
        if right_start < w:
            painter.drawLine(right_start, cy, w, cy)

        # Draw text
        painter.setPen(text_color)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self._text)

    def _paint_vertical(self, painter: QPainter, line_color, text_color) -> None:
        w = self.width()
        h = self.height()
        gap = 8
        edge_pad = 24

        pen = QPen(line_color, 1)
        if self._variant == "dashed":
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setDashPattern([4, 4])
        painter.setPen(pen)

        cx = w // 2  # horizontal center

        if not self._text:
            painter.drawLine(cx, edge_pad, cx, h - edge_pad)
            return

        fm = painter.fontMetrics()
        text_w = fm.horizontalAdvance(self._text)
        text_h = fm.height()

        if self._orientation == "top":
            ty = edge_pad
        elif self._orientation == "bottom":
            ty = h - edge_pad - text_h
        else:  # center
            ty = (h - text_h) // 2

        tx = cx - text_w // 2
        text_rect = QRect(tx, ty, text_w, text_h)

        # Draw top line segment
        if ty - gap > 0:
            painter.drawLine(cx, 0, cx, ty - gap)

        # Draw bottom line segment
        bottom_start = ty + text_h + gap
        if bottom_start < h:
            painter.drawLine(cx, bottom_start, cx, h)

        # Draw text
        painter.setPen(text_color)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self._text)
