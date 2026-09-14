"""Tests for charts package: ElaChartWidget (ECharts-style engine)."""

from __future__ import annotations


import pytest
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtWidgets import QApplication
from PyQt5ElaWidgetTools import eTheme, ElaThemeType

from pyqt5_ela_pro.charts import (
    SERIES_REGISTRY,
    ElaChartWidget,
    format_value,
    nice_ticks,
    parse_data_point,
)
from pyqt5_ela_pro.charts.axes import GridCoord
from pyqt5_ela_pro.charts.series_cartesian import (
    BarSeriesRenderer,
    HeatmapSeriesRenderer,
    LineSeriesRenderer,
    ScatterSeriesRenderer,
)
from pyqt5_ela_pro.charts.series_hierarchy import PieSeriesRenderer


@pytest.fixture(autouse=True)
def _flush_delete_queue(qapp):
    """每个测试结束后处理 deleteLater 队列。

    无事件循环环境下 deleteLater 不生效，遗留的 chart（含其 QTimer /
    事件过滤器）会污染后续测试（如 Qt 崩溃），这里显式冲刷删除队列。
    """
    yield
    qapp.processEvents()


def _line_option():
    return {
        "title": {"text": "示例"},
        "legend": {},
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": ["一", "二", "三", "四"]},
        "yAxis": {"type": "value"},
        "series": [
            {"type": "line", "name": "A", "data": [1, 2, 3, 4]},
            {"type": "bar", "name": "B", "data": [4, 3, 2, 1]},
        ],
    }


def _render_pixels(chart, count_alpha=False):
    """渲染 widget 并返回 (QImage, 采样像素列表)。"""
    chart.resize(480, 360)
    chart.anim.set_progress(1.0)
    img = chart.grab().toImage()
    px = [img.pixelColor(x, y) for y in range(0, 360, 6) for x in range(0, 480, 6)]
    return img, px


class TestRegistryAndUtils:
    def test_registered_series_types(self):
        """MVP 五个系列均已注册。"""
        for t in ("line", "bar", "scatter", "heatmap", "pie"):
            assert t in SERIES_REGISTRY, f"series {t!r} 未注册"

    def test_renderer_classes_registered(self):
        assert SERIES_REGISTRY["line"] is LineSeriesRenderer
        assert SERIES_REGISTRY["bar"] is BarSeriesRenderer
        assert SERIES_REGISTRY["scatter"] is ScatterSeriesRenderer
        assert SERIES_REGISTRY["heatmap"] is HeatmapSeriesRenderer
        assert SERIES_REGISTRY["pie"] is PieSeriesRenderer

    def test_nice_ticks_basic(self):
        lo, hi, ticks = nice_ticks(0, 10, 5)
        assert lo == 0 and hi == 10
        assert ticks == [0.0, 2.0, 4.0, 6.0, 8.0, 10.0]

    def test_nice_ticks_flat(self):
        lo, hi, ticks = nice_ticks(5, 5)
        assert hi > lo
        assert ticks[0] == lo and ticks[-1] == hi

    def test_format_value(self):
        assert format_value(3) == "3"
        assert format_value(3.5) == "3.5"
        assert format_value(3.14159) == "3.14"
        assert format_value(None) == ""

    def test_parse_data_point(self):
        assert parse_data_point(5, 0) == (0, 5.0)
        assert parse_data_point([1, 2], 0) == (1, 2.0)
        assert parse_data_point({"value": 9}, 3) == (3, 9.0)
        assert parse_data_point("bad", 0) == (0, None)


