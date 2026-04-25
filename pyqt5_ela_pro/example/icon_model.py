from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant
from PyQt5ElaWidgetTools import ElaIconType


class T_IconModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._iconKeys = [attr for attr in dir(ElaIconType) if not attr.startswith("_")]
        self._rowCount = len(self._iconKeys)
        self._pIsSearchMode = False
        self._searchKeyList = []

    def rowCount(self, parent=QModelIndex()) -> int:
        return self._rowCount

    def setSearchKeyList(self, searchKeyList: list):
        self.beginResetModel()
        self._searchKeyList = searchKeyList
        if self._pIsSearchMode:
            self._rowCount = len(self.getSearchKeyList())
        else:
            self._rowCount = len(self._iconKeys)
        self.endResetModel()

    def getSearchKeyList(self) -> list:
        return self._searchKeyList

    def setIsSearchMode(self, isSearchMode: bool):
        self._pIsSearchMode = isSearchMode

    def getIsSearchMode(self) -> bool:
        return self._pIsSearchMode

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> QVariant:
        if role == Qt.UserRole:
            if not self._pIsSearchMode:
                if index.row() >= len(self._iconKeys):
                    return QVariant()
                key = self._iconKeys[index.row()]
                try:
                    iconEnum = getattr(ElaIconType, key)
                    return QVariant([key, chr(iconEnum)])
                except:
                    return QVariant()
            else:
                if index.row() >= len(self._searchKeyList):
                    return QVariant()
                iconName = self._searchKeyList[index.row()]
                try:
                    iconEnum = getattr(ElaIconType, iconName)
                    return QVariant([iconName, chr(iconEnum)])
                except:
                    return QVariant()
        return QVariant()

    def getIconNameFromModelIndex(self, index: QModelIndex) -> str:
        if self._pIsSearchMode:
            if index.row() < len(self._searchKeyList):
                return f"ElaIconType.IconName.{self._searchKeyList[index.row()]}"
        else:
            if index.row() < len(self._iconKeys):
                return f"ElaIconType.IconName.{self._iconKeys[index.row()]}"
        return ""
