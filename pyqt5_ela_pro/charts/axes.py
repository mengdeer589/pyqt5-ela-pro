"""
坐标系与轴模型。

- ``Coord``：坐标系协议基类，子类实现
  ``layout(rect)`` / ``map_point(x, y)`` / ``paint_axes(p)`` /
  ``paint_tooltip_marker(p, pos)``；可选 ``set_series(series_opts)``、
  ``invert_x(pos)``（tooltip axis 触发用）。
- ``AxisModel``：category / value 轴模型，支持 name、min/max、nice ticks。
- ``GridCoord``：直角坐标（grid 边距 + x/y 轴 + 刻度网格线）。
- ``PolarCoord``：极坐标（radiusAxis/angleAxis，多边形/圆形网格）。
- ``SingleAxisCoord``：横向单轴。
- ``CalendarCoord``：GitHub 式 周(列)×星期(行) 年历网格。
- ``nice_ticks(vmin, vmax, segments=5)``：数值轴 nice ticks 工具函数。

构造约定：``Coord`` 子类签名为 ``(chart, option)``，``option`` 为完整
图表 option 字典，各坐标系自取所需键（如 ``grid`` / ``xAxis`` …）。
所有配色经 ``T()`` 实时读取，主题切换后重绘即生效。

移植自 InstructionX_UIKit.charts.axes（PySide6 → PyQt5；主题令牌经
charts._tokens 适配到 eTheme / ElaThemeType，原库无 LICENSE，保留出处）。
"""

from __future__ import annotations

import math
from datetime import date, timedelta

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QColor, QFont, QFontMetricsF, QPainter, QPainterPath, QPen

from ._tokens import FONT_FAMILIES, T
from ._utils import to_float as _utils_to_float
from . import _downsample as _ds

__all__ = [
    "nice_ticks",
    "format_value",
    "chart_font",
    "Coord",
    "AxisModel",
    "GridCoord",
    "PolarCoord",
    "SingleAxisCoord",
    "CalendarCoord",
]


# ---------------------------------------------------------------------------
# 工具：字体 / 数值格式化 / nice ticks
# ---------------------------------------------------------------------------


def chart_font(px: int = None, weight: int = None) -> QFont:
    """构造图表用字体（FONT_FAMILIES 字族；px 默认 font.xs）。"""
    font = QFont()
    font.setFamilies(list(FONT_FAMILIES))
    font.setStyleHint(QFont.StyleHint.SansSerif)
    font.setPixelSize(int(px if px else T("font.xs")))
    if weight:
        font.setWeight(QFont.Weight(int(weight)))
    return font


def format_value(v) -> str:
    """数值标签格式化：整数不带小数点，其余保留至多两位小数。"""
    if v is None:
        return ""
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, (int, float)):
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return ""
        if float(v).is_integer() and abs(v) < 1e15:
            return str(int(v))
        return f"{v:.2f}".rstrip("0").rstrip(".")
    return str(v)


def nice_ticks(vmin: float, vmax: float, segments: int = 5):
    """数值轴 nice ticks。

    :param vmin: 数据最小值
    :param vmax: 数据最大值
    :param segments: 目标段数，约 5 段
    :return: ``(nice_min, nice_max, ticks)``，ticks 为含端点的刻度值列表
    """
    vmin = float(vmin)
    vmax = float(vmax)
    if vmin > vmax:
        vmin, vmax = vmax, vmin
    if not math.isfinite(vmin) or not math.isfinite(vmax):
        vmin, vmax = 0.0, 1.0
    if vmin == vmax:
        if vmin == 0:
            vmax = 1.0
        else:
            pad = abs(vmin) * 0.5
            vmin -= pad
            vmax += pad
    segments = max(1, int(segments))
    span = vmax - vmin
    step0 = span / segments
    mag = 10 ** math.floor(math.log10(step0)) if step0 > 0 else 1.0
    step = mag
    for m in (1.0, 2.0, 5.0, 10.0):
        if m * mag >= step0 - 1e-12:
            step = m * mag
            break
    nice_min = math.floor(vmin / step) * step
    nice_max = math.ceil(vmax / step) * step
    if nice_min == nice_max:
        nice_max = nice_min + step
    # 用整数计数避免浮点累积误差
    n = int(round((nice_max - nice_min) / step))
    ticks = []
    for i in range(n + 1):
        t = nice_min + i * step
        ticks.append(0.0 if abs(t) < step * 1e-9 else t)
    return nice_min, nice_max, ticks


# ---------------------------------------------------------------------------
# 坐标协议基类
# ---------------------------------------------------------------------------


