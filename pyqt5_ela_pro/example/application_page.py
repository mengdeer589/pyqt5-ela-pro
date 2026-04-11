"""
[ela_ext] 应用级组件演示页面 - PyQt5ElaWidgetTools
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import (
    ElaText,
    ElaAppBar,
    ElaStatusBar,
    ElaTheme,
    ElaEventBus,
)
from .base_page import ExamplePage


class ApplicationComponentsPage(ExamplePage):
    """ela 应用级组件演示页面"""

    PAGE_TITLE = "ela 应用级组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoAppBar(main_layout)
        self._demoStatusBar(main_layout)
        self._demoTheme(main_layout)
        self._demoEventBus(main_layout)

    def _demoAppBar(self, parent_layout):
        section = ElaText("01. ElaAppBar - 应用栏", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("应用栏组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        app_bar = ElaAppBar(self)
        app_bar.setFixedHeight(50)
        parent_layout.addWidget(app_bar)
        parent_layout.addSpacing(20)

    def _demoStatusBar(self, parent_layout):
        section = ElaText("02. ElaStatusBar - 状态栏", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("状态栏组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        status_bar = ElaStatusBar(self)
        parent_layout.addWidget(status_bar)
        parent_layout.addSpacing(20)

    def _demoTheme(self, parent_layout):
        section = ElaText("03. ElaTheme - 主题管理", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("主题管理组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        parent_layout.addSpacing(20)

    def _demoEventBus(self, parent_layout):
        section = ElaText("04. ElaEventBus - 事件总线", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("事件总线组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        parent_layout.addSpacing(20)
