"""
[ela_ext] 布局组件演示页面
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QFrame
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt
from PyQt5ElaWidgetTools import (
    ElaText,
    ElaPushButton,
    ElaToolBar,
    ElaToolButton,
    ElaIconType,
    ElaImageCard,
)
from ela_ext import ElaFlowLayout
from .base_page import ExamplePage

import os

RESOURCE_PATH = os.path.join(os.path.dirname(__file__), "resource", "images")


def _res(filename):
    return os.path.join(RESOURCE_PATH, filename)


class LayoutComponentsPage(ExamplePage):
    """ela 布局组件演示页面"""

    PAGE_TITLE = "ela 布局组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoFlowLayout(main_layout)
        self._demoToolBar(main_layout)

    def _createSectionHeader(self, title):
        section = ElaText(title, self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        return section

    def _demoFlowLayout(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("01. ElaFlowLayout - 流式布局")
        )

        info = ElaText("组件自动换行排列，拖动窗口宽度可观察流式效果", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        container = QWidget(self)
        container.setFixedHeight(200)
        flow_layout = ElaFlowLayout()
        container.setLayout(flow_layout)

        for i in range(12):
            btn = ElaPushButton(f"按钮 {i + 1}", self)
            btn.setFixedWidth(80)
            flow_layout.addWidget(btn)

        parent_layout.addWidget(container)
        parent_layout.addSpacing(30)

    def _demoToolBar(self, parent_layout):
        parent_layout.addWidget(self._createSectionHeader("02. ElaToolBar - 工具栏"))

        info = ElaText("工具栏组件，可在工具栏中添加各种组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        self._demo_toolbar = ElaToolBar(self)

        for i in range(5):
            tool_btn = ElaToolButton(self)
            tool_btn.setText(f"工具{i + 1}")
            tool_btn.setToolButtonStyle(2)
            self._demo_toolbar.addWidget(tool_btn)

        self._demo_toolbar.addSeparator()

        for i in range(3):
            tool_btn = ElaToolButton(self)
            tool_btn.setText(f"操作{i + 1}")
            tool_btn.setToolButtonStyle(2)
            self._demo_toolbar.addWidget(tool_btn)

        parent_layout.addWidget(self._demo_toolbar)
        parent_layout.addSpacing(20)
