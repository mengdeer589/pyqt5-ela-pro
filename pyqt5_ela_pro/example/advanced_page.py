"""
[ela_ext] 高级组件演示页面 (占位)
"""

from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import ElaText
from .base_page import ExamplePage


class AdvancedComponentsPage(ExamplePage):
    """ela 高级组件演示页面 (占位)"""

    PAGE_TITLE = "ela 高级组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        section = ElaText("高级组件 (待实现)", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        main_layout.addWidget(section)

        info = ElaText(
            "01. ElaRoller - 滚轮组件\n"
            "02. ElaRollerPicker - 滚轮选择器\n"
            "03. ElaScrollPage - 滚动页面\n"
            "04. ElaScrollPageArea - 滚动页面区域",
            self,
        )
        info.setTextPixelSize(14)
        main_layout.addWidget(info)