class TestElaChartWidget:
    def test_initialization(self):
        chart = ElaChartWidget()
        assert chart.option() == {}
        assert chart.series_renderers == []
        assert chart.coords == []
        assert chart.title.text == ""
        chart.deleteLater()

    def test_minimum_size(self):
        chart = ElaChartWidget()
        assert chart.minimumWidth() >= 200
        assert chart.minimumHeight() >= 150
        chart.deleteLater()

    def test_set_option_creates_series_and_coord(self):
        chart = ElaChartWidget()
        chart.set_option(_line_option())
        assert len(chart.series_renderers) == 2
        assert len(chart.coords) == 1
        assert isinstance(chart.coords[0], GridCoord)
        assert chart.title.text == "示例"
        assert len(chart.legend._items) == 2
        chart.deleteLater()

    def test_pie_option_has_no_coord(self):
        chart = ElaChartWidget()
        chart.set_option(
            {"series": [{"type": "pie", "data": [{"name": "a", "value": 1}]}]}
        )
        assert len(chart.series_renderers) == 1
        assert chart.coords == []
        chart.deleteLater()

    def test_unknown_series_type_skipped(self):
        chart = ElaChartWidget()
        chart.set_option({"series": [{"type": "nope", "name": "x", "data": [1]}]})
        assert chart.series_renderers == []
        chart.deleteLater()

    def test_set_option_replaces(self):
        chart = ElaChartWidget()
        chart.set_option(_line_option())
        chart.set_option({"series": [{"type": "pie", "data": [1, 2]}]})
        assert len(chart.series_renderers) == 1
        assert chart.series_renderers[0].name == "series0"
        chart.deleteLater()

    def test_update_option_merges_and_injects_prev_data(self):
        chart = ElaChartWidget()
        chart.set_option(_line_option())
        chart.update_option(
            {"series": [{"data": [9, 8, 7, 6]}, {"data": [1, 1, 1, 1]}]}
        )
        rs = chart.series_renderers
        assert len(rs) == 2
        assert rs[0].prev_data == [1, 2, 3, 4]  # 序号对位注入旧数据
        assert rs[1].prev_data == [4, 3, 2, 1]
        assert rs[0].data() == [9, 8, 7, 6]
        chart.deleteLater()

    def test_animation_manual_progress(self):
        chart = ElaChartWidget()
        chart.set_option(_line_option())
        assert chart.anim.t == 0.0
        chart.anim.set_progress(0.5)
        assert 0.49 < chart.anim.t < 0.51
        chart.anim.set_progress(1.0)
        assert chart.anim.t == 1.0
        chart.deleteLater()

    def test_legend_toggle_series_visibility(self):
        chart = ElaChartWidget()
        chart.set_option(_line_option())
        assert chart.is_series_visible("A")
        chart.set_series_visible("A", False)
        assert not chart.is_series_visible("A")
        assert not chart.series_renderers[0].visible
        chart.set_series_visible("A")
        assert chart.is_series_visible("A")
        chart.deleteLater()


class TestRendering:
    """离屏渲染冒烟：不崩溃 + 关键视觉要素存在。"""

    @pytest.fixture(autouse=True)
    def _restore_theme(self):
        yield
        try:
            if eTheme.getThemeMode() != ElaThemeType.ThemeMode.Light:
                eTheme.setThemeMode(ElaThemeType.ThemeMode.Light)
        except Exception:
            pass

    def test_renders_bar_line_light(self):
        chart = ElaChartWidget()
        chart.set_option(_line_option())
        img, px = _render_pixels(chart)
        colors = [c for c in px if c.alpha() > 0]
        assert len(colors) > 200  # 有实际内容
        chart.deleteLater()

    def test_renders_pie(self):
        chart = ElaChartWidget()
        chart.set_option(
            {
                "series": [
                    {
                        "type": "pie",
                        "radius": ["35%", "65%"],
                        "data": [
                            {"name": "a", "value": 335},
                            {"name": "b", "value": 310},
                            {"name": "c", "value": 234},
                            {"name": "d", "value": 135},
                            {"name": "e", "value": 1548},
                        ],
                    }
                ]
            }
        )
        img, px = _render_pixels(chart)
        # 中心孔区域应接近背景色（环形），外圈存在彩色扇区
        center = img.pixelColor(240, 190)
        ring = [c for c in px if c != center and c.name() not in ("#fdfdfd", "#343434")]
        assert len(ring) > 30
        chart.deleteLater()

    def test_renders_heatmap(self):
        chart = ElaChartWidget()
        data = [[i, j, (i * j) % 10] for i in range(5) for j in range(5)]
        chart.set_option(
            {
                "xAxis": {"type": "category", "data": ["a", "b", "c", "d", "e"]},
                "yAxis": {"type": "category", "data": ["a", "b", "c", "d", "e"]},
                "visualMap": {"min": 0, "max": 10},
                "series": [{"type": "heatmap", "data": data}],
            }
        )
        img, px = _render_pixels(chart)
        distinct = {c.rgb() for c in px}
        assert len(distinct) > 10  # 色带多级渐变
        chart.deleteLater()

    def test_renders_dark_theme(self):
        chart = ElaChartWidget()
        chart.set_option(_line_option())
        eTheme.setThemeMode(ElaThemeType.ThemeMode.Dark)
        chart.anim.set_progress(1.0)
        img = chart.grab().toImage()
        # 深色下画布底色应接近 Ela BasicBase (#343434)
        bg = img.pixelColor(2, 2)
        assert abs(bg.red() - 0x34) < 12 and abs(bg.blue() - 0x34) < 12
        chart.deleteLater()

    def test_render_survives_bad_series_data(self):
        """含 None/坏数据的系列不崩溃（单系列容灾）。"""
        chart = ElaChartWidget()
        chart.set_option(
            {
                "xAxis": {"type": "category", "data": ["a", "b"]},
                "yAxis": {},
                "series": [
                    {"type": "line", "name": "ok", "data": [1, 2]},
                    {"type": "bar", "name": "bad", "data": [None, "x"]},
                ],
            }
        )
        chart.anim.set_progress(1.0)
        assert chart.grab().toImage().width() == chart.width()
        chart.deleteLater()


