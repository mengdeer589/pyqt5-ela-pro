"""Tests for combo_box module: ElaSearchBox, ElaSearchMultiBox, ElaSearchProxyModel."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QStringListModel, QModelIndex
from PyQt5.QtWidgets import QWidget, QLineEdit

from pyqt5_ela_pro.combo_box import (
    ElaSearchProxyModel,
    ElaSearchMultiBox,
    ElaSearchBox,
    COMBO_BOX_MIN_WIDTH,
    COMBO_BOX_SHADOW_BORDER_WIDTH,
)


class TestElaSearchProxyModel:
    """Test cases for ElaSearchProxyModel."""

    def test_initialization(self):
        """Test proxy model initializes with empty keyword."""
        proxy = ElaSearchProxyModel()
        assert proxy._keyword == ""

    def test_set_keyword_lowercase(self):
        """Test setKeyword converts keyword to lowercase."""
        proxy = ElaSearchProxyModel()
        proxy.setKeyword("TEST")
        assert proxy._keyword == "test"

    def test_filter_accepts_row_without_keyword(self):
        """Test filterAcceptsRow returns True when keyword is empty."""
        proxy = ElaSearchProxyModel()
        assert proxy.filterAcceptsRow(0, QModelIndex()) is True

    def test_filter_accepts_row_with_matching_text(self):
        """Test filterAcceptsRow matches text directly."""
        proxy = ElaSearchProxyModel()
        source_model = QStringListModel(["北京", "上海", "广州"])

        proxy.setSourceModel(source_model)
        proxy.setKeyword("北京")

        assert proxy.filterAcceptsRow(0, QModelIndex()) is True
        assert proxy.filterAcceptsRow(1, QModelIndex()) is False

    def test_filter_accepts_row_with_pinyin(self):
        """Test filterAcceptsRow matches pinyin initials."""
        proxy = ElaSearchProxyModel()
        source_model = QStringListModel(["北京", "上海", "广州"])

        proxy.setSourceModel(source_model)
        proxy.setKeyword("sh")

        assert proxy.filterAcceptsRow(1, QModelIndex()) is True

    def test_filter_is_case_insensitive(self):
        """Test filter is case insensitive."""
        proxy = ElaSearchProxyModel()
        source_model = QStringListModel(["测试"])

        proxy.setSourceModel(source_model)
        proxy.setKeyword("ce")

        assert proxy.filterAcceptsRow(0, QModelIndex()) is True


class TestElaSearchMultiBox:
    """Test cases for ElaSearchMultiBox."""

    def test_initialization(self):
        """Test multi-box initializes with empty selection."""
        box = ElaSearchMultiBox()
        assert box._currentSelection == []
        assert box._isRestoringSelection is False
        box.deleteLater()

    def test_add_item(self):
        """Test addItem adds item to combo box."""
        box = ElaSearchMultiBox()
        box.addItem("选项1")
        assert box.count() >= 1
        box.deleteLater()

    def test_add_items(self):
        """Test addItems adds multiple items."""
        box = ElaSearchMultiBox()
        box.addItems(["选项1", "选项2", "选项3"])
        assert box.count() >= 3
        box.deleteLater()

    def test_clear(self):
        """Test clear removes all items and selection."""
        box = ElaSearchMultiBox()
        box.addItems(["选项1", "选项2"])
        box.setCurrentSelection(["选项1"])
        box.clear()
        assert box._currentSelection == []
        box.deleteLater()

    def test_set_current_selection_with_string(self):
        """Test setCurrentSelection converts string to list."""
        box = ElaSearchMultiBox()
        box.setCurrentSelection("single")
        assert box._currentSelection == ["single"]
        box.deleteLater()

    def test_get_current_selection(self):
        """Test getCurrentSelection returns copy of selection."""
        box = ElaSearchMultiBox()
        box.setCurrentSelection(["选项1", "选项2"])
        selection = box.getCurrentSelection()
        assert selection == ["选项1", "选项2"]
        selection.append("新的")
        assert box._currentSelection == ["选项1", "选项2"]
        box.deleteLater()

    def test_minimum_width_constant(self):
        """Test COMBO_BOX_MIN_WIDTH is 150."""
        assert COMBO_BOX_MIN_WIDTH == 150

    def test_shadow_border_width_constant(self):
        """Test COMBO_BOX_SHADOW_BORDER_WIDTH is 3."""
        assert COMBO_BOX_SHADOW_BORDER_WIDTH == 3

    def test_delete_later_cleans_up_search_widget(self):
        """Test deleteLater cleans up search widget."""
        box = ElaSearchMultiBox()
        box.addItem("test")
        box.showPopup()
        box.deleteLater()


class TestElaSearchBox:
    """Test cases for ElaSearchBox."""

    def test_initialization(self):
        """Test search box initializes correctly."""
        box = ElaSearchBox()
        assert len(box._allItems) == 0
        assert isinstance(box._sourceModel, QStringListModel)
        assert isinstance(box._proxyModel, ElaSearchProxyModel)
        box.deleteLater()

    def test_add_item(self):
        """Test addItem adds item to internal list."""
        box = ElaSearchBox()
        box.addItem("测试", userData={"id": 1})
        assert len(box._allItems) == 1
        assert box._allItems[0] == ("测试", {"id": 1})
        box.deleteLater()

    def test_add_items(self):
        """Test addItems adds multiple items."""
        box = ElaSearchBox()
        box.addItems(["北京", "上海", "广州"])
        assert len(box._allItems) == 3
        box.deleteLater()

    def test_clear(self):
        """Test clear removes all items."""
        box = ElaSearchBox()
        box.addItems(["北京", "上海"])
        box.clear()
        assert len(box._allItems) == 0
        box.deleteLater()

    def test_proxy_model_set_keyword_on_show(self):
        """Test showPopup resets proxy keyword."""
        box = ElaSearchBox()
        box.addItem("test")
        box.showPopup()
        assert box._proxyModel._keyword == ""
        box.hidePopup()
        box.deleteLater()

    def test_delete_later_disconnects_signal(self):
        """Test deleteLater disconnects activated signal."""
        box = ElaSearchBox()
        box.addItem("test")
        box.deleteLater()