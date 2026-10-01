"""按钮与菜单

所有「点一下会做事」的控件。

原「增强按钮」页第 01 节是 ElaTagLineEdit（输入框），页名与内容
不符，已挪到「输入与选择」。原生 ElaPushButton / ElaToolButton /
ElaIconButton 从「基础控件」并到这里 —— 它们和 ElaButton 是同一族，
拆两页等于逼用户自己判断「该用哪个」。
"""

from PyQt5.QtCore import QPoint, QTimer, Qt
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout
from PyQt5ElaWidgetTools import (
    ElaIconButton,
    ElaIconType,
    ElaMenu,
    ElaMenuBar,
    ElaMessageBar,
    ElaMessageBarType,
    ElaPushButton,
    ElaText,
    ElaThemeType,
    ElaToggleButton,
    ElaToolButton,
)
from .base_page import ExamplePage
from pyqt5_ela_pro import (
    ElaButton,
    ElaDropDownButton,
    ElaLongPressButton,
    ElaProgressButton,
    ElaSplitButton,
    ElaSvgButton,
    ElaSvgIconButton,
)
from pyqt5_ela_pro.svg_icon import ElaSvgIconLoader


class ButtonsMenusPage(ExamplePage):
    """按钮与菜单示例页。"""

    PAGE_TITLE = "按钮与菜单"

    def __init__(self, parent=None):
        self._nameEdit = None
        self._passwordEdit = None
        self._longPressBtn = None
        self._svg_loader = None
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoPushButton(main_layout)
        self._demoToolButton(main_layout)
        self._demoIconButton(main_layout)
        self._demoToggleButton(main_layout)
        self._demoPrimaryButton(main_layout)
        self._demoLongPressButton(main_layout)
        self._demoProgressButton(main_layout)
        self._demoEsButton(main_layout)
        self._demoEsSvgButton(main_layout)
        self._demoElaButton(main_layout)
        self._demoDropDownButton(main_layout)
        self._demoSplitButton(main_layout)
        self._demoElaMenu(main_layout)
        self._demoMenuBar(main_layout)

    def _demoPushButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "05. PyQt5ElaWidgetTools - ElaPushButton 按钮", self._demoPushButton
            )
        )
        self._addInfoText("按钮组件", parent_layout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        push_btn = ElaPushButton("按钮", self)
        push_btn.setFixedWidth(100)
        btn_layout.addWidget(push_btn)
        push_btn_disabled = ElaPushButton("禁用", self)
        push_btn_disabled.setFixedWidth(100)
        push_btn_disabled.setEnabled(False)
        btn_layout.addWidget(push_btn_disabled)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoToolButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "06. PyQt5ElaWidgetTools - ElaToolButton 工具按钮", self._demoToolButton
            )
        )
        self._addInfoText("工具按钮组件，用于展示图标", parent_layout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        tool_btn = ElaToolButton(self)
        tool_btn.setElaIcon(ElaIconType.IconName.Plus)
        btn_layout.addWidget(tool_btn)
        tool_btn_disabled = ElaToolButton(self)
        tool_btn_disabled.setElaIcon(ElaIconType.IconName.Minus)
        tool_btn_disabled.setEnabled(False)
        btn_layout.addWidget(tool_btn_disabled)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoIconButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "07. PyQt5ElaWidgetTools - ElaIconButton 图标按钮", self._demoIconButton
            )
        )
        self._addInfoText("图标按钮组件", parent_layout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        icon_btn1 = ElaIconButton(ElaIconType.IconName.Plus, 16, self)
        btn_layout.addWidget(icon_btn1)
        icon_btn2 = ElaIconButton(ElaIconType.IconName.Minus, 16, self)
        btn_layout.addWidget(icon_btn2)
        icon_btn_disabled = ElaIconButton(ElaIconType.IconName.Copy, 16, self)
        icon_btn_disabled.setEnabled(False)
        btn_layout.addWidget(icon_btn_disabled)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoToggleButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "07a. PyQt5ElaWidgetTools - ElaToggleButton 切换按钮",
                self._demoToggleButton,
            )
        )
        self._addInfoText(
            "带文字的开关式按钮，状态变化发 toggled（区别于 ElaToggleSwitch："
            "那是纯开关，这个看起来仍是按钮）",
            parent_layout,
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        toggle = ElaToggleButton("静音", self)
        toggle.setFixedWidth(110)
        toggle.setIsToggled(False)
        toggle.toggled.connect(
            lambda state: print(f"ElaToggleButton toggled -> {state}")
        )
        btn_layout.addWidget(toggle)

        on_by_default = ElaToggleButton("默认开启", self)
        on_by_default.setFixedWidth(110)
        on_by_default.setIsToggled(True)
        btn_layout.addWidget(on_by_default)

        disabled = ElaToggleButton("禁用", self)
        disabled.setFixedWidth(110)
        disabled.setEnabled(False)
        btn_layout.addWidget(disabled)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoPrimaryButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "02. PyQt5ElaWidgetTools - ElaPushButton 按钮", self._demoPrimaryButton
            )
        )
        self._addInfoText("按钮组件", parent_layout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        primary_btn = ElaPushButton("按钮", self)
        primary_btn.setFixedWidth(120)
        primary_btn.clicked.connect(lambda: print("按钮 clicked"))
        btn_layout.addWidget(primary_btn)
        primary_btn_disabled = ElaPushButton("禁用", self)
        primary_btn_disabled.setFixedWidth(120)
        primary_btn_disabled.setEnabled(False)
        btn_layout.addWidget(primary_btn_disabled)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _onLongPressTriggered(self):
        print("长按触发成功！")

    def _setLongPressDuration(self, ms):
        if self._longPressBtn:
            self._longPressBtn.setDuration(ms)
            self._longPressBtn.setText(f"长按 {ms / 1000:.1f} 秒")

    def _demoLongPressButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "04. ela_ext - ElaLongPressButton 长按按钮", self._demoLongPressButton
            )
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

    def _onProgressTimerTick(self):
        current = self._progressBtn.progress()
        if current >= 100:
            self._progressTimer.stop()
            self._progressTimerBtn.setText("启动定时更新")
        else:
            self._progressBtn.setProgress(current + 10)

    def _onProgressTimerToggle(self):
        if self._progressTimer.isActive():
            self._progressTimer.stop()
            self._progressTimerBtn.setText("启动定时更新")
        else:
            self._progressBtn.setProgress(0)
            self._progressTimer.start()
            self._progressTimerBtn.setText("停止定时更新")

    def _demoProgressButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "05. pyqt5_ela_pro - ElaProgressButton 进度按钮",
                self._demoProgressButton,
            )
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

    def _getSvgLoader(self):
        if self._svg_loader is None:
            self._svg_loader = ElaSvgIconLoader()
            self._svg_loader.loadFromPackage("fluent_ui_icon_regular.icons")
        return self._svg_loader

    def _demoEsButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "07. ela_ext - ElaSvgIconButton 基础 SVG 图标按钮", self._demoEsButton
            )
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
            (
                "ic_fluent_zoom_out_regular",
                "搜索",
                ElaThemeType.ThemeColor.PrimaryNormal,
            ),
            (
                "ic_fluent_settings_regular",
                "设置",
                ElaThemeType.ThemeColor.PrimaryNormal,
            ),
            ("ic_fluent_delete_regular", "删除", ElaThemeType.ThemeColor.StatusDanger),
            ("ic_fluent_save_regular", "保存", ElaThemeType.ThemeColor.PrimaryNormal),
        ]
        for name, text, theme_color in svg_buttons:
            btn = ElaSvgIconButton(
                text, icon_name=name, theme_color=theme_color, parent=self
            )
            btn.setFixedWidth(120)
            icons_row_layout.addWidget(btn)
        icons_row_layout.addStretch()
        parent_layout.addLayout(icons_row_layout)
        parent_layout.addSpacing(30)

    def _demoEsSvgButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "08. ela_ext - ElaSvgButton 悬浮/点击主题色效果", self._demoEsSvgButton
            )
        )
        self._addInfoText("鼠标悬浮和点击时显示半透明主题色背景效果", parent_layout)
        parent_layout.addSpacing(10)
        self._getSvgLoader()
        icons_row_layout = QHBoxLayout()
        icons_row_layout.setSpacing(15)
        theme_buttons = [
            (
                "ic_fluent_zoom_out_regular",
                "搜索",
                ElaThemeType.ThemeColor.PrimaryNormal,
            ),
            (
                "ic_fluent_settings_regular",
                "设置",
                ElaThemeType.ThemeColor.PrimaryNormal,
            ),
            ("ic_fluent_delete_regular", "删除", ElaThemeType.ThemeColor.StatusDanger),
            ("ic_fluent_edit_regular", "编辑", ElaThemeType.ThemeColor.PrimaryPress),
            ("ic_fluent_copy_regular", "复制", ElaThemeType.ThemeColor.PrimaryNormal),
        ]
        for name, text, theme_color in theme_buttons:
            btn = ElaSvgButton(
                text, icon_name=name, theme_color=theme_color, parent=self
            )
            btn.setFixedWidth(120)
            icons_row_layout.addWidget(btn)
        icons_row_layout.addStretch()
        parent_layout.addLayout(icons_row_layout)
        parent_layout.addSpacing(20)

    def _demoElaButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "09. ela_ext - ElaButton 统一按钮", self._demoElaButton
            )
        )
        self._addInfoText(
            "Ant Design 风格按钮 — 横向 6 种变体，纵向 16 种色彩主题",
            parent_layout,
        )
        parent_layout.addSpacing(8)

        variants = ["outlined", "dashed", "solid", "filled", "text", "link"]
        colors = [
            "default",
            "primary",
            "danger",
            "blue",
            "purple",
            "cyan",
            "green",
            "magenta",
            "pink",
            "red",
            "orange",
            "yellow",
            "volcano",
            "geekblue",
            "lime",
            "gold",
        ]
        # Display labels for colors
        color_labels = {
            "default": "Default",
            "primary": "Primary",
            "danger": "Danger",
            "blue": "Blue",
            "purple": "Purple",
            "cyan": "Cyan",
            "green": "Green",
            "magenta": "Magenta",
            "pink": "Pink",
            "red": "Red",
            "orange": "Orange",
            "yellow": "Yellow",
            "volcano": "Volcano",
            "geekblue": "Geekblue",
            "lime": "Lime",
            "gold": "Gold",
        }

        grid = QGridLayout()
        grid.setSpacing(8)

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
            self._createHeaderRow(
                "09a. pyqt5_ela_pro - ElaDropDownButton 下拉按钮",
                self._demoDropDownButton,
            )
        )
        self._addInfoText("点击展开 ElaMenu 下拉菜单", parent_layout)
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
            self._createHeaderRow(
                "10. pyqt5_ela_pro - ElaSplitButton 拆分按钮", self._demoSplitButton
            )
        )
        self._addInfoText("左侧点击触发操作，右侧弹出下拉菜单", parent_layout)
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

    def _showMenuFeedback(self, action_text: str):
        ElaMessageBar.success(
            ElaMessageBarType.PositionPolicy.Top,
            "菜单反馈",
            f"点击了: {action_text}",
            2000,
        )

    def _demoElaMenu(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "01. PyQt5ElaWidgetTools - ElaMenu 菜单", self._demoElaMenu
            )
        )
        self._addInfoText("点击按钮打开菜单，点击菜单项可看到反馈", parent_layout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        menu_btn = ElaPushButton("菜单", self)
        menu_btn.setFixedWidth(100)
        menu = ElaMenu(self)
        save_action = menu.addAction("保存")
        save_action.triggered.connect(lambda: self._showMenuFeedback("保存"))
        edit_action = menu.addAction("编辑")
        edit_action.triggered.connect(lambda: self._showMenuFeedback("编辑"))
        menu.addSeparator()
        delete_action = menu.addAction("删除")
        delete_action.triggered.connect(lambda: self._showMenuFeedback("删除"))
        menu.addSeparator()
        about_action = menu.addAction("关于")
        about_action.triggered.connect(lambda: self._showMenuFeedback("关于"))
        menu_btn.clicked.connect(
            lambda: menu.popup(menu_btn.mapToGlobal(QPoint(0, menu_btn.height())))
        )
        btn_layout.addWidget(menu_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoMenuBar(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "02. PyQt5ElaWidgetTools - ElaMenuBar 菜单栏", self._demoMenuBar
            )
        )
        self._addInfoText("窗口菜单栏组件", parent_layout)
        menu_bar = ElaMenuBar(self)
        file_menu = menu_bar.addMenu("文件(&F)")
        save_action = file_menu.addAction("保存")
        save_action.triggered.connect(lambda: self._showMenuFeedback("文件-保存"))
        file_menu.addAction("另存为")
        file_menu.addSeparator()
        file_menu.addAction("退出")
        edit_menu = menu_bar.addMenu("编辑(&E)")
        edit_menu.addAction("复制")
        edit_menu.addAction("粘贴")
        help_menu = menu_bar.addMenu("帮助(&H)")
        about_action = help_menu.addAction("关于")
        about_action.triggered.connect(lambda: self._showMenuFeedback("帮助-关于"))
        parent_layout.addWidget(menu_bar)
        parent_layout.addSpacing(20)
