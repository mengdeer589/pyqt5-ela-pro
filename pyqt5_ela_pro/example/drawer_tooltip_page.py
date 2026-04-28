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
    ElaThemeWidget,
    ElaPrimaryButton,
    ElaToolTip,
    ElaToolTipPosition,
    set_tooltip,
    remove_tooltip,
    ElaStateToolTip,
)
from .base_page import ExamplePage


class DrawerTooltipPage(ExamplePage):
    """抽屉与提示组件页面"""

    PAGE_TITLE = "抽屉与提示"

    def __init__(self, parent=None):
        self._drawers = {}
        self._stateTooltip = None
        self._tooltip_demo_btn = None
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoDrawer(main_layout)
        self._demoTooltip(main_layout)
        self._demoTooltipDirect(main_layout)
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
            content = ElaThemeWidget()
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
            close_btn = ElaPrimaryButton(parent=content)
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
            self._createSectionHeader("02. ela_ext - ElaToolTip 工具提示")
        )
        self._addInfoText("鼠标悬停在按钮上查看提示", parent_layout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn1 = ElaPushButton("保存", self)
        btn1.setFixedWidth(100)
        set_tooltip(btn1, "保存当前内容", position=ElaToolTipPosition.Bottom)
        btn_layout.addWidget(btn1)
        btn2 = ElaPushButton("删除", self)
        btn2.setFixedWidth(100)
        set_tooltip(
            btn2, "删除选中项目\n（此操作不可撤销）", position=ElaToolTipPosition.Right
        )
        btn_layout.addWidget(btn2)
        btn3 = ElaPushButton("关于", self)
        btn3.setFixedWidth(100)
        set_tooltip(btn3, "关于本软件 v1.0.0", position=ElaToolTipPosition.Top)
        btn_layout.addWidget(btn3)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoTooltipDirect(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("03. ela_ext - remove_tooltip 与 ElaToolTip 直接使用")
        )
        self._addInfoText("左侧按钮有 tooltip，点击右侧按钮移除/恢复", parent_layout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        self._tooltip_demo_btn = ElaPushButton("有提示的按钮", self)
        self._tooltip_demo_btn.setFixedWidth(120)
        set_tooltip(self._tooltip_demo_btn, "这是一个悬浮提示")
        btn_layout.addWidget(self._tooltip_demo_btn)
        self._tooltip_remove_btn = ElaPushButton("移除提示", self)
        self._tooltip_remove_btn.setFixedWidth(100)

        def _toggle_tooltip():
            if self._tooltip_demo_btn is None:
                return
            if self._tooltip_remove_btn.text() == "移除提示":
                remove_tooltip(self._tooltip_demo_btn)
                self._tooltip_remove_btn.setText("恢复提示")
            else:
                set_tooltip(self._tooltip_demo_btn, "这是一个悬浮提示")
                self._tooltip_remove_btn.setText("移除提示")

        self._tooltip_remove_btn.clicked.connect(_toggle_tooltip)
        btn_layout.addWidget(self._tooltip_remove_btn)
        btn_layout.addSpacing(20)
        show_tip_btn = ElaPushButton("显示 ElaToolTip", self)
        show_tip_btn.setFixedWidth(120)

        def _show_tooltip_direct():
            tip = ElaToolTip("手动定位的提示框", self.window())
            tip.showAt(
                show_tip_btn, position=ElaToolTipPosition.TopRight
            )

        show_tip_btn.clicked.connect(_show_tooltip_direct)
        btn_layout.addWidget(show_tip_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoStateTooltip(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("04. ela_ext - ElaStateToolTip 状态提示")
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

    def _checkValid(self, widget) -> bool:
        try:
            return widget is not None and widget.isWidgetType()
        except RuntimeError:
            return False

    def _showStateTooltip(self, title, content, is_done=False):
        if self._checkValid(self._stateTooltip):
            self._stateTooltip.setTitle(title)
            self._stateTooltip.setContent(content)
            if is_done:
                self._stateTooltip.setState(True)
            return
        self._stateTooltip = ElaStateToolTip(title, content, self)
        self._stateTooltip.closed.connect(self._onStateTooltipClosed)
        pos = self._stateTooltip.getSuitablePos()
        self._stateTooltip.move(pos)
        self._stateTooltip.show()
        if is_done:
            self._stateTooltip.setState(True)

    def _showLoadingStateTooltip(self):
        self._showStateTooltip("正在加载", "请稍候...")
    def _showSuccessStateTooltip(self):
        self._showStateTooltip("加载完成", "数据已成功加载", is_done=True)

    def _onStateTooltipClosed(self):
        self._stateTooltip = None

    def _closeStateTooltip(self):
        if self._checkValid(self._stateTooltip):
            self._stateTooltip.hide()
            self._stateTooltip.deleteLater()
        self._stateTooltip = None
