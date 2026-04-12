"""
ComboBox 组件模块。

提供三种下拉框组件：

- ``ElaMultiSelectComboBox``：支持多选、带拼音搜索的复选框下拉框
- ``ElaSingleSelectComboBox``：单选下拉框
- ``ElaSearchableComboBox``：基于 ``ElaComboBox`` 的可搜索下拉框

所有组件均支持主题适配，自动跟随应用程序的亮/暗主题切换样式。
"""

from __future__ import annotations

import sys
from typing import Any, Optional

from PyQt5.QtCore import QRect, Qt, QSortFilterProxyModel, QStringListModel, QModelIndex
from PyQt5.QtGui import QGuiApplication, QPainter, QPen, QPaintEvent, QPalette, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QBoxLayout
from PyQt5ElaWidgetTools import (
    ElaThemeColor,
    ElaThemeType,
    ElaWindow,
    eApp,
    eTheme,
    ElaComboBox,
    ElaMultiSelectComboBox,
)

from pypinyin import lazy_pinyin


COMBO_BOX_SHADOW_BORDER_WIDTH: int = 3
COMBO_BOX_BORDER_RADIUS: int = 3
COMBO_BOX_MIN_WIDTH: int = 150
COMBO_BOX_SEARCH_THRESHOLD: int = 15
COMBO_BOX_SELECT_ALL_THRESHOLD: int = 5
COMBO_BOX_MAX_SHOW_TEXT: int = 3
COMBO_BOX_ARROW_RIGHT_OFFSET: int = 15
COMBO_BOX_ARROW_WIDTH: int = 10
COMBO_BOX_ARROW_HEIGHT: int = 6
COMBO_BOX_TEXT_MARGIN: int = 5


