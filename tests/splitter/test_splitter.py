"""Tests for splitter module: ElaSplitter, ElaSplitterHandle, create_ela_splitter."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QBoxLayout

from pyqt5_ela_pro.splitter import (
    ElaSplitter,
    ElaSplitterHandle,
    create_ela_splitter,
)


class TestElaSplitter:
    """Test cases for ElaSplitter class."""

    def test_initialization_with_defaults(self):
        """Test splitter initializes with horizontal orientation."""
        splitter = ElaSplitter()

        assert splitter.orientation() == Qt.Orientation.Horizontal
        assert splitter._handle_width == 6

        splitter.deleteLater()

    def test_initialization_with_custom_orientation(self):
        """Test splitter accepts custom orientation."""
        splitter = ElaSplitter(orientation=Qt.Orientation.Vertical)

        assert splitter.orientation() == Qt.Orientation.Vertical

        splitter.deleteLater()

    def test_children_not_collapsible_by_default(self):
        """Test splitter children are not collapsible by default."""
        splitter = ElaSplitter()

        assert splitter.childrenCollapsible() is False

        splitter.deleteLater()

    def test_set_handle_width(self):
        """Test setHandleWidth updates handle width."""
        splitter = ElaSplitter()
        splitter.setHandleWidth(10)

        assert splitter._handle_width == 10

        splitter.deleteLater()

    def test_handle_width_returns_value(self):
        """Test handleWidth returns current width."""
        splitter = ElaSplitter()
        splitter.setHandleWidth(8)

        assert splitter.handleWidth() == 8

        splitter.deleteLater()

    def test_set_grip_length(self):
        """Test set_grip_length updates grip length."""
        splitter = ElaSplitter()
        splitter.set_grip_length(50)

        assert splitter._grip_length == 50

        splitter.deleteLater()

    def test_grip_length_returns_value(self):
        """Test gripLength returns current grip length."""
        splitter = ElaSplitter()
        splitter.set_grip_length(24)

        assert splitter.grip_length() == 24

        splitter.deleteLater()

    def test_create_handle_returns_ela_splitter_handle(self):
        """Test createHandle returns an ElaSplitterHandle."""
        splitter = ElaSplitter()
        handle = splitter.createHandle()

        assert isinstance(handle, ElaSplitterHandle)

        handle.deleteLater()
        splitter.deleteLater()

    def test_handle_has_grip_length_set(self):
        """Test createHandle sets grip length on handle."""
        splitter = ElaSplitter()
        splitter.set_grip_length(50)
        handle = splitter.createHandle()

        assert handle.get_grip_length() == 50

        handle.deleteLater()
        splitter.deleteLater()


class TestElaSplitterHandle:
    """Test cases for ElaSplitterHandle class."""

    def test_initialization(self):
        """Test handle initializes with orientation and parent."""
        splitter = ElaSplitter()
        handle = ElaSplitterHandle(Qt.Orientation.Horizontal, splitter)

        assert handle.orientation() == Qt.Orientation.Horizontal
        assert handle.parent() is splitter

        handle.deleteLater()
        splitter.deleteLater()

    def test_set_grip_length(self):
        """Test set_grip_length updates grip length."""
        splitter = ElaSplitter()
        handle = ElaSplitterHandle(Qt.Orientation.Horizontal, splitter)

        handle.set_grip_length(50)

        assert handle._grip_length == 50

        handle.deleteLater()
        splitter.deleteLater()

    def test_grip_length_returns_value(self):
        """Test get_grip_length returns current length."""
        splitter = ElaSplitter()
        handle = ElaSplitterHandle(Qt.Orientation.Horizontal, splitter)
        handle.set_grip_length(24)

        assert handle.get_grip_length() == 24

        handle.deleteLater()
        splitter.deleteLater()

    def test_initial_is_not_hovered(self):
        """Test handle is not hovered initially."""
        splitter = ElaSplitter()
        handle = ElaSplitterHandle(Qt.Orientation.Horizontal, splitter)

        assert handle._is_hover is False

        handle.deleteLater()
        splitter.deleteLater()

    def test_initial_is_not_pressed(self):
        """Test handle is not pressed initially."""
        splitter = ElaSplitter()
        handle = ElaSplitterHandle(Qt.Orientation.Horizontal, splitter)

        assert handle._is_pressed is False

        handle.deleteLater()
        splitter.deleteLater()

    def test_has_theme_connection(self):
        """Test handle connects to theme change signal."""
        splitter = ElaSplitter()
        handle = ElaSplitterHandle(Qt.Orientation.Horizontal, splitter)

        assert hasattr(handle, '_onThemeChanged')

        handle.deleteLater()
        splitter.deleteLater()

    def test_delete_later_disconnects_theme(self):
        """Test deleteLater disconnects theme signal without error."""
        splitter = ElaSplitter()
        handle = ElaSplitterHandle(Qt.Orientation.Horizontal, splitter)
        handle.deleteLater()
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
            orientation=Qt.Orientation.Vertical
        )

        assert splitter.orientation() == Qt.Orientation.Vertical

        widget1.deleteLater()
        widget2.deleteLater()
        splitter.deleteLater()

    def test_with_sizes_parameter(self):
        """Test create_ela_splitter accepts sizes parameter."""
        widget1 = QWidget()
        widget2 = QWidget()

        splitter = create_ela_splitter(
            [widget1, widget2],
            sizes=[200, 300],
        )

        assert len(splitter.sizes()) == 2

        widget1.deleteLater()
        widget2.deleteLater()
        splitter.deleteLater()

    def test_sizes_wrong_length_raises(self):
        """Test create_ela_splitter raises on mismatched sizes length."""
        widget1 = QWidget()
        widget2 = QWidget()

        with pytest.raises(ValueError, match="sizes 列表长度"):
            create_ela_splitter([widget1, widget2], sizes=[100])

        widget1.deleteLater()
        widget2.deleteLater()

    def test_parent_auto_detected_and_inserted_into_layout(self):
        """Test parent auto-detection and layout insertion."""
        container = QWidget()
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        container.setLayout(layout)

        child1 = QWidget()
        child2 = QWidget()
        child3 = QWidget()
        layout.addWidget(child1)
        layout.addWidget(child2)
        layout.addWidget(child3)

        splitter = create_ela_splitter([child1, child2])

        assert splitter.parentWidget() is container
        assert layout.indexOf(splitter) == 0
        assert splitter.count() == 2

        container.deleteLater()

    def test_parent_auto_detected_adds_when_not_in_layout(self):
        """Test auto-detection addWidget when first widget not in layout."""
        container = QWidget()
        child1 = QWidget(container)
        child2 = QWidget(container)

        splitter = create_ela_splitter([child1, child2])

        assert splitter.parentWidget() is container

        child1.deleteLater()
        child2.deleteLater()
        container.deleteLater()
