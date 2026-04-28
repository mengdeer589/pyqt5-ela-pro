"""
[ela_ext] 滚动弹窗组件演示页面
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QCheckBox
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import ElaText, ElaPushButton
from pyqt5_ela_pro import ElaScrollableMenu
from .base_page import ExamplePage


class GraphicsComponentsPage(ExamplePage):
    """滚动弹窗组件演示页面"""

    PAGE_TITLE = "滚动弹窗"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoScrollableMenu(main_layout)

    def _addInfoText(self, text, parent_layout):
        info = ElaText(text, self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

    def _demoScrollableMenu(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("01. ela_ext - ElaScrollableMenu 可滚动菜单")
        )
        self._addInfoText(
            "基于 ElaMenu + ElaScrollArea，支持大量自定义 widget",
            parent_layout,
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        menu_btn = ElaPushButton("打开菜单", self)
        menu_btn.setFixedWidth(100)

        def _show_menu():
            menu = ElaScrollableMenu(menu_btn)
            for i in range(20):
                cb = QCheckBox(f"复选框 {i + 1}", menu.scrollWidget)
                cb.setChecked(i % 3 == 0)
                menu.addWidgetAction(cb)
            menu.scrollArea.setMinimumHeight(300)
            menu.scrollArea.setMaximumHeight(400)
            menu.popup(menu_btn.mapToGlobal(menu_btn.rect().bottomLeft()))

        menu_btn.clicked.connect(_show_menu)
        btn_layout.addWidget(menu_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)