class ElaSearchProxyModel(QSortFilterProxyModel):
    """支持拼音首字母过滤的代理模型。

    过滤时同时匹配汉字原文和对应的拼音首字母字符串。
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """初始化拼音过滤代理模型。

        :param parent: 父级对象。
        :type parent: QWidget, optional
        """
        super().__init__(parent)
        self._keyword: str = ""

    def setKeyword(self, keyword: str) -> None:
        """设置过滤关键词。

        :param keyword: 要过滤的拼音或汉字关键词。
        :type keyword: str
        """
        self._keyword = keyword.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """判断某一行是否应显示在代理模型中。

        :param source_row: 源模型中的行索引。
        :type source_row: int
        :param source_parent: 父索引。
        :type source_parent: QModelIndex
        :return: 如果该行应显示则返回 ``True``。
        :rtype: bool
        """
        if not self._keyword:
            return True
        src_model = self.sourceModel()
        if src_model is None:
            return False
        index = src_model.index(source_row, 0, source_parent)
        text = index.data()
        if text is None:
            return False
        pinyin_str = "".join(lazy_pinyin(text)).lower()
        return self._keyword in text.lower() or self._keyword in pinyin_str


class ElaSearchMultiBox(ElaMultiSelectComboBox):
    """可搜索多选下拉框。

    基于 ``ElaMultiSelectComboBox`` 扩展，在弹出列表顶部增加了一个搜索框，
    支持汉字原文和拼音首字母过滤。

    :param parent: 父级 widget。
    :type parent: QWidget, optional
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """初始化可搜索多选下拉框。

        :param parent: 父级 widget。
        :type parent: QWidget, optional
        """
        super().__init__(parent)
        self._searchEdit: Optional[QLineEdit] = None
        self._searchWidget: Optional[QWidget] = None
        self._currentSelection: list[str] = []
        self._isRestoringSelection = False

    def addItem(self, text: str) -> None:
        """添加一个选项。

        :param text: 选项文本。
        :type text: str
        """
        super().addItem(text)

    def addItems(self, texts: list[str]) -> None:
        """批量添加选项。

        :param texts: 选项文本列表。
        :type texts: list[str]
        """
        super().addItems(texts)

    def clear(self) -> None:
        """清空所有选项。"""
        super().clear()
        self._currentSelection = []

    def setCurrentSelection(self, selection: list) -> None:
        """设置当前选中项。

        :param selection: 要选中的文本列表。
        :type selection: list
        """
        if isinstance(selection, str):
            selection = [selection]
        self._currentSelection = list(selection)
        super().setCurrentSelection(self._currentSelection)

    def getCurrentSelection(self) -> list[str]:
        """获取当前选中项文本列表。

        :return: 选中的文本列表。
        :rtype: list[str]
        """
        return list(self._currentSelection)

    def showPopup(self) -> None:
        """显示下拉弹窗，在弹窗顶部插入搜索框。"""
        self._isRestoringSelection = True
        self._restoreSelection()
        super().showPopup()
        self._isRestoringSelection = False

        container = self.findChild(QWidget, "ElaComboBoxContainer")
        if container is None:
            return

        self._cleanupSearchWidget()
        self._setupSearchInPopup(container)

    def _restoreSelection(self) -> None:
        """恢复之前的选中状态。"""
        if self._currentSelection:
            super().setCurrentSelection(self._currentSelection)

    def _setupSearchInPopup(self, container: QWidget) -> None:
        """在弹窗中创建搜索框组件。

        :param container: 弹窗容器 widget。
        :type container: QWidget
        """
        layout = container.layout()
        if layout is None:
            return

        self._searchWidget = QWidget()
        self._searchWidget.setObjectName("SearchWidget")
        self._searchWidget.setFixedHeight(40)

        search_layout = QVBoxLayout(self._searchWidget)
        search_layout.setContentsMargins(6, 6, 6, 2)
        search_layout.setSpacing(0)

        self._searchEdit = QLineEdit()
        self._searchEdit.setPlaceholderText("搜索...")
        self._searchEdit.setFixedHeight(28)
        self._searchEdit.textChanged.connect(self._onSearchTextChanged)
        self._applySearchEditPalette()
        search_layout.addWidget(self._searchEdit)

        if isinstance(layout, QBoxLayout):
            layout.insertWidget(0, self._searchWidget)

    def _applySearchEditPalette(self) -> None:
        """应用主题颜色到搜索框。"""
        theme_mode = eTheme.getThemeMode()
        palette = self._searchEdit.palette()
        palette.setColor(QPalette.Text, eTheme.getThemeColor(theme_mode, 13))
        palette.setColor(
            QPalette.PlaceholderText,
            QColor(0, 0, 0, 128) if theme_mode == 0 else QColor(186, 186, 186),
        )
        self._searchEdit.setPalette(palette)

    def _onSearchTextChanged(self, text: str) -> None:
        """搜索框文本变化时过滤项目。

        :param text: 输入的搜索文本。
        :type text: str
        """
        if self._isRestoringSelection:
            return

        text_lower = text.lower()
        view = self.view()
        if view is None:
            return

        for i in range(self.count()):
            item_text = self.itemText(i)
            pinyin_str = "".join(lazy_pinyin(item_text)).lower()
            visible = (
                not text_lower
                or text_lower in item_text.lower()
                or text_lower in pinyin_str
            )
            view.setRowHidden(i, not visible)

        if text_lower and self._currentSelection:
            first_match_idx = -1
            for i in range(self.count()):
                if not view.isRowHidden(i):
                    first_match_idx = i
                    break
            if first_match_idx >= 0:
                index = self.model().index(first_match_idx, 0)
                view.scrollTo(index)

    def _cleanupSearchWidget(self) -> None:
        """删除搜索框组件。"""
        if self._searchWidget:
            self._searchWidget.deleteLater()
            self._searchWidget = None
            self._searchEdit = None

    def hidePopup(self) -> None:
        """关闭弹窗时保存选中状态。"""
        self._currentSelection = super().getCurrentSelection()
        view = self.view()
        if view:
            for i in range(self.count()):
                view.setRowHidden(i, False)
        super().hidePopup()

    def deleteLater(self) -> None:
        """清理搜索框，断开信号，调度自身删除。"""
        self._cleanupSearchWidget()
        super().deleteLater()


