"""Tests for combo_box module: ElaSearchBox, ElaSearchMultiBox, ElaSearchProxyModel."""

from __future__ import annotations

from PyQt5.QtCore import Qt, QStringListModel, QModelIndex
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro.combo_box import (
    ElaSearchProxyModel,
    ElaSearchMultiBox,
    ElaSearchBox,
)


class TestElaSearchProxyModel:
    """Test cases for ElaSearchProxyModel."""

    def test_initialization(self):
        """Test proxy model initializes with empty keyword."""
        proxy = ElaSearchProxyModel()
        assert proxy._keyword == ""
        assert proxy._tokens == []

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
        """Test filterAcceptsRow matches full pinyin."""
        proxy = ElaSearchProxyModel()
        source_model = QStringListModel(["北京", "上海", "广州"])

        proxy.setSourceModel(source_model)
        proxy.setKeyword("sh")

        assert proxy.filterAcceptsRow(1, QModelIndex()) is True

    def test_filter_accepts_row_with_pinyin_initials(self):
        """Test filterAcceptsRow matches pinyin initials (bj -> 北京)."""
        proxy = ElaSearchProxyModel()
        source_model = QStringListModel(["北京", "上海", "广州"])

        proxy.setSourceModel(source_model)
        proxy.setKeyword("bj")

        assert proxy.filterAcceptsRow(0, QModelIndex()) is True
        assert proxy.filterAcceptsRow(1, QModelIndex()) is False

    def test_filter_accepts_row_with_full_pinyin_substring(self):
        """Test filterAcceptsRow matches a full pinyin substring."""
        proxy = ElaSearchProxyModel()
        source_model = QStringListModel(["北京", "上海"])

        proxy.setSourceModel(source_model)
        proxy.setKeyword("beij")

        assert proxy.filterAcceptsRow(0, QModelIndex()) is True
        assert proxy.filterAcceptsRow(1, QModelIndex()) is False

    def test_filter_requires_all_space_separated_tokens(self):
        """Test multiple tokens are ANDed."""
        proxy = ElaSearchProxyModel()
        source_model = QStringListModel(["北京", "上海", "北京上海"])

        proxy.setSourceModel(source_model)
        proxy.setKeyword("bj sh")

        assert proxy.filterAcceptsRow(0, QModelIndex()) is False
        assert proxy.filterAcceptsRow(1, QModelIndex()) is False
        assert proxy.filterAcceptsRow(2, QModelIndex()) is True

    def test_filter_is_case_insensitive(self):
        """Test filter is case insensitive."""
        proxy = ElaSearchProxyModel()
        source_model = QStringListModel(["测试"])

        proxy.setSourceModel(source_model)
        proxy.setKeyword("ce")

        assert proxy.filterAcceptsRow(0, QModelIndex()) is True

    def test_filter_matches_ignoring_punctuation(self):
        """Test compact matching ignores punctuation (gpt4o -> gpt-4o)."""
        proxy = ElaSearchProxyModel()
        source_model = QStringListModel(["gpt-4o", "claude-3"])

        proxy.setSourceModel(source_model)
        proxy.setKeyword("gpt4o")

        assert proxy.filterAcceptsRow(0, QModelIndex()) is True
        assert proxy.filterAcceptsRow(1, QModelIndex()) is False

    def test_pinyin_cache_filled_and_reused(self):
        """Test pinyin cache stores (full, initials) and is reused."""
        proxy = ElaSearchProxyModel()
        proxy.setSourceModel(QStringListModel(["北京"]))

        proxy.setKeyword("bj")
        assert proxy.filterAcceptsRow(0, QModelIndex()) is True
        assert proxy._pinyin_cache["北京"] == ("beijing", "bj")

        proxy.clearPinyinCache()
        assert proxy._pinyin_cache == {}


