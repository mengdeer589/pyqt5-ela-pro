"""
TrendChart 趋势图组件。

继承自 QWidget，支持多曲线绘制、主题切换、网格线、交互式指示器和数据点缓存绘制。
参考 SiliconUI 的 SiTrendChart 和 ElaWidgetTools 的配色。
"""

from __future__ import annotations

import math
from typing import Optional, Callable

from PyQt5.QtCore import Qt, QRect, QRectF, QPointF, QPoint
from PyQt5.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QFontMetrics,
    QPen,
    QFont,
    QPixmap,
)
from PyQt5.QtWidgets import QWidget, QToolTip, QFileDialog
from PyQt5.QtSvg import QSvgGenerator

from PyQt5ElaWidgetTools import eTheme, ElaThemeType


class ElaTrendChart(QWidget):
    """TrendChart 趋势图组件。

    支持多曲线绘制、主题切换、网格线显示和交互式指示器。

    :param parent: 父控件

    Example::

        chart = TrendChart(parent)
        chart.addCurve(x=[1, 2, 3], y=[4, 5, 6], name="系列A")
        chart.addCurve(x=[1, 2, 3], y=[7, 8, 9], name="系列B")
        chart.adjustViewRect()
    """

    _LIGHT_COLORS = [
        QColor("#0072BD"),
        QColor("#D95319"),
        QColor("#EDB120"),
        QColor("#77AC30"),
        QColor("#7E2F8E"),
        QColor("#009688"),
        QColor("#A2142F"),
    ]

    _DARK_COLORS = [
        QColor("#4DA6D9"),
        QColor("#E67A52"),
        QColor("#F5C940"),
        QColor("#8DB34A"),
        QColor("#A855C4"),
        QColor("#40B0A8"),
        QColor("#D45060"),
    ]

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self._curves: list[dict] = []
        self._view_rect = QRectF(0, 0, 100, 100)

        self._x_tick_delta = 10.0
        self._y_tick_delta = 10.0

        self._grid_visible = True
        self._legend_visible = True

        self._line_width = 2.0

        self._indicator_index = -1
        self._indicator_point: Optional[QPointF] = None
        self._indicator_visible = False

        self._tooltip_func: Optional[Callable] = None
        self._on_point_clicked: Optional[Callable] = None

        self._data_pixmap: Optional[QPixmap] = None
        self._last_size = QPoint(-1, -1)

        self.setMouseTracking(True)
        self.setMinimumSize(200, 150)

        self._interaction_enabled = False
        self._panning = False
        self._pan_start_pos = QPoint(0, 0)
        self._pan_start_rect = QRectF()

        eTheme.themeModeChanged.connect(self._onThemeChanged)

    def _onThemeChanged(self) -> None:
        self._assignColors()
        self._data_pixmap = None
        self.update()

    def _getThemeColor(self, color_type: ElaThemeType.ThemeColor) -> QColor:
        return eTheme.getThemeColor(eTheme.getThemeMode(), color_type)

    def _getBackgroundColor(self) -> QColor:
        return self._getThemeColor(ElaThemeType.ThemeColor.BasicBase)

    def _getGridColor(self) -> QColor:
        return self._getThemeColor(ElaThemeType.ThemeColor.BasicBorder)

    def _getTextColor(self) -> QColor:
        return self._getThemeColor(ElaThemeType.ThemeColor.BasicText)

    def _getColors(self) -> list[QColor]:
        mode = eTheme.getThemeMode()
        if mode == ElaThemeType.ThemeMode.Dark:
            return self._DARK_COLORS
        return self._LIGHT_COLORS

    def _assignColors(self) -> None:
        colors = self._getColors()
        for i, curve in enumerate(self._curves):
            curve["color"] = colors[i % len(colors)]

    def _getAxisMarginLeft(self) -> int:
        return 50

    def _getAxisMarginBottom(self) -> int:
        return 30

    def _getAxisMarginTop(self) -> int:
        return 10

    def _getAxisMarginRight(self) -> int:
        return 10

    def _getChartRect(self) -> QRect:
        left = self._getAxisMarginLeft()
        top = self._getAxisMarginTop()
        right = self.width() - self._getAxisMarginRight()
        bottom = self.height() - self._getAxisMarginBottom()
        return QRect(left, top, right - left, bottom - top)

    def _getLegendRect(self) -> QRect:
        if not self._curves:
            return QRect(0, 0, 0, 0)

        chart = self._getChartRect()
        font = QFont(self.font())
        font.setPixelSize(11)
        metrics = QFontMetrics(font)

        item_height = 20
        padding = 8
        line_width = 20

        max_name_width = 0
        for curve in self._curves:
            name = curve.get("name", f"曲线{self._curves.index(curve) + 1}")
            w = metrics.horizontalAdvance(name)
            max_name_width = max(max_name_width, w)

        legend_width = padding * 2 + line_width + max_name_width + 10
        legend_height = (
            padding * 2 + len(self._curves) * item_height + (len(self._curves) - 1) * 4
        )

        legend_x = chart.right() - legend_width - 5
        legend_y = chart.top() + 5

        return QRect(legend_x, legend_y, legend_width, legend_height)

    def addCurve(self, x, y, name: Optional[str] = None) -> None:
        """添加一条曲线。

        :param x: x 轴可迭代数据
        :param y: y 轴可迭代数据
        :param name: 曲线名称，用于 tooltip 显示

        Example::

            chart.addCurve(x=[1, 2, 3], y=[4, 5, 6], name="系列A")
        """
        x_list = list(x)
        y_list = list(y)
        if len(x_list) != len(y_list):
            raise ValueError("x and y must have the same length")

        colors = self._getColors()
        color = colors[len(self._curves) % len(colors)]

        self._curves.append(
            {
                "x": x_list,
                "y": y_list,
                "name": name or f"曲线{len(self._curves) + 1}",
                "color": color,
            }
        )
        self._data_pixmap = None
        self.update()

    def clearCurves(self) -> None:
        """清空所有曲线。"""
        self._curves.clear()
        self._data_pixmap = None
        self.update()

    def setData(self, x, y, name: Optional[str] = None) -> None:
        """设置单条曲线（便捷方法，等同于 clearCurves + addCurve）。

        :param x: x 轴可迭代数据
        :param y: y 轴可迭代数据
        :param name: 曲线名称

        Example::

            chart.setData(x=[1, 2, 3], y=[4, 5, 6], name="系列A")
        """
        self.clearCurves()
        self.addCurve(x, y, name)

    def curves(self) -> list[dict]:
        """返回所有曲线数据。

        :return: 曲线列表，每项包含 x, y, name, color
        """
        return self._curves

    def setViewRect(self, rect: QRectF) -> None:
        """设置视图范围。

        :param rect: 视图矩形
        """
        self._view_rect = rect
        self._data_pixmap = None
        self.update()

    def viewRect(self) -> QRectF:
        """返回视图范围。

        :return: 视图矩形
        """
        return self._view_rect

    def adjustViewRect(self) -> None:
        """自动调整视图范围以适配所有曲线数据。"""
        if not self._curves:
            return

        all_x = []
        all_y = []
        for curve in self._curves:
            all_x.extend(curve["x"])
            all_y.extend(curve["y"])

        if not all_x or not all_y:
            return

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        if max_x - min_x < 1:
            max_x = min_x + 1
        if max_y - min_y < 1:
            max_y = min_y + 1

        margin_x = (max_x - min_x) * 0.1
        margin_y = (max_y - min_y) * 0.1

        self._view_rect = QRectF(
            min_x - margin_x,
            min_y - margin_y,
            (max_x - min_x) + 2 * margin_x,
            (max_y - min_y) + 2 * margin_y,
        )
        self._data_pixmap = None
        self.update()

    def setGridVisible(self, visible: bool) -> None:
        """设置网格线是否显示。

        :param visible: True 显示，False 隐藏
        """
        self._grid_visible = visible
        self.update()

    def gridVisible(self) -> bool:
        """返回网格线是否显示。

        :return: True 显示，False 隐藏
        """
        return self._grid_visible

    def setLegendVisible(self, visible: bool) -> None:
        """设置图例是否显示。

        :param visible: True 显示，False 隐藏
        """
        self._legend_visible = visible
        self.update()

    def legendVisible(self) -> bool:
        """返回图例是否显示。

        :return: True 显示，False 隐藏
        """
        return self._legend_visible

    def setToolTipFunc(self, func: Callable) -> None:
        """设置 tooltip 格式化函数。

        :param func: 接收 name, x, y 返回格式化字符串的函数
        """
        self._tooltip_func = func

    def setOnPointClicked(self, callback: Callable) -> None:
        """设置点击数据点的回调。

        :param callback: 接收 name, x, y 的函数
        """
        self._on_point_clicked = callback

    def setInteractionEnabled(self, enabled: bool) -> None:
        """启用或禁用鼠标拖拽平移和滚轮缩放。

        :param enabled: True 启用交互，False 禁用
        """
        self._interaction_enabled = enabled
        if not enabled:
            self._panning = False

    def isInteractionEnabled(self) -> bool:
        """是否启用了鼠标拖拽平移和滚轮缩放。"""
        return self._interaction_enabled

    def setLineWidth(self, width: float) -> None:
        """设置数据线宽度。

        :param width: 线宽
        """
        self._line_width = width
        self._data_pixmap = None
        self.update()

    def coordinateToPos(self, coord: QPointF) -> QPoint:
        """将数据坐标转换为屏幕坐标。

        :param coord: 数据坐标
        :return: 屏幕坐标
        """
        chart = self._getChartRect()
        if self._view_rect.width() == 0 or self._view_rect.height() == 0:
            return chart.center()

        x = (
            chart.left()
            + (coord.x() - self._view_rect.left())
            / self._view_rect.width()
            * chart.width()
        )
        y = (
            chart.bottom()
            - (coord.y() - self._view_rect.top())
            / self._view_rect.height()
            * chart.height()
        )
        return QPoint(int(x), int(y))

    def posToCoordinate(self, pos: QPoint) -> QPointF:
        """将屏幕坐标转换为数据坐标。

        :param pos: 屏幕坐标
        :return: 数据坐标
        """
        chart = self._getChartRect()
        if chart.width() == 0 or chart.height() == 0:
            return QPointF(0, 0)

        x = (
            self._view_rect.left()
            + (pos.x() - chart.left()) / chart.width() * self._view_rect.width()
        )
        y = (
            self._view_rect.top()
            + (chart.bottom() - pos.y()) / chart.height() * self._view_rect.height()
        )
        return QPointF(x, y)

    def _findNearestPoint(self, pos: QPoint) -> tuple[int, QPointF]:
        """找到最近的数据点。

        :return: (曲线索引, 数据点坐标)
        """
        if not self._curves:
            return -1, QPointF(0, 0)

        coord = self.posToCoordinate(pos)
        nearest_curve_idx = -1
        nearest_point = QPointF(0, 0)
        min_dist = float("inf")

        for i, curve in enumerate(self._curves):
            for j in range(len(curve["x"])):
                px = curve["x"][j]
                py = curve["y"][j]
                dist = (px - coord.x()) ** 2 + (py - coord.y()) ** 2
                if dist < min_dist:
                    min_dist = dist
                    nearest_curve_idx = i
                    nearest_point = QPointF(px, py)

        return nearest_curve_idx, nearest_point

    def _drawDataLines(self, painter: QPainter, chart: QRect) -> None:
        """将数据曲线直接绘制到 painter（矢量）。"""
        for curve in self._curves:
            path = QPainterPath()
            first = True

            for j in range(len(curve["x"])):
                screen_pos = self.coordinateToPos(QPointF(curve["x"][j], curve["y"][j]))
                screen_pos = QPoint(
                    screen_pos.x() - chart.left(), screen_pos.y() - chart.top()
                )

                if first:
                    path.moveTo(screen_pos)
                    first = False
                else:
                    path.lineTo(screen_pos)

            pen = QPen(curve["color"])
            pen.setWidthF(self._line_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(path)

    def _renderDataLine(self) -> None:
        """渲染所有数据线到像素缓存。"""
        if not self._curves:
            self._data_pixmap = None
            return
        chart = self._getChartRect()
        if chart.width() <= 0 or chart.height() <= 0:
            return
        pixmap = QPixmap(chart.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._drawDataLines(painter, chart)
        painter.end()
        self._data_pixmap = pixmap
        self._last_size = QPoint(self.width(), self.height())

    def mouseMoveEvent(self, event) -> None:
        if self._panning:
            delta = event.pos() - self._pan_start_pos
            chart = self._getChartRect()
            if chart.width() == 0 or chart.height() == 0:
                return
            dx = -delta.x() / chart.width() * self._pan_start_rect.width()
            dy = delta.y() / chart.height() * self._pan_start_rect.height()
            self._view_rect = QRectF(
                self._pan_start_rect.left() + dx,
                self._pan_start_rect.top() + dy,
                self._pan_start_rect.width(),
                self._pan_start_rect.height(),
            )
            self._data_pixmap = None
            self.update()
            return

        pos = event.pos()
        chart = self._getChartRect()

        if chart.contains(pos):
            curve_idx, nearest = self._findNearestPoint(pos)
            if curve_idx >= 0:
                self._indicator_index = curve_idx
                self._indicator_point = nearest
                self._indicator_visible = True
                self.update()

                curve = self._curves[curve_idx]
                if self._tooltip_func:
                    tip_text = self._tooltip_func(
                        curve["name"], nearest.x(), nearest.y()
                    )
                else:
                    tip_text = (
                        f"{curve['name']}\nx={nearest.x():.2f}\ny={nearest.y():.2f}"
                    )
                QToolTip.showText(event.globalPos(), tip_text, self)
        else:
            self._indicator_visible = False
            self.update()
            QToolTip.hideText()

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)
        if self._interaction_enabled and event.button() == Qt.MouseButton.LeftButton:
            self._panning = True
            self._pan_start_pos = event.pos()
            self._pan_start_rect = QRectF(self._view_rect)
            self.setCursor(Qt.ClosedHandCursor)
            return
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self._indicator_visible
            and self._indicator_index >= 0
            and self._indicator_point
        ):
            if self._on_point_clicked:
                curve = self._curves[self._indicator_index]
                self._on_point_clicked(
                    curve["name"],
                    self._indicator_point.x(),
                    self._indicator_point.y(),
                )

    def mouseReleaseEvent(self, event) -> None:
        super().mouseReleaseEvent(event)
        if self._panning and event.button() == Qt.MouseButton.LeftButton:
            self._panning = False
            self.setCursor(Qt.ArrowCursor)

    def mouseDoubleClickEvent(self, event) -> None:
        if self._interaction_enabled and event.button() == Qt.MouseButton.LeftButton:
            self.adjustViewRect()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event) -> None:
        if not self._interaction_enabled:
            super().wheelEvent(event)
            return
        chart = self._getChartRect()
        if not chart.contains(event.pos()):
            return
        factor = 1.12 if event.angleDelta().y() > 0 else 1.0 / 1.12
        mouse_data = self.posToCoordinate(event.pos())
        cx = mouse_data.x()
        cy = mouse_data.y()
        old_w = self._view_rect.width()
        old_h = self._view_rect.height()
        new_w = old_w / factor
        new_h = old_h / factor
        self._view_rect = QRectF(
            cx - (cx - self._view_rect.left()) / old_w * new_w,
            cy - (cy - self._view_rect.top()) / old_h * new_h,
            new_w,
            new_h,
        )
        self._data_pixmap = None
        self.update()
        event.accept()

    def leaveEvent(self, event) -> None:
        self._indicator_visible = False
        self.update()
        QToolTip.hideText()
        super().leaveEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        self._paint_chart(painter)

    def _paint_chart(self, painter: QPainter, vector_lines: bool = False) -> None:
        """将图表完整绘制到给定的 QPainter 上。

        :param vector_lines: True 时数据线用矢量路径绘制（SVG 导出用）
        """
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        chart = self._getChartRect()

        bg_color = self._getBackgroundColor()
        painter.fillRect(self.rect(), bg_color)

        if self._grid_visible:
            self._drawGrid(painter, chart)

        if vector_lines and self._curves:
            painter.save()
            painter.translate(chart.topLeft())
            self._drawDataLines(painter, chart)
            painter.restore()
        else:
            if self._data_pixmap is None or self._last_size != QPoint(
                self.width(), self.height()
            ):
                self._renderDataLine()
            if self._data_pixmap:
                painter.drawPixmap(chart.topLeft(), self._data_pixmap)

        self._drawIndicator(painter, chart)
        self._drawAxisLabels(painter, chart)

        if self._legend_visible:
            self._drawLegend(painter, chart)

    def save_to_png(self, filepath: str) -> bool:
        """导出为 PNG 图片。

        :param filepath: 保存路径
        :returns: 是否成功
        """
        pixmap = self.grab()
        return pixmap.save(filepath, "PNG")

    def save_to_svg(self, filepath: str) -> bool:
        """导出为 SVG 矢量图。

        :param filepath: 保存路径
        :returns: 是否成功
        """
        generator = QSvgGenerator()
        generator.setFileName(filepath)
        generator.setSize(self.size())
        generator.setViewBox(QRectF(0, 0, self.width(), self.height()))
        generator.setTitle("ElaTrendChart")
        painter = QPainter(generator)
        self._paint_chart(painter, vector_lines=True)
        painter.end()
        return True

    def _computeTickDelta(self, range_value: float, target_ticks: int = 8) -> float:
        """根据数值范围计算合适的刻度间距，使刻度数接近 target_ticks。"""
        if range_value <= 0:
            return 1.0
        raw = range_value / target_ticks
        magnitude = 10 ** math.floor(math.log10(raw))
        normalized = raw / magnitude
        if normalized < 1.5:
            return magnitude
        elif normalized < 3.5:
            return 2 * magnitude
        elif normalized < 7.5:
            return 5 * magnitude
        else:
            return 10 * magnitude

    def _drawGrid(self, painter: QPainter, chart: QRect) -> None:
        """绘制网格线。"""
        grid_color = self._getGridColor()
        pen = QPen(grid_color)
        pen.setWidth(1)
        painter.setPen(pen)

        x_start = self._view_rect.left()
        x_end = self._view_rect.right()
        y_start = self._view_rect.top()
        y_end = self._view_rect.bottom()

        x_tick = self._computeTickDelta(x_end - x_start)
        y_tick = self._computeTickDelta(y_end - y_start)

        x = x_start
        while x <= x_end:
            if abs(x - 0) < 0.001:
                pen.setWidth(2)
                painter.setPen(pen)
            else:
                pen.setWidth(1)
                painter.setPen(pen)

            pos = self.coordinateToPos(QPointF(x, y_start))
            if chart.left() <= pos.x() <= chart.right():
                painter.drawLine(pos.x(), chart.top(), pos.x(), chart.bottom())
            x += x_tick

        y = y_start
        while y <= y_end:
            if abs(y - 0) < 0.001:
                pen.setWidth(2)
                painter.setPen(pen)
            else:
                pen.setWidth(1)
                painter.setPen(pen)

            pos = self.coordinateToPos(QPointF(x_start, y))
            if chart.top() <= pos.y() <= chart.bottom():
                painter.drawLine(chart.left(), pos.y(), chart.right(), pos.y())
            y += y_tick

    def _drawIndicator(self, painter: QPainter, chart: QRect) -> None:
        """绘制指示器。"""
        if (
            not self._indicator_visible
            or self._indicator_index < 0
            or not self._indicator_point
        ):
            return

        pos = self.coordinateToPos(self._indicator_point)
        if not chart.contains(pos):
            return

        curve = self._curves[self._indicator_index]
        indicator_color = curve["color"]

        pen = QPen(indicator_color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(pos.x(), chart.top(), pos.x(), pos.y())

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(indicator_color)
        painter.drawRect(pos.x() - 5, pos.y() - 5, 10, 10)

    def _drawAxisLabels(self, painter: QPainter, chart: QRect) -> None:
        """绘制坐标轴标签。"""
        text_color = self._getTextColor()
        font = QFont(self.font())
        font.setPixelSize(10)
        painter.setFont(font)
        painter.setPen(text_color)

        metrics = QFontMetrics(font)

        x_tick = self._computeTickDelta(
            self._view_rect.right() - self._view_rect.left()
        )
        y_tick = self._computeTickDelta(
            self._view_rect.bottom() - self._view_rect.top()
        )

        x = self._view_rect.left()
        while x <= self._view_rect.right():
            pos = self.coordinateToPos(QPointF(x, 0))
            if chart.left() <= pos.x() <= chart.right():
                label = f"{x:.0f}"
                painter.drawText(
                    pos.x() - metrics.horizontalAdvance(label) // 2,
                    chart.bottom() + 15,
                    label,
                )
            x += x_tick

        y = self._view_rect.top()
        while y <= self._view_rect.bottom():
            pos = self.coordinateToPos(QPointF(0, y))
            if chart.top() <= pos.y() <= chart.bottom():
                label = f"{y:.0f}"
                painter.drawText(
                    chart.left() - metrics.horizontalAdvance(label) - 5,
                    pos.y() + metrics.ascent() // 2,
                    label,
                )
            y += y_tick

    def _drawLegend(self, painter: QPainter, chart: QRect) -> None:
        """绘制图例。"""
        if not self._curves:
            return

        legend_rect = self._getLegendRect()

        bg_color = self._getBackgroundColor()
        text_color = self._getTextColor()

        painter.setPen(QPen(bg_color))
        painter.setBrush(bg_color)
        painter.drawRoundedRect(legend_rect, 4, 4)

        border_color = self._getGridColor()
        painter.setPen(QPen(border_color))
        painter.drawRoundedRect(legend_rect, 4, 4)

        font = QFont(self.font())
        font.setPixelSize(11)
        painter.setFont(font)
        painter.setPen(text_color)

        item_height = 20
        line_width = 20
        padding = 8

        for i, curve in enumerate(self._curves):
            name = curve.get("name", f"曲线{i + 1}")
            y_offset = padding + i * (item_height + 4)

            line_x = legend_rect.left() + padding
            line_y = legend_rect.top() + y_offset + item_height // 2 - 1

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(curve["color"])
            painter.drawRect(line_x, line_y - 3, line_width, 6)

            text_x = line_x + line_width + 6
            text_y = legend_rect.top() + y_offset + item_height // 2 + 4
            painter.setPen(text_color)
            painter.drawText(text_x, text_y, name)