class TestLineSampling:
    """大数据动态降采样（tsdownsample）行为。"""

    @staticmethod
    def _big_option(n, sampling=True, **axis):
        xopt = {"type": "value"}
        xopt.update(axis)
        return {
            "xAxis": xopt,
            "yAxis": {"type": "value"},
            "series": [
                {
                    "type": "line",
                    "name": "A",
                    "data": [i % 1000 for i in range(n)],
                    "sampling": sampling,
                }
            ],
        }

    def test_large_data_is_sampled(self):
        chart = ElaChartWidget()
        chart.resize(800, 500)
        chart.set_option(self._big_option(100_000))
        chart.anim.set_progress(1.0)
        r = chart.series_renderers[0]
        assert r._sampled is True
        assert len(r._points) <= 800 * 2 + 8  # 像素桶 × pointsPerPixel
        assert r._data_len == 100_000
        chart.deleteLater()

    def test_sampling_can_be_disabled(self):
        chart = ElaChartWidget()
        chart.resize(800, 500)
        chart.set_option(self._big_option(100_000, sampling=False))
        chart.anim.set_progress(1.0)
        r = chart.series_renderers[0]
        assert r._sampled is False
        assert len(r._points) == 100_000
        chart.deleteLater()

    def test_window_filter_renders_only_range(self):
        """xAxis min/max 限定的「当前绘图范围」只渲染窗口内数据。"""
        chart = ElaChartWidget()
        chart.resize(800, 500)
        chart.set_option(self._big_option(100_000, min=10_000, max=11_000))
        chart.anim.set_progress(1.0)
        r = chart.series_renderers[0]
        # 窗口内仅 1001 点（< threshold 2000，不采样但点集=窗口内）
        assert r._sampled is False
        assert 1001 <= len(r._points) <= 1001 + 4
        # 全部点 x 落在窗口
        for pt in r._points:
            assert pt is None or 0 <= pt.x() <= 800
        chart.deleteLater()

    def test_small_window_with_big_data_stays_fast(self):
        chart = ElaChartWidget()
        chart.resize(800, 500)
        chart.set_option(self._big_option(1_000_000, min=0, max=2000))
        chart.anim.set_progress(1.0)
        r = chart.series_renderers[0]
        assert len(r._points) <= 2001  # 窗口内仅 2001 点
        chart.deleteLater()

    def test_zoom_resamples_per_window(self):
        """dataZoom 缩放 / 平移后必须按新窗口实时重采样（缓存 key 含窗口范围）。"""
        import math

        chart = ElaChartWidget()
        chart.resize(900, 500)
        n = 200_000
        data = [500 + 300 * math.sin(i / 180) for i in range(n)]
        chart.set_option(
            {
                "xAxis": {"type": "value"},
                "yAxis": {},
                "series": [
                    {"type": "line", "name": "大数据", "data": data, "sampling": True}
                ],
                "dataZoom": [{"type": "inside"}],
            }
        )
        chart.anim.set_progress(1.0)
        chart.show()
        for _ in range(3):
            QApplication.processEvents()
        r = chart.series_renderers[0]
        dz = next(c for c in chart.components if c.option_key == "dataZoom")

        def first_idx():
            for _ in range(3):
                QApplication.processEvents()
            return r._point_idx[0] if r._point_idx else None

        base = first_idx()
        assert base == 0  # 全幅窗口从起点采样
        dz._wheel_zoom(120, QPointF(chart.width() / 2, chart.height() / 2))
        after_zoom = first_idx()
        assert after_zoom != base, "缩放后采样点集未更新（未按新窗口重采样）"
        # 平移窗口（等宽）—— 旧 bug：n_win 相同导致缓存错误命中
        dz.start += 5
        dz.end += 5
        dz.apply()
        chart.invalidate_layout()
        chart.update()
        after_pan = first_idx()
        assert after_pan != after_zoom, "平移后采样点集未更新（n_win 相同但窗口已变）"
        chart.close()
        chart.deleteLater()

    def test_symbol_interval_sparsifies_symbols(self):
        """大数据符号按 symbolInterval 每隔 N 个原始点画一个。"""
        chart = ElaChartWidget()
        chart.resize(800, 500)
        opt = self._big_option(200_000)
        opt["series"][0]["symbolInterval"] = 500
        chart.set_option(opt)
        chart.anim.set_progress(1.0)
        r = chart.series_renderers[0]
        sym = r._symbol_points(chart.coords[0], False, 500)
        assert len(sym) == 200_000 // 500  # 每 500 个原始点一个符号
        chart.deleteLater()

    def test_unsorted_data_falls_back_safe(self):
        """非单调 x：采样返回空 → 回退全量渲染不崩溃。"""
        import random

        rng = random.Random(7)
        n = 50_000
        data = [[rng.random() * 1000, rng.random() * 100] for _ in range(n)]
        chart = ElaChartWidget()
        chart.resize(600, 400)
        chart.set_option(
            {
                "xAxis": {"type": "value"},
                "yAxis": {"type": "value"},
                "series": [{"type": "line", "name": "A", "data": data}],
            }
        )
        chart.anim.set_progress(1.0)
        assert chart.grab().toImage().width() == chart.width()
        chart.deleteLater()

    def test_big_data_renders_within_budget(self):
        """性能预算：100 万点单帧绘制 < 1s（原始实现 10.5s，期望 ~50ms）。"""
        import time

        chart = ElaChartWidget()
        chart.resize(1000, 600)
        chart.set_option(self._big_option(1_000_000))
        chart.anim.set_progress(1.0)
        t0 = time.perf_counter()
        img = chart.grab().toImage()
        elapsed = time.perf_counter() - t0
        assert img.width() == chart.width()
        assert elapsed < 1.0, f"大数据渲染超预算: {elapsed:.2f}s"
        chart.deleteLater()