class TestElaSearchMultiBox:
    """Test cases for ElaSearchMultiBox."""

    def test_initialization(self):
        """Test multi-box initializes with empty selection."""
        box = ElaSearchMultiBox()
        assert box._currentSelection == []
        assert box._isRestoringSelection is False
        assert box._pinyin_cache == {}
        box.deleteLater()

    def test_add_item(self):
        """Test addItem adds item to combo box."""
        box = ElaSearchMultiBox()
        box.addItem("选项1")
        assert box.count() >= 1
        assert box.items == ["选项1"]
        box.deleteLater()

    def test_add_items(self):
        """Test addItems adds multiple items."""
        box = ElaSearchMultiBox()
        box.addItems(["选项1", "选项2", "选项3"])
        assert box.count() >= 3
        assert box.items == ["选项1", "选项2", "选项3"]
        box.deleteLater()

    def test_clear(self):
        """Test clear removes all items and selection."""
        box = ElaSearchMultiBox()
        box.addItems(["选项1", "选项2"])
        box.setCurrentSelection(["选项1"])
        box.clear()
        assert box._currentSelection == []
        assert box.items == []
        assert box._pinyin_cache == {}
        box.deleteLater()

    def test_set_current_selection_rejects_string(self):
        """Test setCurrentSelection with string iterates chars (expected list)."""
        box = ElaSearchMultiBox()
        box.setCurrentSelection(["single"])
        assert box._currentSelection == ["single"]
        box.deleteLater()

    def test_pinyin_cache_cleared_on_clear(self):
        """Test clear clears the pinyin cache."""
        box = ElaSearchMultiBox()
        box.addItems(["选项1", "选项2"])
        box._pinyin_cache["选项1"] = ("xuanxiang1", "xx1")
        box.clear()
        assert box._pinyin_cache == {}
        box.deleteLater()

    def test_pinyin_cache_filled_on_search(self):
        """Test _onSearchTextChanged fills pinyin cache with (full, initials)."""
        box = ElaSearchMultiBox()
        box.addItems(["北京", "上海"])
        box._onSearchTextChanged("bei")
        assert box._pinyin_cache["北京"] == ("beijing", "bj")
        box.deleteLater()

    def test_search_matches_pinyin_initials(self):
        """Test searching by initials (bj -> 北京) hides non-matching rows."""
        box = ElaSearchMultiBox()
        box.addItems(["北京", "上海"])
        box._onSearchTextChanged("bj")
        view = box.view()
        assert view.isRowHidden(0) is False
        assert view.isRowHidden(1) is True
        box.deleteLater()

    def test_search_matches_space_separated_tokens(self):
        """Test space separated tokens are ANDed."""
        box = ElaSearchMultiBox()
        box.addItems(["北京", "上海", "北京上海"])
        box._onSearchTextChanged("bj sh")
        view = box.view()
        assert view.isRowHidden(0) is True
        assert view.isRowHidden(1) is True
        assert view.isRowHidden(2) is False
        box.deleteLater()

    def test_show_popup_resets_row_filter(self):
        """Test showPopup restores hidden rows from the previous search."""
        box = ElaSearchMultiBox()
        box.addItems(["北京", "上海"])
        box._onSearchTextChanged("bj")
        box.showPopup()
        assert box.view().isRowHidden(1) is False
        box.hidePopup()
        box.deleteLater()

    def test_delete_later_cleans_up_search_widget(self):
        """Test deleteLater cleans up search widget."""
        box = ElaSearchMultiBox()
        box.addItem("test")
        box.showPopup()
        box.hidePopup()  # 关闭 Popup：残留的活动弹出窗口会拦截后续测试的鼠标事件
        box.deleteLater()

    def test_set_search_visible_roundtrip(self, make):
        """Test search visibility toggle roundtrip."""
        box = make(ElaSearchMultiBox)
        assert box.searchVisible() is True
        box.setSearchVisible(False)
        assert box.searchVisible() is False


