"""
[pyqt5_ela_pro] 抽屉与提示组件页面

合并了以下来源的组件:
- pyqt5_ela_pro: 抽屉、提示组件
"""
import traceback

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import (
    ElaText, ElaPushButton, ElaDrawerArea, ElaIconType, ElaToggleSwitch, ElaDialog,
)
from pyqt5_ela_pro import (
    ElaToast,
    ElaMessageDialog,
    ElaConfirmDialog,
    show_notify,
)
from pyqt5_ela_pro import (
    ElaDrawer,
    ElaDrawerPosition,
    ElaThemeWidget,
    ElaButton,
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
        self._demoElaDrawerArea(main_layout)
        self._demoDrawer(main_layout)
        self._demoTooltip(main_layout)
        self._demoTooltipDirect(main_layout)
        self._demoStateTooltip(main_layout)
        self._demoToast(main_layout)
        self._demoNotifyPopup(main_layout)
        self._demoMessageDialog(main_layout)
        self._demoConfirmDialog(main_layout)
        self._demoElaDialog(main_layout)

    def _demoElaDrawerArea(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("00. PyQt5ElaWidgetTools - ElaDrawerArea 折叠面板", self._demoElaDrawerArea)
        )
        self._addInfoText("可折叠面板，点击开关或点击头部展开/收起内容区域", parent_layout)

        drawer = ElaDrawerArea(self)
        header = QWidget(self)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        icon = ElaText(self)
        icon.setTextPixelSize(15)
        icon.setElaIcon(ElaIconType.IconName.MessageArrowDown)
        icon.setFixedSize(25, 25)
        header_layout.addWidget(icon)

        header_text = ElaText("ElaDrawerArea", self)
        header_text.setTextPixelSize(15)
        header_layout.addWidget(header_text)
        header_layout.addStretch()

        switch_text = ElaText("关", self)
        switch_text.setTextPixelSize(15)
        switch_btn = ElaToggleSwitch(self)

        def _on_toggle(toggled: bool):
            switch_text.setText("开" if toggled else "关")
            drawer.expand() if toggled else drawer.collapse()

        switch_btn.toggled.connect(_on_toggle)
        drawer.expandStateChanged.connect(switch_btn.setIsToggled)

        header_layout.addWidget(switch_text)
        header_layout.addWidget(switch_btn)
        drawer.setDrawerHeader(header)

        for i, label in enumerate(["测试窗口1", "测试窗口2", "测试窗口3"], 1):
            w = QWidget(self)
            w.setFixedHeight(75)
            wl = QHBoxLayout(w)
            wl.addSpacing(60)
            cb = ElaText(label, self)
            cb.setTextPixelSize(14)
            wl.addWidget(cb)
            wl.addStretch()
            drawer.addDrawer(w)

        parent_layout.addWidget(drawer)
        parent_layout.addSpacing(20)

    def _demoDrawer(self, parent_layout):
        parent_layout.addWidget(self._createSectionHeader("=== ela_ext - 抽屉组件 ==="))
        self._demoSiSideDrawer(parent_layout)

    def _demoTooltip(self, parent_layout):
        parent_layout.addWidget(self._createSectionHeader("=== ela_ext - 提示组件 ==="))
        self._demoToolTip(parent_layout)

    def _demoSiSideDrawer(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("01. ela_ext - ElaDrawer 四方向抽屉", self._demoSiSideDrawer)
        )
        self._addInfoText("SiliconUI 风格抽屉，支持上下左右四个方向滑入", parent_layout)
        default_font_family = QFont().defaultFamily()
        for name, pos, size in [
            ("左侧抽屉", ElaDrawerPosition.Left, 300),
            ("右侧抽屉", ElaDrawerPosition.Right, 380),
            ("顶部抽屉", ElaDrawerPosition.Top, 200),
            ("底部抽屉", ElaDrawerPosition.Bottom, 200),
        ]:
            drawer = ElaDrawer(position=pos, drawer_size=size, parent=self)
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
            close_btn = ElaButton("关闭抽屉", variant="solid", color="primary", parent=content)
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
        parent_layout.addLayout(
            self._createHeaderRow("02. ela_ext - ElaToolTip 工具提示", self._demoToolTip)
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
        parent_layout.addLayout(
            self._createHeaderRow("03. ela_ext - remove_tooltip 与 ElaToolTip 直接使用", self._demoTooltipDirect)
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
        close_tip_btn = ElaPushButton("关闭 ToolTip", self)
        close_tip_btn.setFixedWidth(100)
        self._direct_tip = None

        def _show_tooltip_direct():
            if self._direct_tip is not None:
                try:
                    self._direct_tip.hide()
                    self._direct_tip.deleteLater()
                except RuntimeError:
                    pass
            self._direct_tip = ElaToolTip("手动定位的提示框", self.window())
            self._direct_tip.showAt(
                show_tip_btn, position=ElaToolTipPosition.TopRight
            )

        def _close_tooltip_direct():
            if self._direct_tip is not None:
                try:
                    self._direct_tip.hide()
                    self._direct_tip.deleteLater()
                except RuntimeError:
                    pass
                self._direct_tip = None

        show_tip_btn.clicked.connect(_show_tooltip_direct)
        close_tip_btn.clicked.connect(_close_tooltip_direct)
        btn_layout.addWidget(show_tip_btn)
        btn_layout.addWidget(close_tip_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoStateTooltip(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("04. ela_ext - ElaStateToolTip 状态提示", self._demoStateTooltip)
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
        try:
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
        except Exception:
            print(traceback.format_exc())

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

    def _demoToast(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("05. ela_ext - ElaToast 通知提示", self._demoToast)
        )
        self._addInfoText(
            "非模态通知，支持成功/信息/警告/错误四种类型，自动淡入→停留→淡出", parent_layout
        )
        row = QHBoxLayout()
        row.setSpacing(15)
        for text, slot in [
            ("成功", lambda: ElaToast.success("操作成功完成！",parent=self)),
            ("信息", lambda: ElaToast.info("这是一条信息提示",parent=self)),
            ("警告", lambda: ElaToast.warning("请注意，磁盘空间不足",parent=self)),
            ("错误", lambda: ElaToast.error("发生错误，请重试",parent=self)),
        ]:
            btn = ElaPushButton(text, self)
            btn.setFixedWidth(80)
            btn.clicked.connect(slot)
            row.addWidget(btn)
        row.addStretch()
        parent_layout.addLayout(row)
        parent_layout.addSpacing(20)

    def _demoNotifyPopup(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("06. ela_ext - ElaNotifyPopup 通知弹窗", self._demoNotifyPopup)
        )
        self._addInfoText(
            "右下角通知弹窗，从屏幕边缘滑入，支持自动关闭和鼠标悬停保持",
            parent_layout,
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        show_btn = ElaPushButton("显示通知", self)
        show_btn.setFixedWidth(100)
        show_btn.clicked.connect(self._onShowNotify)
        btn_layout.addWidget(show_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _onShowNotify(self):
        show_notify(
            title="提示",
            content="这是一条通知信息，用于提醒用户某些重要事项。",
            timeout=10000,
        )

    def _demoMessageDialog(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("07. ela_ext - ElaMessageDialog 消息对话框", self._demoMessageDialog)
        )
        self._addInfoText(
            "简化的消息对话框接口，使用 ElaText 组件渲染内容", parent_layout
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        info_btn = ElaPushButton("显示消息", self)
        info_btn.setFixedWidth(100)
        info_btn.clicked.connect(self._onShowMessageDialog)
        btn_layout.addWidget(info_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _onShowMessageDialog(self):
        result = ElaMessageDialog.show(
            self,
            title="提示",
            message="确定要退出应用程序吗？此操作不可撤销。",
            middleText="稍后提醒",
        )
        if result == 0:
            print("您点击了取消按钮")
        elif result == 1:
            print("您点击了确定按钮")
        elif result == 2:
            print("您点击了稍后提醒按钮")

    def _demoConfirmDialog(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("08. ela_ext - ElaConfirmDialog 确认对话框", self._demoConfirmDialog)
        )
        self._addInfoText(
            "全 QPainter 自绘的确认对话框，支持 bottom（下方）和 top（上方）弹出位置",
            parent_layout,
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_bottom = ElaPushButton("下方弹出", self)
        btn_bottom.setFixedWidth(100)
        btn_bottom.clicked.connect(lambda: self._onShowConfirmDialog(btn_bottom, "bottom"))
        btn_layout.addWidget(btn_bottom)
        btn_top = ElaPushButton("上方弹出", self)
        btn_top.setFixedWidth(100)
        btn_top.clicked.connect(lambda: self._onShowConfirmDialog(btn_top, "top"))
        btn_layout.addWidget(btn_top)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _onShowConfirmDialog(self, btn, position="bottom"):
        result = ElaConfirmDialog.show(btn, "提示", f"确定要执行此操作吗？（{position}）", position=position)
        if result:
            print("用户点击了确认")
        else:
            print("用户点击了取消")

    def _demoElaDialog(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("09. PyQt5ElaWidgetTools - ElaDialog 对话框", self._demoElaDialog)
        )
        self._addInfoText(
            "Ela 主题对话框，支持窗口按钮控制、默认关闭设置、固定大小模式",
            parent_layout,
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        dlg_btn = ElaPushButton("打开 ElaDialog", self)
        dlg_btn.setFixedWidth(120)

        def _on_open_dialog():
            dlg = ElaDialog(self)
            dlg.setWindowTitle("示例对话框")
            dlg.setIsDefaultClosed(False)
            dlg.setIsFixedSize(True)
            dlg.closeButtonClicked.connect(dlg.reject)
            dlg.accepted.connect(lambda: print("ElaDialog accepted"))
            dlg.rejected.connect(lambda: print("ElaDialog rejected"))
            dlg.exec()

        dlg_btn.clicked.connect(_on_open_dialog)
        btn_layout.addWidget(dlg_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)
