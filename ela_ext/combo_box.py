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
from PyQt5.QtGui import QGuiApplication, QPainter, QPen, QPaintEvent
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QBoxLayout
from PyQt5ElaWidgetTools import (
    ElaCheckBox,
    ElaLineEdit,
    ElaPushButton,
    ElaThemeColor,
    ElaThemeType,
    ElaWindow,
    eApp,
    eTheme,
    ElaComboBox,
)

from pypinyin import lazy_pinyin

from .scrollable_menu import ElaScrollableMenu


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


class ElaComboBoxBase(ElaPushButton):
    """带下拉菜单的按钮基类。

    封装了一个 ``ElaScrollableMenu`` 弹出菜单，支持在其中添加自定义组件。
    子类通过覆盖 ``_onCheckboxStateChanged`` 和 ``_updateDisplayText``
    来实现单选或多选逻辑。

    Attributes:
        searchThreshold: 显示搜索框的选项数量阈值，默认为 15。
        maxShowText: 多选模式下显示文本的最大数量，超出则截断，默认为 3。
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        searchThreshold: int = COMBO_BOX_SEARCH_THRESHOLD,
    ) -> None:
        """初始化带下拉菜单的组合框基类。

        :param parent: 父级 widget。
        :type parent: QWidget, optional
        :param searchThreshold: 当选项数量达到此阈值时显示拼音搜索框，默认为 15。
        :type searchThreshold: int
        """
        super().__init__(parent)  # type: ignore[arg-type]
        self._multiSelect: bool = False
        self._minWidth = COMBO_BOX_MIN_WIDTH
        self.setMinimumWidth(self._minWidth)
        self._selectedItem: str = ""
        self._searchThreshold = searchThreshold

        self._shadowBorderWidth = COMBO_BOX_SHADOW_BORDER_WIDTH
        self._pBorderRadius = COMBO_BOX_BORDER_RADIUS
        self.maxShowText: int = COMBO_BOX_MAX_SHOW_TEXT

        self._popupMenu: Optional[ElaScrollableMenu] = ElaScrollableMenu(self)
        self.clicked.connect(self.showMenu)
        self.checkboxes: list[ElaCheckBox] = []

        self._searchEdit = ElaLineEdit(self._popupMenu.scroll_widget)
        self._searchEdit.setPlaceholderText("搜索选项...")
        self._popupMenu.addWidgetAction(self._searchEdit)
        self._searchEdit.setVisible(False)
        self._searchEdit.textChanged.connect(self._searchText)

        self._allSelectBtn: Optional[ElaCheckBox] = None

    @property
    def searchThreshold(self) -> int:
        """显示搜索框的选项数量阈值。"""
        return self._searchThreshold

    @searchThreshold.setter
    def searchThreshold(self, value: int) -> None:
        """设置显示搜索框的选项数量阈值。"""
        self._searchThreshold = value

    @property
    def maxShowText(self) -> int:
        """多选模式下显示文本的最大数量。"""
        return self._maxShowText

    @maxShowText.setter
    def maxShowText(self, value: int) -> None:
        """设置多选模式下显示文本的最大数量。"""
        self._maxShowText = value
        self._updateDisplayText()

    def _searchText(self, text: str) -> None:
        """根据输入文本过滤所有选项，支持拼音首字母匹配。

        :param text: 用户在搜索框中输入的文本。
        :type text: str
        """
        text_lower = text.lower()
        for checkbox in self.checkboxes:
            cb_text = checkbox.text()
            pinyin_str = "".join(lazy_pinyin(cb_text)).lower()
            checkbox.setVisible(
                text_lower in pinyin_str or text_lower in cb_text.lower()
            )

    def paintEvent(self, a0: QPaintEvent) -> None:  # ty:ignore[invalid-method-override]
        """绘制自定义下拉按钮外观，包含阴影边框和下拉箭头。

        :param a0: 绘制事件。
        :type a0: QPaintEvent
        """
        current_theme = eTheme.getThemeMode()
        color = (
            self.getLightPressColor()
            if current_theme == ElaThemeType.ThemeMode.Dark
            else self.getDarkPressColor()
        )
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        eTheme.drawEffectShadow(
            painter, self.rect(), self._shadowBorderWidth, self._pBorderRadius
        )

        painter.save()
        foreground_rect = QRect(
            self._shadowBorderWidth,
            self._shadowBorderWidth,
            self.width() - 2 * self._shadowBorderWidth,
            self.height() - 2 * self._shadowBorderWidth,
        )
        painter.setPen(
            ElaThemeColor(current_theme, ElaThemeType.ThemeColor.BasicBorder)
        )
        if not self.isEnabled():
            brush_color = ElaThemeColor(
                current_theme, ElaThemeType.ThemeColor.BasicDisable
            )
        elif self.isDown():
            brush_color = ElaThemeColor(
                current_theme, ElaThemeType.ThemeColor.BasicPress
            )
        elif self.underMouse():
            brush_color = ElaThemeColor(
                current_theme, ElaThemeType.ThemeColor.BasicHover
            )
        else:
            brush_color = ElaThemeColor(
                current_theme, ElaThemeType.ThemeColor.BasicBase
            )
        painter.setBrush(brush_color)
        painter.drawRoundedRect(
            foreground_rect, self._pBorderRadius, self._pBorderRadius
        )
        if self.isDown():
            painter.setPen(
                ElaThemeColor(current_theme, ElaThemeType.ThemeColor.BasicBaseLine)
            )
            painter.drawLine(
                foreground_rect.x() + self._pBorderRadius,
                self.height() - self._shadowBorderWidth,
                foreground_rect.width(),
                self.height() - self._shadowBorderWidth,
            )
        if self.isEnabled():
            text_color = ElaThemeColor(current_theme, ElaThemeType.ThemeColor.BasicText)
        else:
            text_color = ElaThemeColor(
                current_theme, ElaThemeType.ThemeColor.BasicTextDisable
            )
        painter.setPen(text_color)
        foreground_rect = foreground_rect.adjusted(COMBO_BOX_TEXT_MARGIN, 0, 0, 0)
        painter.drawText(
            foreground_rect,
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
            | Qt.TextFlag.TextWordWrap,
            self.text(),
        )
        painter.restore()
        if not painter.isActive():
            return
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(QPen(color, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        arrow_right = self.width() - COMBO_BOX_ARROW_RIGHT_OFFSET
        arrow_center_y = self.height() // 2
        arrow_width = COMBO_BOX_ARROW_WIDTH
        arrow_height = COMBO_BOX_ARROW_HEIGHT

        left_x = arrow_right - arrow_width
        right_x = arrow_right
        top_y = arrow_center_y - arrow_height // 2
        bottom_y = arrow_center_y + arrow_height // 2

        painter.drawLine(left_x, top_y, arrow_right - arrow_width // 2, bottom_y)
        painter.drawLine(arrow_right - arrow_width // 2, bottom_y, right_x, top_y)

    def showMenu(self) -> None:
        """在按钮左下角弹出下拉菜单。"""
        if self.checkboxes:
            menu_pos = self.mapToGlobal(self.rect().bottomLeft())
            self._popupMenu.exec_(menu_pos)

    def addItem(self, text: str, isChecked: bool = False) -> ElaCheckBox:
        """添加一个选项到下拉列表。

        当选项数量达到阈值时自动显示搜索框（默认阈值 15）。
        当选项数量 >= 5 时自动显示全选按钮。

        :param text: 选项显示文本。
        :type text: str
        :param isChecked: 是否默认选中。
        :type isChecked: bool
        :return: 创建的 ``ElaCheckBox`` 实例。
        :rtype: ElaCheckBox
        """
        checkbox = ElaCheckBox(text, self._popupMenu.scroll_widget)
        checkbox.setChecked(isChecked)
        checkbox.setMinimumHeight(25)
        self._popupMenu.addWidgetAction(checkbox)
        self.checkboxes.append(checkbox)

        if self._allSelectBtn:
            if (
                len(self.checkboxes) >= COMBO_BOX_SELECT_ALL_THRESHOLD
                and self._allSelectBtn.isHidden()
            ):
                self._allSelectBtn.setVisible(True)

        if (
            len(self.checkboxes) >= self._searchThreshold
            and self._searchEdit.isHidden()
        ):
            self._searchEdit.setVisible(True)

        checkbox.stateChanged.connect(self._onCheckboxStateChanged)

        return checkbox

    def addItems(self, items: list[str]) -> None:
        """批量添加选项。先清空现有选项，再依次添加。

        :param items: 选项文本列表。
        :type items: list[str]
        """
        self.clear()
        for item in items:
            self.addItem(item)

    def _clearCheckboxes(self) -> None:
        """清空所有选项，复位状态。"""
        for checkbox in self.checkboxes:
            try:
                checkbox.stateChanged.disconnect(self._onCheckboxStateChanged)
            except TypeError:
                pass
            self._popupMenu.scroll_layout.removeWidget(checkbox)
            checkbox.deleteLater()
        self.checkboxes.clear()

    def _clearSearchEdit(self) -> None:
        """删除搜索框并断开相关信号。"""
        if self._searchEdit:
            try:
                self._searchEdit.textChanged.disconnect(self._searchText)
            except (TypeError, RuntimeError):
                pass
            self._searchEdit.deleteLater()
            self._searchEdit = None

    def _clearAllSelectButton(self) -> None:
        """删除全选按钮并断开相关信号。"""
        if self._allSelectBtn:
            try:
                self._allSelectBtn.stateChanged.disconnect(self._selectAll)
            except TypeError:
                pass
            self._popupMenu.scroll_layout.removeWidget(self._allSelectBtn)
            self._allSelectBtn.deleteLater()
            self._allSelectBtn = None

    def clear(self) -> None:
        """清空所有选项并重置选中状态。"""
        self._clearCheckboxes()
        self._selectedItem = ""
        self._updateDisplayText()

    def currentSelection(self) -> list[str]:
        """获取当前选中的选项文本列表。

        :return: 选中的文本列表，多选模式返回所有选中项，
            单选模式返回单个元素的列表（若未选中则返回空列表）。
        :rtype: list[str]
        """
        if self._multiSelect:
            return [cb.text() for cb in self.checkboxes if cb.isChecked()]
        else:
            return [self._selectedItem] if self._selectedItem else []

    def currentSelectionIndex(self) -> list[int]:
        """获取当前选中选项的索引列表。

        :return: 选中项的零基索引列表。
        :rtype: list[int]
        """
        if self._multiSelect:
            return [
                self.checkboxes.index(cb) for cb in self.checkboxes if cb.isChecked()
            ]
        else:
            if self._selectedItem:
                for i, cb in enumerate(self.checkboxes):
                    if cb.text() == self._selectedItem:
                        return [i]
            return []

    def setCurrentSelection(self, items: list[str]) -> None:
        """设置当前选中项。

        :param items: 要选中的文本列表。多选模式下会选中列表中的所有匹配项；
            单选模式下只保留最后一个匹配项。
        :type items: list[str]
        """
        if self._multiSelect:
            for checkbox in self.checkboxes:
                checkbox.setChecked(checkbox.text() in items)
        else:
            self._selectedItem = items[-1] if items else ""
            for checkbox in self.checkboxes:
                checkbox.setChecked(checkbox.text() == self._selectedItem)
        self._updateDisplayText()

    def _onCheckboxStateChanged(self, state: int) -> None:
        """复选框状态变化时的回调，由子类实现。

        :param state: Qt 复选框状态值（0 未选中，1 半选，2 全选）。
        :type state: int
        :raises NotImplementedError: 基类必须被子类覆盖。
        """
        raise NotImplementedError

    def deleteLater(self) -> None:
        """清理所有子组件，断开信号连接，调度自身删除。"""
        self._clearCheckboxes()
        self._clearSearchEdit()
        self._clearAllSelectButton()
        try:
            self.clicked.disconnect(self.showMenu)
        except (TypeError, RuntimeError):
            pass
        if self._popupMenu:
            self._popupMenu.deleteLater()
            self._popupMenu = None
        super().deleteLater()


class ElaMultiSelectComboBox(ElaComboBoxBase):
    """多选下拉框组件。

    支持多选、全选/取消全选、拼音搜索。当选中项超过 ``maxShowText``
    （默认 3）时，显示文本会被截断并加上省略号。

    Attributes:
        searchThreshold: 显示搜索框的选项数量阈值，默认为 15。
        maxShowText: 显示文本的最大数量，超出则截断，默认为 3。

    :param parent: 父级 widget。
    :type parent: QWidget, optional
    :param searchThreshold: 显示搜索框的选项数量阈值，默认为 15。
    :type searchThreshold: int

    Example::

        combo = ElaMultiSelectComboBox()
        combo.addItems(["Python", "Java", "C++"])
        combo.setCurrentSelection(["Python"])
        print(combo.currentSelection())  # ["Python"]
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        searchThreshold: int = COMBO_BOX_SEARCH_THRESHOLD,
    ) -> None:
        """初始化多选下拉框。

        :param parent: 父级 widget。
        :type parent: QWidget, optional
        :param searchThreshold: 显示搜索框的选项数量阈值，默认为 15。
        :type searchThreshold: int
        """
        super().__init__(parent, searchThreshold)
        self._multiSelect = True
        self._maxShowText = COMBO_BOX_MAX_SHOW_TEXT

        self._allSelectBtn = ElaCheckBox("全选", self._popupMenu.scroll_widget)
        self._allSelectBtn.setVisible(False)
        self._popupMenu.addWidgetAction(self._allSelectBtn)
        self._allSelectBtn.stateChanged.connect(self._selectAll)

        self._updateDisplayText()

    def _selectAll(self, status: int) -> None:
        """全选/取消全选逻辑。

        :param status: Qt 复选框状态值。
        :type status: int
        """
        for checkbox in self.checkboxes:
            checkbox.setChecked(status)
        if self._allSelectBtn:
            self._allSelectBtn.setText("取消全选" if status else "全选")
        self._updateDisplayText()

    def _updateDisplayText(self) -> None:
        """更新按钮显示文本，反映当前选中状态。"""
        current_selects = self.currentSelection()
        if not current_selects:
            self.setText("下拉选择...")
        elif len(current_selects) > self._maxShowText:
            self.setText(",".join(current_selects[: self._maxShowText]) + "...")
        else:
            self.setText(",".join(current_selects))

    def _onCheckboxStateChanged(self, state: int) -> None:
        """多选模式下，复选框状态变化仅触发显示文本更新。

        :param state: Qt 复选框状态值。
        :type state: int
        """
        self._updateDisplayText()

    def multiSelect(self) -> bool:
        """返回是否为多选模式。

        :return: 始终返回 ``True``。
        :rtype: bool
        """
        return True


