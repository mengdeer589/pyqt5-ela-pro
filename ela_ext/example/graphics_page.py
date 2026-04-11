"""
[ela_ext] 图形组件演示页面 (占位)
"""

from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import ElaText
from .base_page import ExamplePage


class GraphicsComponentsPage(ExamplePage):
    """ela 图形组件演示页面 (占位)"""

    PAGE_TITLE = "ela 图形组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        section = ElaText("图形组件 (待实现)", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        main_layout.addWidget(section)

        info = ElaText(
            "01. ElaGraphicsScene - 图形场景\n"
            "02. ElaGraphicsView - 图形视图\n"
            "03. ElaGraphicsItem - 图形项\n"
            "04. ElaGraphicsLineItem - 线条图形项",
            self,
        )
        info.setTextPixelSize(14)
        main_layout.addWidget(info)
