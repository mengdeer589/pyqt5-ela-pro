"""Tests for ela_side_drawer module: ElaDrawer, ElaDrawerPanel, ElaDrawerDim."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt, QRect, QEvent, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro.ela_side_drawer import (
    ElaDrawerPosition,
    ElaDrawerPanel,
    ElaDrawerDim,
    ElaDrawer,
)


class TestElaDrawerPosition:
    """Test cases for ElaDrawerPosition enum."""

    def test_left_value(self):
        """Test Left position has value 0."""
        assert ElaDrawerPosition.Left == 0

    def test_right_value(self):
        """Test Right position has value 1."""
        assert ElaDrawerPosition.Right == 1

    def test_top_value(self):
        """Test Top position has value 2."""
        assert ElaDrawerPosition.Top == 2

    def test_bottom_value(self):
        """Test Bottom position has value 3."""
        assert ElaDrawerPosition.Bottom == 3


class TestElaDrawerPanel:
    """Test cases for ElaDrawerPanel class."""

    def test_initialization_with_defaults(self):
        """Test drawer panel initializes with default values."""
        panel = ElaDrawerPanel()

        assert panel._corner_radius == 12
        assert panel._position == ElaDrawerPosition.Right

        panel.deleteLater()

    def test_initialization_with_custom_values(self):
        """Test drawer panel accepts custom corner radius and position."""
        panel = ElaDrawerPanel(position=ElaDrawerPosition.Left, corner_radius=8)

        assert panel._corner_radius == 8
        assert panel._position == ElaDrawerPosition.Left

        panel.deleteLater()

    def test_has_translucent_background(self):
        """Test drawer panel has translucent background attribute."""
        panel = ElaDrawerPanel()

        assert panel.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        panel.deleteLater()

    def test_set_bg_color(self):
        """Test setBgColor updates background color."""
        panel = ElaDrawerPanel()
        color = QColor(255, 0, 0)
        panel.setBgColor(color)

        assert panel._bg_color == color

        panel.deleteLater()

    def test_set_position(self):
        """Test setPosition updates position."""
        panel = ElaDrawerPanel()

        panel.setPosition(ElaDrawerPosition.Top)

        assert panel._position == ElaDrawerPosition.Top

        panel.deleteLater()


class TestElaDrawerDim:
    """Test cases for ElaDrawerDim class."""

    def test_initialization(self):
        """Test drawer dim initializes with default bg color."""
        dim = ElaDrawerDim()

        assert dim._bg_color == QColor(0, 0, 0, 102)

        dim.deleteLater()

    def test_set_bg_color(self):
        """Test setBgColor updates background color."""
        dim = ElaDrawerDim()
        color = QColor(255, 0, 0, 128)
        dim.setBgColor(color)

        assert dim._bg_color == color

        dim.deleteLater()


class TestElaDrawer:
    """Test cases for ElaDrawer class."""

    def test_initialization_with_defaults(self):
        """Test drawer initializes with default values."""
        parent = QWidget()
        drawer = ElaDrawer(parent=parent)

        assert drawer._position == ElaDrawerPosition.Right
        assert drawer._drawer_size == 360
        assert drawer._is_opened is False
        assert drawer._close_on_dim_clicked is True
        assert drawer._animation_duration == 250

        parent.deleteLater()
        drawer.deleteLater()

    def test_initialization_with_custom_values(self):
        """Test drawer accepts custom position and drawer_size."""
        parent = QWidget()
        drawer = ElaDrawer(position=ElaDrawerPosition.Left, drawer_size=400, parent=parent)

        assert drawer._position == ElaDrawerPosition.Left
        assert drawer._drawer_size == 400

        parent.deleteLater()
        drawer.deleteLater()

    def test_has_closed_signal(self):
        """Test drawer has closed signal."""
        parent = QWidget()
        drawer = ElaDrawer(parent=parent)

        assert hasattr(drawer, 'closed')
        assert callable(drawer.closed)

        parent.deleteLater()
        drawer.deleteLater()

    def test_has_showed_signal(self):
        """Test drawer has showed signal."""
        parent = QWidget()
        drawer = ElaDrawer(parent=parent)

        assert hasattr(drawer, 'opened')
        assert callable(drawer.opened)

        parent.deleteLater()
        drawer.deleteLater()

    def test_initial_state_is_hidden(self):
        """Test drawer is initially hidden."""
        parent = QWidget()
        drawer = ElaDrawer(parent=parent)

        assert not drawer.isVisible()

        parent.deleteLater()
        drawer.deleteLater()

    def test_initial_opened_is_false(self):
        """Test opened() returns False initially."""
        parent = QWidget()
        drawer = ElaDrawer(parent=parent)

        assert drawer.isOpened() is False

        parent.deleteLater()
        drawer.deleteLater()

    def test_set_content_widget(self):
        """Test setContentWidget returns self for chaining."""
        parent = QWidget()
        drawer = ElaDrawer(parent=parent)
        content = QWidget()

        result = drawer.setContentWidget(content)

        assert result is drawer

        parent.deleteLater()
        drawer.deleteLater()

    def test_set_drawer_size(self):
        """Test setDrawerSize updates drawer size."""
        parent = QWidget()
        drawer = ElaDrawer(parent=parent)

        drawer.setDrawerSize(500)

        assert drawer._drawer_size == 500

        parent.deleteLater()
        drawer.deleteLater()

    def test_set_corner_radius(self):
        """Test setCornerRadius updates corner radius."""
        parent = QWidget()
        drawer = ElaDrawer(parent=parent)

        drawer.setCornerRadius(20)

        assert drawer._corner_radius == 20

        parent.deleteLater()
        drawer.deleteLater()

    def test_set_close_on_dim_clicked(self):
        """Test setCloseOnDimClicked updates flag."""
        parent = QWidget()
        drawer = ElaDrawer(parent=parent)

        drawer.setCloseOnDimClicked(False)

        assert drawer._close_on_dim_clicked is False

        parent.deleteLater()
        drawer.deleteLater()

    def test_set_animation_duration(self):
        """Test setAnimationDuration updates duration."""
        parent = QWidget()
        drawer = ElaDrawer(parent=parent)

        drawer.setAnimationDuration(500)

        assert drawer._animation_duration == 500

        parent.deleteLater()
        drawer.deleteLater()

    def test_delete_later_disconnects_theme_signal(self):
        """Test deleteLater disconnects theme signal."""
        parent = QWidget()
        drawer = ElaDrawer(parent=parent)
        drawer.deleteLater()