class Coord:
    """坐标系协议基类。

    子类必须实现 ``layout`` / ``map_point`` / ``paint_axes`` /
    ``paint_tooltip_marker``。可选：
    ``set_series(series_opts)`` 接收原始系列 option 列表用于范围统计；
    ``invert_x(pos)`` 由像素反推主轴数据值（tooltip axis 触发用）。
    """

    #: 坐标系种类名（"grid" / "polar" / "singleAxis" / "calendar"），
    #: 供 ElaChartWidget.coord_for 按 series.coordinateSystem 匹配。
    kind = ""

    def __init__(self, chart=None, option: dict = None):
        self.chart = chart
        self.option = dict(option or {})
        self.rect = QRectF()

    # -- 协议 ------------------------------------------------------------
    def layout(self, rect: QRectF) -> None:
        """按可用矩形完成几何布局。"""
        self.rect = QRectF(rect)

    def map_point(self, x, y=None) -> QPointF:
        """数据 → 像素。polar 为 (angle, radius)；calendar/single 单参。"""
        raise NotImplementedError

    def paint_axes(self, p: QPainter) -> None:
        """绘制轴线 / 刻度 / 网格 / 标签（主题感知，T() 实时取色）。"""
        raise NotImplementedError

    def paint_tooltip_marker(self, p: QPainter, pos: QPointF) -> None:
        """绘制十字线 / 指示线。"""
        raise NotImplementedError

    # -- 可选 ------------------------------------------------------------
    def set_series(self, series_opts: list) -> None:
        """接收原始系列 option 列表（布局前调用，用于数值范围统计）。"""

    def invert_x(self, pos: QPointF):
        """像素 → 主轴数据值（默认不支持，返回 None）。"""
        return None


# ---------------------------------------------------------------------------
# 轴模型
# ---------------------------------------------------------------------------


def _iter_data_values(data):
    """从系列 data 中迭代全部数值（支持 number / [x, y] / {"value": v}）。"""
    for item in data or []:
        if item is None:
            continue
        v = item
        if isinstance(item, dict):
            v = item.get("value")
        if isinstance(v, (list, tuple)):
            for sub in v:
                if isinstance(sub, (int, float)) and not isinstance(sub, bool):
                    yield float(sub)
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            yield float(v)


class AxisModel:
    """坐标轴模型：category（list[str]）或 value（自动 nice ticks）。

    :param opt: option 中 ``xAxis`` / ``yAxis`` / ``radiusAxis`` 等子字典，
        支持 ``type`` / ``data`` / ``name`` / ``min`` / ``max``
    :param default_type: opt 未给 ``type`` 时的兜底
    """

    def __init__(self, opt: dict = None, default_type: str = "value"):
        opt = dict(opt or {})
        self.opt = opt
        self.type = str(opt.get("type") or default_type)
        self.name = str(opt.get("name") or "")
        self.categories = [str(c) for c in (opt.get("data") or [])]
        #: dataZoom 全量类别缓存：``categories`` 可能被窗口替换，
        #: 本属性始终保留完整列表，供窗外类别映射与窗口偏移换算
        self._all_categories = list(self.categories)
        self.min = opt.get("min")
        self.max = opt.get("max")
        # value 轴：布局前由 set_extent 填充
        self.vmin = 0.0
        self.vmax = 1.0
        self._ticks = [0.0, 1.0]

    # -- 范围 ------------------------------------------------------------
    def set_extent(
        self,
        data_min: float = None,
        data_max: float = None,
        segments: int = 5,
    ) -> None:
        """按数据范围计算 value 轴 nice ticks（min/max 可覆盖端点）。

        非法 min/max（空字符串 / 非数值 / NaN 等输入）降级为未设置。
        """
        if self.type != "value":
            return
        lo = 0.0 if data_min is None else float(data_min)
        hi = 1.0 if data_max is None else float(data_max)
        lo = _to_float(lo, 0.0)
        hi = _to_float(hi, 1.0)
        user_lo = _opt_bound(self.min)
        user_hi = _opt_bound(self.max)
        # 数据全为正时基线取 0、全为负时顶取 0，更符合常规图表观感
        if user_lo is None and lo > 0:
            lo = 0.0
        if user_hi is None and hi < 0:
            hi = 0.0
        if user_lo is not None:
            lo = user_lo
        if user_hi is not None:
            hi = user_hi
        self.vmin, self.vmax, self._ticks = nice_ticks(lo, hi, segments)
        if user_lo is not None:
            self.vmin = user_lo
        if user_hi is not None:
            self.vmax = user_hi

    def ticks(self) -> list:
        """刻度列表：category 返回类别字符串，value 返回数值列表。"""
        if self.type == "category":
            return list(self.categories)
        return list(self._ticks)

    # -- 映射（一维：start→end 像素区间） ----------------------------------
    def local_index(self, value) -> int:
        """category 轴数据值 → 窗口内下标（dataZoom 窗口外返回越界下标）。"""
        if self.type != "category":
            return value
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return int(value) - self.window_offset()
        return self.category_index(value)

    def map(self, value, start: float, end: float, *, local: bool = False) -> float:
        """数据值 → [start, end] 区间内的像素坐标。

        category 轴不 clamp：窗口外类别返回越界坐标，由各系列的
        clipRect 裁剪。``local=True`` 表示 value 已是窗口内下标。
        """
        if self.type == "category":
            if (
                local
                and isinstance(value, (int, float))
                and not isinstance(value, bool)
            ):
                idx = int(value)
            else:
                idx = self.local_index(value)
            n = max(1, len(self.categories))
            band = (end - start) / n
            return start + band * (idx + 0.5)
        v = _to_float(value, self.vmin)
        span = self.vmax - self.vmin
        frac = 0.0 if span == 0 else (v - self.vmin) / span
        return start + (end - start) * frac

    def band_width(self, start: float, end: float) -> float:
        """category 轴单个 band 的像素宽度（value 轴返回 0）。"""
        if self.type != "category" or not self.categories:
            return 0.0
        return abs(end - start) / len(self.categories)

    def category_index(self, value) -> int:
        """类别值（名字或序号）→ 下标（不 clamp）。"""
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return int(value)
        s = str(value)
        if s in self.categories:
            return self.categories.index(s)
        all_cats = getattr(self, "_all_categories", None) or []
        if s in all_cats:
            return all_cats.index(s)  # 窗外类别：全量下标（越界）
        return 0

    def window_offset(self) -> int:
        """dataZoom 类别窗口在全量类别中的起始下标（无窗口时 0）。"""
        all_cats = getattr(self, "_all_categories", None) or []
        if self.categories and all_cats:
            try:
                return all_cats.index(self.categories[0])
            except ValueError:
                return 0
        return 0

    def invert(self, px: float, start: float, end: float):
        """像素 → 数据值（category 返回窗口内下标，越界收敛到窗口边缘）。"""
        if end == start:
            return 0
        frac = (px - start) / (end - start)
        if self.type == "category":
            n = max(1, len(self.categories))
            return min(max(int(frac * n), 0), n - 1)
        return self.vmin + frac * (self.vmax - self.vmin)

    # -- 外观 ------------------------------------------------------------
    def label_font(self) -> QFont:
        """axisLabel 字体（font.xs）。"""
        return chart_font(T("font.xs"))


