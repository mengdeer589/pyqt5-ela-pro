"""
[ela_ext] 菜单组件演示页面 - PyQt5ElaWidgetTools
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import (
    ElaText,
    ElaToolButton,
    ElaMenu,
    ElaMenuBar,
    ElaSuggestBox,
)
from .base_page import ExamplePage


class MenuComponentsPage(ExamplePage):
    """ela 菜单组件演示页面"""

    PAGE_TITLE = "ela 菜单组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoMenu(main_layout)
        self._demoMenuBar(main_layout)
        self._demoSuggestBox(main_layout)

    def _demoMenu(self, parent_layout):
        section = ElaText("01. ElaMenu - 菜单", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("点击按钮打开菜单", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        menu_btn = ElaToolButton(self)
        menu_btn.setText("菜单")
        menu_btn.setToolButtonStyle(2)

        menu = ElaMenu(self)
        menu.addAction("保存")
        menu.addAction("编辑")
        menu.addSeparator()
        menu.addAction("删除")
        menu.addSeparator()
        menu.addAction("关于")

        menu_btn.setMenu(menu)
        btn_layout.addWidget(menu_btn)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoMenuBar(self, parent_layout):
        section = ElaText("02. ElaMenuBar - 菜单栏", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("窗口菜单栏组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        menu_bar = ElaMenuBar(self)
        file_menu = menu_bar.addMenu("文件(&F)")
        file_menu.addAction("保存")
        file_menu.addAction("另存为")
        file_menu.addSeparator()
        file_menu.addAction("退出")

        edit_menu = menu_bar.addMenu("编辑(&E)")
        edit_menu.addAction("复制")
        edit_menu.addAction("粘贴")

        help_menu = menu_bar.addMenu("帮助(&H)")
        help_menu.addAction("关于")

        parent_layout.addWidget(menu_bar)
        parent_layout.addSpacing(20)

    def _demoSuggestBox(self, parent_layout):
        section = ElaText("03. ElaSuggestBox - 建议框", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("输入时显示建议列表", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        suggest_box = ElaSuggestBox(self)
        suggest_box.setFixedWidth(300)
        suggest_box.addSuggestion("Python")
        suggest_box.addSuggestion("JavaScript")
        suggest_box.addSuggestion("C++")
        suggest_box.addSuggestion("Java")
        suggest_box.addSuggestion("Go")
        suggest_box.addSuggestion("Rust")
        suggest_box.addSuggestion("TypeScript")
        parent_layout.addWidget(suggest_box)
        parent_layout.addSpacing(20)
