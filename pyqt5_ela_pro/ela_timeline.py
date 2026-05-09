"""
时间线组件，风格参考 ElaWidgetTools 的 ElaTimeline。

垂直排列时间节点，包含时间戳、标题、正文和可选图标。

用法::

    timeline = ElaTimeline(parent=self)
    timeline.addItem(ElaTimeline.TimelineItem(
        title="事件", content="描述", timestamp="2024-01-01",
    ))
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, QRect, QSize, QRectF
from PyQt5.QtGui import QPainter, QPen, QFont, QFontMetrics, QPaintEvent
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaIconType

from .widget_base import ElaThemeWidget


class ElaTimeline(ElaThemeWidget):
    """时间线组件。

    :param parent: 父控件
    """

    class TimelineItem:
        def __init__(
            self,
            title: str = "",
            content: str = "",
            timestamp: str = "",
            icon: ElaIconType.IconName = ElaIconType.IconName.None_,
        ):
            self.title = title
            self.content = content
            self.timestamp = timestamp
            self.icon = icon

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._items: list[ElaTimeline.TimelineItem] = []
        self._current_step = 0
        self.setObjectName("ElaTimeline")
        self._icon_font = QFont("ElaAwesome")

    def addItem(self, item: TimelineItem) -> None:
        self._items.append(item)
        self.updateGeometry()
        self.update()

    def clearItems(self) -> None:
        self._items.clear()
        self.updateGeometry()
        self.update()

    def itemCount(self) -> int:
        return len(self._items)

    def setCurrentStep(self, index: int) -> None:
        self._current_step = max(0, min(index, len(self._items) - 1))
        self.update()

    def currentStep(self) -> int:
        return self._current_step

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self._items:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        mode = self._theme_mode
        primary = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.PrimaryNormal)
        border = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBorder)
        text = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicText)
        details = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicDetailsText)

        left_margin = 80
        cd = 12
        cr = cd // 2
        icd = 24
        icr = icd // 2
        line_x = left_margin + cr
        content_x = 100
        content_w = self.width() - 120
        gap = 8

        cy = 0
        for i, item in enumerate(self._items):
            has_icon = item.icon != ElaIconType.IconName.None_
            cur_cd = icd if has_icon else cd
            cur_cr = cur_cd // 2

            title_font = self.font()
            title_font.setPixelSize(14)
            title_font.setBold(True)
            tfm = QFontMetrics(title_font)
            th = tfm.height()

            content_font = self.font()
            content_font.setPixelSize(13)
            cfm = QFontMetrics(content_font)
            cth = 0
            if item.content:
                br = cfm.boundingRect(
                    QRect(0, 0, content_w, 10000),
                    Qt.TextFlag.TextWordWrap,
                    item.content,
                )
                cth = br.height()

            ich = th + (4 + cth if cth > 0 else 0)
            ih = max(60, ich + 10)
            cc_y = cy + cur_cr

            # Timestamp
            ts_font = self.font()
            ts_font.setPixelSize(12)
            painter.setFont(ts_font)
            painter.setPen(details)
            painter.drawText(
                QRect(
                    0,
                    cc_y - ts_font.pixelSize() // 2,
                    left_margin - 10,
                    ts_font.pixelSize(),
                ),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                item.timestamp,
            )

            # Circle
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(primary if i == self._current_step else border)
            if has_icon:
                painter.drawEllipse(QRectF(line_x - icr, cc_y - icr, icd, icd))
                self._icon_font.setPixelSize(12)
                painter.setFont(self._icon_font)
                painter.setPen(Qt.GlobalColor.white)
                painter.drawText(
                    QRectF(line_x - icr, cc_y - icr, icd, icd),
                    Qt.AlignmentFlag.AlignCenter,
                    chr(int(item.icon)),
                )
            else:
                painter.drawEllipse(QRectF(left_margin, cc_y - cr, cd, cd))

            # Line
            if i < len(self._items) - 1:
                painter.setPen(QPen(border, 1))
                painter.drawLine(line_x, cc_y + cur_cr, line_x, cy + ih + gap)

            # Title
            painter.setFont(title_font)
            painter.setPen(text)
            painter.drawText(
                QRect(content_x, cy, content_w, th),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                item.title,
            )

            # Content
            if item.content:
                painter.setFont(content_font)
                painter.setPen(details)
                painter.drawText(
                    QRect(content_x, cy + th + 4, content_w, cth),
                    Qt.TextFlag.TextWordWrap
                    | Qt.AlignmentFlag.AlignLeft
                    | Qt.AlignmentFlag.AlignTop,
                    item.content,
                )

            cy += ih + gap

    def sizeHint(self) -> QSize:
        if not self._items:
            return QSize(400, 0)
        content_w = 400 - 120
        gap = 8
        th = 0
        for item in self._items:
            title_font = QFont()
            title_font.setPixelSize(14)
            title_font.setBold(True)
            tfm = QFontMetrics(title_font)
            th2 = tfm.height()

            content_font = QFont()
            content_font.setPixelSize(13)
            cfm = QFontMetrics(content_font)
            cth = 0
            if item.content:
                br = cfm.boundingRect(
                    QRect(0, 0, content_w, 10000),
                    Qt.TextFlag.TextWordWrap,
                    item.content,
                )
                cth = br.height()
            ich = th2 + (4 + cth if cth > 0 else 0)
            th += max(60, ich + 10) + gap
        return QSize(400, th)
