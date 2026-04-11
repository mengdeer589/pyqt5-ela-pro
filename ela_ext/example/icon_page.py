"""
[ela_ext] 图标组件演示页面
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QListView
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import (
    ElaText,
    ElaIconButton,
    ElaIconType,
    ElaListView,
    ElaLineEdit,
    ElaMessageBar,
    ElaMessageBarType,
)
from .base_page import ExamplePage
from .icon_model import T_IconModel
from .icon_delegate import T_IconDelegate


class IconBrowserPage(ExamplePage):
    """ela 图标组件演示页面"""

    PAGE_TITLE = "ela 图标组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoIconBrowser(main_layout)
        self._demoIconButtons(main_layout)

    def _demoIconBrowser(self, parent_layout):
        section = ElaText("01. 图标浏览器 - 所有可用图标", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("一堆常用图标被放置于此，左键单击以复制其枚举", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        self._iconKeys = [attr for attr in dir(ElaIconType) if not attr.startswith("_")]

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

        parent_layout.addWidget(self._searchEdit)
        parent_layout.addWidget(self._iconView)
        parent_layout.addSpacing(30)

    def _onIconClicked(self, index: QModelIndex):
        iconName = self._iconModel.getIconNameFromModelIndex(index)
        if not iconName:
            return
        from PyQt5.QtWidgets import QApplication

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

    def _demoIconButtons(self, parent_layout):
        section = ElaText("02. 图标按钮 - 带图标的按钮", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("图标按钮组件演示", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        icon_btn1 = ElaIconButton(ElaIconType.IconName.FloppyDisk, 16, self)
        icon_btn1.setFixedSize(40, 40)
        btn_layout.addWidget(icon_btn1)

        icon_btn2 = ElaIconButton(ElaIconType.IconName.Pencil, 16, self)
        icon_btn2.setFixedSize(40, 40)
        btn_layout.addWidget(icon_btn2)

        icon_btn3 = ElaIconButton(ElaIconType.IconName.Trash, 16, self)
        icon_btn3.setFixedSize(40, 40)
        btn_layout.addWidget(icon_btn3)

        icon_btn4 = ElaIconButton(ElaIconType.IconName.MagnifyingGlass, 16, self)
        icon_btn4.setFixedSize(40, 40)
        btn_layout.addWidget(icon_btn4)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