class ElaSingleSelectComboBox(ElaComboBoxBase):
    """单选下拉框组件。

    每次只能选中一个选项。选中新选项时会自动取消其他选项的选中状态
    并关闭弹出菜单。

    :param parent: 父级 widget。
    :type parent: QWidget, optional
    :param searchThreshold: 显示搜索框的选项数量阈值，默认为 15。
    :type searchThreshold: int
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        searchThreshold: int = COMBO_BOX_SEARCH_THRESHOLD,
    ) -> None:
        """初始化单选下拉框。

        :param parent: 父级 widget。
        :type parent: QWidget, optional
        :param searchThreshold: 显示搜索框的选项数量阈值，默认为 15。
        :type searchThreshold: int
        """
        super().__init__(parent, searchThreshold)
        self._multiSelect = False
        self._updateDisplayText()

    def _updateDisplayText(self) -> None:
        """更新按钮显示文本。"""
        self.setText(self._selectedItem if self._selectedItem else "下拉选择...")

    def _onCheckboxStateChanged(self, state: int) -> None:
        """单选模式下，选中某个选项时会取消其他所有选项的选中状态。

        :param state: Qt 复选框状态值。
        :type state: int
        """
        is_checked = bool(state)
        if is_checked:
            sender = self.sender()
            if sender is not None and hasattr(sender, "text"):
                self._selectedItem = sender.text()  # ty:ignore[call-non-callable]
            for cb in self.checkboxes:
                if cb != sender:
                    try:
                        cb.blockSignals(True)
                        cb.setChecked(False)
                    finally:
                        cb.blockSignals(False)
            self._popupMenu.close()
        else:
            self._selectedItem = ""
        self._updateDisplayText()

    def multiSelect(self) -> bool:
        """返回是否为多选模式。

        :return: 始终返回 ``False``。
        :rtype: bool
        """
        return False


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


class ElaSearchableComboBox(ElaComboBox):
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
        search_layout.addWidget(self._searchEdit)

        if isinstance(layout, QBoxLayout):
            layout.insertWidget(0, self._searchWidget)

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


if __name__ == "__main__":
    QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    class MainWindow(QWidget):
        def __init__(self, parent: Optional[QWidget] = None):
            super().__init__(parent)
            self.lay = QVBoxLayout(self)

            self.multi_combox = ElaMultiSelectComboBox(self)
            self.multi_combox.addItems([f"项目{i}" for i in range(50)])
            self.lay.addWidget(self.multi_combox)

            self.single_combox = ElaSingleSelectComboBox(self)
            self.single_combox.addItems([f"单选项目{i}" for i in range(10)])
            self.lay.addWidget(self.single_combox)

            get_item_btn = ElaPushButton("获取选中项")
            get_item_btn.clicked.connect(
                lambda: print(
                    f"多选: {self.multi_combox.currentSelection()}\n"
                    f"单选: {self.single_combox.currentSelection()}"
                )
            )
            self.lay.addWidget(get_item_btn)

    app = QApplication(sys.argv)
    eApp.init()
    w = ElaWindow()
    w.addPageNode("11", MainWindow(w), "demo")
    w.resize(400, 300)
    w.show()
    app.exec()