def _to_float(v, default=0.0) -> float:
    """数值轴映射用宽松转换（NaN/Inf 过滤，防止污染 QPainter 坐标）。"""
    return _utils_to_float(v, default)


def _opt_bound(v):
    """解析轴 min/max 选项：合法数值返回 float，非法返回 None（视为未设置）。"""
    try:
        return _utils_to_float(v, None)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# 直角坐标系
# ---------------------------------------------------------------------------


def _parse_margin(v, default):
    """解析 grid / singleAxis 边距：数值 px 或百分比字符串（"10%"）。

    返回 ``(is_pct, value)``：百分比在 layout 时按 rect 宽 / 高换算；
    非法输入降级为 default（default 可为 None 表示「未设置」）。
    """
    fallback = float(default) if default is not None else None
    if isinstance(v, str):
        s = v.strip()
        if s.endswith("%"):
            try:
                return True, float(s[:-1])
            except ValueError:
                return False, fallback
        if not s:
            return False, fallback
    if v is None:
        return False, fallback
    try:
        return False, float(v)
    except (TypeError, ValueError):
        return False, fallback


def _margin_px(spec, total):
    """把 ``_parse_margin`` 的 ``(is_pct, v)`` 换算为像素（v 为 None 时原样返回）。"""
    is_pct, v = spec
    if v is None:
        return None
    return total * v / 100.0 if is_pct else v


