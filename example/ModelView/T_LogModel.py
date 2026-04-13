from PyQt5.QtCore import *


class T_LogModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._logList = []

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._logList)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> QVariant:
        if role == Qt.DisplayRole:
            return self._logList[index.row()]
        return QVariant()

    def setLogList(self, logList: list):
        self.beginResetModel()
        self._logList = logList
        self.endResetModel()

    def appendLogList(self, log: str):
        self.beginResetModel()
        self._logList.append(log)
        self.endResetModel()

    def getLogList(self) -> list:
        return self._logList