class ElaSearchBox(ElaComboBox):
    """可搜索下拉框。

    基于标准 ``ElaComboBox`` 扩展，在弹出列表顶部增加了一个搜索框，
    支持汉字原文和拼音首字母过滤。
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """初始化可搜索下拉框。

        :param parent: 父级 widget。
        :type parent: QWidget, optional
        """
        super().__init__(parent)  # type: ignore[arg-type]
        self._allItems: list[tuple[str, Any]] = []
        self._sourceModel = QStringListModel()
        self._proxyModel = ElaSearchProxyModel(self)
        self._proxyModel.setSourceModel(self._sourceModel)
        self.setModel(self._proxyModel)

        self._searchEdit: Optional[QLineEdit] = None
        self._searchWidget: Optional[QWidget] = None

        self.activated.connect(self._onActivated)

    def addItem(self, text: str, userData: Any = None) -> None:  # type: ignore[override]
        """添加一个选项。

        :param text: 选项文本。
        :type text: str
        :param userData: 关联的用户数据。
        :type userData: Any
        """
        self._allItems.append((text, userData))
        self._sourceModel.setStringList([item[0] for item in self._allItems])

    def addItems(self, texts: list[str]) -> None:  # type: ignore[override]
        """批量添加选项。

        :param texts: 选项文本列表。
        :type texts: list[str]
        """
        for text in texts:
            self._allItems.append((text, None))
        self._sourceModel.setStringList([item[0] for item in self._allItems])

    def clear(self) -> None:
        """清空所有选项并重置选择状态。"""
        self._allItems.clear()
        self._sourceModel.setStringList([])
        self.setCurrentIndex(-1)

    def _cleanupSearchWidget(self) -> None:
        """删除搜索框组件。"""
        if self._searchWidget:
            self._searchWidget.deleteLater()
            self._searchWidget = None
            self._searchEdit = None

    def showPopup(self) -> None:
        """显示下拉弹窗，在弹窗顶部插入搜索框。"""
        self._proxyModel.setKeyword("")
        super().showPopup()

        container = self.findChild(QWidget, "ElaComboBoxContainer")
        if container is None:
            return

        if self._searchWidget is None:
            self._setupSearchInPopup(container)
        else:
            if self._searchWidget.parent() is not None:
                self._searchWidget.setParent(None)
            layout = container.layout()
            if layout is not None and isinstance(layout, QBoxLayout):
                layout.insertWidget(0, self._searchWidget)
            if self._searchEdit:
                self._applySearchEditPalette()
                self._searchEdit.blockSignals(True)
                self._searchEdit.clear()
                self._searchEdit.blockSignals(False)
                self._searchEdit.setFocus()

    def _setupSearchInPopup(self, container: QWidget) -> None:
        """在弹窗中创建搜索框组件。

        :param container: 弹窗容器 widget。
        :type container: QWidget
        """
        layout = container.layout()
        if layout is None:
            return

        self._searchWidget = QWidget()
        self._searchWidget.setObjectName("SearchWidget")
        self._searchWidget.setFixedHeight(40)

        search_layout = QVBoxLayout(self._searchWidget)
        search_layout.setContentsMargins(6, 6, 6, 2)
        search_layout.setSpacing(0)

        self._searchEdit = QLineEdit()
        self._searchEdit.setPlaceholderText("搜索...")
        self._searchEdit.setFixedHeight(28)
        self._searchEdit.textChanged.connect(self._onSearchTextChanged)
        self._applySearchEditPalette()
        search_layout.addWidget(self._searchEdit)

        if isinstance(layout, QBoxLayout):
            layout.insertWidget(0, self._searchWidget)

    def _applySearchEditPalette(self) -> None:
        """应用主题颜色到搜索框。"""
        theme_mode = eTheme.getThemeMode()
        palette = self._searchEdit.palette()
        palette.setColor(QPalette.Text, eTheme.getThemeColor(theme_mode, 13))
        palette.setColor(
            QPalette.PlaceholderText,
            QColor(0, 0, 0, 128) if theme_mode == 0 else QColor(186, 186, 186),
        )
        self._searchEdit.setPalette(palette)

    def _onSearchTextChanged(self, text: str) -> None:
        """搜索框文本变化时更新过滤关键词。

        :param text: 输入的搜索文本。
        :type text: str
        """
        self._proxyModel.setKeyword(text)

    def _onActivated(self, row: int) -> None:
        """选项激活回调，设置当前选中文本。

        :param row: 代理模型中的行索引。
        :type row: int
        """
        proxy_index = self._proxyModel.index(row, 0)
        source_index = self._proxyModel.mapToSource(proxy_index)
        real_row = source_index.row()
        if 0 <= real_row < len(self._allItems):
            text = self._allItems[real_row][0]
            self.setCurrentText(text)

    def hidePopup(self) -> None:
        """关闭弹窗时清理搜索框。"""
        self._cleanupSearchWidget()
        super().hidePopup()

    def deleteLater(self) -> None:
        """清理搜索框，断开信号，调度自身删除。"""
        self._cleanupSearchWidget()
        try:
            self.activated.disconnect(self._onActivated)
        except (TypeError, RuntimeError):
            pass
        super().deleteLater()
