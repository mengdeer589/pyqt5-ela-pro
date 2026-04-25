"""
[pyqt5_ela_pro] 示例页面基类
"""

import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import ElaScrollArea, ElaText
from pyqt5_ela_pro import ElaThemeWidget

RESOURCE_PATH = os.path.join(os.path.dirname(__file__), "resource", "images")


def _res(filename):
    return os.path.join(RESOURCE_PATH, filename)


class ExamplePage(ElaThemeWidget):
    """示例页面基类，提供通用布局结构"""

    PAGE_TITLE = "[ela_ext] 示例页面"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setupUI()

    def _setupUI(self):
        self._scrollArea = ElaScrollArea(self)
        self._scrollArea.setWidgetResizable(True)
        self._scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        scrollWidget = ElaThemeWidget()
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

    def _createSectionHeader(self, title):
        section = ElaText(title, self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        return section

    def _addInfoText(self, text, parent_layout):
        info = ElaText(text, self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
