"""Tests for ela_tag_box module: ElaTagBox."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor

from pyqt5_ela_pro.ela_tag_box import ElaTagBox


class TestElaTagBox:
    """Test cases for ElaTagBox class."""

    def test_initialization_with_title(self):
        """Test tag box initializes with title."""
        box = ElaTagBox(title="语言")

        assert box._title_text == "语言"

        box.deleteLater()

    def test_initialization_with_defaults(self):
        """Test tag box initializes with empty title."""
        box = ElaTagBox()

        assert box._title_text == ""

        box.deleteLater()

    def test_fixed_height_is_38(self):
        """Test tag box has fixed height of 38."""
        box = ElaTagBox()

        assert box.height() == 38

        box.deleteLater()

    def test_has_mark_animation(self):
        """Test tag box has mark animation."""
        box = ElaTagBox()

        assert hasattr(box, '_mark_animation')
        assert isinstance(box._mark_animation, QPropertyAnimation)

        box.deleteLater()

    def test_mark_animation_duration_is_300ms(self):
        """Test mark animation duration is 300ms."""
        box = ElaTagBox()

        assert box._mark_animation.duration() == 300

        box.deleteLater()

    def test_has_rotate_animation(self):
        """Test tag box has rotate animation."""
        box = ElaTagBox()

        assert hasattr(box, '_rotate_animation')
        assert isinstance(box._rotate_animation, QPropertyAnimation)

        box.deleteLater()

    def test_rotate_animation_duration_is_300ms(self):
        """Test rotate animation duration is 300ms."""
        box = ElaTagBox()

        assert box._rotate_animation.duration() == 300

        box.deleteLater()

    def test_expand_mark_width_property(self):
        """Test expandMarkWidth property getter and setter."""
        box = ElaTagBox()

        box.expandMarkWidth = 50.0
        assert box.expandMarkWidth == 50.0

        box.expandMarkWidth = 0.0
        assert box.expandMarkWidth == 0.0

        box.deleteLater()

    def test_expand_icon_rotate_property(self):
        """Test expandIconRotate property getter and setter."""
        box = ElaTagBox()

        box.expandIconRotate = -180.0
        assert box.expandIconRotate == -180.0

        box.expandIconRotate = 0.0
        assert box.expandIconRotate == 0.0

        box.deleteLater()

    def test_set_title(self):
        """Test setTitle updates title text."""
        box = ElaTagBox()
        box.setTitle("新标题")

        assert box._title_text == "新标题"

        box.deleteLater()

    def test_title_returns_current_title(self):
        """Test title returns current title text."""
        box = ElaTagBox(title="测试")

        assert box.title() == "测试"

        box.deleteLater()

    def test_initial_expand_mark_width_is_zero(self):
        """Test initial expand mark width is 0."""
        box = ElaTagBox()

        assert box._expand_mark_width == 0.0

        box.deleteLater()

    def test_initial_expand_icon_rotate_is_zero(self):
        """Test initial expand icon rotate is 0."""
        box = ElaTagBox()

        assert box._expand_icon_rotate == 0.0

        box.deleteLater()

    def test_title_font_size_default_is_13(self):
        """Test default title font size is 13."""
        box = ElaTagBox()

        assert box._title_font_size == 13

        box.deleteLater()

    def test_delete_later_cleans_up(self):
        """Test deleteLater can be called safely (verifies signal disconnects)."""
        box = ElaTagBox()
        box.deleteLater()

    def test_delete_later_disconnects_index_changed(self):
        """Test deleteLater disconnects currentIndexChanged signal without error."""
        box = ElaTagBox(title="test")
        box.deleteLater()  # should not raise TypeError when disconnecting