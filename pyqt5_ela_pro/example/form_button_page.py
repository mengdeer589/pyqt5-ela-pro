"""
[pyqt5_ela_pro] 表单与按钮组件页面

合并了以下来源的组件:
- pyqt5_ela_pro: 表单组件
- PyQt5ElaWidgetTools: 按钮组件
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox
from PyQt5.QtCore import QTimer
from PyQt5ElaWidgetTools import ElaText, ElaPushButton, ElaIconType
from pyqt5_ela_pro import (
    ElaThemeWidget,
    ElaTagLineEdit,
    ElaLongPressButton,
    ElaPrimaryButton,
    ElaThemeToolButton,
    ElaMessageDialog,
    ElaProgressButton,
    ElaNotifyPopup,
    ElaScrollableMenu,
    show_notify,
)
from .base_page import ExamplePage


class FormButtonPage(ExamplePage):
    """表单与按钮组件页面"""

    PAGE_TITLE = "表单与按钮"

    def __init__(self, parent=None):
        self._nameEdit = None
        self._passwordEdit = None
        self._longPressBtn = None
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoForm(main_layout)
        self._demoButton(main_layout)

    def _demoForm(self, parent_layout):
        self._demoTagLineEdit(parent_layout)

    def _demoButton(self, parent_layout):
        self._demoPrimaryButton(parent_layout)
        self._demoLongPressButton(parent_layout)
        self._demoProgressButton(parent_layout)
        self._demoNotifyPopup(parent_layout)
        self._demoToolButtonExt(parent_layout)
        self._demoScrollableMenu(parent_layout)
        self._demoMessageDialog(parent_layout)

    def _addInfoText(self, text, parent_layout):
        info = ElaText(text, self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

    def _demoTagLineEdit(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("01. pyqt5_ela_pro - ElaTagLineEdit 具名输入框")
        )
        self._addInfoText(
            "带有标题标签的输入框组件，支持主题适配和错误状态", parent_layout
        )
        edit_layout = QVBoxLayout()
        edit_layout.setSpacing(15)
        self._nameEdit = ElaTagLineEdit(self, title="用户名")
        self._nameEdit.setFixedWidth(300)
        self._nameEdit.setText("admin")
        edit_layout.addWidget(self._nameEdit)
        self._passwordEdit = ElaTagLineEdit(self, title="密码")
        self._passwordEdit.setFixedWidth(300)
        self._passwordEdit.setEchoMode(QLineEdit.Password)
        edit_layout.addWidget(self._passwordEdit)
        email_edit = ElaTagLineEdit(self, title="邮箱")
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
        parent_layout.addWidget(
            self._createSectionHeader("02. PyQt5ElaWidgetTools - ElaPushButton 按钮")
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
        parent_layout.addWidget(
            self._createSectionHeader("03. ela_ext - ElaPrimaryButton 主要按钮")
        )
        self._addInfoText(
            "使用 Primary 主题色的按钮，与 ElaToggleButton ON 状态外观一致",
            parent_layout,
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        primary_btn = ElaPrimaryButton(parent=self)
        primary_btn.setText("主要按钮")
        primary_btn.setFixedWidth(120)
        primary_btn.clicked.connect(lambda: print("ElaPrimaryButton clicked"))
        btn_layout.addWidget(primary_btn)
        primary_btn_icon = ElaPrimaryButton(parent=self)
        primary_btn_icon.setText("带图标")
        primary_btn_icon.setFixedWidth(120)
        primary_btn_icon.setElaIcon(ElaIconType.IconName.FloppyDisk, 16)
        btn_layout.addWidget(primary_btn_icon)
        primary_btn_disabled = ElaPrimaryButton(parent=self)
        primary_btn_disabled.setText("禁用状态")
        primary_btn_disabled.setFixedWidth(120)
        primary_btn_disabled.setEnabled(False)
        btn_layout.addWidget(primary_btn_disabled)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

        parent_layout.addWidget(
            self._createSectionHeader("04. ela_ext - ElaLongPressButton 长按按钮")
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
        parent_layout.addWidget(
            self._createSectionHeader("05. pyqt5_ela_pro - ElaProgressButton 进度按钮")
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

    def _demoToolButtonExt(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("06. ela_ext - ElaThemeToolButton 图标文字并排按钮")
        )
        self._addInfoText(
            "ToolButton 样式设置为文字在图标旁边，适合工具栏使用", parent_layout
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        tool_btn = ElaThemeToolButton(parent=self)
        tool_btn.setText("保存")
        tool_btn.setFixedWidth(100)
        tool_btn.setElaIcon(ElaIconType.IconName.FloppyDisk)
        tool_btn.clicked.connect(lambda: print("保存 clicked"))
        btn_layout.addWidget(tool_btn)
        tool_btn_icon = ElaThemeToolButton(parent=self)
        tool_btn_icon.setText("编辑")
        tool_btn_icon.setFixedWidth(100)
        tool_btn_icon.setElaIcon(ElaIconType.IconName.Pencil)
        tool_btn_icon.clicked.connect(lambda: print("编辑 clicked"))
        btn_layout.addWidget(tool_btn_icon)
        tool_btn_disabled = ElaThemeToolButton(parent=self)
        tool_btn_disabled.setText("禁用")
        tool_btn_disabled.setFixedWidth(100)
        tool_btn_disabled.setEnabled(False)
        btn_layout.addWidget(tool_btn_disabled)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoScrollableMenu(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("07. ela_ext - ElaScrollableMenu 可滚动菜单")
        )
        self._addInfoText(
            "点击按钮弹出可滚动菜单，支持任意 widget 和滚动",
            parent_layout,
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        menu_btn = ElaPushButton("打开菜单", self)
        menu_btn.setFixedWidth(100)

        def _show_menu():
            menu = ElaScrollableMenu(menu_btn)
            for i in range(15):
                cb = QCheckBox(f"选项 {i + 1}", menu.scrollWidget)
                menu.addWidgetAction(cb)
            menu.scrollArea.setMinimumHeight(300)
            menu.scrollArea.setMaximumHeight(400)
            menu.popup(menu_btn.mapToGlobal(menu_btn.rect().bottomLeft()))

        menu_btn.clicked.connect(_show_menu)
        btn_layout.addWidget(menu_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoMessageDialog(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("08. pyqt5_ela_pro - ElaMessageDialog 消息对话框")
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

    def _demoNotifyPopup(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("08. pyqt5_ela_pro - ElaNotifyPopup 通知弹窗")
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
