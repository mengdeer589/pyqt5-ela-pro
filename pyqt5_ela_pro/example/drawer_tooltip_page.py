"""
[pyqt5_ela_pro] 抽屉与提示组件页面

合并了以下来源的组件:
- pyqt5_ela_pro: 抽屉、提示组件
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import ElaText, ElaPushButton
from pyqt5_ela_pro import (
    ElaDrawer,
    ElaDrawerPosition,
    ThemeWidget,
    ElaPrimaryBtn,
    ElaToolTipPosition,
    set_tooltip,
    StateToolTip,
)
from .base_page import ExamplePage


class DrawerTooltipPage(ExamplePage):
    """抽屉与提示组件页面"""

    PAGE_TITLE = "抽屉与提示"

    def __init__(self, parent=None):
        self._drawers = {}
        self._stateTooltip = None
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoDrawer(main_layout)
        self._demoTooltip(main_layout)
        self._demoStateTooltip(main_layout)

    def _addInfoText(self, text, parent_layout):
        info = ElaText(text, self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

    def _demoDrawer(self, parent_layout):
        parent_layout.addWidget(self._createSectionHeader("=== ela_ext - 抽屉组件 ==="))
        self._demoSiSideDrawer(parent_layout)

    def _demoTooltip(self, parent_layout):
        parent_layout.addWidget(self._createSectionHeader("=== ela_ext - 提示组件 ==="))
        self._demoToolTip(parent_layout)

    def _demoSiSideDrawer(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("01. ela_ext - ElaDrawer 四方向抽屉")
        )
        self._addInfoText("SiliconUI 风格抽屉，支持上下左右四个方向滑入", parent_layout)
        default_font_family = QFont().defaultFamily()
        for name, pos, size in [
            ("左侧抽屉", ElaDrawerPosition.Left, 300),
            ("右侧抽屉", ElaDrawerPosition.Right, 380),
            ("顶部抽屉", ElaDrawerPosition.Top, 200),
            ("底部抽屉", ElaDrawerPosition.Bottom, 200),
        ]:
            drawer = ElaDrawer(self, position=pos, drawer_size=size)
            content = ThemeWidget()
            content_layout = QVBoxLayout(content)
            content_layout.setContentsMargins(16, 16, 16, 16)
            content_layout.setSpacing(12)
            title = ElaText(name, content)
            title.setTextPixelSize(18)
            title.setFont(QFont(default_font_family, 18, QFont.Bold))
            content_layout.addWidget(title)
            desc = ElaText(f"这是一个{name}，可以放置设置项、表单等内容。", content)
            desc.setTextPixelSize(14)
            content_layout.addWidget(desc)
            content_layout.addStretch()
            close_btn = ElaPrimaryBtn(content)
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

    def _demoToolTip(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("02. ela_ext - ToolTip 工具提示")
        )
        self._addInfoText("鼠标悬停在按钮上查看提示", parent_layout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn1 = ElaPushButton("保存", self)
        btn1.setFixedWidth(100)
        set_tooltip(btn1, "保存当前内容", position=ElaToolTipPosition.BOTTOM)
        btn_layout.addWidget(btn1)
        btn2 = ElaPushButton("删除", self)
        btn2.setFixedWidth(100)
        set_tooltip(
            btn2, "删除选中项目\n（此操作不可撤销）", position=ElaToolTipPosition.RIGHT
        )
        btn_layout.addWidget(btn2)
        btn3 = ElaPushButton("关于", self)
        btn3.setFixedWidth(100)
        set_tooltip(btn3, "关于本软件 v1.0.0", position=ElaToolTipPosition.TOP)
        btn_layout.addWidget(btn3)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoStateTooltip(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("03. ela_ext - StateToolTip 状态提示")
        )
        self._addInfoText("显示加载状态、成功/失败状态的提示", parent_layout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        loading_btn = ElaPushButton("显示加载中", self)
        loading_btn.setFixedWidth(120)
        loading_btn.clicked.connect(self._showLoadingStateTooltip)
        btn_layout.addWidget(loading_btn)
        success_btn = ElaPushButton("显示成功", self)
        success_btn.setFixedWidth(120)
        success_btn.clicked.connect(self._showSuccessStateTooltip)
        btn_layout.addWidget(success_btn)
        close_btn = ElaPushButton("关闭提示", self)
        close_btn.setFixedWidth(120)
        close_btn.clicked.connect(self._closeStateTooltip)
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _destroyStateTooltip(self):
        if self._stateTooltip is not None:
            self._stateTooltip.hide()
            self._stateTooltip.deleteLater()
            self._stateTooltip = None

    def _showLoadingStateTooltip(self):
        self._destroyStateTooltip()
        self._stateTooltip = StateToolTip("正在加载", "请稍候...", self)
        self._stateTooltip.closedSignal.connect(self._onStateTooltipClosed)
        pos = self._stateTooltip.getSuitablePos()
        self._stateTooltip.move(pos)
        self._stateTooltip.show()

    def _showSuccessStateTooltip(self):
        if self._stateTooltip is not None:
            self._stateTooltip.setTitle("加载完成")
            self._stateTooltip.setContent("数据已成功加载")
            self._stateTooltip.setState(True)
        else:
            self._stateTooltip = StateToolTip("加载完成", "数据已成功加载", self)
            self._stateTooltip.closedSignal.connect(self._onStateTooltipClosed)
            pos = self._stateTooltip.getSuitablePos()
            self._stateTooltip.move(pos)
            self._stateTooltip.show()
            self._stateTooltip.setState(True)

    def _onStateTooltipClosed(self):
        self._stateTooltip = None

    def _closeStateTooltip(self):
        self._destroyStateTooltip()
