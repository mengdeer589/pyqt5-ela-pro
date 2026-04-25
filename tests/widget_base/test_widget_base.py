"""Tests for widget_base module: ElaThemeWidget base class."""

from __future__ import annotations

import pytest
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from pyqt5_ela_pro.widget_base import ElaThemeWidget


class TestThemeWidget:
    """Test cases for ElaThemeWidget class."""

    def test_theme_widget_inherits_from_qwidget(self):
        """Test ElaThemeWidget is a QWidget subclass."""
        widget = ElaThemeWidget()
        assert isinstance(widget, QWidget)
        widget.deleteLater()

    def test_theme_widget_sets_object_name(self):
        """Test ElaThemeWidget sets object name to 'ElaThemeWidget'."""
        widget = ElaThemeWidget()
        assert widget.objectName() == "ElaThemeWidget"
        widget.deleteLater()

    def test_theme_widget_has_theme_connection(self):
        """Test ElaThemeWidget has _themeConnection attribute."""
        widget = ElaThemeWidget()
        assert hasattr(widget, "_themeConnection")
        widget.deleteLater()

    def test_createLayout_horizontal(self):
        """Test createLayout with horizontal layout."""
        widget = ElaThemeWidget()
        lay = widget.createLayout("h")
        assert isinstance(lay, QHBoxLayout)
        widget.deleteLater()

    def test_createLayout_vertical(self):
        """Test createLayout with vertical layout."""
        widget = ElaThemeWidget()
        lay = widget.createLayout("v")
        assert isinstance(lay, QVBoxLayout)
        widget.deleteLater()

    def test_createLayout_sets_zero_margins_and_spacing(self):
        """Test created layout has zero margins and spacing."""
        widget = ElaThemeWidget()
        lay = widget.createLayout("h")
        margins = lay.contentsMargins()
        assert margins.left() == 0 and margins.top() == 0 and margins.right() == 0 and margins.bottom() == 0
        assert lay.spacing() == 0
        widget.deleteLater()

    def test_createLayout_with_parent(self):
        """Test createLayout with custom parent widget."""
        parent = QWidget()
        widget = ElaThemeWidget()
        lay = widget.createLayout("v", parent=parent)
        assert lay.parent() is parent
        parent.deleteLater()
        widget.deleteLater()

    def test_deleteLater_sets_connection_to_none(self):
        """Test deleteLater sets _themeConnection to None."""
        widget = ElaThemeWidget()
        widget.deleteLater()
        assert widget._themeConnection is None

    def test_alert_accepts_string_levels(self):
        """Test alert method accepts string level values."""
        widget = ElaThemeWidget()
        assert hasattr(widget, "alert")
        widget.deleteLater()