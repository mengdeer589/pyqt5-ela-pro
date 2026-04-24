"""Tests for scrollable_menu module: ElaScrollableMenu."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro.scrollable_menu import (
    ElaScrollableMenu,
    SCROLLABLE_MENU_MIN_HEIGHT,
    SCROLLABLE_MENU_LIGHT_BG_COLOR,
    SCROLLABLE_MENU_DARK_BG_COLOR,
)


class TestElaScrollableMenu:
    """Test cases for ElaScrollableMenu class."""

    def test_initialization(self):
        """Test menu initializes with scroll area and widget."""
        menu = ElaScrollableMenu()

        assert hasattr(menu, "scroll_area")
        assert hasattr(menu, "scroll_widget")
        assert hasattr(menu, "scroll_layout")
        assert menu.minimumHeight() == SCROLLABLE_MENU_MIN_HEIGHT

        menu.deleteLater()

    def test_light_bg_color_constant(self):
        """Test SCROLLABLE_MENU_LIGHT_BG_COLOR is white."""
        assert SCROLLABLE_MENU_LIGHT_BG_COLOR == "#ffffff"

    def test_dark_bg_color_constant(self):
        """Test SCROLLABLE_MENU_DARK_BG_COLOR is dark."""
        assert SCROLLABLE_MENU_DARK_BG_COLOR == "#202020"

    def test_add_widget_action(self):
        """Test addWidgetAction adds widget to scroll layout."""
        menu = ElaScrollableMenu()
        widget = QWidget()

        menu.addWidgetAction(widget)

        assert menu.scroll_layout.count() > 0

        widget.deleteLater()
        menu.deleteLater()

    def test_clear_menu_removes_all_widgets(self):
        """Test clearMenu removes all widgets from layout."""
        menu = ElaScrollableMenu()

        menu.addWidgetAction(QWidget())
        menu.addWidgetAction(QWidget())
        menu.addWidgetAction(QWidget())

        initial_count = menu.scroll_layout.count()

        menu.clearMenu()

        assert menu.scroll_layout.count() == 0

        menu.deleteLater()

    def test_min_height_constant(self):
        """Test SCROLLABLE_MENU_MIN_HEIGHT is 50."""
        assert SCROLLABLE_MENU_MIN_HEIGHT == 50

    def test_has_theme_connection(self):
        """Test menu connects to theme change signal."""
        menu = ElaScrollableMenu()
        assert menu._themeConnection is not None
        menu.deleteLater()

    def test_disconnect_signals(self):
        """Test _disconnectSignals clears theme connection."""
        menu = ElaScrollableMenu()
        menu._disconnectSignals()
        assert menu._themeConnection is None
        menu.deleteLater()

    def test_delete_later_calls_clear_menu(self):
        """Test deleteLater clears menu before deletion."""
        menu = ElaScrollableMenu()
        menu.addWidgetAction(QWidget())

        menu.deleteLater()