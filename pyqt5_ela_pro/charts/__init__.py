"""
pyqt5_ela_pro.charts：类 ECharts 原生图表引擎（纯 QPainter + Ela 主题）。

包级导出：``ElaChartWidget`` / ``register_series`` / ``register_component`` /
注册表 / 协议基类 / 坐标系 / 内置组件。

主题：全部颜色经 ``charts._tokens.T`` 映射到 ``eTheme`` / ``ElaThemeType``
语义令牌，深浅色切换实时换肤，观感与 Ela 组件库一致。

说明：本引擎移植自 InstructionX_UIKit.charts（ECharts 风格 set_option API，
PySide6 → PyQt5 改写；原库无 LICENSE，保留出处）。当前阶段已内置
line / bar / scatter / heatmap / pie 五个系列；``series_cartesian`` /
``series_hierarchy`` 后续阶段增量追加其余系列，``components`` /
``interact``（mark*/dataZoom/brush/visualMap/timeline/toolbox）稍后引入。
"""

from .core import (
    COMPONENT_REGISTRY,
    SERIES_REGISTRY,
    ChartAnimation,
    ElaChartWidget,
    Legend,
    SeriesRenderer,
    SimpleLineSeriesRenderer,
    Title,
    Tooltip,
    default_palette,
    format_value,
    nice_ticks,
    parse_data_point,
    register_component,
    register_series,
)
from .axes import (
    AxisModel,
    CalendarCoord,
    Coord,
    GridCoord,
    PolarCoord,
    SingleAxisCoord,
    chart_font,
)

__all__ = [
    "ElaChartWidget",
    "ChartAnimation",
    "SeriesRenderer",
    "Coord",
    "Title",
    "Legend",
    "Tooltip",
    "AxisModel",
    "GridCoord",
    "PolarCoord",
    "SingleAxisCoord",
    "CalendarCoord",
    "SERIES_REGISTRY",
    "COMPONENT_REGISTRY",
    "register_series",
    "register_component",
    "default_palette",
    "nice_ticks",
    "format_value",
    "parse_data_point",
    "chart_font",
    "SimpleLineSeriesRenderer",
]

#: 系列 / 组件模块导入即完成注册（全部系列 + mark*/graphic/map +
#: dataZoom/brush/visualMap/timeline/toolbox）
from . import series_cartesian as _series_cartesian  # noqa: E402,F401
from . import series_hierarchy as _series_hierarchy  # noqa: E402,F401
from . import components as _components  # noqa: E402,F401
from . import interact as _interact  # noqa: E402,F401

del _series_cartesian, _series_hierarchy, _components, _interact