class GridCoord(Coord):
    """直角坐标系：grid 边距 + x/y 轴 + 刻度网格线。

    option 键：``grid`` {left,right,top,bottom}（默认 48/24/40/36）、
    ``xAxis`` / ``yAxis``。边距支持数值 px 或百分比字符串（如 ``"10%"``）。
    ``map_point(x, y)``：x 为类别名/下标或数值，y 为数值。
    ``invert_x(pos)`` 供 tooltip axis 触发。
    """

    kind = "grid"

    def __init__(self, chart=None, option: dict = None):
        super().__init__(chart, option)
        xopt = dict(self.option.get("xAxis") or {})
        yopt = dict(self.option.get("yAxis") or {})
        x_default = "category" if xopt.get("data") else "value"
        self.x_axis = AxisModel(xopt, x_default)
        self.y_axis = AxisModel(yopt, "value")
        grid = dict(self.option.get("grid") or {})
        self._m_left = _parse_margin(grid.get("left"), 48)
        self._m_right = _parse_margin(grid.get("right"), 24)
        self._m_top = _parse_margin(grid.get("top"), 40)
        self._m_bottom = _parse_margin(grid.get("bottom"), 36)
        self.m_left = self.m_right = self.m_top = self.m_bottom = 0.0
        self.plot = QRectF()  # 绘图区（扣除边距）

    # -- 数据范围 ---------------------------------------------------------
    def _numpy_extent(self, data):
        """numpy 快速路径：返回 (x_min, x_max, y_min, y_max) 或 None。

        纯数值列表：x 按下标语义（0 .. n-1）；[x, y] 列表：取两列；
        含字典 / None / 混合形式返回 None（调用方回退 Python 循环）。
        """
        if not data or _ds.np is None:
            return None
        try:
            arr = _ds.np.asarray(data, dtype=_ds.np.float64)
        except (TypeError, ValueError):
            return None
        if arr.ndim == 1 and arr.size:
            ymin, ymax = float(arr.min()), float(arr.max())
            return 0.0, float(arr.size - 1), ymin, ymax
        if arr.ndim == 2 and arr.shape[1] >= 2 and arr.shape[0]:
            xcol, ycol = arr[:, 0], arr[:, 1]
            return (
                float(xcol.min()),
                float(xcol.max()),
                float(ycol.min()),
                float(ycol.max()),
            )
        return None

    def set_series(self, series_opts: list) -> None:
        ys = []
        xs = []
        for s in series_opts or []:
            if not isinstance(s, dict):
                continue
            if s.get("coordinateSystem") not in (None, "cartesian2d", "grid"):
                continue
            data = s.get("data") or []
            ext = self._numpy_extent(data)
            if ext is not None:
                x0, x1, y0, y1 = ext
                ys.extend((y0, y1))
                if self.x_axis.type == "value":
                    xs.extend((x0, x1))
                continue
            for i, item in enumerate(data):
                y = _datum_y(item)
                if y is not None:
                    ys.append(y)
                if self.x_axis.type == "value":
                    x = _datum_x(item)
                    if isinstance(x, (int, float)) and not isinstance(x, bool):
                        xs.append(float(x))
                    elif y is not None:
                        # 纯数值数据：x 取下标（index 语义），保证 value-x 轴范围正确
                        xs.append(float(i))
        if ys:
            self.y_axis.set_extent(min(ys), max(ys))
        else:
            self.y_axis.set_extent(0.0, 1.0)
        if self.x_axis.type == "value":
            if xs:
                self.x_axis.set_extent(min(xs), max(xs))
            else:
                self.x_axis.set_extent(0.0, 1.0)

    # -- 协议 -------------------------------------------------------------
    def layout(self, rect: QRectF) -> None:
        super().layout(rect)
        # 百分比边距在此换算（左右相对宽、上下相对高）
        self.m_left = _margin_px(self._m_left, rect.width())
        self.m_right = _margin_px(self._m_right, rect.width())
        self.m_top = _margin_px(self._m_top, rect.height())
        self.m_bottom = _margin_px(self._m_bottom, rect.height())
        self.plot = QRectF(
            rect.left() + self.m_left,
            rect.top() + self.m_top,
            max(10.0, rect.width() - self.m_left - self.m_right),
            max(10.0, rect.height() - self.m_top - self.m_bottom),
        )

    def map_point(self, x, y=None) -> QPointF:
        px = self.x_axis.map(x, self.plot.left(), self.plot.right())
        py = self.y_axis.map(_to_float(y), self.plot.bottom(), self.plot.top())
        return QPointF(px, py)

    def invert_x(self, pos: QPointF):
        return self.x_axis.invert(pos.x(), self.plot.left(), self.plot.right())

    def paint_axes(self, p: QPainter) -> None:
        p.save()
        font = self.x_axis.label_font()
        p.setFont(font)
        fm = QFontMetricsF(font)
        c_grid = QColor(T("color.border"))
        c_axis = QColor(T("color.border.strong"))
        c_text = QColor(T("color.text.secondary"))
        c_name = QColor(T("color.text.tertiary"))

        # y 轴：水平网格线 + 刻度标签
        for tv in self.y_axis.ticks():
            py = self.y_axis.map(tv, self.plot.bottom(), self.plot.top())
            p.setPen(QPen(c_grid, 1))
            p.drawLine(QPointF(self.plot.left(), py), QPointF(self.plot.right(), py))
            p.setPen(c_text)
            p.drawText(
                QRectF(
                    self.rect.left(),
                    py - fm.height() / 2,
                    max(8.0, self.plot.left() - self.rect.left() - 6),
                    fm.height(),
                ),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                format_value(tv),
            )
        # x 轴：类别标签 / 数值刻度 + 纵向网格线
        if self.x_axis.type == "category":
            for i, cat in enumerate(self.x_axis.categories):
                px = self.x_axis.map(i, self.plot.left(), self.plot.right(), local=True)
                p.setPen(QPen(c_grid, 1))
                p.drawLine(
                    QPointF(px, self.plot.top()), QPointF(px, self.plot.bottom())
                )
                p.setPen(c_text)
                p.drawText(
                    QRectF(px - 40, self.plot.bottom() + 4, 80, fm.height()),
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                    str(cat),
                )
        else:
            for tv in self.x_axis.ticks():
                px = self.x_axis.map(tv, self.plot.left(), self.plot.right())
                p.setPen(QPen(c_grid, 1))
                p.drawLine(
                    QPointF(px, self.plot.top()), QPointF(px, self.plot.bottom())
                )
                p.setPen(c_text)
                p.drawText(
                    QRectF(px - 40, self.plot.bottom() + 4, 80, fm.height()),
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                    format_value(tv),
                )
        # 轴线（下 / 左）
        p.setPen(QPen(c_axis, 1))
        p.drawLine(self.plot.bottomLeft(), self.plot.bottomRight())
        p.drawLine(self.plot.bottomLeft(), self.plot.topLeft())
        # 轴名称
        if self.x_axis.name:
            p.setPen(c_name)
            p.drawText(
                QRectF(
                    self.plot.right() - 80,
                    self.plot.bottom() + 4 + fm.height(),
                    80,
                    fm.height(),
                ),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
                self.x_axis.name,
            )
        if self.y_axis.name:
            p.setPen(c_name)
            p.drawText(
                QRectF(
                    self.rect.left(),
                    self.plot.top() - fm.height() - 4,
                    120,
                    fm.height(),
                ),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                self.y_axis.name,
            )
        p.restore()

    def paint_tooltip_marker(self, p: QPainter, pos: QPointF) -> None:
        p.save()
        pen = QPen(QColor(T("color.border.strong")), 1)
        pen.setStyle(Qt.PenStyle.DashLine)
        p.setPen(pen)
        x = min(max(pos.x(), self.plot.left()), self.plot.right())
        y = min(max(pos.y(), self.plot.top()), self.plot.bottom())
        p.drawLine(QPointF(x, self.plot.top()), QPointF(x, self.plot.bottom()))
        p.drawLine(QPointF(self.plot.left(), y), QPointF(self.plot.right(), y))
        p.restore()


