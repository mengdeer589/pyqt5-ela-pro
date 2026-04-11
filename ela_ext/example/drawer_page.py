"""
[ela_ext] 抽屉组件演示页面
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import ElaText, ElaPushButton
from ela_ext import (
    ElaSideDrawer,
    ElaDrawerPosition,
    ThemeWidget,
    ElaPrimaryButton,
)
from .base_page import ExamplePage


class DrawerComponentsPage(ExamplePage):
    """抽屉/导航组件演示页面"""

    PAGE_TITLE = "[ela_ext] 抽屉组件"

    def __init__(self, parent=None):
        self._drawers = {}
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoSiSideDrawer(main_layout)

    def _demoSiSideDrawer(self, parent_layout):
        section = ElaText("01. ElaSideDrawer - 四方向抽屉", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText(
            "SiliconUI 风格抽屉，支持上下左右四个方向滑入",
            self,
        )
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        for name, pos, size in [
            ("左侧抽屉", ElaDrawerPosition.Left, 300),
            ("右侧抽屉", ElaDrawerPosition.Right, 380),
            ("顶部抽屉", ElaDrawerPosition.Top, 200),
            ("底部抽屉", ElaDrawerPosition.Bottom, 200),
        ]:
            drawer = ElaSideDrawer(self, position=pos, drawer_size=size)
            content = ThemeWidget()
            content_layout = QVBoxLayout(content)
            content_layout.setContentsMargins(16, 16, 16, 16)
            content_layout.setSpacing(12)

            title = ElaText(name, content)
            title.setTextPixelSize(18)
            title.setFont(QFont("微软雅黑", 18, QFont.Bold))
            content_layout.addWidget(title)

            desc = ElaText(f"这是一个{name}，可以放置设置项、表单等内容。", content)
            desc.setTextPixelSize(14)
            content_layout.addWidget(desc)

            content_layout.addStretch()

            close_btn = ElaPrimaryButton(content)
            close_btn.setText("关闭抽屉")
            close_btn.setFixedWidth(120)
            close_btn.clicked.connect(drawer.closeDrawer)
            content_layout.addWidget(close_btn)

            drawer.setContentWidget(content)
            self._drawers[name] = drawer

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        for name, drawer in self._drawers.items():
            btn = ElaPushButton(name, self)
            btn.setFixedWidth(100)
            btn.clicked.connect(drawer.showDrawer)
            btn_layout.addWidget(btn)

        btn_layout.addStretch()

        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)
