"""Tests for tooltips module: ElaToolTip, ElaStateToolTip, set_tooltip, remove_tooltip."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtWidgets import QWidget, QLabel

from pyqt5_ela_pro.tooltips import (
    ElaToolTip,
    ElaStateToolTip,
    set_tooltip,
    remove_tooltip,
    ElaToolTipPosition,
    TOOLTIP_BORDER_RADIUS,
    TOOLTIP_LIGHT_BG_COLOR,
    TOOLTIP_DARK_BG_COLOR,
)


class TestToolTip:
    """Test cases for ElaToolTip class."""

    def test_tooltip_initialization(self):
        """Test ElaToolTip initializes with text."""
        tooltip = ElaToolTip("Test tooltip")

        assert tooltip._text == "Test tooltip"

        tooltip.deleteLater()

    def test_tooltip_has_frameless_window_flag(self):
        """Test ElaToolTip uses frameless window."""
        tooltip = ElaToolTip()

        flags = tooltip.windowFlags()
        assert flags & Qt.FramelessWindowHint

        tooltip.deleteLater()

    def test_tooltip_has_tool_window_flag(self):
        """Test ElaToolTip uses Tool window type."""
        tooltip = ElaToolTip()

        flags = tooltip.windowFlags()
        assert flags & Qt.Tool

        tooltip.deleteLater()

    def test_tooltip_has_stays_on_top_flag(self):
        """Test ElaToolTip stays on top of other windows."""
        tooltip = ElaToolTip()

        flags = tooltip.windowFlags()
        assert flags & Qt.WindowStaysOnTopHint

        tooltip.deleteLater()

    def test_tooltip_set_text(self):
        """Test setText updates tooltip text."""
        tooltip = ElaToolTip()
        tooltip.setText("New text")

        assert tooltip._text == "New text"
        assert tooltip._label.text() == "New text"

        tooltip.deleteLater()

    def test_tooltip_has_translucent_background(self):
        """Test ElaToolTip has translucent background."""
        tooltip = ElaToolTip()

        assert tooltip.testAttribute(Qt.WA_TranslucentBackground)

        tooltip.deleteLater()

    def test_tooltip_border_radius_constant(self):
        """Test TOOLTIP_BORDER_RADIUS is 8."""
        assert TOOLTIP_BORDER_RADIUS == 8


class TestElaToolTipPosition:
    """Test cases for ElaToolTipPosition enum."""

    def test_ela_tool_tip_position_has_top(self):
        """Test ElaToolTipPosition.Top exists."""
        assert ElaToolTipPosition.Top is not None

    def test_ela_tool_tip_position_has_bottom(self):
        """Test ElaToolTipPosition.Bottom exists."""
        assert ElaToolTipPosition.Bottom is not None

    def test_ela_tool_tip_position_has_left(self):
        """Test ElaToolTipPosition.Left exists."""
        assert ElaToolTipPosition.Left is not None

    def test_ela_tool_tip_position_has_right(self):
        """Test ElaToolTipPosition.Right exists."""
        assert ElaToolTipPosition.Right is not None

    def test_ela_tool_tip_position_has_all_8_positions(self):
        """Test all 8 positions exist."""
        assert len(ElaToolTipPosition) == 8

        positions = [
            ElaToolTipPosition.Top,
            ElaToolTipPosition.Bottom,
            ElaToolTipPosition.Left,
            ElaToolTipPosition.Right,
            ElaToolTipPosition.TopLeft,
            ElaToolTipPosition.TopRight,
            ElaToolTipPosition.BottomLeft,
            ElaToolTipPosition.BottomRight,
        ]

        for pos in positions:
            assert pos is not None


class TestSetTooltip:
    """Test cases for set_tooltip function."""

    def test_set_tooltip_accepts_widget_and_text(self, qapp):
        """Test set_tooltip accepts widget and text parameters."""
        widget = QWidget()

        set_tooltip(widget, "Test tooltip")

        widget.deleteLater()
        qapp.processEvents()

    def test_set_tooltip_accepts_position_parameter(self, qapp):
        """Test set_tooltip accepts position parameter."""
        widget = QWidget()

        set_tooltip(widget, "Test", position=ElaToolTipPosition.Top)

        widget.deleteLater()
        qapp.processEvents()


class TestRemoveTooltip:
    """Test cases for remove_tooltip function."""

    def test_remove_tooltip_accepts_widget(self, qapp):
        """Test remove_tooltip accepts widget parameter."""
        widget = QWidget()

        remove_tooltip(widget)

        widget.deleteLater()
        qapp.processEvents()

    def test_remove_tooltip_does_not_raise_on_unregistered_widget(self, qapp):
        """Test remove_tooltip doesn't raise on widget without tooltip."""
        widget = QWidget()

        remove_tooltip(widget)

        widget.deleteLater()
        qapp.processEvents()


class TestStateToolTip:
    """Test cases for ElaStateToolTip class."""

    def test_state_tooltip_initialization(self):
        """Test ElaStateToolTip initializes with title and content."""
        st = ElaStateToolTip("Title", "Content")

        assert st._title == "Title"
        assert st._content == "Content"

        st.deleteLater()

    def test_state_tooltip_has_closed_signal(self):
        """Test ElaStateToolTip has closed signal (was closedSignal)."""
        st = ElaStateToolTip()
        assert hasattr(st, "closed")
        st.deleteLater()

    def test_state_tooltip_has_title_and_content_labels(self):
        """Test ElaStateToolTip has title and content labels."""
        st = ElaStateToolTip("Title", "Content")

        assert hasattr(st, "_titleLabel")
        assert hasattr(st, "_contentLabel")

        st.deleteLater()