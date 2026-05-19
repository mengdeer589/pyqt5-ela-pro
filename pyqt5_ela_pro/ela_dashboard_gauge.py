"""
ElaDashboardGauge - 仪表盘组件。

全 QPainter 自绘，支持值范围、刻度、指针、颜色分段、
动画过渡和深浅色主题自适应。

用法::

    from pyqt5_ela_pro import ElaDashboardGauge

    gauge = ElaDashboardGauge(parent=self)
    gauge.setMinimum(0)
    gauge.setMaximum(200)
    gauge.setValue(120)
    gauge.setTitle("转速")
    gauge.setUnit("r/min")
"""

from __future__ import annotations

import math
from typing import Optional

from PyQt5.QtCore import Qt, QRectF, QPointF, QSize, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QColor, QPaintEvent, QFont
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import eTheme, ElaThemeType

from .widget_base import ElaThemeWidget


class ElaDashboardGauge(ElaThemeWidget):
    """仪表盘组件。

    全 QPainter 自绘圆形仪表盘，支持值范围、刻度、指针、
    动画过渡和深浅色主题自适应。

    :param parent: 父控件
    """

    valueChanged = pyqtSignal(float)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._minimum = 0.0
        self._maximum = 100.0
        self._value = 0.0
        self._animated_value = 0.0
        self._major_tick_count = 10
        self._minor_tick_count = 5
        self._start_angle = 225
        self._span_angle = 270
        self._arc_width = 12
        self._value_pixel_size = 22
        self._is_animated = True
        self._decimals = 0
        self._title = ""
        self._unit = ""
        self._danger_percent = 0.85
        self._warning_percent = 0.65
        self._tick_warning_percent = 0.7
        self._anim_timer = None

        self.setObjectName("ElaDashboardGauge")
        self.setMinimumSize(100, 100)

    def sizeHint(self):
        return QSize(260, 260)

    # ── Public API ────────────────────────────────────────

    def setMinimum(self, minimum: float) -> None:
        """设置最小值。

        :param minimum: 最小值
        """
        self._minimum = minimum
        self._value = max(self._minimum, min(self._value, self._maximum))
        self._animated_value = max(
            self._minimum, min(self._animated_value, self._maximum)
        )
        self.update()

    def minimum(self) -> float:
        """获取最小值。

        :returns: 最小值
        """
        return self._minimum

    def setMaximum(self, maximum: float) -> None:
        """设置最大值。

        :param maximum: 最大值
        """
        self._maximum = maximum
        self._value = max(self._minimum, min(self._value, self._maximum))
        self._animated_value = max(
            self._minimum, min(self._animated_value, self._maximum)
        )
        self.update()

    def maximum(self) -> float:
        """获取最大值。

        :returns: 最大值
        """
        return self._maximum

    def setValue(self, value: float) -> None:
        """设置当前值（带动画过渡）。

        :param value: 当前值
        """
        value = max(self._minimum, min(value, self._maximum))
        if self._value == value:
            return
        self._value = value

        if self._is_animated:
            if self._anim_timer is not None:
                self._anim_timer.stop()
            self._anim_start = self._animated_value
            self._anim_target = value
            self._anim_progress = 0.0
            self._anim_timer = QTimer(self)
            self._anim_timer.setInterval(16)
            self._anim_timer.timeout.connect(self._onAnimTick)
            self._anim_timer.start()
        else:
            self._animated_value = value
            self.update()
        self.valueChanged.emit(value)

    def _onAnimTick(self) -> None:
        if self._anim_timer is None:
            return
        self._anim_progress += self._anim_timer.interval() / 600.0
        t = 1 - pow(1 - self._anim_progress, 3)
        if self._anim_progress >= 1.0:
            self._anim_timer.stop()
            self._anim_timer = None
        self._animated_value = (
            self._anim_start + (self._anim_target - self._anim_start) * t
        )
        self.update()

    def value(self) -> float:
        """获取当前值。

        :returns: 当前值
        """
        return self._value

    def setMajorTickCount(self, n: int) -> None:
        """设置主刻度数量。

        :param n: 主刻度数
        """
        self._major_tick_count = max(2, n)
        self.update()

    def majorTickCount(self) -> int:
        """获取主刻度数量。

        :returns: 主刻度数
        """
        return self._major_tick_count

    def setMinorTickCount(self, n: int) -> None:
        """设置每主刻度的副刻度数量。

        :param n: 副刻度数
        """
        self._minor_tick_count = max(1, n)
        self.update()

    def minorTickCount(self) -> int:
        """获取每主刻度的副刻度数量。

        :returns: 副刻度数
        """
        return self._minor_tick_count

    def setStartAngle(self, angle: int) -> None:
        """设置弧形起始角度。

        :param angle: 起始角度（度）
        """
        self._start_angle = angle
        self.update()

    def startAngle(self) -> int:
        """获取弧形起始角度。

        :returns: 起始角度（度）
        """
        return self._start_angle

    def setSpanAngle(self, angle: int) -> None:
        """设置弧形跨度角度。

        :param angle: 跨度角度（度）
        """
        self._span_angle = max(10, min(angle, 360))
        self.update()

    def spanAngle(self) -> int:
        """获取弧形跨度角度。

        :returns: 跨度角度（度）
        """
        return self._span_angle

    def setArcWidth(self, width: int) -> None:
        """设置弧线宽度。

        :param width: 弧线宽度（像素）
        """
        self._arc_width = max(2, width)
        self.update()

    def arcWidth(self) -> int:
        """获取弧线宽度。

        :returns: 弧线宽度（像素）
        """
        return self._arc_width

    def setValuePixelSize(self, size: int) -> None:
        """设置值文本字号。

        :param size: 字号（像素）
        """
        self._value_pixel_size = max(10, size)
        self.update()

    def valuePixelSize(self) -> int:
        """获取值文本字号。

        :returns: 字号（像素）
        """
        return self._value_pixel_size

    def setIsAnimated(self, animated: bool) -> None:
        """设置值变化是否带动画过渡。

        :param animated: 是否带动画
        """
        self._is_animated = animated

    def isAnimated(self) -> bool:
        """当前值变化是否带动画过渡。

        :returns: 动画状态
        """
        return self._is_animated

    def setDecimals(self, n: int) -> None:
        """设置值文本的小数位数。

        :param n: 小数位数
        """
        self._decimals = max(0, n)
        self.update()

    def decimals(self) -> int:
        """获取值文本的小数位数。

        :returns: 小数位数
        """
        return self._decimals

    def setTitle(self, title: str) -> None:
        """设置标题文字。

        :param title: 标题
        """
        self._title = title
        self.update()

    def title(self) -> str:
        """获取标题文字。

        :returns: 标题
        """
        return self._title

    def setUnit(self, unit: str) -> None:
        """设置值单位。

        :param unit: 单位字符串
        """
        self._unit = unit
        self.update()

    def unit(self) -> str:
        """获取值单位。

        :returns: 单位字符串
        """
        return self._unit

    def setDangerPercent(self, percent: float) -> None:
        """设置危险阈值百分比（超过此值时弧线和指针变红色）。

        :param percent: 百分比（0.0 ~ 1.0）
        """
        self._danger_percent = max(0.0, min(1.0, percent))
        self.update()

    def dangerPercent(self) -> float:
        """获取危险阈值百分比。

        :returns: 百分比
        """
        return self._danger_percent

    def setWarningPercent(self, percent: float) -> None:
        """设置警告阈值百分比（超过此值时弧线变橙色）。

        :param percent: 百分比（0.0 ~ 1.0）
        """
        self._warning_percent = max(0.0, min(1.0, percent))
        self.update()

    def warningPercent(self) -> float:
        """获取警告阈值百分比。

        :returns: 百分比
        """
        return self._warning_percent

    def setTickWarningPercent(self, percent: float) -> None:
        """设置刻度变色阈值百分比（超过此值时刻度变橙色/红色）。

        :param percent: 百分比（0.0 ~ 1.0）
        """
        self._tick_warning_percent = max(0.0, min(1.0, percent))
        self.update()

    def tickWarningPercent(self) -> float:
        """获取刻度变色阈值百分比。

        :returns: 百分比
        """
        return self._tick_warning_percent

    # ── Internal ──────────────────────────────────────────

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    def _percent(self) -> float:
        rng = self._maximum - self._minimum
        if rng <= 0:
            return 0.0
        display = self._animated_value
        return (display - self._minimum) / rng

    def _arcColor(self, percent: float) -> QColor:
        if percent >= self._danger_percent:
            return eTheme.getThemeColor(
                self._theme_mode, ElaThemeType.ThemeColor.StatusDanger
            )
        if percent >= self._warning_percent:
            return QColor(0xF7, 0x94, 0x0B)
        return eTheme.getThemeColor(
            self._theme_mode, ElaThemeType.ThemeColor.PrimaryNormal
        )

    def _tickColor(self, percent: float) -> QColor:
        if percent >= self._danger_percent:
            return eTheme.getThemeColor(
                self._theme_mode, ElaThemeType.ThemeColor.StatusDanger
            )
        if percent >= self._tick_warning_percent:
            return QColor(0xF7, 0x94, 0x0B)
        return eTheme.getThemeColor(self._theme_mode, ElaThemeType.ThemeColor.BasicText)

    # ── Paint ─────────────────────────────────────────────

    def paintEvent(self, _event: QPaintEvent) -> None:
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

            side = min(self.width(), self.height())
            painter.translate(self.width() / 2.0, self.height() / 2.0)
            painter.scale(side / 260.0, side / 260.0)

            radius = 110.0
            aw = self._arc_width
            arc_r = radius - aw / 2.0

            # ── Track arc ──
            track_pen = QPen(
                eTheme.getThemeColor(
                    self._theme_mode, ElaThemeType.ThemeColor.BasicChute
                ),
                aw,
            )
            track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(track_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            arc_rect = QRectF(-arc_r, -arc_r, arc_r * 2, arc_r * 2)
            painter.drawArc(arc_rect, self._start_angle * 16, -self._span_angle * 16)

            # ── Value arc ──
            percent = self._percent()
            value_span = int(self._span_angle * percent)
            arc_color = self._arcColor(percent)
            value_pen = QPen(arc_color, aw)
            value_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(value_pen)
            painter.drawArc(arc_rect, self._start_angle * 16, -value_span * 16)

            # ── Ticks ──
            tick_outer_r = radius - aw - 4
            major_len = 10
            minor_len = 5
            total_ticks = self._major_tick_count * self._minor_tick_count
            pen_major = QPen(self._tickColor(0.0), 2.0)
            pen_minor = QPen(self._tickColor(0.0), 1.0)
            tick_font = QFont(self.font())
            tick_font.setPixelSize(10)

            for i in range(total_ticks + 1):
                tick_angle = self._start_angle - (self._span_angle * i / total_ticks)
                rad = math.radians(tick_angle)
                is_major = i % self._minor_tick_count == 0
                tlen = major_len if is_major else minor_len

                x1 = tick_outer_r * math.cos(rad)
                y1 = -tick_outer_r * math.sin(rad)
                x2 = (tick_outer_r - tlen) * math.cos(rad)
                y2 = -(tick_outer_r - tlen) * math.sin(rad)

                tick_pct = i / total_ticks
                tc = self._tickColor(tick_pct)
                p = QPen(pen_major if is_major else pen_minor)
                p.setColor(tc)
                painter.setPen(p)
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

                if is_major:
                    tick_val = (
                        self._minimum + (self._maximum - self._minimum) * tick_pct
                    )
                    label = f"{tick_val:.{self._decimals}f}"
                    lr = self._decimals * 3 if self._decimals > 0 else 0
                    painter.setFont(tick_font)
                    painter.setPen(tc)
                    label_r = tick_outer_r - tlen - 12
                    lx = label_r * math.cos(rad)
                    ly = -label_r * math.sin(rad)
                    painter.drawText(
                        QRectF(lx - 20 - lr, ly - 8, 40 + lr * 2, 16),
                        Qt.AlignmentFlag.AlignCenter,
                        label,
                    )

            # ── Needle ──
            needle_angle = self._start_angle - self._span_angle * percent
            needle_len = tick_outer_r - major_len - 20
            needle_tail = 12

            painter.save()
            painter.rotate(-(needle_angle - 90))
            needle_path = QPainterPath()
            needle_path.moveTo(QPointF(0, -needle_len))
            needle_path.lineTo(QPointF(-3, 0))
            needle_path.lineTo(QPointF(0, needle_tail))
            needle_path.lineTo(QPointF(3, 0))
            needle_path.closeSubpath()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(arc_color)
            painter.drawPath(needle_path)

            painter.setBrush(
                eTheme.getThemeColor(
                    self._theme_mode, ElaThemeType.ThemeColor.BasicText
                )
            )
            painter.drawEllipse(QPointF(0, 0), 6, 6)
            painter.setBrush(
                eTheme.getThemeColor(
                    self._theme_mode, ElaThemeType.ThemeColor.WindowBase
                )
            )
            painter.drawEllipse(QPointF(0, 0), 3, 3)
            painter.restore()

            # ── Value text ──
            display_val = self._animated_value
            value_text = f"{display_val:.{self._decimals}f}"
            if self._unit:
                value_text += f" {self._unit}"

            val_font = QFont(self.font())
            val_font.setPixelSize(self._value_pixel_size)
            val_font.setBold(True)
            painter.setFont(val_font)
            painter.setPen(arc_color)
            painter.drawText(
                QRectF(-80, 15, 160, 40), Qt.AlignmentFlag.AlignCenter, value_text
            )

            # ── Title ──
            if self._title:
                title_font = QFont(self.font())
                title_font.setPixelSize(13)
                painter.setFont(title_font)
                painter.setPen(
                    eTheme.getThemeColor(
                        self._theme_mode, ElaThemeType.ThemeColor.BasicDetailsText
                    )
                )
                painter.drawText(
                    QRectF(-80, 50, 160, 20), Qt.AlignmentFlag.AlignCenter, self._title
                )
        except Exception:
            import traceback

            traceback.print_exc()
