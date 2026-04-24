"""Tests for parquet_table module: ElaParquetTable, ElaInfoBarWidget, ElaPagerWidget."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt, pyqtSignal

from pyqt5_ela_pro.parquet_table import (
    ElaInfoBarWidget,
    ElaPagerWidget,
    INFO_BAR_HEIGHT,
    INFO_BAR_SPACING,
    PAGER_HEIGHT,
    PAGER_SPACING,
)


class TestConstants:
    """Test cases for module constants."""

    def test_info_bar_height(self):
        """Test INFO_BAR_HEIGHT is 40."""
        assert INFO_BAR_HEIGHT == 40

    def test_info_bar_spacing(self):
        """Test INFO_BAR_SPACING is 10."""
        assert INFO_BAR_SPACING == 10

    def test_pager_height(self):
        """Test PAGER_HEIGHT is 50."""
        assert PAGER_HEIGHT == 50

    def test_pager_spacing(self):
        """Test PAGER_SPACING is 12."""
        assert PAGER_SPACING == 12


class TestElaInfoBarWidget:
    """Test cases for ElaInfoBarWidget class."""

    def test_initialization(self):
        """Test info bar initializes correctly."""
        bar = ElaInfoBarWidget()

        assert bar._col_name == ""
        assert bar._col_index == 0
        assert bar._min_val == ""
        assert bar._max_val == ""
        assert bar._last_val == ""

        bar.deleteLater()

    def test_fixed_height_is_info_bar_height(self):
        """Test info bar has fixed height of INFO_BAR_HEIGHT."""
        bar = ElaInfoBarWidget()

        assert bar.height() == INFO_BAR_HEIGHT

        bar.deleteLater()

    def test_update_info(self):
        """Test update_info updates all values."""
        bar = ElaInfoBarWidget()

        bar.update_info("年龄", 2, "18", "100", "50")

        assert bar._col_name == "年龄"
        assert bar._col_index == 2
        assert bar._min_val == "18"
        assert bar._max_val == "100"
        assert bar._last_val == "50"

        bar.deleteLater()

    def test_clear_info(self):
        """Test clear_info updates label text."""
        bar = ElaInfoBarWidget()
        bar.update_info("年龄", 2, "18", "100", "50")

        bar.clear_info()

        assert "当前列" in bar._col_label.text()

        bar.deleteLater()


class TestElaPagerWidget:
    """Test cases for ElaPagerWidget class."""

    def test_initialization(self):
        """Test pager initializes correctly."""
        pager = ElaPagerWidget(total_rows=100, total_cols=5, current_page=1)

        assert pager._total_rows == 100
        assert pager._total_cols == 5
        assert pager._current_page == 1
        assert pager._total_pages == 1

        pager.deleteLater()

    def test_fixed_height_is_pager_height(self):
        """Test pager has fixed height of PAGER_HEIGHT."""
        pager = ElaPagerWidget(total_rows=100, total_cols=5, current_page=1)

        assert pager.height() == PAGER_HEIGHT

        pager.deleteLater()

    def test_has_page_request_signal(self):
        """Test pager has pageRequest signal."""
        pager = ElaPagerWidget(total_rows=100, total_cols=5, current_page=1)

        assert hasattr(pager, 'pageRequest')
        assert callable(pager.pageRequest)

        pager.deleteLater()

    def test_update_state(self):
        """Test update_state updates pager state."""
        pager = ElaPagerWidget(total_rows=100, total_cols=5, current_page=1)

        pager.update_state(total_rows=200, total_cols=10, current_page=2, total_pages=20)

        assert pager._total_rows == 200
        assert pager._total_cols == 10
        assert pager._current_page == 2
        assert pager._total_pages == 20

        pager.deleteLater()

    def test_prev_button_disabled_on_first_page(self):
        """Test prev button is disabled on first page."""
        pager = ElaPagerWidget(total_rows=100, total_cols=5, current_page=1)

        assert pager._prev_btn.isEnabled() is False

        pager.deleteLater()

    def test_next_button_disabled_on_last_page(self):
        """Test next button is disabled on last page."""
        pager = ElaPagerWidget(total_rows=100, total_cols=5, current_page=10)

        pager._total_pages = 10
        pager._update_button_states()

        assert pager._next_btn.isEnabled() is False

        pager.deleteLater()

    def test_total_pages_calculation(self):
        """Test total pages calculation with page size."""
        pager = ElaPagerWidget(total_rows=100, total_cols=5, current_page=1)
        pager._page_size = 10

        pager._total_pages = (100 + 10 - 1) // 10

        assert pager._total_pages == 10

        pager.deleteLater()


class TestElaParquetTableImport:
    """Test cases for ElaParquetTable import behavior."""

    def test_polars_not_installed_raises_import_error(self):
        """Test ElaParquetTable raises ImportError when polars is not available."""
        import sys
        from pyqt5_ela_pro import parquet_table

        original_pl = getattr(parquet_table, 'pl', None)
        parquet_table.pl = None

        try:
            with pytest.raises(ImportError, match="polars"):
                parquet_table.ElaParquetTable.__init__(
                    parquet_table.ElaParquetTable.__new__(parquet_table.ElaParquetTable),
                    "test.parquet"
                )
        finally:
            if original_pl is not None:
                parquet_table.pl = original_pl

    def test_file_not_found_raises_error(self):
        """Test ElaParquetTable raises FileNotFoundError for missing file."""
        import sys
        from pyqt5_ela_pro import parquet_table

        original_pl = getattr(parquet_table, 'pl', None)
        mock_pl = MagicMock()
        parquet_table.pl = mock_pl

        try:
            with pytest.raises(FileNotFoundError):
                parquet_table.ElaParquetTable("nonexistent_file.parquet")
        finally:
            if original_pl is not None:
                parquet_table.pl = original_pl