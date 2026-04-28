"""
增强型表格视图组件，支持异步数据加载和丰富的单元格样式配置。

提供 ``ElaDataTable``，即 ``ElaTableView`` 的高级封装：

- 同步和异步方式填充表格数据
- 支持按列索引或表头名称设置列宽
- 丰富的单元格样式配置（文本、字体、前景/背景色、图标、提示等）
- 自定义行背景色（通过自定义代理实现）
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Callable, Optional, Union
import weakref

from PyQt5.QtCore import Qt, QModelIndex, QThread, pyqtSignal
from PyQt5.QtGui import (
    QIcon,
    QStandardItem,
    QFont,
    QColor,
    QStandardItemModel,
    QPainter,
)
from PyQt5.QtWidgets import (
    QWidget,
    QHeaderView,
    QAbstractItemView,
    QStyledItemDelegate,
    QStyleOptionViewItem,
)
from PyQt5ElaWidgetTools import ElaTableView


TABLE_MIN_SECTION_SIZE: int = 60
TABLE_ROW_MIN_HEIGHT: int = 46
TABLE_THREAD_QUIT_TIMEOUT: int = 1000


class ElaRowColorDelegate(QStyledItemDelegate):
    """为指定行绘制自定义背景色的代理。

    颜色存储在以行索引为键的内部字典中。
    不在字典中的行使用默认绘制行为。

    :param parent: 父级 widget，通常为 ``ElaDataTable`` 实例。
    :type parent: QWidget, optional
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """初始化行颜色代理。

        :param parent: 父级 widget，通常为 ``ElaDataTable`` 实例。
        :type parent: QWidget, optional
        """
        super().__init__(parent)
        self._row_colors: dict[int, QColor] = {}

    def setRowColor(self, row: int, color: QColor) -> None:
        """设置指定行的背景色。

        :param row: 零基行索引。
        :type row: int
        :param color: 要应用的背景色。
        :type color: QColor
        """
        self._row_colors[row] = color

    def clearAllColors(self) -> None:
        """清除所有已存储的行颜色。"""
        self._row_colors.clear()

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> None:  # ty:ignore[invalid-method-override]
        """绘制单元格，在设置了行颜色时填充背景。

        :param painter: 绘图工具。
        :type painter: QPainter
        :param option: 单元格样式选项。
        :type option: QStyleOptionViewItem
        :param index: 单元格对应的模型索引。
        :type index: QModelIndex
        """
        if index.row() in self._row_colors:
            painter.save()
            color = self._row_colors[index.row()]
            painter.fillRect(option.rect, color)
            painter.restore()
        super().paint(painter, option, index)


class _LoadThread(QThread):
    """在后台线程中加载表格数据的线程。

    加载完成时发射 ``finished`` 信号并附带行数据列表。
    在线程结束前调用 :py:meth:`cancel` 可抑制信号发射。

    :param rows: 行数据列表（每行是一个单元格值列表）。
    :type rows: list
    """

    finished = pyqtSignal(list)

    def __init__(self, rows: list) -> None:
        super().__init__()
        self._rows = rows
        self._isCanceled = False

    def cancel(self) -> None:
        """将线程标记为已取消。``finished`` 信号将不会被发射。"""
        self._isCanceled = True

    def run(self) -> None:
        """执行加载操作。若未取消则发射 ``finished`` 信号。"""
        if not self._isCanceled:
            self.finished.emit(list(self._rows))
        self._isCanceled = False


