"""
ElaGroupBox - 主题感知分组框组件。

全 QPainter 自绘，圆角边框，居中标题，自动适配深浅色主题。
参考 ElaWidgetTools C++ 版 ElaGroupBox 设计。

用法::

    from pyqt5_ela_pro import ElaGroupBox

    group = ElaGroupBox("基本信息", parent=self)
    layout = QVBoxLayout(group)
    layout.addWidget(QLineEdit(self))
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, QRect, QRectF, QSize
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QPaintEvent, QFontMetrics
from PyQt5.QtWidgets import QWidget, QSizePolicy

from PyQt5ElaWidgetTools import eTheme, ElaThemeType

from .widget_base import ElaThemeWidget


class ElaGroupBox(ElaThemeWidget):
    """主题感知分组框。

    全 QPainter 自绘圆角边框，居中标题文字，自动适配深浅色主题。

    :param title: 标题文字
    :param border_radius: 边框圆角半径
    :param parent: 父控件
    """

    def __init__(
        self,
        title: str = "",
        border_radius: int = 6,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self._title = title
        self._border_radius = border_radius
        self._title_pixel_size = 14

        self.setObjectName("ElaGroupBox")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    # ── Public API ────────────────────────────────────────

    def setTitle(self, title: str) -> None:
        self._title = title
        self.update()

    def title(self) -> str:
        return self._title

    def setBorderRadius(self, radius: int) -> None:
        self._border_radius = radius
        self.update()

    def borderRadius(self) -> int:
        return self._border_radius

    # ── Internal ──────────────────────────────────────────

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    # ── Paint ─────────────────────────────────────────────

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = self.width()
        h = self.height()
        br = self._border_radius
        mode = self._theme_mode

        # Title sizing
        fm = QFontMetrics(self.font())
        title_text_w = fm.horizontalAdvance(self._title) if self._title else 0
        title_h = fm.height()

        # Colors
        bg_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicPress)
        border_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBaseLine)
        title_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicText)

        # Widget background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg_color)
        painter.drawRect(self.rect())

        # Frame border (rounded rect)
        margin = 2
        frame_top = title_h // 2 + 2
        frame_rect = QRectF(
            margin,
            frame_top,
            w - 2 * margin,
            h - frame_top - margin,
        )
        path = QPainterPath()
        path.addRoundedRect(frame_rect, br, br)
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # Title background gap
        if self._title:
            pad = 12
            gap_w = min(title_text_w + pad * 2, w)
            gap_x = (w - gap_w) // 2
            gap_rect = QRect(gap_x, 0, gap_w, title_h + 4)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            painter.drawRect(gap_rect)

            # Title text
            painter.setPen(title_color)
            title_font = self.font()
            painter.setFont(title_font)
            painter.drawText(gap_rect, Qt.AlignmentFlag.AlignCenter, self._title)

    def sizeHint(self) -> QSize:
        fm = QFontMetrics(self.font())
        title_h = fm.height() + 8
        return QSize(160, title_h + 32)
