"""Tests for ela_tag_search_box module: ElaTagSearchBox."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve

from pyqt5_ela_pro.ela_tag_search_box import ElaTagSearchBox


class TestElaTagSearchBox:
    """Test cases for ElaTagSearchBox class."""

    def test_initialization_with_title(self):
        """Test tag search box initializes with title."""
        box = ElaTagSearchBox(title="语言")

        assert box._title_text == "语言"

        box.deleteLater()

    def test_initialization_with_defaults(self):
        """Test tag search box initializes with empty title."""
        box = ElaTagSearchBox()

        assert box._title_text == ""

        box.deleteLater()

    def test_fixed_height_is_38(self):
        """Test tag search box has fixed height of 38."""
        box = ElaTagSearchBox()

        assert box.height() == 38

        box.deleteLater()

    def test_has_mark_animation(self):
        """Test tag search box has mark animation."""
        box = ElaTagSearchBox()

        assert hasattr(box, '_mark_animation')
        assert isinstance(box._mark_animation, QPropertyAnimation)

        box.deleteLater()

    def test_mark_animation_duration_is_300ms(self):
        """Test mark animation duration is 300ms."""
        box = ElaTagSearchBox()

        assert box._mark_animation.duration() == 300

        box.deleteLater()

    def test_has_rotate_animation(self):
        """Test tag search box has rotate animation."""
        box = ElaTagSearchBox()

        assert hasattr(box, '_rotate_animation')
        assert isinstance(box._rotate_animation, QPropertyAnimation)

        box.deleteLater()

    def test_expand_mark_width_property(self):
        """Test expandMarkWidth property."""
        box = ElaTagSearchBox()

        box.expandMarkWidth = 50.0
        assert box.expandMarkWidth == 50.0

        box.deleteLater()

    def test_expand_icon_rotate_property(self):
        """Test expandIconRotate property."""
        box = ElaTagSearchBox()

        box.expandIconRotate = -180.0
        assert box.expandIconRotate == -180.0

        box.deleteLater()

    def test_set_title(self):
        """Test setTitle updates title text."""
        box = ElaTagSearchBox()
        box.setTitle("新标题")

        assert box._title_text == "新标题"

        box.deleteLater()

    def test_title_returns_current_title(self):
        """Test title returns current title text."""
        box = ElaTagSearchBox(title="测试")

        assert box.title() == "测试"

        box.deleteLater()

    def test_inherits_from_search_box(self):
        """Test tag search box inherits search functionality."""
        from pyqt5_ela_pro.combo_box import ElaSearchBox

        box = ElaTagSearchBox()
        assert isinstance(box, ElaSearchBox)

        box.deleteLater()

    def test_title_font_size_default_is_13(self):
        """Test default title font size is 13."""
        box = ElaTagSearchBox()

        assert box._title_font_size == 13

        box.deleteLater()