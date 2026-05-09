"""
步骤条组件，风格参考 ElaWidgetTools 的 ElaSteps。

支持设置步骤数和标题、前进/后退切换。

用法::

    steps = ElaSteps(parent=self)
    steps.setStepTitles(["步骤一", "步骤二", "步骤三"])
    steps.currentStepChanged.connect(lambda v: print(f"当前步骤: {v}"))
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QFont, QPaintEvent
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import eTheme, ElaThemeType

from .widget_base import ElaThemeWidget


class ElaSteps(ElaThemeWidget):
    """步骤条组件。

    :param parent: 父控件
    """

    currentStepChanged = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._current_step = 0
        self._step_count = 3
        self._step_titles: list[str] = []

        self.setObjectName("ElaSteps")
        self.setFixedHeight(70)
        self._icon_font = QFont("ElaAwesome")

    def setCurrentStep(self, n: int) -> None:
        self._current_step = max(0, min(n, self._step_count - 1))
        self.update()

    def currentStep(self) -> int:
        return self._current_step

    def setStepCount(self, n: int) -> None:
        self._step_count = max(1, n)
        self.update()

    def stepCount(self) -> int:
        return self._step_count

    def setStepTitles(self, titles: list[str]) -> None:
        self._step_titles = list(titles)
        self._step_count = max(1, len(titles))
        self.update()

    def stepTitles(self) -> list[str]:
        return self._step_titles

    def next(self) -> None:
        if self._current_step < self._step_count - 1:
            self._current_step += 1
            self.currentStepChanged.emit(self._current_step)
            self.update()

    def previous(self) -> None:
        if self._current_step > 0:
            self._current_step -= 1
            self.currentStepChanged.emit(self._current_step)
            self.update()

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        if self._step_count <= 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = self.width()
        circle_diameter = 28
        circle_radius = circle_diameter // 2
        circle_y = 8
        title_y = 42
        line_center_y = circle_y + circle_radius
        margin = 50
        usable = w - margin * 2
        spacing = usable / (self._step_count - 1) if self._step_count > 1 else 0

        mode = self._theme_mode
        primary = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.PrimaryNormal)
        base = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBase)
        border = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBorder)
        details_text = eTheme.getThemeColor(
            mode, ElaThemeType.ThemeColor.BasicDetailsText
        )
        text_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicText)

        for i in range(self._step_count):
            cx = margin + i * spacing if self._step_count > 1 else w / 2.0

            # Connecting line
            if i < self._step_count - 1:
                nx = margin + (i + 1) * spacing
                painter.setPen(QPen(primary if i < self._current_step else border, 2))
                painter.drawLine(
                    QPointF(cx + circle_radius, line_center_y),
                    QPointF(nx - circle_radius, line_center_y),
                )

            rect = QRectF(
                cx - circle_radius, circle_y, circle_diameter, circle_diameter
            )
            painter.setPen(Qt.PenStyle.NoPen)

            if i < self._current_step:
                painter.setBrush(primary)
                painter.drawEllipse(rect)
                self._icon_font.setPixelSize(14)
                painter.setFont(self._icon_font)
                painter.setPen(Qt.GlobalColor.white)
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, chr(0xEA6C))
            elif i == self._current_step:
                painter.setBrush(primary)
                painter.drawEllipse(rect)
                num_font = self.font()
                num_font.setPixelSize(14)
                num_font.setBold(True)
                painter.setFont(num_font)
                painter.setPen(Qt.GlobalColor.white)
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(i + 1))
            else:
                painter.setBrush(base)
                painter.drawEllipse(rect)
                painter.setPen(QPen(border, 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(rect)
                num_font = self.font()
                num_font.setPixelSize(14)
                num_font.setBold(True)
                painter.setFont(num_font)
                painter.setPen(details_text)
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(i + 1))

            # Title
            if i < len(self._step_titles):
                title_font = self.font()
                title_font.setPixelSize(13)
                painter.setFont(title_font)
                painter.setPen(text_color)
                painter.drawText(
                    QRectF(cx - 60, title_y, 120, 20),
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                    self._step_titles[i],
                )