class TestMoreSeries:
    """其余系列（cartesian 6 + hierarchy 9 + map）注册与渲染冒烟。"""

    ALL = [
        "pictorialBar",
        "effectScatter",
        "candlestick",
        "boxplot",
        "parallel",
        "themeRiver",
        "radar",
        "gauge",
        "funnel",
        "sunburst",
        "treemap",
        "tree",
        "sankey",
        "graph",
        "lines",
        "map",
    ]

    def test_all_registered(self):
        for t in self.ALL:
            assert t in SERIES_REGISTRY, f"series {t!r} 未注册"

    @pytest.mark.parametrize(
        "suffix", ["mix", "hierarchy", "relational", "map", "lines"]
    )
    def test_render_smoke(self, suffix):
        chart = ElaChartWidget()
        chart.resize(700, 450)
        chart.set_option(_option_for(suffix))
        chart.anim.set_progress(1.0)
        assert chart.grab().toImage().width() == chart.width()
        # 停止 effectScatter 等动画定时器，避免活动 QTimer 污染后续测试
        for r in chart.series_renderers:
            stop = getattr(r, "stopAnimation", None)
            if callable(stop):
                stop()
        chart.deleteLater()


class TestComponents:
    def test_mark_components_instantiated(self):
        chart = ElaChartWidget()
        chart.set_option(
            {
                "xAxis": {"type": "category", "data": ["一", "二", "三", "四"]},
                "yAxis": {},
                "series": [
                    {
                        "type": "line",
                        "name": "A",
                        "data": [5, 8, 3, 9],
                        "markPoint": {"data": [{"type": "max"}]},
                        "markLine": {"data": [{"type": "average"}]},
                        "markArea": {"data": [[{"xAxis": "一"}, {"xAxis": "二"}]]},
                    }
                ],
                "graphic": [
                    {
                        "type": "rect",
                        "left": 10,
                        "top": 10,
                        "shape": {"width": 40, "height": 20},
                    }
                ],
            }
        )
        chart.anim.set_progress(1.0)
        keys = {c.option_key for c in chart.components}
        assert {"markPoint", "markLine", "markArea", "graphic"} <= keys
        mp = next(c for c in chart.components if c.option_key == "markPoint")
        assert len(mp._marks) == 1  # max 标注
        ml = next(c for c in chart.components if c.option_key == "markLine")
        assert len(ml._lines) == 1
        chart.deleteLater()

    def test_map_series(self):
        chart = ElaChartWidget()
        chart.set_option(
            {
                "series": [
                    {
                        "type": "map",
                        "name": "区域",
                        "data": [
                            {"name": "华北", "value": 120},
                            {"name": "华东", "value": 200},
                        ],
                    }
                ]
            }
        )
        chart.anim.set_progress(1.0)
        r = chart.series_renderers[0]
        assert len(r._polys) == 7  # DEMO_MAP 7 个区块
        hit = r.hit_test(r._polys[0][1].boundingRect().center())
        assert hit is not None
        chart.deleteLater()


