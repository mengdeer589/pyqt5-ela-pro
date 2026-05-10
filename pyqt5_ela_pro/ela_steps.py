"""
步骤条组件，风格参考 ElaWidgetTools 的 ElaSteps。

支持设置步骤标题、前进/后退切换。
步骤数由标题列表自动决定。

用法::

    steps = ElaSteps(parent=self)
    steps.step_titles = ["步骤一", "步骤二", "步骤三"]
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
        self._step_titles: list[str] = []

        self.setObjectName("ElaSteps")
        self.setFixedHeight(70)
        self._icon_font = QFont("ElaAwesome")

    # ── Derived step count ───────────────────────────────

    @property
    def step_count(self) -> int:
        """当前步骤数（由 ``step_titles`` 自动派生，最少为 1）。

        :returns: 步骤数
        """
        return max(1, len(self._step_titles))

    # ── Public API ───────────────────────────────────────

    def setCurrentStep(self, n: int) -> None:
        """设置当前步骤。

        值会在 ``0`` ~ ``step_count - 1`` 范围内自动修正。
        仅当值变化时发射 ``currentStepChanged`` 信号。

        :param n: 步骤索引
        """
        old = self._current_step
        self._current_step = max(0, min(n, self.step_count - 1))
        if self._current_step != old:
            self.currentStepChanged.emit(self._current_step)
        self.update()

    def currentStep(self) -> int:
        """获取当前步骤索引。

        :returns: 步骤索引
        """
        return self._current_step

    @property
    def step_titles(self) -> list[str]:
        """获取步骤标题列表（返回副本）。

        :returns: 标题列表
        """
        return list(self._step_titles)

    @step_titles.setter
    def step_titles(self, titles: list[str]) -> None:
        """设置步骤标题列表，步骤数由此自动决定。

        如果当前步骤超出新范围，会自动修正。
        """
        self._step_titles = list(titles)
        if self._current_step >= self.step_count:
            self._current_step = max(0, self.step_count - 1)
        self.update()

    def next(self) -> None:
        """前进到下一步。已在最后一步时无效果。"""
        if self._current_step < self.step_count - 1:
            self._current_step += 1
            self.currentStepChanged.emit(self._current_step)
            self.update()

    def previous(self) -> None:
        """后退到上一步。已在第一步时无效果。"""
        if self._current_step > 0:
            self._current_step -= 1
            self.currentStepChanged.emit(self._current_step)
            self.update()

    # ── Internal ─────────────────────────────────────────

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    # ── Paint ────────────────────────────────────────────

    def paintEvent(self, event: QPaintEvent) -> None:
        if self.step_count <= 0:
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
        spacing = usable / (self.step_count - 1) if self.step_count > 1 else 0

        mode = self._theme_mode
        primary = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.PrimaryNormal)
        base = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBase)
        border = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBorder)
        details_text = eTheme.getThemeColor(
            mode, ElaThemeType.ThemeColor.BasicDetailsText
        )
        text_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicText)

        for i in range(self.step_count):
            cx = margin + i * spacing if self.step_count > 1 else w / 2.0

            # Connecting line
            if i < self.step_count - 1:
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
