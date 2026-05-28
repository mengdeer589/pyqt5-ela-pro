from __future__ import annotations


from pyqt5_ela_pro.ela_pagination import ElaPagination


class TestElaPaginationInit:
    def test_initialization_with_defaults(self):
        p = ElaPagination()
        assert p._current_page == 1
        assert p._total_pages == 1
        assert p._button_size == 28
        assert p._pager_count == 11
        assert p._jumper_visible is False
        assert p._hover_index == -1
        p.deleteLater()

    def test_has_current_page_changed_signal(self):
        p = ElaPagination()
        assert hasattr(p, "currentPageChanged")
        assert callable(p.currentPageChanged)
        p.deleteLater()

    def test_hover_index_initially_negative_one(self):
        p = ElaPagination()
        assert p._hover_index == -1
        p.deleteLater()


class TestElaPaginationCurrentPage:
    def test_current_page_default(self):
        p = ElaPagination()
        assert p.currentPage() == 1
        p.deleteLater()

    def test_set_current_page(self):
        p = ElaPagination()
        p.setTotalPages(5)
        p.setCurrentPage(3)
        assert p.currentPage() == 3
        p.deleteLater()

    def test_set_current_page_clamps_to_min(self):
        p = ElaPagination()
        p.setTotalPages(5)
        p.setCurrentPage(0)
        assert p.currentPage() == 1
        p.deleteLater()

    def test_set_current_page_clamps_to_max(self):
        p = ElaPagination()
        p.setTotalPages(5)
        p.setCurrentPage(10)
        assert p.currentPage() == 1
        p.deleteLater()

    def test_set_current_page_negative(self):
        p = ElaPagination()
        p.setTotalPages(5)
        p.setCurrentPage(-1)
        assert p.currentPage() == 1
        p.deleteLater()

    def test_set_current_page_emits_signal(self):
        p = ElaPagination()
        p.setTotalPages(5)
        received = []
        p.currentPageChanged.connect(lambda v: received.append(v))
        p.setCurrentPage(3)
        assert 3 in received
        p.deleteLater()

    def test_set_current_page_same_value_no_emit(self):
        p = ElaPagination()
        p.setTotalPages(5)
        p.setCurrentPage(1)
        received = []
        p.currentPageChanged.connect(lambda v: received.append(v))
        p.setCurrentPage(1)
        assert len(received) == 0
        p.deleteLater()


class TestElaPaginationTotalPages:
    def test_total_pages_default(self):
        p = ElaPagination()
        assert p.totalPages() == 1
        p.deleteLater()

    def test_set_total_pages(self):
        p = ElaPagination()
        p.setTotalPages(20)
        assert p.totalPages() == 20
        p.deleteLater()

    def test_set_total_pages_clamps_to_min_1(self):
        p = ElaPagination()
        p.setTotalPages(0)
        assert p.totalPages() == 1
        p.deleteLater()

    def test_set_total_pages_negative(self):
        p = ElaPagination()
        p.setTotalPages(-5)
        assert p.totalPages() == 1
        p.deleteLater()

    def test_set_total_pages_corrects_current_page(self):
        p = ElaPagination()
        p.setTotalPages(3)
        p.setCurrentPage(3)
        p.setTotalPages(1)
        assert p.currentPage() == 1
        p.deleteLater()


class TestElaPaginationButtonSize:
    def test_button_size_default(self):
        p = ElaPagination()
        assert p.buttonSize() == 28
        p.deleteLater()

    def test_set_button_size(self):
        p = ElaPagination()
        p.setButtonSize(36)
        assert p.buttonSize() == 36
        p.deleteLater()

    def test_set_button_size_updates_height(self):
        p = ElaPagination()
        p.setButtonSize(36)
        assert p.height() >= 36
        p.deleteLater()


class TestElaPaginationPagerCount:
    def test_pager_count_default(self):
        p = ElaPagination()
        assert p.pagerCount() == 11
        p.deleteLater()

    def test_set_pager_count(self):
        p = ElaPagination()
        p.setPagerCount(7)
        assert p.pagerCount() == 7
        p.deleteLater()


class TestElaPaginationJumper:
    def test_jumper_visible_default(self):
        p = ElaPagination()
        assert p.isJumperVisible() is False
        p.deleteLater()

    def test_set_jumper_visible(self):
        p = ElaPagination()
        p.setJumperVisible(True)
        assert p.isJumperVisible() is True
        p.deleteLater()

    def test_jumper_edit_hidden_by_default(self):
        p = ElaPagination()
        assert p._jumper_edit.isVisible() is False
        p.deleteLater()

    def test_jumper_edit_visible_after_set(self):
        p = ElaPagination()
        p.setJumperVisible(True)
        assert p._jumper_edit.isHidden() is False
        p.deleteLater()


