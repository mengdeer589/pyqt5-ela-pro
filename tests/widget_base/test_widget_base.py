"""Tests for widget_base module: ThemeWidget base class."""

from __future__ import annotations

import pytest
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from pyqt5_ela_pro.widget_base import ThemeWidget


class TestThemeWidget:
    """Test cases for ThemeWidget class."""

    def test_theme_widget_inherits_from_qwidget(self):
        """Test ThemeWidget is a QWidget subclass."""
        widget = ThemeWidget()
        assert isinstance(widget, QWidget)
        widget.deleteLater()

    def test_theme_widget_sets_object_name(self):
        """Test ThemeWidget sets object name to 'ThemeWidget'."""
        widget = ThemeWidget()
        assert widget.objectName() == "ThemeWidget"
        widget.deleteLater()

    def test_theme_widget_has_theme_connection(self):
        """Test ThemeWidget has _themeConnection attribute."""
        widget = ThemeWidget()
        assert hasattr(widget, "_themeConnection")
        widget.deleteLater()

    def test_create_lay_horizontal(self):
        """Test create_lay with horizontal layout."""
        widget = ThemeWidget()
        lay = widget.create_lay("h")
        assert isinstance(lay, QHBoxLayout)
        widget.deleteLater()

    def test_create_lay_vertical(self):
        """Test create_lay with vertical layout."""
        widget = ThemeWidget()
        lay = widget.create_lay("v")
        assert isinstance(lay, QVBoxLayout)
        widget.deleteLater()

    def test_create_lay_sets_zero_margins_and_spacing(self):
        """Test created layout has zero margins and spacing."""
        widget = ThemeWidget()
        lay = widget.create_lay("h")
        margins = lay.contentsMargins()
        assert margins.left() == 0 and margins.top() == 0 and margins.right() == 0 and margins.bottom() == 0
        assert lay.spacing() == 0
        widget.deleteLater()

    def test_create_lay_with_parent(self):
        """Test create_lay with custom parent widget."""
        parent = QWidget()
        widget = ThemeWidget()
        lay = widget.create_lay("v", parent=parent)
        assert lay.parent() is parent
        parent.deleteLater()
        widget.deleteLater()

    def test_deleteLater_sets_connection_to_none(self):
        """Test deleteLater sets _themeConnection to None."""
        widget = ThemeWidget()
        widget.deleteLater()
        assert widget._themeConnection is None

    def test_alert_accepts_string_levels(self):
        """Test alert method accepts string level values."""
        widget = ThemeWidget()
        assert hasattr(widget, "alert")
        widget.deleteLater()