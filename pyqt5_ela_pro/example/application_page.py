"""
[pyqt5_ela_pro] 应用级组件演示页面 — PyQt5ElaWidgetTools 原生
"""

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QApplication
from PyQt5ElaWidgetTools import (
    ElaText,
    ElaAppBar,
    ElaStatusBar,
    ElaPushButton,
)
from .base_page import ExamplePage


class ApplicationComponentsPage(ExamplePage):
    """ela 应用级组件演示页面"""

    PAGE_TITLE = "应用组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoAppBar(main_layout)
        self._demoStatusBar(main_layout)

    def _demoAppBar(self, parent_layout):
        parent_layout.addLayout(self._createHeaderRow("01. ElaAppBar - 应用栏", self._demoAppBar))
        self._addInfoText("应用栏组件", parent_layout)
        app_bar = ElaAppBar(self)
        app_bar.setFixedHeight(50)
        parent_layout.addWidget(app_bar)
        parent_layout.addSpacing(20)

    def _demoStatusBar(self, parent_layout):
        parent_layout.addLayout(self._createHeaderRow("02. ElaStatusBar - 状态栏", self._demoStatusBar))
        self._addInfoText("状态栏组件", parent_layout)
        status_bar = ElaStatusBar(self)
        parent_layout.addWidget(status_bar)
        parent_layout.addSpacing(20)
