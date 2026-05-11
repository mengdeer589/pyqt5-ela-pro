from __future__ import annotations

import pytest
from PyQt5.QtCore import Qt

from pyqt5_ela_pro.ela_dashboard_gauge import ElaDashboardGauge


class TestElaDashboardGaugeInit:
    def test_initialization_with_defaults(self):
        g = ElaDashboardGauge()
        assert g.minimum() == 0.0
        assert g.maximum() == 100.0
        assert g.value() == 0.0
        assert g.majorTickCount() == 10
        assert g.minorTickCount() == 5
        assert g.startAngle() == 225
        assert g.spanAngle() == 270
        assert g.arcWidth() == 12
        assert g.valuePixelSize() == 22
        assert g.isAnimated() is True
        assert g.decimals() == 0
        assert g.title() == ""
        assert g.unit() == ""
        assert g.dangerPercent() == 0.85
        assert g.warningPercent() == 0.65
        assert g.tickWarningPercent() == 0.7
        g.deleteLater()

    def test_size_hint(self):
        g = ElaDashboardGauge()
        sz = g.sizeHint()
        assert sz.width() == 260
        assert sz.height() == 260
        g.deleteLater()

    def test_has_value_changed_signal(self):
        g = ElaDashboardGauge()
        assert hasattr(g, "valueChanged")
        assert callable(g.valueChanged)
        g.deleteLater()


class TestElaDashboardGaugeRange:
    def test_set_minimum(self):
        g = ElaDashboardGauge()
        g.setMinimum(20)
        assert g.minimum() == 20
        g.deleteLater()

    def test_set_maximum(self):
        g = ElaDashboardGauge()
        g.setMaximum(200)
        assert g.maximum() == 200
        g.deleteLater()

    def test_value_clamped_to_maximum(self):
        g = ElaDashboardGauge()
        g.setValue(150)
        assert g.value() == 100.0
        g.deleteLater()

    def test_value_clamped_to_minimum(self):
        g = ElaDashboardGauge()
        g.setValue(-10)
        assert g.value() == 0.0
        g.deleteLater()


class TestElaDashboardGaugeValue:
    def test_set_value(self):
        g = ElaDashboardGauge()
        g.setIsAnimated(False)
        g.setValue(75)
        assert g.value() == 75.0
        g.deleteLater()

    def test_set_value_emits_signal(self):
        g = ElaDashboardGauge()
        g.setIsAnimated(False)
        received = []
        g.valueChanged.connect(lambda v: received.append(v))
        g.setValue(50)
        assert 50.0 in received
        g.deleteLater()

    def test_set_value_same_no_emit(self):
        g = ElaDashboardGauge()
        g.setIsAnimated(False)
        g.setValue(50)
        received = []
        g.valueChanged.connect(lambda v: received.append(v))
        g.setValue(50)
        assert len(received) == 0
        g.deleteLater()


class TestElaDashboardGaugeTicks:
    def test_major_tick_count_min_2(self):
        g = ElaDashboardGauge()
        g.setMajorTickCount(1)
        assert g.majorTickCount() >= 2
        g.deleteLater()

    def test_minor_tick_count_min_1(self):
        g = ElaDashboardGauge()
        g.setMinorTickCount(0)
        assert g.minorTickCount() >= 1
        g.deleteLater()


class TestElaDashboardGaugeAngles:
    def test_span_angle_clamped(self):
        g = ElaDashboardGauge()
        g.setSpanAngle(5)
        assert g.spanAngle() == 10
        g.setSpanAngle(400)
        assert g.spanAngle() == 360
        g.deleteLater()


class TestElaDashboardGaugeMetadata:
    def test_set_title(self):
        g = ElaDashboardGauge()
        g.setTitle("速度")
        assert g.title() == "速度"
        g.deleteLater()

    def test_set_unit(self):
        g = ElaDashboardGauge()
        g.setUnit("km/h")
        assert g.unit() == "km/h"
        g.deleteLater()

    def test_set_decimals(self):
        g = ElaDashboardGauge()
        g.setDecimals(2)
        assert g.decimals() == 2
        g.deleteLater()


class TestElaDashboardGaugeThresholds:
    def test_danger_percent_clamped(self):
        g = ElaDashboardGauge()
        g.setDangerPercent(1.5)
        assert g.dangerPercent() == 1.0
        g.setDangerPercent(-0.5)
        assert g.dangerPercent() == 0.0
        g.deleteLater()

    def test_warning_percent(self):
        g = ElaDashboardGauge()
        g.setWarningPercent(0.5)
        assert g.warningPercent() == 0.5
        g.deleteLater()

    def test_tick_warning_percent(self):
        g = ElaDashboardGauge()
        g.setTickWarningPercent(0.6)
        assert g.tickWarningPercent() == 0.6
        g.deleteLater()


class TestElaDashboardGaugeTheme:
    def test_on_theme_changed_updates_mode(self):
        g = ElaDashboardGauge()
        from PyQt5ElaWidgetTools import ElaThemeType
        g._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert g._theme_mode == ElaThemeType.ThemeMode.Dark
        g.deleteLater()


class TestElaDashboardGaugeDeleteLater:
    def test_delete_later_cleans_up(self):
        g = ElaDashboardGauge()
        g.deleteLater()