def _datum_y(item):
    """取数据项的 y 值：number / [x, y] / {"value": ...}。"""
    if item is None:
        return None
    v = item.get("value") if isinstance(item, dict) else item
    if isinstance(v, (list, tuple)):
        if len(v) >= 2 and isinstance(v[1], (int, float)):
            return float(v[1])
        if len(v) == 1 and isinstance(v[0], (int, float)):
            return float(v[0])
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    return None


def _datum_x(item):
    """取数据项的 x 值（无则 None，调用方用下标代替）。"""
    if item is None:
        return None
    v = item.get("value") if isinstance(item, dict) else item
    if isinstance(v, (list, tuple)) and v:
        return v[0]
    return None


# ---------------------------------------------------------------------------
# 极坐标系
# ---------------------------------------------------------------------------


class PolarCoord(Coord):
    """极坐标系：radiusAxis（value）+ angleAxis（category/value）。

    option 键：``polar`` {"shape": "polygon"|"circle"}、``radiusAxis``、
    ``angleAxis``。``map_point(angle, radius)``：angle 为类别名/下标或数值，
    radius 为数值；角度自正上方起顺时针。
    """

    kind = "polar"

    def __init__(self, chart=None, option: dict = None):
        super().__init__(chart, option)
        polar = dict(self.option.get("polar") or {})
        self.shape = str(polar.get("shape") or "polygon")
        aopt = dict(self.option.get("angleAxis") or {})
        a_default = "category" if aopt.get("data") else "value"
        self.angle_axis = AxisModel(aopt, a_default)
        self.radius_axis = AxisModel(dict(self.option.get("radiusAxis") or {}), "value")
        self.center = QPointF()
        self.radius = 1.0

    def set_series(self, series_opts: list) -> None:
        rs = []
        for s in series_opts or []:
            if not isinstance(s, dict) or s.get("coordinateSystem") != "polar":
                continue
            for item in s.get("data") or []:
                r = _datum_y(item)
                if r is not None:
                    rs.append(r)
        if rs:
            self.radius_axis.set_extent(0.0, max(rs))
        else:
            self.radius_axis.set_extent(0.0, 1.0)
        if self.angle_axis.type == "value":
            self.angle_axis.set_extent(0.0, 360.0, segments=4)

    def layout(self, rect: QRectF) -> None:
        super().layout(rect)
        margin = 28.0  # 外圈类别标签预留
        self.center = rect.center()
        self.radius = max(10.0, min(rect.width(), rect.height()) / 2 - margin)

    def _angle_frac(self, angle) -> float:
        ax = self.angle_axis
        if ax.type == "category":
            n = max(1, len(ax.categories))
            return (ax.category_index(angle) % n) / n
        span = ax.vmax - ax.vmin
        return 0.0 if span == 0 else (_to_float(angle) - ax.vmin) / span

    def map_point(self, x, y=None) -> QPointF:
        """(angle, radius) → 像素。angle 类别/数值；radius 数值。"""
        frac = self._angle_frac(x)
        theta = -math.pi / 2 + frac * 2 * math.pi  # 正上方起顺时针
        r_span = self.radius_axis.vmax - self.radius_axis.vmin
        r_frac = 0.0 if r_span == 0 else (_to_float(y) - self.radius_axis.vmin) / r_span
        r_frac = min(max(r_frac, 0.0), 1.0)
        r = self.radius * r_frac
        return QPointF(
            self.center.x() + r * math.cos(theta), self.center.y() + r * math.sin(theta)
        )

    def _ring_path(self, frac: float) -> QPainterPath:
        r = self.radius * frac
        path = QPainterPath()
        if (
            self.shape == "circle"
            or self.angle_axis.type != "category"
            or not self.angle_axis.categories
        ):
            path.addEllipse(self.center, r, r)
            return path
        n = len(self.angle_axis.categories)
        for i in range(n):
            theta = -math.pi / 2 + i / n * 2 * math.pi
            pt = QPointF(
                self.center.x() + r * math.cos(theta),
                self.center.y() + r * math.sin(theta),
            )
            if i == 0:
                path.moveTo(pt)
            else:
                path.lineTo(pt)
        path.closeSubpath()
        return path

    def paint_axes(self, p: QPainter) -> None:
        p.save()
        c_grid = QColor(T("color.border"))
        c_text = QColor(T("color.text.secondary"))
        font = self.radius_axis.label_font()
        p.setFont(font)
        fm = QFontMetricsF(font)
        ticks = self.radius_axis.ticks()
        span = self.radius_axis.vmax - self.radius_axis.vmin
        # 环形网格（多边形 / 圆形）
        for tv in ticks[1:]:
            frac = 1.0 if span == 0 else (tv - self.radius_axis.vmin) / span
            p.setPen(QPen(c_grid, 1))
            p.drawPath(self._ring_path(frac))
        # 角轴辐条 + 外圈类别标签
        if self.angle_axis.type == "category" and self.angle_axis.categories:
            n = len(self.angle_axis.categories)
            for i, cat in enumerate(self.angle_axis.categories):
                theta = -math.pi / 2 + i / n * 2 * math.pi
                outer = QPointF(
                    self.center.x() + self.radius * math.cos(theta),
                    self.center.y() + self.radius * math.sin(theta),
                )
                p.setPen(QPen(c_grid, 1))
                p.drawLine(self.center, outer)
                lx = self.center.x() + (self.radius + 14) * math.cos(theta)
                ly = self.center.y() + (self.radius + 14) * math.sin(theta)
                p.setPen(c_text)
                p.drawText(
                    QRectF(lx - 40, ly - fm.height() / 2, 80, fm.height()),
                    Qt.AlignmentFlag.AlignCenter,
                    str(cat),
                )
        # 半径刻度标签（沿正上方辐条）
        for tv in ticks[1:]:
            frac = 1.0 if span == 0 else (tv - self.radius_axis.vmin) / span
            p.setPen(c_text)
            p.drawText(
                QRectF(
                    self.center.x() + 2,
                    self.center.y() - self.radius * frac - fm.height() / 2,
                    48,
                    fm.height(),
                ),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                format_value(tv),
            )
        p.restore()

    def paint_tooltip_marker(self, p: QPainter, pos: QPointF) -> None:
        p.save()
        pen = QPen(QColor(T("color.border.strong")), 1)
        pen.setStyle(Qt.PenStyle.DashLine)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(self.center, pos)
        r = math.hypot(pos.x() - self.center.x(), pos.y() - self.center.y())
        if r > 1:
            p.drawEllipse(self.center, r, r)
        p.restore()


