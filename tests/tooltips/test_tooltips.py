"""Tests for tooltips module: ToolTip, StateToolTip, set_tooltip, remove_tooltip."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtWidgets import QWidget, QLabel

from pyqt5_ela_pro.tooltips import (
    ToolTip,
    StateToolTip,
    set_tooltip,
    remove_tooltip,
    ElaToolTipPosition,
    TOOLTIP_BORDER_RADIUS,
    TOOLTIP_LIGHT_BG_COLOR,
    TOOLTIP_DARK_BG_COLOR,
)


class TestToolTip:
    """Test cases for ToolTip class."""

    def test_tooltip_initialization(self):
        """Test ToolTip initializes with text."""
        tooltip = ToolTip("Test tooltip")

        assert tooltip._text == "Test tooltip"

        tooltip.deleteLater()

    def test_tooltip_has_frameless_window_flag(self):
        """Test ToolTip uses frameless window."""
        tooltip = ToolTip()

        flags = tooltip.windowFlags()
        assert flags & Qt.FramelessWindowHint

        tooltip.deleteLater()

    def test_tooltip_has_tool_window_flag(self):
        """Test ToolTip uses Tool window type."""
        tooltip = ToolTip()

        flags = tooltip.windowFlags()
        assert flags & Qt.Tool

        tooltip.deleteLater()

    def test_tooltip_has_stays_on_top_flag(self):
        """Test ToolTip stays on top of other windows."""
        tooltip = ToolTip()

        flags = tooltip.windowFlags()
        assert flags & Qt.WindowStaysOnTopHint

        tooltip.deleteLater()

    def test_tooltip_set_text(self):
        """Test setText updates tooltip text."""
        tooltip = ToolTip()
        tooltip.setText("New text")

        assert tooltip._text == "New text"
        assert tooltip._label.text() == "New text"

        tooltip.deleteLater()

    def test_tooltip_has_translucent_background(self):
        """Test ToolTip has translucent background."""
        tooltip = ToolTip()

        assert tooltip.testAttribute(Qt.WA_TranslucentBackground)

        tooltip.deleteLater()

    def test_tooltip_border_radius_constant(self):
        """Test TOOLTIP_BORDER_RADIUS is 8."""
        assert TOOLTIP_BORDER_RADIUS == 8


class TestElaToolTipPosition:
    """Test cases for ElaToolTipPosition enum."""

    def test_ela_tool_tip_position_has_top(self):
        """Test ElaToolTipPosition.TOP exists."""
        assert ElaToolTipPosition.TOP is not None

    def test_ela_tool_tip_position_has_bottom(self):
        """Test ElaToolTipPosition.BOTTOM exists."""
        assert ElaToolTipPosition.BOTTOM is not None

    def test_ela_tool_tip_position_has_left(self):
        """Test ElaToolTipPosition.LEFT exists."""
        assert ElaToolTipPosition.LEFT is not None

    def test_ela_tool_tip_position_has_right(self):
        """Test ElaToolTipPosition.RIGHT exists."""
        assert ElaToolTipPosition.RIGHT is not None

    def test_ela_tool_tip_position_has_all_8_positions(self):
        """Test all 8 positions exist."""
        assert len(ElaToolTipPosition) == 8

        positions = [
            ElaToolTipPosition.TOP,
            ElaToolTipPosition.BOTTOM,
            ElaToolTipPosition.LEFT,
            ElaToolTipPosition.RIGHT,
            ElaToolTipPosition.TOP_LEFT,
            ElaToolTipPosition.TOP_RIGHT,
            ElaToolTipPosition.BOTTOM_LEFT,
            ElaToolTipPosition.BOTTOM_RIGHT,
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

        set_tooltip(widget, "Test", position=ElaToolTipPosition.TOP)

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
    """Test cases for StateToolTip class."""

    def test_state_tooltip_initialization(self):
        """Test StateToolTip initializes with title and content."""
        st = StateToolTip("Title", "Content")

        assert st._title == "Title"
        assert st._content == "Content"

        st.deleteLater()

    def test_state_tooltip_has_closed_signal(self):
        """Test StateToolTip has closed signal (was closedSignal)."""
        st = StateToolTip()
        assert hasattr(st, "closed")
        st.deleteLater()

    def test_state_tooltip_has_title_and_content_labels(self):
        """Test StateToolTip has title and content labels."""
        st = StateToolTip("Title", "Content")

        assert hasattr(st, "_titleLabel")
        assert hasattr(st, "_contentLabel")

        st.deleteLater()