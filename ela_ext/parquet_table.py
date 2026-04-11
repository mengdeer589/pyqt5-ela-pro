"""
Parquet 表格视图组件，支持分页功能。

基于 ``ElaDataTable`` 扩展，数据来源为 Parquet 文件，
通过 ``polars`` 进行高效读取，按页展示数据。
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, TYPE_CHECKING

from PyQt5.QtCore import pyqtSignal, QModelIndex
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5ElaWidgetTools import (
    ElaText,
    ElaPushButton,
    ElaLineEdit,
    eTheme,
    ElaThemeType,
)

from . import ThemeWidget
from .table_view import ElaDataTable


if TYPE_CHECKING:
    import polars as pl
else:
    try:
        import polars as pl
    except ImportError:
        pl = None


INFO_BAR_HEIGHT: int = 40
INFO_BAR_SPACING: int = 10
INFO_BAR_LABEL_SPACING: int = 20
PAGER_HEIGHT: int = 50
PAGER_SPACING: int = 12


class ElaInfoBarWidget(ThemeWidget):
    """列信息显示栏，显示当前选中列的统计信息。"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._col_name: str = ""
        self._col_index: int = 0
        self._min_val: str = ""
        self._max_val: str = ""
        self._last_val: str = ""
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFixedHeight(INFO_BAR_HEIGHT)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(INFO_BAR_SPACING)

        self._col_label = ElaText(self)  # type: ignore
        self._col_label.setText("当前列: -")
        self._col_label.setTextPixelSize(12)

        self._col_index_label = ElaText(self)  # type: ignore
        self._col_index_label.setText("第 - 列")
        self._col_index_label.setTextPixelSize(12)

        self._min_label = ElaText(self)  # type: ignore
        self._min_label.setText("最小值: -")
        self._min_label.setTextPixelSize(12)

        self._max_label = ElaText(self)  # type: ignore
        self._max_label.setText("最大值: -")
        self._max_label.setTextPixelSize(12)

        self._last_label = ElaText(self)  # type: ignore
        self._last_label.setText("最后一行: -")
        self._last_label.setTextPixelSize(12)

        layout.addWidget(self._col_label)
        layout.addSpacing(INFO_BAR_LABEL_SPACING)
        layout.addWidget(self._col_index_label)
        layout.addSpacing(INFO_BAR_SPACING)
        layout.addWidget(self._min_label)
        layout.addSpacing(INFO_BAR_SPACING)
        layout.addWidget(self._max_label)
        layout.addSpacing(INFO_BAR_SPACING)
        layout.addWidget(self._last_label)
        layout.addStretch(1)

        self._apply_colors()

    def _apply_colors(self) -> None:
        mode = eTheme.getThemeMode()

        col_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicDetailsText)
        self._col_label.setStyleSheet(f"color: {col_color.name()};")

        col_index_color = eTheme.getThemeColor(
            mode, ElaThemeType.ThemeColor.PrimaryNormal
        )
        self._col_index_label.setStyleSheet(f"color: {col_index_color.name()};")

        min_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.PrimaryHover)
        self._min_label.setStyleSheet(f"color: {min_color.name()};")

        max_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.StatusDanger)
        self._max_label.setStyleSheet(f"color: {max_color.name()};")

        last_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.PrimaryPress)
        self._last_label.setStyleSheet(f"color: {last_color.name()};")

    def update_info(
        self, col_name: str, col_index: int, min_val: str, max_val: str, last_val: str
    ) -> None:
        self._col_name = col_name
        self._col_index = col_index
        self._min_val = min_val
        self._max_val = max_val
        self._last_val = last_val

        self._col_label.setText(f"当前列: {col_name}")
        self._col_index_label.setText(f"第 {col_index} 列")
        self._min_label.setText(f"最小值: {min_val}")
        self._max_label.setText(f"最大值: {max_val}")
        self._last_label.setText(f"最后一行: {last_val}")

    def clear_info(self) -> None:
        self._col_label.setText("当前列: -")
        self._col_index_label.setText("第 - 列")
        self._min_label.setText("最小值: -")
        self._max_label.setText("最大值: -")
        self._last_label.setText("最后一行: -")


