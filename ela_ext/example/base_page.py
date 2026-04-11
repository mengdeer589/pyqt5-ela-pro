"""
[ela_ext] 示例页面基类
"""

from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PyQt5ElaWidgetTools import ElaScrollArea
from ela_ext import ThemeWidget


class ExamplePage(ThemeWidget):
    """示例页面基类，提供通用布局结构"""

    PAGE_TITLE = "[ela_ext] 示例页面"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setupUI()

    def _setupUI(self):
        self._scrollArea = ElaScrollArea(self)
        self._scrollArea.setWidgetResizable(True)

        scrollWidget = ThemeWidget()
        mainLayout = QVBoxLayout(scrollWidget)
        mainLayout.setContentsMargins(20, 20, 20, 20)
        mainLayout.setSpacing(15)

        self._addDemoContent(mainLayout)

        mainLayout.addStretch()

        self._scrollArea.setWidget(scrollWidget)

        containerLayout = QVBoxLayout(self)
        containerLayout.setContentsMargins(0, 0, 0, 0)
        containerLayout.addWidget(self._scrollArea)

    def _addDemoContent(self, main_layout):
        raise NotImplementedError("子类必须实现 _addDemoContent 方法")