class TestInteract:
    def test_datazoom_slider_windows_categories(self):
        chart = ElaChartWidget()
        chart.resize(700, 450)
        chart.set_option(
            {
                "xAxis": {
                    "type": "category",
                    "data": ["一", "二", "三", "四", "五", "六"],
                },
                "yAxis": {},
                "series": [{"type": "bar", "name": "A", "data": [1, 2, 3, 4, 5, 6]}],
                "dataZoom": [{"type": "slider", "start": 0, "end": 50}],
            }
        )
        chart.anim.set_progress(1.0)
        dz = next(c for c in chart.components if c.option_key == "dataZoom")
        cats = chart.coords[0].x_axis.categories
        assert 2 < len(cats) < 6  # 0-50% 窗口
        # 拖把手
        dz.on_mouse_press(dz._h_start.center())
        dz.on_mouse_move(dz._h_start.center() + QPointF(30, 0))
        dz.on_mouse_release(dz._h_start.center() + QPointF(30, 0))
        assert dz.start > 0
        chart.deleteLater()

    def test_datazoom_restore(self):
        chart = ElaChartWidget()
        chart.resize(700, 450)
        chart.set_option(
            {
                "xAxis": {
                    "type": "category",
                    "data": ["一", "二", "三", "四", "五", "六"],
                },
                "yAxis": {},
                "series": [{"type": "bar", "name": "A", "data": [1, 2, 3, 4, 5, 6]}],
                "dataZoom": [{"type": "inside", "start": 20, "end": 60}],
            }
        )
        chart.anim.set_progress(1.0)
        dz = next(c for c in chart.components if c.option_key == "dataZoom")
        dz.restore()
        assert dz.start == 20.0 and dz.end == 60.0
        chart.deleteLater()

    def test_wheel_inside_zoom_consumes_event(self):
        """滚轮缩放事件必须被图表消费（accept），滚动容器不得同时滚动。

        回归：dataZoom inside 开启时，plot 内滚轮只缩放、不触发页面滚动。
        """
        from PyQt5.QtCore import QPoint
        from PyQt5.QtGui import QWheelEvent
        from PyQt5.QtWidgets import QScrollArea, QVBoxLayout

        sa = QScrollArea()
        sa.resize(600, 400)
        content = __import__("PyQt5.QtWidgets", fromlist=["QWidget"]).QWidget()
        lay = QVBoxLayout(content)
        chart = ElaChartWidget(content)
        chart.setMinimumHeight(700)
        chart.set_option(
            {
                "xAxis": {
                    "type": "category",
                    "data": ["一", "二", "三", "四", "五", "六"],
                },
                "yAxis": {},
                "series": [{"type": "line", "name": "A", "data": [1, 2, 3, 4, 5, 6]}],
                "dataZoom": [{"type": "inside"}],
            }
        )
        chart.anim.set_progress(1.0)
        lay.addWidget(chart)
        sa.setWidget(content)
        sa.show()
        for _ in range(3):
            QApplication.processEvents()

        dz = next(c for c in chart.components if c.option_key == "dataZoom")
        sb = sa.verticalScrollBar()
        plot = chart.coords[0].plot
        ev = QWheelEvent(
            plot.center(),
            chart.mapToGlobal(plot.center().toPoint()),
            QPoint(0, 0),
            QPoint(0, 120),
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.NoScrollPhase,
            False,
        )
        QApplication.sendEvent(chart, ev)
        QApplication.processEvents()
        assert ev.isAccepted(), "滚轮事件未被图表显式 accept（页面会同时滚动）"
        assert dz.end < 100.0, "plot 内滚轮未缩放"
        assert sb.value() == 0, "plot 内滚轮不应滚动容器"
        chart.deleteLater()
        sa.deleteLater()

    def test_wheel_outside_plot_does_not_zoom(self):
        """plot 外滚轮不缩放（事件未消费 → 正常冒泡给容器）。"""
        from PyQt5.QtCore import QPoint
        from PyQt5.QtGui import QWheelEvent

        chart = ElaChartWidget()
        chart.resize(600, 400)
        chart.set_option(
            {
                "xAxis": {
                    "type": "category",
                    "data": ["一", "二", "三", "四", "五", "六"],
                },
                "yAxis": {},
                "series": [{"type": "line", "name": "A", "data": [1, 2, 3, 4, 5, 6]}],
                "dataZoom": [{"type": "inside"}],
            }
        )
        chart.anim.set_progress(1.0)
        dz = next(c for c in chart.components if c.option_key == "dataZoom")
        ev = QWheelEvent(
            QPointF(4, chart.height() - 6),
            chart.mapToGlobal(QPoint(4, chart.height() - 6)),
            QPoint(0, 0),
            QPoint(0, 120),
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.NoScrollPhase,
            False,
        )
        QApplication.sendEvent(chart, ev)
        QApplication.processEvents()
        assert dz.end == 100.0, "plot 外滚轮不应缩放"
        assert not ev.isAccepted(), "plot 外滚轮不应被图表消费"
        chart.deleteLater()

    def test_wheel_on_slider_track_zooms(self):
        """dataZoom slider 轨道上滚轮也缩放（ECharts 习惯）。"""
        from PyQt5.QtCore import QPoint
        from PyQt5.QtGui import QWheelEvent

        chart = ElaChartWidget()
        chart.resize(600, 400)
        chart.set_option(
            {
                "xAxis": {
                    "type": "category",
                    "data": ["一", "二", "三", "四", "五", "六"],
                },
                "yAxis": {},
                "series": [{"type": "bar", "name": "A", "data": [1, 2, 3, 4, 5, 6]}],
                "dataZoom": [{"type": "slider"}, {"type": "inside"}],
            }
        )
        chart.anim.set_progress(1.0)
        dz = next(c for c in chart.components if c.option_key == "dataZoom")
        track = dz._track
        ev = QWheelEvent(
            track.center(),
            chart.mapToGlobal(track.center().toPoint()),
            QPoint(0, 0),
            QPoint(0, 120),
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.NoScrollPhase,
            False,
        )
        QApplication.sendEvent(chart, ev)
        QApplication.processEvents()
        assert ev.isAccepted()
        assert dz.end < 100.0, "slider 轨道滚轮未缩放"
        chart.deleteLater()

    def test_visualmap_map_color(self):
        chart = ElaChartWidget()
        chart.set_option(
            {
                "series": [{"type": "pie", "data": [1]}],
                "visualMap": {"min": 0, "max": 10},
            }
        )
        vm = next(c for c in chart.components if c.option_key == "visualMap")
        c_lo = vm.map_color(0)
        c_hi = vm.map_color(10)
        assert c_lo.name() != c_hi.name()
        chart.deleteLater()

    def test_timeline_goto_updates_option(self):
        chart = ElaChartWidget()
        chart.set_option(
            {
                "xAxis": {"type": "category", "data": ["一", "二"]},
                "yAxis": {},
                "series": [{"type": "bar", "name": "2024", "data": [1, 2]}],
                "timeline": {"data": ["2024", "2025"]},
                "options": [
                    {"series": [{"name": "2025", "data": [3, 4]}]},
                    {"series": [{"name": "2026", "data": [5, 6]}]},
                ],
            }
        )
        chart.anim.set_progress(1.0)
        tl = next(c for c in chart.components if c.option_key == "timeline")
        tl.goto(1)
        assert tl.current == 1
        assert chart.series_renderers[0].data() == [5, 6]
        chart.deleteLater()

    def test_toolbox_toggles_and_restores(self):
        chart = ElaChartWidget()
        chart.resize(700, 450)
        chart.set_option(
            {
                "xAxis": {"type": "category", "data": ["一", "二", "三", "四"]},
                "yAxis": {},
                "series": [{"type": "bar", "name": "A", "data": [1, 2, 3, 4]}],
                "toolbox": {"feature": ["dataZoom", "restore"]},
            }
        )
        chart.anim.set_progress(1.0)
        tb = next(c for c in chart.components if c.option_key == "toolbox")
        assert getattr(chart, "datazoom_enabled", True) is True
        tb.trigger("dataZoom")
        assert getattr(chart, "datazoom_enabled", True) is False
        tb.trigger("restore")  # 不崩溃
        chart.deleteLater()


