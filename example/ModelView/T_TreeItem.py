from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5ElaWidgetTools import *


class T_TreeItem(QObject):
    ChildrenItems = None

    def __init__(self, itemTitle: str, parent=None):
        super().__init__(parent)
        self._itemKey = QUuid.createUuid().toString(QUuid.WithoutBraces)
        self._itemTitle = itemTitle
        self._pParentItem = parent
        self._isChecked = False
        self._pChildrenItems = []

    def getItemKey(self) -> str:
        return self._itemKey

    def getItemTitle(self) -> str:
        return self._itemTitle

    def setIsChecked(self, isChecked: bool):
        self._isChecked = isChecked

    def getIsChecked(self) -> bool:
        return self._isChecked

    def getParentItem(self):
        return self._pParentItem

    def setChildChecked(self, isChecked: bool):
        if isChecked:
            for node in self._pChildrenItems:
                node.setIsChecked(isChecked)
                node.setChildChecked(isChecked)
        else:
            for node in self._pChildrenItems:
                node.setChildChecked(isChecked)
                node.setIsChecked(isChecked)

    def getChildCheckState(self) -> Qt.CheckState:
        isAllChecked = True
        isAnyChecked = False
        for node in self._pChildrenItems:
            if node.getIsChecked():
                isAnyChecked = True
            else:
                isAllChecked = False
            childState = node.getChildCheckState()
            if childState == Qt.CheckState.PartiallyChecked:
                isAllChecked = False
                isAnyChecked = True
                break
            elif childState == Qt.CheckState.Unchecked:
                isAllChecked = False

        if len(self._pChildrenItems) > 0:
            if isAllChecked:
                return Qt.CheckState.Checked
            if isAnyChecked:
                return Qt.CheckState.PartiallyChecked
            return Qt.CheckState.Unchecked
        return Qt.CheckState.Checked

    def appendChildItem(self, childItem):
        self._pChildrenItems.append(childItem)

    def getChildrenItems(self) -> list:
        return self._pChildrenItems

    def getIsHasChild(self) -> bool:
        return len(self._pChildrenItems) > 0

    def getRow(self) -> int:
        if self._pParentItem:
            return self._pParentItem.getChildrenItems().index(self)
        return 0


class T_TreeViewModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rootItem = T_TreeItem("root", self)
        self._itemsMap = {}
        for i in range(20):
            level1Item = T_TreeItem(f"Lv1--TreeItem{i + 1}", self._rootItem)
            for j in range(6):
                level2Item = T_TreeItem(f"Lv2--TreeItem{j + 1}", level1Item)
                for k in range(6):
                    level3Item = T_TreeItem(f"Lv3--TreeItem{k + 1}", level2Item)
                    for l in range(6):
                        level4Item = T_TreeItem(f"Lv4--TreeItem{l + 1}", level3Item)
                        level3Item.appendChildItem(level4Item)
                        self._itemsMap[level4Item.getItemKey()] = level4Item
                    level2Item.appendChildItem(level3Item)
                    self._itemsMap[level3Item.getItemKey()] = level3Item
                level1Item.appendChildItem(level2Item)
                self._itemsMap[level2Item.getItemKey()] = level2Item
            self._rootItem.appendChildItem(level1Item)
            self._itemsMap[level1Item.getItemKey()] = level1Item

    def parent(self, child: QModelIndex) -> QModelIndex:
        if not child.isValid():
            return QModelIndex()
        childItem = child.internalPointer()
        parentItem = childItem.getParentItem()
        if parentItem == self._rootItem:
            return QModelIndex()
        elif parentItem is None:
            return QModelIndex()
        return self.createIndex(parentItem.getRow(), 0, parentItem)

    def index(
        self, row: int, column: int, parent: QModelIndex = QModelIndex()
    ) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()
        childItem = None
        if len(parentItem.getChildrenItems()) > row:
            childItem = parentItem.getChildrenItems()[row]
        if childItem:
            return self.createIndex(row, column, childItem)
        return QModelIndex()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()
        return len(parentItem.getChildrenItems())

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> QVariant:
        if role == Qt.DisplayRole:
            return index.internalPointer().getItemTitle()
        elif role == Qt.DecorationRole:
            return QIcon()
        elif role == Qt.CheckStateRole:
            item = index.internalPointer()
            if item.getIsHasChild():
                return item.getChildCheckState()
            else:
                return (
                    Qt.CheckState.Checked
                    if item.getIsChecked()
                    else Qt.CheckState.Unchecked
                )
        return QVariant()

    def setData(
        self, index: QModelIndex, value: QVariant, role: int = Qt.EditRole
    ) -> bool:
        if role == Qt.CheckStateRole:
            item = index.internalPointer()
            item.setIsChecked(not item.getIsChecked())
            item.setChildChecked(item.getIsChecked())
            self.dataChanged.emit(QModelIndex(), QModelIndex(), [role])
            return True
        return super().setData(index, value, role)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = super().flags(index)
        flags |= Qt.ItemFlag.ItemIsUserCheckable
        return flags

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ) -> QVariant:
        if orientation == Qt.Orientation.Horizontal and role == Qt.DisplayRole:
            return "ElaTreeView-Example-4Level"
        return super().headerData(section, orientation, role)

    def getItemCount(self) -> int:
        return len(self._itemsMap)
