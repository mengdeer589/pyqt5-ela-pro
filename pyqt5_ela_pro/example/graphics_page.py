"""
[pyqt5_ela_pro] 其他组件占位页面
"""

from PyQt5.QtWidgets import QVBoxLayout
from PyQt5ElaWidgetTools import ElaText
from .base_page import ExamplePage


class GraphicsComponentsPage(ExamplePage):
    """其他组件占位页面"""

    PAGE_TITLE = "其他组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        main_layout.addWidget(self._createSectionHeader("其他组件"))
        info = ElaText("此页面保留用于未来的组件演示。", self)
        info.setTextPixelSize(14)
        main_layout.addWidget(info)
