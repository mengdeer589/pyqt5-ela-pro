"""
[pyqt5_ela_pro] 表单与按钮组件页面

合并了以下来源的组件:
- pyqt5_ela_pro: 表单组件
- PyQt5ElaWidgetTools: 按钮组件
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit
from PyQt5.QtCore import Qt, QTimer
from PyQt5ElaWidgetTools import ElaText, ElaPushButton, ElaIconType, ElaThemeType, ElaMenu
from pyqt5_ela_pro import (
    ElaThemeWidget,
    ElaButton,
    ElaConfirmDialog,
    ElaDropDownButton,
    ElaSplitButton,
    ElaToast,
    ElaTagLineEdit,
    ElaLongPressButton,
    ElaMessageDialog,
    ElaProgressButton,
    ElaNotifyPopup,
    ElaSvgButton,
    ElaSvgIconButton,
    show_notify,
)
from pyqt5_ela_pro.svg_icon import ElaSvgIconLoader
from .base_page import ExamplePage


class FormButtonPage(ExamplePage):
    """表单与按钮组件页面"""

    PAGE_TITLE = "表单与按钮"

    def __init__(self, parent=None):
        self._nameEdit = None
        self._passwordEdit = None
        self._longPressBtn = None
        self._svg_loader = None
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoForm(main_layout)
        self._demoButton(main_layout)

    def _demoForm(self, parent_layout):
        self._demoTagLineEdit(parent_layout)

    def _getSvgLoader(self):
        if self._svg_loader is None:
            self._svg_loader = ElaSvgIconLoader()
            self._svg_loader.loadFromPackage("fluent_ui_icon_regular.icons")
        return self._svg_loader

    def _demoButton(self, parent_layout):
        self._demoPrimaryButton(parent_layout)
        self._demoLongPressButton(parent_layout)
        self._demoProgressButton(parent_layout)
        self._demoNotifyPopup(parent_layout)
        self._demoEsButton(parent_layout)
        self._demoEsSvgButton(parent_layout)
        self._demoElaButton(parent_layout)
        self._demoDropDownButton(parent_layout)
        self._demoSplitButton(parent_layout)
        self._demoToast(parent_layout)
        self._demoMessageDialog(parent_layout)
        self._demoConfirmDialog(parent_layout)

    def _demoTagLineEdit(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("01. pyqt5_ela_pro - ElaTagLineEdit 具名输入框", self._demoTagLineEdit)
        )
        self._addInfoText(
            "带有标题标签的输入框组件，支持主题适配和错误状态", parent_layout
        )
        edit_layout = QVBoxLayout()
        edit_layout.setSpacing(15)
        self._nameEdit = ElaTagLineEdit(title="用户名", parent=self)
        self._nameEdit.setFixedWidth(300)
        self._nameEdit.setText("admin")
        edit_layout.addWidget(self._nameEdit)
        self._passwordEdit = ElaTagLineEdit(title="密码", parent=self)
        self._passwordEdit.setFixedWidth(300)
        self._passwordEdit.setEchoMode(QLineEdit.Password)
        edit_layout.addWidget(self._passwordEdit)
        email_edit = ElaTagLineEdit(title="邮箱", parent=self)
        email_edit.setFixedWidth(300)
        email_edit.setText("test@example.com")
        edit_layout.addWidget(email_edit)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        validate_btn = ElaPushButton("模拟验证失败", self)
        validate_btn.setFixedWidth(120)
        validate_btn.clicked.connect(self._onValidateFailed)
        btn_layout.addWidget(validate_btn)
        clear_btn = ElaPushButton("清除错误", self)
        clear_btn.setFixedWidth(100)
        clear_btn.clicked.connect(self._onClearError)
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        edit_layout.addLayout(btn_layout)
        parent_layout.addLayout(edit_layout)
        parent_layout.addSpacing(20)

    def _onValidateFailed(self):
        self._nameEdit.notifyInvalidInput()
        self._passwordEdit.notifyInvalidInput()

    def _onClearError(self):
        if self._nameEdit:
            self._nameEdit.clearError()
        if self._passwordEdit:
            self._passwordEdit.clearError()

    def _demoPrimaryButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("02. PyQt5ElaWidgetTools - ElaPushButton 按钮", self._demoPrimaryButton)
        )
        self._addInfoText("按钮组件", parent_layout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        primary_btn = ElaPushButton("按钮", self)
        primary_btn.setFixedWidth(120)
        primary_btn.clicked.connect(
            lambda: ElaMessageDialog.show(self, "提示", "按钮 clicked")
        )
        btn_layout.addWidget(primary_btn)
        primary_btn_disabled = ElaPushButton("禁用", self)
        primary_btn_disabled.setFixedWidth(120)
        primary_btn_disabled.setEnabled(False)
        btn_layout.addWidget(primary_btn_disabled)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoLongPressButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("04. ela_ext - ElaLongPressButton 长按按钮", self._demoLongPressButton)
        )
        self._addInfoText(
            "按住按钮一段时间后才能触发点击事件，适合危险操作防误触", parent_layout
        )
        btn_layout2 = QHBoxLayout()
        btn_layout2.setSpacing(15)
        self._longPressBtn = ElaLongPressButton(duration=800, parent=self)
        self._longPressBtn.setText("长按 0.8 秒")
        self._longPressBtn.setFixedWidth(160)
        self._longPressBtn.longPressed.connect(self._onLongPressTriggered)
        btn_layout2.addWidget(self._longPressBtn)
        duration_label = ElaText("时长:", self)
        duration_label.setTextPixelSize(14)
        btn_layout2.addWidget(duration_label)
        for ms in [300, 500, 800, 1000]:
            btn = ElaPushButton(f"{ms}ms", self)
            btn.setFixedWidth(60)
            btn.clicked.connect(lambda checked, m=ms: self._setLongPressDuration(m))
            btn_layout2.addWidget(btn)
        btn_layout2.addStretch()
        parent_layout.addLayout(btn_layout2)
        parent_layout.addSpacing(20)

    def _setLongPressDuration(self, ms):
        if self._longPressBtn:
            self._longPressBtn.setDuration(ms)
            self._longPressBtn.setText(f"长按 {ms / 1000:.1f} 秒")

    def _onLongPressTriggered(self):
        print("长按触发成功！")

    def _onProgressTimerToggle(self):
        if self._progressTimer.isActive():
            self._progressTimer.stop()
            self._progressTimerBtn.setText("启动定时更新")
        else:
            self._progressBtn.setProgress(0)
            self._progressTimer.start()
            self._progressTimerBtn.setText("停止定时更新")

    def _onProgressTimerTick(self):
        current = self._progressBtn.getProgress()
        if current >= 100:
            self._progressTimer.stop()
            self._progressTimerBtn.setText("启动定时更新")
        else:
            self._progressBtn.setProgress(current + 10)

    def _demoProgressButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("05. pyqt5_ela_pro - ElaProgressButton 进度按钮", self._demoProgressButton)
        )
        self._addInfoText(
            "显示进度的按钮组件，通过 setProgress() 设置进度 (0-100)", parent_layout
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        self._progressBtn = ElaProgressButton(parent=self)
        self._progressBtn.setText("下载")
        self._progressBtn.setFixedWidth(120)
        btn_layout.addWidget(self._progressBtn)
        for percent in [0, 25, 50, 75, 100]:
            btn = ElaPushButton(f"{percent}%", self)
            btn.setFixedWidth(50)
            btn.clicked.connect(
                lambda checked, p=percent: self._progressBtn.setProgress(p)
            )
            btn_layout.addWidget(btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)

        auto_layout = QHBoxLayout()
        auto_layout.setSpacing(15)
        self._progressTimerBtn = ElaPushButton("启动定时更新", self)
        self._progressTimerBtn.setFixedWidth(100)
        self._progressTimerBtn.clicked.connect(self._onProgressTimerToggle)
        auto_layout.addWidget(self._progressTimerBtn)
        self._progressTimer = QTimer(self)
        self._progressTimer.setInterval(1000)
        self._progressTimer.timeout.connect(self._onProgressTimerTick)
        auto_layout.addStretch()
        parent_layout.addLayout(auto_layout)
        parent_layout.addSpacing(20)

    def _demoEsButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("07. ela_ext - ElaSvgIconButton 基础 SVG 图标按钮", self._demoEsButton)
        )
        self._addInfoText(
            "继承 ElaPushButton 的外观，使用 SVG 图标，图标颜色与文字一致",
            parent_layout,
        )
        parent_layout.addSpacing(10)
        self._getSvgLoader()
        icons_row_layout = QHBoxLayout()
        icons_row_layout.setSpacing(15)
        svg_buttons = [
            ("ic_fluent_zoom_out_regular", "搜索", ElaThemeType.ThemeColor.PrimaryNormal),
            ("ic_fluent_settings_regular", "设置", ElaThemeType.ThemeColor.PrimaryNormal),
            ("ic_fluent_delete_regular", "删除", ElaThemeType.ThemeColor.StatusDanger),
            ("ic_fluent_save_regular", "保存", ElaThemeType.ThemeColor.PrimaryNormal),
        ]
        for name, text, theme_color in svg_buttons:
            btn = ElaSvgIconButton(text, icon_name=name, theme_color=theme_color, parent=self)
            btn.setFixedWidth(120)
            icons_row_layout.addWidget(btn)
        icons_row_layout.addStretch()
        parent_layout.addLayout(icons_row_layout)
        parent_layout.addSpacing(30)

    def _demoEsSvgButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("08. ela_ext - ElaSvgButton 悬浮/点击主题色效果", self._demoEsSvgButton)
        )
        self._addInfoText("鼠标悬浮和点击时显示半透明主题色背景效果", parent_layout)
        parent_layout.addSpacing(10)
        self._getSvgLoader()
        icons_row_layout = QHBoxLayout()
        icons_row_layout.setSpacing(15)
        theme_buttons = [
            ("ic_fluent_zoom_out_regular", "搜索", ElaThemeType.ThemeColor.PrimaryNormal),
            ("ic_fluent_settings_regular", "设置", ElaThemeType.ThemeColor.PrimaryNormal),
            ("ic_fluent_delete_regular", "删除", ElaThemeType.ThemeColor.StatusDanger),
            ("ic_fluent_edit_regular", "编辑", ElaThemeType.ThemeColor.PrimaryPress),
            ("ic_fluent_copy_regular", "复制", ElaThemeType.ThemeColor.PrimaryNormal),
        ]
        for name, text, theme_color in theme_buttons:
            btn = ElaSvgButton(text, icon_name=name, theme_color=theme_color, parent=self)
            btn.setFixedWidth(120)
            icons_row_layout.addWidget(btn)
        icons_row_layout.addStretch()
        parent_layout.addLayout(icons_row_layout)
        parent_layout.addSpacing(20)

    def _demoElaButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("09. ela_ext - ElaButton 统一按钮", self._demoElaButton)
        )
        self._addInfoText(
            "Ant Design 风格按钮 — 横向 6 种变体，纵向 16 种色彩主题",
            parent_layout,
        )
        parent_layout.addSpacing(8)

        variants = ["outlined", "dashed", "solid", "filled", "text", "link"]
        colors = [
            "default", "primary", "danger",
            "blue", "purple", "cyan", "green",
            "magenta", "pink", "red", "orange",
            "yellow", "volcano", "geekblue", "lime", "gold",
        ]
        # Display labels for colors
        color_labels = {
            "default": "Default", "primary": "Primary", "danger": "Danger",
            "blue": "Blue", "purple": "Purple", "cyan": "Cyan", "green": "Green",
            "magenta": "Magenta", "pink": "Pink", "red": "Red", "orange": "Orange",
            "yellow": "Yellow", "volcano": "Volcano", "geekblue": "Geekblue",
            "lime": "Lime", "gold": "Gold",
        }

        grid = QGridLayout()
        grid.setSpacing(6)

        # Header row
        corner = ElaText("颜色\\变体", self)
        corner.setTextPixelSize(12)
        grid.addWidget(corner, 0, 0, Qt.AlignmentFlag.AlignCenter)
        for j, v in enumerate(variants):
            lbl = ElaText(v.capitalize(), self)
            lbl.setTextPixelSize(12)
            grid.addWidget(lbl, 0, j + 1, Qt.AlignmentFlag.AlignCenter)

        # Data rows
        for i, c in enumerate(colors):
            clbl = ElaText(color_labels[c], self)
            clbl.setTextPixelSize(12)
            grid.addWidget(clbl, i + 1, 0, Qt.AlignmentFlag.AlignCenter)
            for j, v in enumerate(variants):
                btn = ElaButton(color_labels[c], variant=v, color=c, parent=self)
                grid.addWidget(btn, i + 1, j + 1)

        parent_layout.addLayout(grid)
        parent_layout.addSpacing(12)

        # ── Extra: danger, disabled, sizes, icons ──
        row = QHBoxLayout()
        row.setSpacing(12)
        for label, v, c, d in [
            ("危险 Solid", "solid", "default", True),
            ("危险 Outlined", "outlined", "default", True),
        ]:
            b = ElaButton(label, variant=v, danger=d, parent=self)
            row.addWidget(b)
        disabled_s = ElaButton("禁用 Solid", variant="solid", parent=self)
        disabled_s.setEnabled(False)
        row.addWidget(disabled_s)
        disabled_o = ElaButton("禁用 Outlined", variant="outlined", parent=self)
        disabled_o.setEnabled(False)
        row.addWidget(disabled_o)
        for sz in ("small", "middle", "large"):
            b = ElaButton(sz.capitalize(), variant="outlined", size=sz, parent=self)
            row.addWidget(b)
        row.addStretch()
        parent_layout.addLayout(row)
        parent_layout.addSpacing(8)

        # ── Icon buttons ──
        row = QHBoxLayout()
        row.setSpacing(12)
        for text, icon, v, c in [
            ("保存", ElaIconType.IconName.FloppyDisk, "solid", "primary"),
            ("编辑", ElaIconType.IconName.Pencil, "outlined", "default"),
            ("复制", ElaIconType.IconName.Copy, "solid", "danger"),
            ("设置", ElaIconType.IconName.Gear, "dashed", "primary"),
            ("标记", ElaIconType.IconName.BadgeCheck, "filled", "purple"),
            ("旋转", ElaIconType.IconName.ArrowRotateRight, "text", "default"),
        ]:
            row.addWidget(ElaButton(text, icon=icon, variant=v, color=c, parent=self))
        row.addStretch()
        parent_layout.addLayout(row)
        parent_layout.addSpacing(20)

    def _demoDropDownButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("09a. pyqt5_ela_pro - ElaDropDownButton 下拉按钮", self._demoDropDownButton)
        )
        self._addInfoText(
            "点击展开 ElaMenu 下拉菜单", parent_layout
        )
        row = QHBoxLayout()
        row.setSpacing(15)

        btn = ElaDropDownButton(parent=self)
        btn.setText("操作")
        menu = ElaMenu(btn)
        menu.addAction("选项一")
        menu.addAction("选项二")
        menu.addSeparator()
        menu.addAction("选项三")
        btn.setMenu(menu)
        row.addWidget(btn)

        btn2 = ElaDropDownButton(parent=self)
        btn2.setText("设置")
        btn2.setElaIcon(ElaIconType.IconName.Gear)
        menu2 = ElaMenu(btn2)
        menu2.addAction("偏好设置")
        menu2.addAction("账户")
        btn2.setMenu(menu2)
        row.addWidget(btn2)

        row.addStretch()
        parent_layout.addLayout(row)
        parent_layout.addSpacing(20)

    def _demoSplitButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("10. pyqt5_ela_pro - ElaSplitButton 拆分按钮", self._demoSplitButton)
        )
        self._addInfoText(
            "左侧点击触发操作，右侧弹出下拉菜单", parent_layout
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        btn = ElaSplitButton(parent=self)
        btn.setText("保存")
        btn.setElaIcon(ElaIconType.IconName.FloppyDisk)
        btn.clicked.connect(lambda: print("保存 clicked"))
        btn_layout.addWidget(btn)

        menu_btn = ElaSplitButton(parent=self)
        menu_btn.setText("更多")
        menu_btn.setElaIcon(ElaIconType.IconName.Gear)
        menu = ElaMenu(menu_btn)
        menu.addAction("操作一")
        menu.addAction("操作二")
        menu.addSeparator()
        menu.addAction("操作三")
        menu_btn.setMenu(menu)
        menu_btn.clicked.connect(lambda: print("更多 clicked"))
        btn_layout.addWidget(menu_btn)

        no_icon = ElaSplitButton(parent=self)
        no_icon.setText("纯文字")
        menu2 = ElaMenu(no_icon)
        menu2.addAction("选项A")
        menu2.addAction("选项B")
        no_icon.setMenu(menu2)
        no_icon.clicked.connect(lambda: print("纯文字 clicked"))
        btn_layout.addWidget(no_icon)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoToast(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("11. pyqt5_ela_pro - ElaToast 通知提示", self._demoToast)
        )
        self._addInfoText(
            "非模态通知，支持成功/信息/警告/错误四种类型，自动淡入→停留→淡出", parent_layout
        )
        row = QHBoxLayout()
        row.setSpacing(15)
        for text, slot in [
            ("成功", lambda: ElaToast.success("操作成功完成！")),
            ("信息", lambda: ElaToast.info("这是一条信息提示")),
            ("警告", lambda: ElaToast.warning("请注意，磁盘空间不足")),
            ("错误", lambda: ElaToast.error("发生错误，请重试")),
        ]:
            btn = ElaPushButton(text, self)
            btn.setFixedWidth(80)
            btn.clicked.connect(slot)
            row.addWidget(btn)
        row.addStretch()
        parent_layout.addLayout(row)
        parent_layout.addSpacing(20)

    def _demoMessageDialog(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("09. pyqt5_ela_pro - ElaMessageDialog 消息对话框", self._demoMessageDialog)
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
            self._createHeaderRow("10. ela_ext - ElaConfirmDialog 确认对话框", self._demoConfirmDialog)
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

    def _demoNotifyPopup(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("08. pyqt5_ela_pro - ElaNotifyPopup 通知弹窗", self._demoNotifyPopup)
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
