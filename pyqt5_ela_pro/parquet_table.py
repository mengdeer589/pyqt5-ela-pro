"""
Parquet 表格视图组件，支持分页功能。

基于 ``ElaDataTable`` 扩展，数据来源为 Parquet 文件，
通过 ``polars`` 进行高效读取，按页展示数据。
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union, TYPE_CHECKING

from PyQt5.QtCore import pyqtSignal, QModelIndex
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5ElaWidgetTools import (
    ElaText,
    eTheme,
    ElaThemeType,
)

from . import ElaThemeWidget
from .ela_pagination import ElaPagination
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


class ElaInfoBarWidget(ElaThemeWidget):
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
        self._col_label.setText("列: -")
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
        mode = self._theme_mode

        col_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicDetailsText)
        self._set_label_color(self._col_label, col_color)

        col_index_color = eTheme.getThemeColor(
            mode, ElaThemeType.ThemeColor.PrimaryNormal
        )
        self._set_label_color(self._col_index_label, col_index_color)

        min_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.PrimaryHover)
        self._set_label_color(self._min_label, min_color)

        max_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.StatusDanger)
        self._set_label_color(self._max_label, max_color)

        last_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.PrimaryPress)
        self._set_label_color(self._last_label, last_color)

    @staticmethod
    def _set_label_color(label, color):
        palette = label.palette()
        palette.setColor(QPalette.WindowText, color)
        label.setPalette(palette)

    def update_info(
        self, col_name: str, col_index: int, min_val: str, max_val: str, last_val: str
    ) -> None:
        """更新列信息显示。

        :param col_name: 列名
        :param col_index: 列索引
        :param min_val: 最小值
        :param max_val: 最大值
        :param last_val: 最后一行值
        """
        self._col_name = col_name
        self._col_index = col_index
        self._min_val = min_val
        self._max_val = max_val
        self._last_val = last_val

        self._col_label.setText(f"列: {col_name}")
        self._col_index_label.setText(f"第 {col_index} 列")
        self._min_label.setText(f"最小值: {min_val}")
        self._max_label.setText(f"最大值: {max_val}")
        self._last_label.setText(f"最后一行: {last_val}")

    def clear_info(self) -> None:
        """清空列信息显示。"""
        self._col_label.setText("列: -")
        self._col_index_label.setText("第 - 列")
        self._min_label.setText("最小值: -")
        self._max_label.setText("最大值: -")
        self._last_label.setText("最后一行: -")

    def _update_bg_color(self, mode: ElaThemeType.ThemeMode) -> None:
        super()._update_bg_color(mode)
        if hasattr(self, "_col_label"):
            self._apply_colors()


class ElaParquetTable(ElaThemeWidget):
    """Parquet 表格视图，支持分页。

    继承自 ``ElaThemeWidget``，数据来源为 Parquet 文件，
    通过 ``polars`` 进行高效读取，按页展示数据。

    :param parquet_path: Parquet 文件路径（可选，也可后续通过 ``loadData`` 传入）
        :param page_size: 每页记录数，默认 50，最大 5000
    :param parent: 父级 widget

    :raises ImportError: 当 polars 未安装时
    """

    pageChanged = pyqtSignal(int, int)
    loadingFinished = pyqtSignal(int)

    def __init__(
        self,
        parquet_path: Union[str, Path] = "",
        page_size: int = 50,
        parent: Optional[QWidget] = None,
    ) -> None:
        if pl is None:
            raise ImportError(
                "polars is required for ElaParquetTable. "
                "Please install it with: pip install polars"
            )

        super().__init__(parent)

        self._page_size = max(50, min(page_size, 5000))
        self._current_page = 1
        self._total_rows = 0
        self._parquet_path = ""
        self._lf = None
        self._column_stats_cache: dict[str, dict] = {}

        self._setup_ui()

        if parquet_path:
            self.loadData(parquet_path)

    def _setup_ui(self) -> None:
        self._table = ElaDataTable(self)
        self._info_bar = ElaInfoBarWidget(self)

        self._pager_container = QWidget(self)
        pager_layout = QHBoxLayout(self._pager_container)
        pager_layout.setContentsMargins(15, 0, 15, 0)
        pager_layout.setSpacing(12)

        self._total_label = ElaText(self)
        self._total_label.setTextPixelSize(13)
        self._total_label.setMinimumWidth(180)

        self._pagination = ElaPagination(self)
        self._pagination.setJumperVisible(True)
        self._pagination.currentPageChanged.connect(self.goToPage)

        pager_layout.addWidget(self._total_label)
        pager_layout.addStretch(1)
        pager_layout.addWidget(self._pagination)

        self._main_lay = self.createLayout("v", self)
        self._main_lay.addWidget(self._table, 1)
        self._main_lay.addWidget(self._info_bar, 0)
        self._main_lay.addWidget(self._pager_container, 0)

        self._info_bar.setVisible(False)
        self._pager_container.setVisible(False)

        self._table.clicked.connect(self._on_cell_clicked)

        self._loading = False

    def deleteLater(self) -> None:
        """断开信号并清理资源。"""
        try:
            self._table.clicked.disconnect(self._on_cell_clicked)
        except (TypeError, RuntimeError):
            pass
        super().deleteLater()

    def _load_data(self) -> None:
        if self._lf is None:
            return
        df = self._lf.slice(
            (self._current_page - 1) * self._page_size, self._page_size
        ).collect()
        headers = df.columns
        rows = df.rows()
        data = [headers] + [list(r) for r in rows]
        self._table.setTableData(data)

        total_cols = len(headers)
        total_pages = max(
            1, (self._total_rows + self._page_size - 1) // self._page_size
        )
        self._total_label.setText(f"共 {self._total_rows} 行 × {total_cols} 列")
        self._pagination.setTotalPages(total_pages)
        self._pagination.setCurrentPage(self._current_page)
        self._info_bar.setVisible(True)
        self._pager_container.setVisible(total_pages > 1)

        self.loadingFinished.emit(self._total_rows)

    def _on_cell_clicked(self, index: QModelIndex) -> None:
        if self._lf is None:
            return
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

        stats_df = self._lf.select(
            pl.col(column_name).min().alias("min"),
            pl.col(column_name).max().alias("max"),
            pl.col(column_name).last().alias("last"),
        ).collect()
        return {
            "min": stats_df["min"][0],
            "max": stats_df["max"][0],
            "last": stats_df["last"][0],
        }

    def goToPage(self, page: int) -> None:
        """跳转到指定页码。

        :param page: 目标页码（从 1 开始）
        """
        if self._lf is None:
            return
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
        """翻到下一页。"""
        self.goToPage(self._current_page + 1)

    def prevPage(self) -> None:
        """翻到上一页。"""
        self.goToPage(self._current_page - 1)

    def setPageSize(self, page_size: int) -> None:
        """设置每页记录数（会重置到第一页）。

        :param page_size: 每页记录数，范围 50~5000
        """
        page_size = max(50, min(page_size, 5000))
        if page_size == self._page_size:
            return
        self._page_size = page_size
        self._current_page = 1
        self._load_data()

    def totalRows(self) -> int:
        """获取总行数。

        :returns: 总行数
        """
        return self._total_rows

    def currentPage(self) -> int:
        """获取当前页码。

        :returns: 当前页码
        """
        return self._current_page

    def pageSize(self) -> int:
        """获取每页记录数。

        :returns: 每页记录数
        """
        return self._page_size

    def totalPages(self) -> int:
        """获取总页数。

        :returns: 总页数
        """
        return max(1, (self._total_rows + self._page_size - 1) // self._page_size)

    def loadData(self, parquet_path: Union[str, Path]) -> None:
        """加载新的 parquet 文件。

        :param parquet_path: Parquet 文件路径
        :raises FileNotFoundError: 当文件不存在时
        """
        parquet_path = str(parquet_path)
        if not Path(parquet_path).is_file():
            raise FileNotFoundError(f"Parquet file not found: {parquet_path}")
        self._parquet_path = parquet_path
        self._lf = pl.scan_parquet(parquet_path)
        self._total_rows = self._lf.select(pl.len()).collect().item()  # type: ignore
        self._current_page = 1
        self._column_stats_cache.clear()
        self._info_bar.clear_info()
        self._load_data()