class ElaDataTable(ElaTableView):
    """增强型表格视图，提供数据加载和样式配置工具。

    封装 ``ElaTableView`` 和 ``QStandardItemModel``，提供以下功能：

    - 同步或异步方式设置表格数据
    - 按列索引或表头名称管理列宽
    - 丰富的单元格样式配置（文本、字体、颜色、图标、提示等）
    - 自定义行背景色
    - 插入和删除行
    - 表头点击排序（默认关闭，需调用 ``setSortingEnabled(True)`` 开启）

    :param parent: 父级 widget，为 ``None`` 时表示顶级窗口。
    :type parent: QWidget, optional

    Example::

        table = ElaDataTable()
        table.setTableData(data)
        table.setSortingEnabled(True)  # 开启排序
        table.sortChanged.connect(lambda col, order: print(f"按列 {col} 排序"))
    """

    sortChanged = pyqtSignal(int, Qt.SortOrder)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """初始化增强型表格视图。

        配置交替行颜色、选择行为、列宽策略和自定义行背景代理。

        :param parent: 父级 widget，为 ``None`` 时表示顶级窗口。
        :type parent: QWidget, optional
        """
        super().__init__(parent)  # type: ignore[arg-type]
        self._model = QStandardItemModel(self)
        self.setModel(self._model)

        self.setAlternatingRowColors(True)
        vh = self.verticalHeader()
        if vh:
            vh.setHidden(True)
        hh = self.horizontalHeader()
        if hh:
            hh.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            hh.setMinimumSectionSize(TABLE_MIN_SECTION_SIZE)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        if vh:
            vh.setMinimumSectionSize(TABLE_ROW_MIN_HEIGHT)

        self._columnWidths: dict[int | str, int] = {}
        self._columnAlignments: dict[int, Qt.AlignmentFlag] = {}
        self._row_color_delegate = ElaRowColorDelegate(self)
        self.setItemDelegate(self._row_color_delegate)

        self.tableViewShow.connect(self._applyColumnWidths)

        self._load_thread: Optional[_LoadThread] = None
        self._isLoadThreadConnected: bool = False

        self._sorting_enabled = False
        self._current_sort_column = -1
        self._current_sort_order = Qt.AscendingOrder
        hh.sectionClicked.connect(self._onHeaderClicked)

    def _applyColumnWidths(self) -> None:
        """将缓存的所有列宽应用到视图中。"""
        for col, width in self._columnWidths.items():
            self.setColumnWidth(col, width)

    def _onHeaderClicked(self, logicalIndex: int) -> None:
        """处理表头点击排序。

        :param logicalIndex: 点击的列索引
        :type logicalIndex: int
        """
        if not self._sorting_enabled:
            return
        if self._current_sort_column == logicalIndex:
            self._current_sort_order = (
                Qt.DescendingOrder
                if self._current_sort_order == Qt.AscendingOrder
                else Qt.AscendingOrder
            )
        else:
            self._current_sort_column = logicalIndex
            self._current_sort_order = Qt.AscendingOrder
        self._sortByColumn(logicalIndex, self._current_sort_order)
        self.horizontalHeader().setSortIndicator(logicalIndex, self._current_sort_order)
        self.sortChanged.emit(logicalIndex, self._current_sort_order)

    def _sortByColumn(self, column: int, order: Qt.SortOrder) -> None:
        """对指定列排序，支持中文拼音排序和数字排序。

        :param column: 列索引
        :type column: int
        :param order: 排序顺序
        :type order: Qt.SortOrder
        """
        col_type = self._getColumnType(column)
        if col_type == "numeric":
            self._sortNumeric(column, order)
        elif col_type == "chinese":
            self._sortByPinyin(column, order)
        else:
            self._model.sort(column, order)

    def _getColumnType(self, column: int) -> str:
        """判断列的类型：数字、中文、字符串。

        :param column: 列索引
        :type column: int
        :return: 列类型：numeric, chinese, 或 string
        :rtype: str
        """
        numeric_count = 0
        chinese_count = 0
        sample_size = min(20, self._model.rowCount())

        for row in range(sample_size):
            item = self._model.item(row, column)
            if item:
                text = item.text().strip()
                if text:
                    if self._isNumeric(text):
                        numeric_count += 1
                    elif self._containsChinese(text):
                        chinese_count += 1

        if numeric_count == sample_size and sample_size > 0:
            return "numeric"
        if chinese_count > 0:
            return "chinese"
        return "string"

    def _isNumeric(self, text: str) -> bool:
        """判断文本是否为数字。

        :param text: 文本
        :type text: str
        :return: 是否为数字
        :rtype: bool
        """
        try:
            float(text.replace(",", "").replace(" ", ""))
            return True
        except ValueError:
            return False

    def _containsChinese(self, text: str) -> bool:
        """判断文本是否包含中文。

        :param text: 文本
        :type text: str
        :return: 是否包含中文
        :rtype: bool
        """
        return any("\u4e00" <= char <= "\u9fff" for char in text)

    def _sortByPinyin(self, column: int, order: Qt.SortOrder) -> None:
        """使用拼音对列进行排序。

        :param column: 列索引
        :type column: int
        :param order: 排序顺序
        :type order: Qt.SortOrder
        """
        from pypinyin import lazy_pinyin

        row_count = self._model.rowCount()
        if row_count == 0:
            return

        items_with_pinyin = []
        for row in range(row_count):
            item = self._model.item(row, column)
            text = item.text() if item else ""
            pinyin = "".join(lazy_pinyin(text))
            items_with_pinyin.append((pinyin, row, text))

        reverse = order == Qt.DescendingOrder
        items_with_pinyin.sort(key=lambda x: x[0], reverse=reverse)

        self._reorderRows(column, [row for _, row, _ in items_with_pinyin])

    def _sortNumeric(self, column: int, order: Qt.SortOrder) -> None:
        """对数字列进行排序。

        :param column: 列索引
        :type column: int
        :param order: 排序顺序
        :type order: Qt.SortOrder
        """
        row_count = self._model.rowCount()
        if row_count == 0:
            return

        items_with_value = []
        for row in range(row_count):
            item = self._model.item(row, column)
            text = item.text() if item else "0"
            try:
                value = float(text.replace(",", "").replace(" ", ""))
            except ValueError:
                value = 0
            items_with_value.append((value, row))

        reverse = order == Qt.DescendingOrder
        items_with_value.sort(key=lambda x: x[0], reverse=reverse)

        self._reorderRows(column, [row for _, row in items_with_value])

    def _reorderRows(self, column: int, row_order: list[int]) -> None:
        """根据排序后的顺序重新排列行。

        使用 takeRow/appendRow 就地移动 QStandardItem，避免序列化再重建。

        :param column: 排序列索引（保留参数，未使用）
        :param row_order: 按目标顺序排列的行索引列表
        """
        row_count = self._model.rowCount()
        if row_count <= 1:
            return

        rows = []
        while self._model.rowCount() > 0:
            rows.append(self._model.takeRow(0))

        for original_row in row_order:
            self._model.appendRow(rows[original_row])

    def setSortingEnabled(self, enabled: bool) -> None:
        """开启或关闭表头点击排序功能。

        :param enabled: 是否开启排序，``True`` 开启，``False`` 关闭
        :type enabled: bool
        """
        self._sorting_enabled = enabled
        self.horizontalHeader().setSortIndicatorShown(enabled)
        if not enabled:
            self.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
            self._current_sort_column = -1

    def isSortingEnabled(self) -> bool:
        """返回排序功能是否已开启。

        :return: 排序功能是否开启
        :rtype: bool
        """
        return self._sorting_enabled

    def setColumnAlignment(self, column: int, alignment: Qt.AlignmentFlag) -> None:
        """设置指定列的文本对齐方式。

        设置后，该列所有单元格将使用指定的对齐方式（水平+垂直居中）。
        默认情况下，所有列水平和垂直居中对齐。

        :param column: 列索引（零基）
        :type column: int
        :param alignment: 水平对齐方式，请使用 ``Qt.AlignLeft``、``Qt.AlignCenter``、``Qt.AlignRight``
        :type alignment: Qt.AlignmentFlag
        """
        full_alignment = alignment | Qt.AlignVCenter
        self._columnAlignments[column] = full_alignment
        for row in range(self._model.rowCount()):
            item = self._model.item(row, column)
            if item:
                item.setTextAlignment(full_alignment)

    def setRowCount(self, rows: int) -> None:
        """设置底层模型的行数。

        :param rows: 行数。
        :type rows: int
        """
        self._model.setRowCount(rows)

    def setColumnCount(self, cols: int) -> None:
        """设置底层模型的列数。

        :param cols: 列数。
        :type cols: int
        """
        self._model.setColumnCount(cols)

    def setColumnWidth(self, column: int, width: int) -> None:
        """设置指定列的宽度并缓存，以备后续重新应用。

        :param column: 零基列索引。
        :type column: int
        :param width: 宽度值（像素）。
        :type width: int
        """
        self._columnWidths[column] = width
        super().setColumnWidth(column, width)

    def setColumnWidths(self, widths: dict[int | str, int]) -> None:
        """批量设置多个列的宽度。

        键可以是整数列索引，也可以是字符串表头名称。
        对于字符串键，方法会在所有列中搜索匹配的表头。

        :param widths: 列索引（int）或表头名称（str）到宽度（像素）的映射。
        :type widths: dict[int | str, int]
        """
        self._columnWidths.update(widths)
        for key, width in widths.items():
            if isinstance(key, int):
                super().setColumnWidth(key, width)
            else:
                for col in range(self.columnCount()):
                    header_item = self._model.horizontalHeaderItem(col)
                    if header_item and header_item.text() == key:
                        super().setColumnWidth(col, width)
                        break

    def setTableData(
        self,
        data: list[list[Any]] | dict[str, Iterable[Any]],
        center_columns: Optional[set[int]] = None,
        show_row_index: bool = False,
    ) -> None:
        """同步填充表格数据。

        *data* 支持两种格式：

        - **列表格式**: 第一个元素为表头字符串列表，其余为行数据列表。
        - **字典格式**: 键为列名，值为该列的可迭代对象。所有值列表长度应一致。

        默认情况下，所有列居中对齐。可通过 ``setColumnAlignment()`` 设置指定列的对齐方式。

        :param data: 表头+行数据列表，或列名到列数据可迭代对象的字典。
        :type data: list[list[Any]] or dict[str, Iterable[Any]]
        :param center_columns: 已废弃，请使用 ``setColumnAlignment()`` 设置对齐方式。
        :type center_columns: set[int], optional
        :param show_row_index: 若为 ``True``，在垂直表头中显示行号。
        :type show_row_index: bool
        """
        if not data:
            return

        if isinstance(data, dict):
            headers = list(data.keys())
            col_count = len(headers)
            if col_count == 0:
                return
            col_values = [list(data[h]) for h in headers]
            row_count = len(col_values[0])
            rows = [
                [col_values[col_idx][row_idx] for col_idx in range(col_count)]
                for row_idx in range(row_count)
            ]
        else:
            headers = data[0]
            rows = data[1:]

        self._model.blockSignals(True)

        self.setHorizontalHeaderLabels(headers)
        self.setColumnCount(len(headers))
        self.setRowCount(len(rows))

        if show_row_index:
            vh = self.verticalHeader()
            if vh:
                vh.setHidden(False)
            self.setVerticalHeaderLabels([str(i + 1) for i in range(len(rows))])

        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_data in enumerate(row_data):
                item = QStandardItem(str(cell_data))
                if center_columns and col_idx in center_columns:
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                elif col_idx in self._columnAlignments:
                    item.setTextAlignment(self._columnAlignments[col_idx])
                else:
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self._model.setItem(row_idx, col_idx, item)

        self._model.blockSignals(False)
        self._model.layoutChanged.emit()

    def setTableDataAsync(
        self,
        data: list[list[Any]],
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """在后台线程中异步填充表格数据。

        表头立即设置，行数据在后台线程中加载并应用。
        如果在之前的加载仍在运行时再次调用此方法，
        旧线程会被取消并替换。

        :param data: 第一个元素为表头字符串列表，其余为行数据列表。
        :type data: list[list[Any]]
        :param callback: 数据应用完成后调用的可选无参 callable。
            以弱引用方式存储以避免阻止垃圾回收。
        :type callback: Callable[[], None], optional
        """
        if not data:
            return

        if self._load_thread is not None:
            self._load_thread.cancel()
            if self._load_thread.isRunning():
                self._load_thread.quit()
                self._load_thread.wait(TABLE_THREAD_QUIT_TIMEOUT)
            if self._isLoadThreadConnected:
                try:
                    self._load_thread.finished.disconnect()
                except TypeError:
                    pass
                self._isLoadThreadConnected = False
            self._load_thread.deleteLater()
            self._load_thread = None

        headers = data[0]
        rows = data[1:]
        self.setHorizontalHeaderLabels(headers)
        self.setColumnCount(len(headers))

        callback_ref = weakref.ref(callback) if callable(callback) else None

        def on_finished(rows_data: list[list[Any]]) -> None:
            if self._load_thread is None or self._load_thread._isCanceled:
                return
            self._model.blockSignals(True)
            try:
                self.setRowCount(len(rows_data))
                for row_idx, row_data in enumerate(rows_data):
                    for col_idx, cell_data in enumerate(row_data):
                        item = QStandardItem(str(cell_data))
                        if col_idx in self._columnAlignments:
                            item.setTextAlignment(self._columnAlignments[col_idx])
                        else:
                            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self._model.setItem(row_idx, col_idx, item)
            finally:
                self._model.blockSignals(False)
            self._model.layoutChanged.emit()
            if callback_ref:
                cb = callback_ref()
                if cb is not None:
                    cb()

        self._load_thread = _LoadThread(rows)
        self._load_thread.finished.connect(on_finished)
        self._isLoadThreadConnected = True
        self._load_thread.start()

    def setHorizontalHeaderLabels(self, labels: list[str]) -> None:
        """设置水平表头标签。

        :param labels: 表头字符串列表。
        :type labels: list[str]
        """
        self._model.setHorizontalHeaderLabels(labels)

    def setVerticalHeaderLabels(self, labels: list[str]) -> None:
        """设置垂直表头标签。

        :param labels: 标签字符串列表。
        :type labels: list[str]
        """
        self._model.setVerticalHeaderLabels(labels)

    def setItem(
        self, row: int, col: int, item: Union[QStandardItem, Any], center: bool = False
    ) -> None:
        """在指定行和列处设置单元格项。

        :param row: 零基行索引。
        :type row: int
        :param col: 零基列索引。
        :type col: int
        :param item: ``QStandardItem`` 实例，或会被转换为字符串
            并包装为 ``QStandardItem`` 的任意值。
        :type item: QStandardItem or Any
        :param center: 若为 ``True``，文本居中对齐。
        :type center: bool
        """
        if not isinstance(item, QStandardItem):
            item = QStandardItem(str(item))
        if center:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self._model.setItem(row, col, item)

    def item(self, row: int, col: int) -> Optional[QStandardItem]:
        """获取指定行和列处的 ``QStandardItem``。

        :param row: 零基行索引。
        :type row: int
        :param col: 零基列索引。
        :type col: int
        :return: 指定位置的 item，若不存在则返回 ``None``。
        :rtype: QStandardItem or None
        """
        return self._model.item(row, col)

    def setCellWidget(self, row: int, col: int, widget: QWidget) -> None:
        """在指定单元格中嵌入一个 widget。

        :param row: 零基行索引。
        :type row: int
        :param col: 零基列索引。
        :type col: int
        :param widget: 要嵌入单元格的 widget。
        :type widget: QWidget
        """
        index = self._model.index(row, col)
        self.setIndexWidget(index, widget)

    def cellWidget(self, row: int, col: int) -> Optional[QWidget]:
        """获取嵌入在指定单元格中的 widget。

        :param row: 零基行索引。
        :type row: int
        :param col: 零基列索引。
        :type col: int
        :return: 单元格中的 widget，若无则返回 ``None``。
        :rtype: QWidget or None
        """
        index = self._model.index(row, col)
        return self.indexWidget(index)

    def setItemText(self, row: int, col: int, text: str) -> None:
        """设置单元格的文本。

        :param row: 零基行索引。
        :type row: int
        :param col: 零基列索引。
        :type col: int
        :param text: 显示文本。
        :type text: str
        """
        self.setItem(row, col, QStandardItem(text))

    def setItemAlignment(self, row: int, col: int, alignment: Qt.AlignmentFlag) -> None:
        """设置单元格的文本对齐方式。

        :param row: 零基行索引。
        :type row: int
        :param col: 零基列索引。
        :type col: int
        :param alignment: 对齐标志（如 ``Qt.AlignmentFlag.AlignCenter``）。
        :type alignment: Qt.AlignmentFlag
        """
        item = self.item(row, col)
        if item:
            item.setTextAlignment(alignment)

    def setItemFont(self, row: int, col: int, font: QFont) -> None:
        """设置单元格的字体。

        :param row: 零基行索引。
        :type row: int
        :param col: 零基列索引。
        :type col: int
        :param font: 要应用的字体。
        :type font: QFont
        """
        item = self.item(row, col)
        if item:
            item.setFont(font)

    def setItemForeground(self, row: int, col: int, color: QColor) -> None:
        """设置单元格的前景色（文字颜色）。

        :param row: 零基行索引。
        :type row: int
        :param col: 零基列索引。
        :type col: int
        :param color: 文字颜色。
        :type color: QColor
        """
        item = self.item(row, col)
        if item:
            item.setForeground(color)

    def setItemBackground(self, row: int, col: int, color: QColor) -> None:
        """设置单元格的背景色。

        :param row: 零基行索引。
        :type row: int
        :param col: 零基列索引。
        :type col: int
        :param color: 背景色。
        :type color: QColor
        """
        item = self.item(row, col)
        if item:
            item.setBackground(color)

    def setItemIcon(self, row: int, col: int, icon: QIcon) -> None:
        """设置单元格的图标。

        :param row: 零基行索引。
        :type row: int
        :param col: 零基列索引。
        :type col: int
        :param icon: 要显示的图标。
        :type icon: QIcon
        """
        item = self.item(row, col)
        if item:
            item.setIcon(icon)

    def setItemToolTip(self, row: int, col: int, toolTip: str) -> None:
        """设置单元格的提示文本。

        :param row: 零基行索引。
        :type row: int
        :param col: 零基列索引。
        :type col: int
        :param toolTip: 提示文本。
        :type toolTip: str
        """
        item = self.item(row, col)
        if item:
            item.setToolTip(toolTip)

    def setItemCheckable(self, row: int, col: int, checkable: bool) -> None:
        """设置单元格是否可勾选（显示复选框）。

        :param row: 零基行索引。
        :type row: int
        :param col: 零基列索引。
        :type col: int
        :param checkable: 单元格是否可勾选。
        :type checkable: bool
        """
        item = self.item(row, col)
        if item:
            item.setCheckable(checkable)

    def setItemEditable(self, row: int, col: int, editable: bool) -> None:
        """设置单元格是否可编辑。

        :param row: 零基行索引。
        :type row: int
        :param col: 零基列索引。
        :type col: int
        :param editable: 单元格是否可编辑。
        :type editable: bool
        """
        item = self.item(row, col)
        if item:
            flags = item.flags()
            if editable:
                flags |= Qt.ItemFlag.ItemIsEditable
            else:
                flags &= ~Qt.ItemFlag.ItemIsEditable
            item.setFlags(flags)

    def insertRow(self, row: int, items: Optional[list[Any]] = None) -> None:
        """在指定位置插入一个新行。

        :param row: 插入位置。
        :type row: int
        :param items: 新行的单元格值列表。设为 ``None`` 时插入空行。
        :type items: list, optional
        """
        if items is None:
            self._model.insertRow(row)
        else:
            self._model.insertRow(row, [QStandardItem(str(item)) for item in items])

    def removeRow(self, row: int) -> None:
        """移除指定位置的行。

        :param row: 要移除的零基行索引。
        :type row: int
        """
        self._model.removeRow(row)

    def clear(self) -> None:
        """清空所有数据，包括表头。"""
        self._model.clear()

    def clearContents(self) -> None:
        """移除所有数据行，保留表头。"""
        self._model.removeRows(0, self._model.rowCount())

    def rowCount(self) -> int:
        """返回模型中的行数。

        :return: 行数。
        :rtype: int
        """
        return self._model.rowCount()

    def columnCount(self) -> int:
        """返回模型中的列数。

        :return: 列数。
        :rtype: int
        """
        return self._model.columnCount()

    def model(self) -> QStandardItemModel:
        """返回底层的 ``QStandardItemModel``。

        :return: 模型实例。
        :rtype: QStandardItemModel
        """
        return self._model

    def setRowBackground(self, row: int, color: QColor) -> None:
        """设置整行的背景色。

        通过自定义代理绘制行背景。颜色会应用到该行所有单元格。

        :param row: 零基行索引。
        :type row: int
        :param color: 背景色。
        :type color: QColor
        """
        self._row_color_delegate.setRowColor(row, color)
        vp = self.viewport()
        if vp:
            vp.update()

    def clearRowBackgrounds(self) -> None:
        """移除所有自定义行背景色。"""
        self._row_color_delegate.clearAllColors()
        vp = self.viewport()
        if vp:
            vp.update()

    def deleteLater(self) -> None:
        """清理加载线程，断开信号连接，调度自身删除。"""
        if self._load_thread is not None:
            self._load_thread.cancel()
            if self._load_thread.isRunning():
                self._load_thread.quit()
                self._load_thread.wait(TABLE_THREAD_QUIT_TIMEOUT)
            if self._isLoadThreadConnected:
                try:
                    self._load_thread.finished.disconnect()
                except (TypeError, RuntimeError):
                    pass
                self._isLoadThreadConnected = False
            self._load_thread.deleteLater()
            self._load_thread = None
        try:
            self.tableViewShow.disconnect(self._applyColumnWidths)
        except (TypeError, RuntimeError):
            pass
        hh = self.horizontalHeader()
        if hh:
            try:
                hh.sectionClicked.disconnect(self._onHeaderClicked)
            except (TypeError, RuntimeError):
                pass
        super().deleteLater()

    def columnName(self, column: int) -> Optional[str]:
        """根据列索引获取表头文本。

        :param column: 零基列索引。
        :type column: int
        :return: 表头文本，若列不存在则返回 ``None``。
        :rtype: str or None
        """
        header_item = self._model.horizontalHeaderItem(column)
        return header_item.text() if header_item else None