# ---------------------------------------------------------------------------
# 单轴坐标系
# ---------------------------------------------------------------------------


class SingleAxisCoord(Coord):
    """横向单轴坐标系（一行数值轴，系列在其上排布）。

    option 键：``singleAxis`` {left,right,top,bottom,type,min,max,name}
    （left/right 默认 40；top/bottom 不给时取可用区垂直居中）。
    ``map_point(value)`` 单参调用，返回轴线上像素点。
    """

    kind = "singleAxis"

    def __init__(self, chart=None, option: dict = None):
        super().__init__(chart, option)
        sopt = dict(self.option.get("singleAxis") or {})
        self.axis = AxisModel(sopt, "value")
        # 边距支持 px / 百分比（"10%"）；top/bottom 非法输入降级为 None（垂直居中）
        self._m_left = _parse_margin(sopt.get("left"), 40)
        self._m_right = _parse_margin(sopt.get("right"), 40)
        self._m_top = _parse_margin(sopt.get("top"), None)
        self._m_bottom = _parse_margin(sopt.get("bottom"), None)
        self.m_left = self.m_right = self.m_top = self.m_bottom = 0.0
        self.line_y = 0.0
        self.plot = QRectF()

    def set_series(self, series_opts: list) -> None:
        vs = []
        for s in series_opts or []:
            if not isinstance(s, dict) or s.get("coordinateSystem") != "singleAxis":
                continue
            vs.extend(_iter_data_values(s.get("data")))
        if vs:
            self.axis.set_extent(min(vs), max(vs))
        else:
            self.axis.set_extent(0.0, 1.0)

    def layout(self, rect: QRectF) -> None:
        super().layout(rect)
        self.m_left = _margin_px(self._m_left, rect.width())
        self.m_right = _margin_px(self._m_right, rect.width())
        self.m_top = _margin_px(self._m_top, rect.height())
        self.m_bottom = _margin_px(self._m_bottom, rect.height())
        left = rect.left() + self.m_left
        right = rect.right() - self.m_right
        if self.m_top is not None:
            y = rect.top() + self.m_top
        elif self.m_bottom is not None:
            y = rect.bottom() - self.m_bottom
        else:
            y = rect.center().y()
        self.line_y = y
        self.plot = QRectF(left, y, max(10.0, right - left), 0.0)

    def map_point(self, x, y=None) -> QPointF:
        px = self.axis.map(x, self.plot.left(), self.plot.right())
        return QPointF(px, self.line_y)

    def invert_x(self, pos: QPointF):
        return self.axis.invert(pos.x(), self.plot.left(), self.plot.right())

    def paint_axes(self, p: QPainter) -> None:
        p.save()
        c_axis = QColor(T("color.border.strong"))
        c_grid = QColor(T("color.border"))
        c_text = QColor(T("color.text.secondary"))
        font = self.axis.label_font()
        p.setFont(font)
        fm = QFontMetricsF(font)
        p.setPen(QPen(c_axis, 1))
        p.drawLine(
            QPointF(self.plot.left(), self.line_y),
            QPointF(self.plot.right(), self.line_y),
        )
        for tv in self.axis.ticks():
            px = self.axis.map(tv, self.plot.left(), self.plot.right())
            p.setPen(QPen(c_grid, 1))
            p.drawLine(QPointF(px, self.line_y - 4), QPointF(px, self.line_y + 4))
            p.setPen(c_text)
            p.drawText(
                QRectF(px - 40, self.line_y + 6, 80, fm.height()),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                format_value(tv),
            )
        if self.axis.name:
            p.setPen(QColor(T("color.text.tertiary")))
            p.drawText(
                QRectF(
                    self.plot.right() + 6,
                    self.line_y - fm.height() / 2,
                    80,
                    fm.height(),
                ),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                self.axis.name,
            )
        p.restore()

    def paint_tooltip_marker(self, p: QPainter, pos: QPointF) -> None:
        p.save()
        pen = QPen(QColor(T("color.border.strong")), 1)
        pen.setStyle(Qt.PenStyle.DashLine)
        p.setPen(pen)
        x = min(max(pos.x(), self.plot.left()), self.plot.right())
        p.drawLine(QPointF(x, self.rect.top() + 8), QPointF(x, self.rect.bottom() - 8))
        p.restore()


