"""Tests for ela_trend_chart module: ElaTrendChart."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt, QRect, QPointF, QPoint
from PyQt5.QtGui import QColor

from pyqt5_ela_pro.ela_trend_chart import ElaTrendChart


class TestElaTrendChart:
    """Test cases for ElaTrendChart class."""

    def test_initialization(self):
        """Test trend chart initializes correctly."""
        chart = ElaTrendChart()

        assert chart._curves == []
        assert chart._grid_visible is True
        assert chart._legend_visible is True
        assert chart._indicator_index == -1
        assert chart._indicator_point is None
        assert chart._indicator_visible is False

        chart.deleteLater()

    def test_has_mouse_tracking_enabled(self):
        """Test trend chart has mouse tracking enabled."""
        chart = ElaTrendChart()

        assert chart.hasMouseTracking() is True

        chart.deleteLater()

    def test_minimum_size(self):
        """Test trend chart has minimum size of 200x150."""
        chart = ElaTrendChart()

        assert chart.minimumWidth() >= 200
        assert chart.minimumHeight() >= 150

        chart.deleteLater()

    def test_add_curve(self):
        """Test addCurve adds a curve to the chart."""
        chart = ElaTrendChart()

        chart.addCurve(x=[1, 2, 3], y=[4, 5, 6], name="系列A")

        assert len(chart._curves) == 1
        assert chart._curves[0]["name"] == "系列A"

        chart.deleteLater()

    def test_add_multiple_curves(self):
        """Test addCurve works with multiple curves."""
        chart = ElaTrendChart()

        chart.addCurve(x=[1, 2, 3], y=[4, 5, 6], name="系列A")
        chart.addCurve(x=[1, 2, 3], y=[7, 8, 9], name="系列B")

        assert len(chart._curves) == 2

        chart.deleteLater()

    def test_clear_curves(self):
        """Test clearCurves removes all curves."""
        chart = ElaTrendChart()
        chart.addCurve(x=[1, 2, 3], y=[4, 5, 6], name="系列A")

        chart.clearCurves()

        assert len(chart._curves) == 0

        chart.deleteLater()

    def test_set_grid_visible(self):
        """Test setGridVisible updates grid visibility."""
        chart = ElaTrendChart()

        chart.setGridVisible(False)

        assert chart._grid_visible is False

        chart.deleteLater()

    def test_set_legend_visible(self):
        """Test setLegendVisible updates legend visibility."""
        chart = ElaTrendChart()

        chart.setLegendVisible(False)

        assert chart._legend_visible is False

        chart.deleteLater()

    def test_grid_visible_by_default(self):
        """Test grid is visible by default."""
        chart = ElaTrendChart()

        assert chart._grid_visible is True

        chart.deleteLater()

    def test_legend_visible_by_default(self):
        """Test legend is visible by default."""
        chart = ElaTrendChart()

        assert chart._legend_visible is True

        chart.deleteLater()

    def test_axis_margins(self):
        """Test axis margin methods return expected values."""
        chart = ElaTrendChart()

        assert chart._getAxisMarginLeft() == 50
        assert chart._getAxisMarginBottom() == 30
        assert chart._getAxisMarginTop() == 10
        assert chart._getAxisMarginRight() == 10

        chart.deleteLater()

    def test_light_colors_list_exists(self):
        """Test _LIGHT_COLORS list exists and has colors."""
        assert len(ElaTrendChart._LIGHT_COLORS) > 0
        assert all(isinstance(c, QColor) for c in ElaTrendChart._LIGHT_COLORS)

    def test_dark_colors_list_exists(self):
        """Test _DARK_COLORS list exists and has colors."""
        assert len(ElaTrendChart._DARK_COLORS) > 0
        assert all(isinstance(c, QColor) for c in ElaTrendChart._DARK_COLORS)

    def test_view_rect_initial_values(self):
        """Test initial view rect is set correctly."""
        chart = ElaTrendChart()

        assert chart._view_rect.width() == 100
        assert chart._view_rect.height() == 100

        chart.deleteLater()

    def test_tick_deltas(self):
        """Test tick delta values are set."""
        chart = ElaTrendChart()

        assert chart._x_tick_delta == 10.0
        assert chart._y_tick_delta == 10.0

        chart.deleteLater()

    def test_line_width_default(self):
        """Test default line width is 2.0."""
        chart = ElaTrendChart()

        assert chart._line_width == 2.0

        chart.deleteLater()