class ElaPagerWidget(ThemeWidget):
    """翻页控件组合，包含记录数、上下页、页码跳转。"""

    pageRequest = pyqtSignal(int)

    def __init__(
        self,
        total_rows: int,
        total_cols: int,
        current_page: int,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._total_rows = total_rows
        self._total_cols = total_cols
        self._current_page = current_page
        self._total_pages = 1

        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setFixedHeight(PAGER_HEIGHT)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(PAGER_SPACING)

        self._total_label = ElaText(self)  # type: ignore
        self._total_label.setText(f"共 {self._total_rows} 行 × {self._total_cols} 列")
        self._total_label.setTextPixelSize(13)
        self._total_label.setMinimumWidth(180)

        self._prev_btn = ElaPushButton("上一页", self)
        self._prev_btn.setFixedWidth(70)
        self._prev_btn.clicked.connect(self._on_prev_clicked)

        self._page_label = ElaText("第", self)
        self._page_label.setTextPixelSize(13)

        self._page_edit = ElaLineEdit(self)
        self._page_edit.setFixedWidth(60)
        self._page_edit.setValidator(QIntValidator(1, self._total_pages))
        self._page_edit.setPlaceholderText("页码")
        self._page_edit.returnPressed.connect(self._on_page_edit_entered)

        self._page_of_label = ElaText("页 / 共", self)
        self._page_of_label.setTextPixelSize(13)

        self._total_pages_label = ElaText(f"{self._total_pages} 页", self)
        self._total_pages_label.setTextPixelSize(13)

        self._next_btn = ElaPushButton("下一页", self)
        self._next_btn.setFixedWidth(70)
        self._next_btn.clicked.connect(self._on_next_clicked)

        layout.addWidget(self._total_label)
        layout.addStretch(1)
        layout.addWidget(self._prev_btn)
        layout.addWidget(self._page_label)
        layout.addWidget(self._page_edit)
        layout.addWidget(self._page_of_label)
        layout.addWidget(self._total_pages_label)
        layout.addWidget(self._next_btn)
        layout.addStretch(1)

        self._update_button_states()

    def _update_button_states(self) -> None:
        self._prev_btn.setEnabled(self._current_page > 1)
        self._next_btn.setEnabled(self._current_page < self._total_pages)
        self._page_edit.setText(str(self._current_page))

    def _on_prev_clicked(self) -> None:
        if self._current_page > 1:
            self.pageRequest.emit(self._current_page - 1)

    def _on_next_clicked(self) -> None:
        if self._current_page < self._total_pages:
            self.pageRequest.emit(self._current_page + 1)

    def _on_page_edit_entered(self) -> None:
        text = self._page_edit.text()
        if text:
            try:
                target = int(text)
                if 1 <= target <= self._total_pages:
                    self.pageRequest.emit(target)
            except ValueError:
                pass

    def update_state(
        self, total_rows: int, total_cols: int, current_page: int, total_pages: int
    ) -> None:
        self._total_rows = total_rows
        self._total_cols = total_cols
        self._current_page = current_page
        self._total_pages = total_pages

        self._total_label.setText(f"共 {self._total_rows} 行 × {self._total_cols} 列")
        self._total_pages_label.setText(f"{self._total_pages} 页")
        self._page_edit.setValidator(QIntValidator(1, self._total_pages))
        self._update_button_states()


class ElaParquetTable(ThemeWidget):
    """Parquet 表格视图，支持分页。

    继承自 ``ThemeWidget``，数据来源为 Parquet 文件，
    通过 ``polars`` 进行高效读取，按页展示。

    :param parquet_path: Parquet 文件路径。
    :type parquet_path: str
    :param page_size: 每页显示的记录数，默认 50。
    :type page_size: int
    :param parent: 父级 widget。
    :type parent: QWidget, optional

    :raises ImportError: 当 polars 未安装时。
    :raises FileNotFoundError: 当指定的 parquet 文件不存在时。
    """

    pageChanged = pyqtSignal(int, int)
    loadingFinished = pyqtSignal(int)

    def __init__(
        self,
        parquet_path: str,
        page_size: int = 50,
        parent: Optional[QWidget] = None,
    ) -> None:
        if pl is None:
            raise ImportError(
                "polars is required for ElaParquetTable. "
                "Please install it with: pip install polars"
            )

        if not Path(parquet_path).is_file():
            raise FileNotFoundError(f"Parquet file not found: {parquet_path}")

        super().__init__(parent)

        self._parquet_path = parquet_path
        self._page_size = page_size
        self._current_page = 1
        self._total_rows = 0
        self._column_stats_cache: dict[str, dict] = {}
        self._lf = pl.scan_parquet(parquet_path)
        self._total_rows = len(self._lf.collect())  # type: ignore

        self._setup_ui()

    def _setup_ui(self) -> None:
        self._table = ElaDataTable(self)
        self._info_bar = ElaInfoBarWidget(self)
        self._pager = ElaPagerWidget(
            total_rows=self._total_rows,
            total_cols=0,
            current_page=self._current_page,
            parent=self,
        )

        self._main_lay = self.create_lay("v", self)
        self._main_lay.addWidget(self._table, 1)
        self._main_lay.addWidget(self._info_bar, 0)
        self._main_lay.addWidget(self._pager, 0)

        self._pager.pageRequest.connect(self.goToPage)
        self._table.clicked.connect(self._on_cell_clicked)

        self._load_data()

    def _load_data(self) -> None:
        data = (
            self._lf.slice((self._current_page - 1) * self._page_size, self._page_size)
            .collect()
            .to_dict()
        )
        self._table.setTableData(data)

        total_cols = len(data)
        total_pages = max(
            1, (self._total_rows + self._page_size - 1) // self._page_size
        )
        self._pager.update_state(
            self._total_rows, total_cols, self._current_page, total_pages
        )

        self.loadingFinished.emit(self._total_rows)

    def _on_cell_clicked(self, index: QModelIndex) -> None:
        col_name = self._table.model().horizontalHeaderItem(index.column()).text()
        if not col_name:
            self._info_bar.clear_info()
            return

        col_index = index.column() + 1

        if col_name in self._column_stats_cache:
            stats = self._column_stats_cache[col_name]
        else:
            stats = self._compute_column_stats(col_name)
            if stats:
                self._column_stats_cache[col_name] = stats

        if stats:
            self._info_bar.update_info(
                col_name, col_index, stats["min"], stats["max"], stats["last"]
            )
        else:
            self._info_bar.clear_info()

    def _compute_column_stats(self, column_name: str) -> Optional[dict]:
        schema = self._lf.collect_schema()

        if column_name not in schema:
            return None

        dtype = schema[column_name]
        numeric_types = (
            pl.Int64,
            pl.Int32,
            pl.Int16,
            pl.Int8,
            pl.UInt64,
            pl.UInt32,
            pl.UInt16,
            pl.UInt8,
            pl.Float64,
            pl.Float32,
        )
        if not isinstance(dtype, numeric_types):
            return None

        col_data = self._lf.select(pl.col(column_name)).collect()

        return {
            "min": col_data[column_name].min(),
            "max": col_data[column_name].max(),
            "last": col_data.tail(1)[column_name][0],
        }

    def goToPage(self, page: int) -> None:
        if page < 1:
            page = 1
        total_pages = max(
            1, (self._total_rows + self._page_size - 1) // self._page_size
        )
        if page > total_pages:
            page = total_pages

        self._current_page = page
        self._load_data()
        self.pageChanged.emit(page, total_pages)

    def nextPage(self) -> None:
        self.goToPage(self._current_page + 1)

    def prevPage(self) -> None:
        self.goToPage(self._current_page - 1)

    def setPageSize(self, page_size: int) -> None:
        if page_size < 1:
            page_size = 1
        self._page_size = page_size
        self._current_page = 1
        self._load_data()

    def getTotalRows(self) -> int:
        return self._total_rows

    def getCurrentPage(self) -> int:
        return self._current_page

    def getPageSize(self) -> int:
        return self._page_size

    def getTotalPages(self) -> int:
        return max(1, (self._total_rows + self._page_size - 1) // self._page_size)

    def loadData(self, parquet_path: str) -> None:
        """加载新的 parquet 文件。

        :param parquet_path: Parquet 文件路径。
        :type parquet_path: str
        """
        if not Path(parquet_path).is_file():
            raise FileNotFoundError(f"Parquet file not found: {parquet_path}")
        self._parquet_path = parquet_path
        self._lf = pl.scan_parquet(parquet_path)
        self._total_rows = len(self._lf.collect())  # type: ignore
        self._current_page = 1
        self._column_stats_cache.clear()
        self._info_bar.clear_info()
        self._load_data()