# ---------------------------------------------------------------------------
# 日历坐标系
# ---------------------------------------------------------------------------

_WEEKDAY_LABELS = {0: "周一", 2: "周三", 4: "周五"}  # 行下标 -> 标签
_MONTH_LABELS = [
    "1月",
    "2月",
    "3月",
    "4月",
    "5月",
    "6月",
    "7月",
    "8月",
    "9月",
    "10月",
    "11月",
    "12月",
]


class CalendarCoord(Coord):
    """日历坐标系：GitHub 式 周(列)×星期(行) 年历网格。

    option 键：``calendar`` {"year": int, "cellSize": px 或 "auto",
    "range": ["YYYY-MM-DD", "YYYY-MM-DD"]（可选，默认全年；支持跨年 range，
    月份标签逐月遍历）}。行 = 星期（0=周一 … 6=周日），列 = 周序。
    ``map_point(date)`` 单参：日期（"YYYY-MM-DD" / datetime.date / (y,m,d)）
    → 单元格中心；``cell_rect(date)`` → 单元格矩形；``date_at(pos)`` 反查。
    """

    kind = "calendar"

    def __init__(self, chart=None, option: dict = None):
        super().__init__(chart, option)
        cal = dict(self.option.get("calendar") or {})
        self.cal_opt = cal
        # 非法 year（如 "abc"）降级为当前年份，不崩溃
        try:
            self.year = int(cal.get("year") or date.today().year)
        except (TypeError, ValueError):
            self.year = date.today().year
        self.cell_size_opt = cal.get("cellSize", 14)
        rng = cal.get("range")
        if isinstance(rng, (list, tuple)) and len(rng) >= 2:
            self.start = self._parse_date(rng[0]) or date(self.year, 1, 1)
            self.end = self._parse_date(rng[1]) or date(self.year, 12, 31)
        else:
            self.start = date(self.year, 1, 1)
            self.end = date(self.year, 12, 31)
        if self.end < self.start:
            self.start, self.end = self.end, self.start
        self._cell = 14.0
        self._origin = QPointF()  # 第一列（周）左上角
        self._weeks = 1

    # -- 日期工具 ---------------------------------------------------------
    @staticmethod
    def _parse_date(v):
        """ "YYYY-MM-DD" / date / (y, m, d) → datetime.date（失败 None）。"""
        if isinstance(v, date):
            return v
        if isinstance(v, (list, tuple)) and len(v) >= 3:
            try:
                return date(int(v[0]), int(v[1]), int(v[2]))
            except (TypeError, ValueError):
                return None
        if isinstance(v, str):
            try:
                parts = v.strip().split("-")
                return date(int(parts[0]), int(parts[1]), int(parts[2]))
            except (TypeError, ValueError, IndexError):
                return None
        return None

    def _first_monday(self) -> date:
        return self.start - timedelta(days=self.start.weekday())

    def _month_dates(self) -> list:
        """start→end 逐月 1 日列表（跨年 range 正确，不依赖 self.year）。"""
        out = []
        d = date(self.start.year, self.start.month, 1)
        while d <= self.end:
            out.append(d)
            if d.month == 12:
                d = date(d.year + 1, 1, 1)
            else:
                d = date(d.year, d.month + 1, 1)
        return out

    # -- 协议 -------------------------------------------------------------
    def layout(self, rect: QRectF) -> None:
        super().layout(rect)
        label_top = 16.0  # 月份标签高度
        label_left = 28.0  # 星期标签宽度
        first = self._first_monday()
        self._weeks = max(1, (self.end - first).days // 7 + 1)
        avail_w = max(20.0, rect.width() - label_left - 4)
        avail_h = max(20.0, rect.height() - label_top - 4)
        if str(self.cell_size_opt).lower() == "auto":
            self._cell = max(3.0, min(avail_w / self._weeks, avail_h / 7.0))
        else:
            self._cell = max(3.0, _to_float(self.cell_size_opt, 14.0))
        # 水平居中
        grid_w = self._cell * self._weeks
        ox = rect.left() + label_left + max(0.0, (avail_w - grid_w) / 2)
        self._origin = QPointF(ox, rect.top() + label_top)

    def cell_rect(self, day) -> QRectF:
        """日期 → 单元格矩形（无法解析 / 范围外返回空矩形）。"""
        d = self._parse_date(day)
        if d is None or d < self.start or d > self.end:
            return QRectF()
        first = self._first_monday()
        delta = (d - first).days
        col = delta // 7
        row = d.weekday()
        return QRectF(
            self._origin.x() + col * self._cell,
            self._origin.y() + row * self._cell,
            self._cell,
            self._cell,
        )

    def map_point(self, x, y=None) -> QPointF:
        """日期 → 单元格中心。"""
        r = self.cell_rect(x)
        if r.isNull():
            return QPointF(self._origin)
        return r.center()

    def cell_size(self) -> float:
        """当前单元格边长（px）。"""
        return self._cell

    def weeks(self) -> int:
        """总列数（周数）。"""
        return self._weeks

    def paint_axes(self, p: QPainter) -> None:
        p.save()
        c_text = QColor(T("color.text.tertiary"))
        font = chart_font(T("font.xs"))
        p.setFont(font)
        fm = QFontMetricsF(font)
        p.setPen(c_text)
        # 星期标签（Mon/Wed/Fri 三行）
        for row, label in _WEEKDAY_LABELS.items():
            y = self._origin.y() + row * self._cell
            p.drawText(
                QRectF(
                    self.rect.left(),
                    y,
                    max(8.0, self._origin.x() - self.rect.left() - 4),
                    self._cell,
                ),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                label,
            )
        # 月份标签：每月 1 日所在列（去重；跨年逐月遍历）
        first = self._first_monday()
        last_col = -1
        for d in self._month_dates():
            anchor = d if d >= self.start else self.start
            col = (anchor - first).days // 7
            if col == last_col:
                continue
            last_col = col
            x = self._origin.x() + col * self._cell
            p.drawText(
                QRectF(x, self.rect.top(), 40, fm.height()),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                _MONTH_LABELS[d.month - 1],
            )
        p.restore()

    def paint_tooltip_marker(self, p: QPainter, pos: QPointF) -> None:
        p.save()
        d = self.date_at(pos)
        if d is not None:
            r = self.cell_rect(d)
            pen = QPen(QColor(T("color.primary")), 1.4)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(r.adjusted(0.5, 0.5, -0.5, -0.5))
        p.restore()

    def date_at(self, pos: QPointF):
        """像素 → 日期（网格外返回 None）。"""
        if self._cell <= 0:
            return None
        col = int((pos.x() - self._origin.x()) // self._cell)
        row = int((pos.y() - self._origin.y()) // self._cell)
        if col < 0 or col >= self._weeks or row < 0 or row > 6:
            return None
        d = self._first_monday() + timedelta(days=col * 7 + row)
        if d < self.start or d > self.end:
            return None
        return d
