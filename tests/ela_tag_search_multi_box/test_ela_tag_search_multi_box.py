"""Tests for ela_tag_search_multi_box module: ElaTagSearchMultiBox."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock
from PyQt5.QtCore import Qt, QPropertyAnimation

from pyqt5_ela_pro.ela_tag_search_multi_box import ElaTagSearchMultiBox


class TestElaTagSearchMultiBox:
    """Test cases for ElaTagSearchMultiBox class."""

    def test_initialization_with_title(self):
        """Test tag search multi box initializes with title."""
        box = ElaTagSearchMultiBox(title="语言")

        assert box._title_text == "语言"

        box.deleteLater()

    def test_initialization_with_defaults(self):
        """Test tag search multi box initializes with empty title."""
        box = ElaTagSearchMultiBox()

        assert box._title_text == ""

        box.deleteLater()

    def test_fixed_height_is_38(self):
        """Test tag search multi box has fixed height of 38."""
        box = ElaTagSearchMultiBox()

        assert box.height() == 38

        box.deleteLater()

    def test_has_mark_animation(self):
        """Test tag search multi box has mark animation."""
        box = ElaTagSearchMultiBox()

        assert hasattr(box, '_mark_animation')
        assert isinstance(box._mark_animation, QPropertyAnimation)

        box.deleteLater()

    def test_mark_animation_duration_is_300ms(self):
        """Test mark animation duration is 300ms."""
        box = ElaTagSearchMultiBox()

        assert box._mark_animation.duration() == 300

        box.deleteLater()

    def test_has_rotate_animation(self):
        """Test tag search multi box has rotate animation."""
        box = ElaTagSearchMultiBox()

        assert hasattr(box, '_rotate_animation')
        assert isinstance(box._rotate_animation, QPropertyAnimation)

        box.deleteLater()

    def test_expand_mark_width_property(self):
        """Test expandMarkWidth property."""
        box = ElaTagSearchMultiBox()

        box.expandMarkWidth = 50.0
        assert box.expandMarkWidth == 50.0

        box.deleteLater()

    def test_expand_icon_rotate_property(self):
        """Test expandIconRotate property."""
        box = ElaTagSearchMultiBox()

        box.expandIconRotate = -180.0
        assert box.expandIconRotate == -180.0

        box.deleteLater()

    def test_set_title(self):
        """Test setTitle updates title text."""
        box = ElaTagSearchMultiBox()
        box.setTitle("新标题")

        assert box._title_text == "新标题"

        box.deleteLater()

    def test_title_returns_current_title(self):
        """Test title returns current title text."""
        box = ElaTagSearchMultiBox(title="测试")

        assert box.title() == "测试"

        box.deleteLater()

    def test_inherits_from_search_multi_box(self):
        """Test tag search multi box inherits search and multi-select."""
        from pyqt5_ela_pro.combo_box import ElaSearchMultiBox

        box = ElaTagSearchMultiBox()
        assert isinstance(box, ElaSearchMultiBox)

        box.deleteLater()

    def test_max_visible_items_is_10(self):
        """Test max visible items is set to 10."""
        box = ElaTagSearchMultiBox()

        assert box.maxVisibleItems() == 10

        box.deleteLater()

    def test_get_target_mark_width_empty(self):
        """Test _getTargetMarkWidth returns 0 when no items."""
        box = ElaTagSearchMultiBox()

        width = box._getTargetMarkWidth()

        assert width == 0.0

        box.deleteLater()

    def test_title_font_size_default_is_13(self):
        """Test default title font size is 13."""
        box = ElaTagSearchMultiBox()

        assert box._title_font_size == 13

        box.deleteLater()