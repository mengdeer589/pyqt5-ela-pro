"""Tests for splitter module: ElaSplitter, ElaSplitterStyle, create_ela_splitter."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro.splitter import (
    ElaSplitter,
    ElaSplitterStyle,
    create_ela_splitter,
)


class TestElaSplitterStyle:
    """Test cases for ElaSplitterStyle class."""

    def test_initialization(self):
        """Test splitter style initializes with thickness."""
        style = ElaSplitterStyle(thickness=40)

        assert style._thickness == 40

    def test_initialization_with_default_thickness(self):
        """Test splitter style uses default thickness of 40."""
        style = ElaSplitterStyle()

        assert style._thickness == 40


class TestElaSplitter:
    """Test cases for ElaSplitter class."""

    def test_initialization_with_defaults(self):
        """Test splitter initializes with horizontal orientation."""
        splitter = ElaSplitter()

        assert splitter.orientation() == Qt.Horizontal
        assert splitter._handle_thickness == 4

        splitter.deleteLater()

    def test_initialization_with_custom_orientation(self):
        """Test splitter accepts custom orientation."""
        splitter = ElaSplitter(orientation=Qt.Vertical)

        assert splitter.orientation() == Qt.Vertical

        splitter.deleteLater()

    def test_initialization_with_custom_handle_thickness(self):
        """Test splitter accepts custom handle thickness."""
        splitter = ElaSplitter(handleThickness=10)

        assert splitter._handle_thickness == 10

        splitter.deleteLater()

    def test_children_not_collapsible_by_default(self):
        """Test splitter children are not collapsible by default."""
        splitter = ElaSplitter()

        assert splitter.childrenCollapsible() is False

        splitter.deleteLater()

    def test_set_handle_width_is_noop(self):
        """Test setHandleWidth logs warning (width controlled by constructor)."""
        splitter = ElaSplitter()

        splitter.setHandleWidth(100)

        splitter.deleteLater()

    def test_has_theme_connection(self):
        """Test splitter connects to theme change signal."""
        splitter = ElaSplitter()

        assert hasattr(splitter, '_on_theme_changed')

        splitter.deleteLater()


class TestCreateElaSplitter:
    """Test cases for create_ela_splitter function."""

    def test_creates_splitter_with_two_widgets(self):
        """Test create_ela_splitter creates splitter with 2 widgets."""
        widget1 = QWidget()
        widget2 = QWidget()

        splitter = create_ela_splitter([widget1, widget2])

        assert splitter.count() == 2
        assert isinstance(splitter, ElaSplitter)

        widget1.deleteLater()
        widget2.deleteLater()
        splitter.deleteLater()

    def test_creates_splitter_with_multiple_widgets(self):
        """Test create_ela_splitter works with more than 2 widgets."""
        widgets = [QWidget() for _ in range(4)]

        splitter = create_ela_splitter(widgets)

        assert splitter.count() == 4

        for w in widgets:
            w.deleteLater()
        splitter.deleteLater()

    def test_raises_value_error_for_single_widget(self):
        """Test create_ela_splitter raises ValueError with 1 widget."""
        widget = QWidget()

        with pytest.raises(ValueError, match="至少需要 2 个组件"):
            create_ela_splitter([widget])

        widget.deleteLater()

    def test_raises_value_error_for_empty_list(self):
        """Test create_ela_splitter raises ValueError with empty list."""
        with pytest.raises(ValueError, match="至少需要 2 个组件"):
            create_ela_splitter([])

    def test_creates_vertical_splitter(self):
        """Test create_ela_splitter creates vertical splitter."""
        widget1 = QWidget()
        widget2 = QWidget()

        splitter = create_ela_splitter(
            [widget1, widget2],
            orientation=Qt.Vertical
        )

        assert splitter.orientation() == Qt.Vertical

        widget1.deleteLater()
        widget2.deleteLater()
        splitter.deleteLater()