class TestElaSearchBox:
    """Test cases for ElaSearchBox."""

    def test_initialization(self):
        """Test search box initializes with the native combo model."""
        box = ElaSearchBox()
        assert box.items == []
        assert box.count() == 0
        assert box._pinyin_cache == {}
        box.deleteLater()

    def test_add_item(self):
        """Test addItem adds item and user data to the native model."""
        box = ElaSearchBox()
        box.addItem("测试", "u1")
        assert box.count() == 1
        assert box.itemText(0) == "测试"
        assert box.itemData(0, Qt.ItemDataRole.UserRole) == "u1"
        assert box.findData("u1") == 0
        box.deleteLater()

    def test_add_items(self):
        """Test addItems adds multiple items."""
        box = ElaSearchBox()
        box.addItems(["北京", "上海", "广州"])
        assert box.items == ["北京", "上海", "广州"]
        box.deleteLater()

    def test_insert_item_keeps_items_in_sync(self):
        """Test native insertItem is reflected by items property."""
        box = ElaSearchBox()
        box.addItems(["a", "c"])
        box.insertItem(1, "b")
        assert box.items == ["a", "b", "c"]
        box.deleteLater()

    def test_insert_items_keeps_items_in_sync(self):
        """Test native insertItems is reflected by items property."""
        box = ElaSearchBox()
        box.addItems(["c"])
        box.insertItems(0, ["a", "b"])
        assert box.items == ["a", "b", "c"]
        box.deleteLater()

    def test_remove_item_keeps_items_in_sync(self):
        """Test native removeItem is reflected by items property."""
        box = ElaSearchBox()
        box.addItems(["a", "b", "c"])
        box.removeItem(1)
        assert box.items == ["a", "c"]
        box.deleteLater()

    def test_set_item_text_keeps_items_in_sync(self):
        """Test native setItemText is reflected by items property."""
        box = ElaSearchBox()
        box.addItems(["a", "b"])
        box.setItemText(0, "z")
        assert box.items == ["z", "b"]
        box.deleteLater()

    def test_clear(self):
        """Test clear removes all items and resets the pinyin cache."""
        box = ElaSearchBox()
        box.addItems(["北京", "上海"])
        box._onSearchTextChanged("bj")
        box.clear()
        assert box.items == []
        assert box._pinyin_cache == {}
        box.deleteLater()

    def test_search_matches_pinyin_initials(self):
        """Test searching by initials (bj -> 北京) hides non-matching rows."""
        box = ElaSearchBox()
        box.addItems(["北京", "上海"])
        box._onSearchTextChanged("bj")
        view = box.view()
        assert view.isRowHidden(0) is False
        assert view.isRowHidden(1) is True
        box.deleteLater()

    def test_search_matches_full_pinyin(self):
        """Test searching by full pinyin (bei -> 北京)."""
        box = ElaSearchBox()
        box.addItems(["北京", "上海"])
        box._onSearchTextChanged("bei")
        view = box.view()
        assert view.isRowHidden(0) is False
        assert view.isRowHidden(1) is True
        box.deleteLater()

    def test_search_matches_ignoring_punctuation(self, make):
        """Test compact matching ignores punctuation (gpt4o -> gpt-4o)."""
        box = make(ElaSearchBox)
        box.addItems(["gpt-4o", "claude-3"])
        box._onSearchTextChanged("gpt4o")
        view = box.view()
        assert view.isRowHidden(0) is False
        assert view.isRowHidden(1) is True

    def test_search_resets_when_keyword_cleared(self):
        """Test clearing the keyword restores all rows."""
        box = ElaSearchBox()
        box.addItems(["北京", "上海"])
        box._onSearchTextChanged("上海")
        box._onSearchTextChanged("")
        view = box.view()
        assert view.isRowHidden(0) is False
        assert view.isRowHidden(1) is False
        box.deleteLater()

    def test_show_popup_resets_row_filter(self):
        """Test showPopup restores hidden rows from the previous search."""
        box = ElaSearchBox()
        box.addItems(["北京", "上海"])
        box._onSearchTextChanged("bj")
        box.showPopup()
        assert box.view().isRowHidden(1) is False
        box.hidePopup()
        box.deleteLater()

    def test_popup_creates_search_edit_and_filters(self):
        """Test the popup search edit drives the row filter."""
        box = ElaSearchBox()
        box.addItems(["北京", "上海"])
        box.showPopup()
        assert box._searchEdit is not None
        box._searchEdit.setText("bj")
        view = box.view()
        assert view.isRowHidden(0) is False
        assert view.isRowHidden(1) is True
        box.hidePopup()
        box.deleteLater()

    def test_delete_later_cleans_up_search_widget(self):
        """Test deleteLater cleans up search widget."""
        box = ElaSearchBox()
        box.addItem("test")
        box.showPopup()
        box.hidePopup()
        box.deleteLater()

    def test_set_search_visible_roundtrip(self, make):
        """Test search visibility toggle roundtrip."""
        box = make(ElaSearchBox)
        assert box.searchVisible() is True
        box.setSearchVisible(False)
        assert box.searchVisible() is False

    def test_disable_search_skips_widget(self, make, qapp):
        """Test disabled search is not created in the popup."""
        box = make(ElaSearchBox, make(QWidget))
        box.addItem("a")
        box.setSearchVisible(False)
        box.resize(240, 28)
        box.show()
        qapp.processEvents()
        box.showPopup()
        qapp.processEvents()
        assert box._searchWidget is None
        box.hidePopup()
        qapp.processEvents()
