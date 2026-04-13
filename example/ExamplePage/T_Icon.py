from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5ElaWidgetTools import *
from ExamplePage.T_BasePage import *
from ModelView.T_IconModel import T_IconModel
from ModelView.T_IconDelegate import T_IconDelegate


class T_Icon(T_BasePage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("ElaIcon")
        self.createCustomWidget("一堆常用图标被放置于此，左键单击以复制其枚举")

        # 使用dir获取所有图标名称（排除内部属性）
        self._iconKeys = [attr for attr in dir(ElaIconType) if not attr.startswith("_")]

        centralWidget = QWidget(self)
        centerVLayout = QVBoxLayout(centralWidget)
        centerVLayout.setContentsMargins(0, 0, 5, 0)
        centralWidget.setWindowTitle("ElaIcon")

        self._iconView = ElaListView(self)
        self._iconView.setIsTransparent(True)
        self._iconView.setFlow(QListView.Flow.LeftToRight)
        self._iconView.setViewMode(QListView.ViewMode.IconMode)
        self._iconView.setResizeMode(QListView.ResizeMode.Adjust)
        self._iconView.clicked.connect(self._onIconClicked)
        self._iconModel = T_IconModel(self)
        self._iconDelegate = T_IconDelegate(self)
        self._iconView.setModel(self._iconModel)
        self._iconView.setItemDelegate(self._iconDelegate)
        self._iconView.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self._searchEdit = ElaLineEdit(self)
        self._searchEdit.setPlaceholderText("搜索图标")
        self._searchEdit.setFixedSize(300, 35)
        self._searchEdit.textEdited.connect(self._onSearchEditTextEdit)
        self._searchEdit.focusIn.connect(self._onSearchEditTextEdit)

        centerVLayout.addSpacing(13)
        centerVLayout.addWidget(self._searchEdit)
        centerVLayout.addWidget(self._iconView)
        self.addCentralWidget(centralWidget, True, True, 0)

    def _onIconClicked(self, index: QModelIndex):
        iconName = self._iconModel.getIconNameFromModelIndex(index)
        if not iconName:
            return
        QApplication.clipboard().setText(iconName)
        ElaMessageBar.success(
            ElaMessageBarType.PositionPolicy.Top,
            "复制完成",
            f"{iconName}已被复制到剪贴板",
            1000,
            self,
        )

    def _onSearchEditTextEdit(self, searchText: str):
        if not searchText:
            self._iconModel.setIsSearchMode(False)
            self._iconModel.setSearchKeyList([])
            self._iconView.clearSelection()
            self._iconView.viewport().update()
            return

        searchKeyList = []
        for key in self._iconKeys:
            if key.lower().__contains__(searchText.lower()):
                searchKeyList.append(key)

        self._iconModel.setIsSearchMode(True)
        self._iconModel.setSearchKeyList(searchKeyList)
        self._iconView.clearSelection()
        self._iconView.scrollTo(self._iconModel.index(0, 0))
        self._iconView.viewport().update()