def _option_for(suffix):
    """渲染冒烟用 option 构造器。"""
    if suffix == "mix":
        return {
            "xAxis": {"type": "category", "data": ["一", "二", "三"]},
            "yAxis": {},
            "series": [
                {
                    "type": "pictorialBar",
                    "name": "象形",
                    "data": [3, 5, 4],
                    "symbol": "circle",
                    "symbolRepeat": True,
                    "symbolSize": 14,
                },
                {
                    "type": "candlestick",
                    "name": "K",
                    "data": [[20, 34, 10, 38], [40, 35, 30, 50], [31, 38, 29, 42]],
                },
                {
                    "type": "boxplot",
                    "name": "箱",
                    "data": [[1, 2, 3, 4, 8], [2, 3, 4, 5, 9], [1, 3, 5, 6, 10]],
                },
            ],
        }
    if suffix == "hierarchy":
        return {
            "series": [
                {
                    "type": "radar",
                    "name": "雷达",
                    "indicator": [{"name": "A", "max": 10}, {"name": "B", "max": 10}],
                    "data": [{"name": "s1", "value": [5, 8]}],
                },
                {"type": "gauge", "name": "仪表", "data": [{"name": "v", "value": 60}]},
                {
                    "type": "funnel",
                    "name": "漏斗",
                    "data": [{"name": "a", "value": 10}, {"name": "b", "value": 6}],
                },
                {
                    "type": "sunburst",
                    "name": "旭日",
                    "data": [
                        {
                            "name": "r",
                            "children": [
                                {"name": "a", "value": 3},
                                {"name": "b", "value": 2},
                            ],
                        }
                    ],
                },
                {
                    "type": "treemap",
                    "name": "树图",
                    "data": [
                        {
                            "name": "r",
                            "children": [
                                {"name": "a", "value": 3},
                                {"name": "b", "value": 2},
                            ],
                        }
                    ],
                },
                {
                    "type": "tree",
                    "name": "树",
                    "data": [{"name": "r", "children": [{"name": "a"}, {"name": "b"}]}],
                },
            ],
        }
    if suffix == "relational":
        return {
            "series": [
                {
                    "type": "sankey",
                    "name": "桑基",
                    "data": [{"name": "a"}, {"name": "b"}, {"name": "c"}],
                    "links": [
                        {"source": "a", "target": "b", "value": 3},
                        {"source": "b", "target": "c", "value": 2},
                    ],
                },
                {
                    "type": "graph",
                    "name": "关系",
                    "data": [{"name": "A"}, {"name": "B"}, {"name": "C"}],
                    "links": [
                        {"source": "A", "target": "B"},
                        {"source": "B", "target": "C"},
                    ],
                },
                {"type": "parallel", "name": "并行", "data": [[1, 2, 3], [4, 5, 6]]},
            ],
        }
    if suffix == "map":
        return {
            "series": [
                {"type": "map", "name": "区域", "data": [{"name": "华北", "value": 1}]}
            ]
        }
    # lines
    return {
        "xAxis": {"type": "value"},
        "yAxis": {},
        "series": [
            {
                "type": "lines",
                "name": "线",
                "data": [{"coords": [[1, 2], [5, 6]]}, {"coords": [[3, 4], [7, 2]]}],
            },
            {
                "type": "effectScatter",
                "name": "涟漪",
                "data": [[2, 3], [4, 5]],
                "rippleEffect": {"period": 2},
            },
            {
                "type": "themeRiver",
                "name": "河",
                "data": [
                    ["2024-01-01", 5, "a"],
                    ["2024-01-02", 8, "a"],
                    ["2024-01-01", 3, "b"],
                    ["2024-01-02", 6, "b"],
                ],
            },
        ],
    }