class TestElaPaginationPageLabel:
    def test_page_label_exists(self):
        p = ElaPagination()
        assert hasattr(p, "_page_label")
        p.deleteLater()

    def test_page_label_hidden_by_default(self):
        p = ElaPagination()
        assert p._page_label.isVisible() is False
        p.deleteLater()

    def test_page_label_visible_with_jumper(self):
        p = ElaPagination()
        p.setJumperVisible(True)
        assert p._page_label.isHidden() is False
        p.deleteLater()

    def test_page_label_text_format(self):
        p = ElaPagination()
        p.setTotalPages(50)
        p.setJumperVisible(True)
        assert "1" in p._page_label.text()
        assert "50" in p._page_label.text()
        p.deleteLater()

    def test_page_label_updates_on_set_current(self):
        p = ElaPagination()
        p.setTotalPages(50)
        p.setJumperVisible(True)
        p.setCurrentPage(25)
        assert "25" in p._page_label.text()
        assert "50" in p._page_label.text()
        p.deleteLater()


class TestElaPaginationVisiblePages:
    def test_get_visible_pages_single_page(self):
        p = ElaPagination()
        p.setTotalPages(1)
        pages = p._getVisiblePages()
        assert pages == [1]
        p.deleteLater()

    def test_get_visible_pages_few_pages(self):
        p = ElaPagination()
        p.setTotalPages(5)
        pages = p._getVisiblePages()
        assert pages == [1, 2, 3, 4, 5]
        p.deleteLater()

    def test_get_visible_pages_first_page_many(self):
        p = ElaPagination()
        p.setTotalPages(50)
        p.setPagerCount(11)
        p.setCurrentPage(1)
        pages = p._getVisiblePages()
        assert 1 in pages
        assert -1 in pages  # right ellipsis
        assert 50 in pages
        p.deleteLater()

    def test_get_visible_pages_last_page_many(self):
        p = ElaPagination()
        p.setTotalPages(50)
        p.setPagerCount(11)
        p.setCurrentPage(50)
        pages = p._getVisiblePages()
        assert 1 in pages
        assert -3 in pages  # left ellipsis
        assert 50 in pages
        p.deleteLater()

    def test_get_visible_pages_middle_page_many(self):
        p = ElaPagination()
        p.setTotalPages(50)
        p.setPagerCount(11)
        p.setCurrentPage(25)
        pages = p._getVisiblePages()
        assert 1 in pages
        assert -3 in pages
        assert 25 in pages
        assert -1 in pages
        assert 50 in pages
        p.deleteLater()


class TestElaPaginationButtonRects:
    def test_get_button_rects_returns_list(self):
        p = ElaPagination()
        p.setTotalPages(5)
        rects = p._getButtonRects()
        assert len(rects) > 0
        assert all(len(item) == 2 for item in rects)
        p.deleteLater()

    def test_first_rect_is_prev_button(self):
        p = ElaPagination()
        p.setTotalPages(5)
        rects = p._getButtonRects()
        assert rects[0][1] == 0  # prev button
        p.deleteLater()

    def test_last_rect_is_next_button(self):
        p = ElaPagination()
        p.setTotalPages(5)
        rects = p._getButtonRects()
        assert rects[-1][1] == -2  # next button
        p.deleteLater()


class TestElaPaginationJumperEntered:
    def test_on_jumper_entered_valid(self):
        p = ElaPagination()
        p.setTotalPages(10)
        p._jumper_edit.setText("5")
        received = []
        p.currentPageChanged.connect(lambda v: received.append(v))
        p._onJumperEntered()
        assert p.currentPage() == 5
        p.deleteLater()

    def test_on_jumper_entered_invalid(self):
        p = ElaPagination()
        p.setTotalPages(10)
        p._jumper_edit.setText("abc")
        p._onJumperEntered()
        assert p.currentPage() == 1
        p.deleteLater()

    def test_on_jumper_entered_out_of_range(self):
        p = ElaPagination()
        p.setTotalPages(10)
        p._jumper_edit.setText("999")
        p._onJumperEntered()
        assert p.currentPage() == 1
        p.deleteLater()


class TestElaPaginationTheme:
    def test_on_theme_changed_updates_mode(self):
        p = ElaPagination()
        from PyQt5ElaWidgetTools import ElaThemeType
        p._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert p._theme_mode == ElaThemeType.ThemeMode.Dark
        p.deleteLater()


class TestElaPaginationDeleteLater:
    def test_delete_later_cleans_up(self):
        p = ElaPagination()
        p.deleteLater()
