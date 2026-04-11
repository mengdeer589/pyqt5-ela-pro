"""
[ela_ext] 导航组件演示页面 - PyQt5ElaWidgetTools
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import (
    ElaText,
    ElaNavigationBar,
    ElaBreadcrumbBar,
    ElaPivot,
    ElaTabBar,
    ElaTabWidget,
)
from .base_page import ExamplePage


class NavigationComponentsPage(ExamplePage):
    """ela 导航组件演示页面"""

    PAGE_TITLE = "ela 导航组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoBreadcrumbBar(main_layout)
        self._demoPivot(main_layout)
        self._demoTabBar(main_layout)
        self._demoTabWidget(main_layout)

    def _demoBreadcrumbBar(self, parent_layout):
        section = ElaText("01. ElaBreadcrumbBar - 面包屑导航", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("面包屑导航组件，支持点击切换", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        breadcrumb = ElaBreadcrumbBar(self)
        breadcrumb_list = [f"项目{i}" for i in range(1, 8)]
        breadcrumb.setBreadcrumbList(breadcrumb_list)
        parent_layout.addWidget(breadcrumb)
        parent_layout.addSpacing(20)

    def _demoPivot(self, parent_layout):
        section = ElaText("02. ElaPivot - Pivot标签", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("Pivot标签组件，适合切换视图", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        pivot = ElaPivot(self)
        pivot.setPivotSpacing(8)
        pivot.setMarkWidth(75)
        pivot.appendPivot("本地歌曲")
        pivot.appendPivot("下载歌曲")
        pivot.appendPivot("下载视频")
        pivot.appendPivot("正在下载")
        pivot.setCurrentIndex(0)
        parent_layout.addWidget(pivot)
        parent_layout.addSpacing(20)

    def _demoTabBar(self, parent_layout):
        section = ElaText("03. ElaTabBar - 标签栏", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("标签栏组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        tab_bar = ElaTabBar(self)
        tab_bar.addTab("标签1")
        tab_bar.addTab("标签2")
        tab_bar.addTab("标签3")
        parent_layout.addWidget(tab_bar)
        parent_layout.addSpacing(20)

    def _demoTabWidget(self, parent_layout):
        section = ElaText("04. ElaTabWidget - 标签页", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("标签页组件，包含多个页面", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        tab_widget = ElaTabWidget(self)
        tab_widget.setFixedHeight(200)
        tab_widget.setIsTabTransparent(True)

        page1 = ElaText("新标签页1", self)
        page1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_page = page1.font()
        font_page.setPixelSize(32)
        page1.setFont(font_page)

        page2 = ElaText("新标签页2", self)
        page2.setFont(font_page)
        page2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        page3 = ElaText("新标签页3", self)
        page3.setFont(font_page)
        page3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tab_widget.addTab(page1, "新标签页1")
        tab_widget.addTab(page2, "新标签页2")
        tab_widget.addTab(page3, "新标签页3")
        parent_layout.addWidget(tab_widget)
        parent_layout.addSpacing(20)