class TestInteraction:
    def test_bar_hit_test(self):
        chart = ElaChartWidget()
        chart.set_option(_line_option())
        chart.resize(480, 360)
        chart.anim.set_progress(1.0)
        bar = chart.series_renderers[1]
        # 第一根柱的几何中心应可命中
        r = bar._bars[0]["rect"]
        hit = bar.hit_test(r.center())
        assert hit is not None
        assert hit["series"] == "B"
        chart.deleteLater()

    def test_pie_hit_test(self):
        chart = ElaChartWidget()
        chart.set_option(
            {
                "series": [
                    {
                        "type": "pie",
                        "data": [
                            {"name": "big", "value": 800},
                            {"name": "small", "value": 200},
                        ],
                    }
                ]
            }
        )
        chart.resize(480, 360)
        chart.anim.set_progress(1.0)
        pie = chart.series_renderers[0]
        # 从圆心向大扇区方向偏移采样（大扇区自 12 点起 288°）
        center = pie._center
        pt = QPointF(center.x(), center.y() - pie._r_out * 0.6)
        hit = pie.hit_test(pt)
        assert hit is not None
        assert hit["name"] == "big"
        chart.deleteLater()

    def test_color_for_series_custom(self):
        chart = ElaChartWidget()
        chart.set_option({"series": [{"type": "pie", "color": "#ff00aa", "data": [1]}]})
        assert chart.series_renderers[0].color().name() == "#ff00aa"
        chart.deleteLater()


class TestChartOptionalDownsample:
    """可选依赖 tsdownsample 缺失时的降级行为。"""

    def test_render_without_tsdownsample(self, monkeypatch):
        from pyqt5_ela_pro.charts import _downsample as ds

        monkeypatch.setattr(ds, "_AVAILABLE", False)
        monkeypatch.setattr(ds, "np", None)
        assert ds.available() is False
        assert ds.is_sorted([1, 2, 3]) is False
        assert ds.downsample_indices(None, None, 100) is None

        chart = ElaChartWidget()
        chart.set_option(_line_option())
        chart.resize(480, 360)
        chart.anim.set_progress(1.0)
        img = chart.grab().toImage()
        assert not img.isNull()
        assert chart.series_renderers
        chart.deleteLater()
