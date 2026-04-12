"""
[pyqt5_ela_pro] 表单与按钮组件页面

合并了以下来源的组件:
- pyqt5_ela_pro: 表单组件
- PyQt5ElaWidgetTools: 按钮组件
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit
from PyQt5ElaWidgetTools import ElaText, ElaPushButton, ElaIconType
from pyqt5_ela_pro import (
    ThemeWidget,
    ElaCapsuleLineEdit,
    ElaTagBox,
    ElaTagMultiBox,
    ElaTagSearchBox,
    ElaTagSearchMultiBox,
    ElaSearchBox,
    ElaSearchMultiBox,
    ElaLongPressBtn,
    ElaPrimaryBtn,
    ElaToolBtn,
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
        self._demoCapsuleLineEdit(parent_layout)
        self._demoCapsuleComboBox(parent_layout)
        self._demoCapsuleMultiCombo(parent_layout)
        self._demoCapsuleSearchableCombo(parent_layout)
        self._demoCapsuleSearchableMultiCombo(parent_layout)
        self._demoSearchableCombo(parent_layout)
        self._demoSearchableMultiCombo(parent_layout)

    def _demoButton(self, parent_layout):
        self._demoPrimaryButton(parent_layout)
        self._demoLongPressButton(parent_layout)
        self._demoToolButtonExt(parent_layout)

    def _addInfoText(self, text, parent_layout):
        info = ElaText(text, self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

    def _demoCapsuleLineEdit(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("01. ela_ext - ElaCapsuleLineEdit 具名输入框")
        )
        self._addInfoText(
            "带有标题标签的输入框组件，支持主题适配和错误状态", parent_layout
        )
        edit_layout = QVBoxLayout()
        edit_layout.setSpacing(15)
        self._nameEdit = ElaCapsuleLineEdit(self, title="用户名")
        self._nameEdit.setFixedWidth(300)
        self._nameEdit.setText("admin")
        edit_layout.addWidget(self._nameEdit)
        self._passwordEdit = ElaCapsuleLineEdit(self, title="密码")
        self._passwordEdit.setFixedWidth(300)
        self._passwordEdit.setEchoMode(QLineEdit.Password)
        edit_layout.addWidget(self._passwordEdit)
        email_edit = ElaCapsuleLineEdit(self, title="邮箱")
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

    def _demoCapsuleComboBox(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("02. ela_ext - ElaTagBox 具名组合框")
        )
        self._addInfoText("带有标题标签的组合框，只读模式", parent_layout)
        combo_layout = QHBoxLayout()
        combo_layout.setSpacing(15)
        combo_readonly = ElaTagBox(self, title="语言")
        combo_readonly.setFixedWidth(200)
        combo_readonly.addItems(["Python", "C++", "JavaScript", "Rust", "Go"])
        combo_layout.addWidget(combo_readonly)
        combo_disabled = ElaTagBox(self, title="禁用")
        combo_disabled.setFixedWidth(200)
        combo_disabled.setEnabled(False)
        combo_disabled.addItems(["Python", "C++", "JavaScript"])
        combo_layout.addWidget(combo_disabled)
        combo_layout.addStretch()
        parent_layout.addLayout(combo_layout)
        parent_layout.addSpacing(20)

    def _demoCapsuleMultiCombo(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("03. ela_ext - ElaTagMultiBox 具名多选组合框")
        )
        self._addInfoText("带有标题标签的多选组合框，支持多选功能", parent_layout)
        combo_layout = QHBoxLayout()
        combo_layout.setSpacing(15)
        multi_combo = ElaTagMultiBox(self, title="语言")
        multi_combo.setFixedWidth(300)
        items = ["Python", "C++", "JavaScript", "Rust", "Go", "TypeScript"]
        multi_combo.addItems(items)
        multi_combo.setCurrentSelection(["Python", "C++"])
        combo_layout.addWidget(multi_combo)
        combo_layout.addStretch()
        parent_layout.addLayout(combo_layout)
        parent_layout.addSpacing(20)

    def _demoCapsuleSearchableCombo(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "04. pyqt5_ela_pro - ElaTagSearchBox 具名可搜索组合框"
            )
        )
        self._addInfoText("带有标题标签的可搜索组合框，支持中文拼音搜索", parent_layout)
        search_combo = ElaTagSearchBox(self, title="语言")
        items = [
            "Python",
            "JavaScript",
            "C++",
            "Java",
            "Go",
            "Rust",
            "TypeScript",
            "Swift",
            "Kotlin",
            "Ruby",
            "PHP",
            "C#",
            "上海",
            "北京",
            "深圳",
        ]
        search_combo.addItems(items)
        parent_layout.addWidget(search_combo)
        parent_layout.addSpacing(20)

    def _demoCapsuleSearchableMultiCombo(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "05. pyqt5_ela_pro - ElaTagSearchMultiBox 具名可搜索多选下拉框"
            )
        )
        self._addInfoText(
            "带有标题标签的可搜索多选下拉框，支持中文拼音搜索", parent_layout
        )
        combo_layout = QHBoxLayout()
        combo_layout.setSpacing(15)
        searchable_multi_combo = ElaTagSearchMultiBox(self, title="语言")
        searchable_multi_combo.setFixedWidth(300)
        items = [
            "Python",
            "JavaScript",
            "C++",
            "Java",
            "Go",
            "Rust",
            "TypeScript",
            "上海",
            "北京",
            "深圳",
        ]
        searchable_multi_combo.addItems(items)
        searchable_multi_combo.setCurrentSelection(["Python", "上海"])
        combo_layout.addWidget(searchable_multi_combo)
        combo_layout.addStretch()
        parent_layout.addLayout(combo_layout)
        parent_layout.addSpacing(20)

    def _demoSearchableCombo(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("08. pyqt5_ela_pro - ElaSearchBox 可搜索组合框")
        )
        self._addInfoText("可搜索组合框组件", parent_layout)
        search_combo = ElaSearchBox(self)
        items = [
            "Python",
            "JavaScript",
            "C++",
            "Java",
            "Go",
            "Rust",
            "TypeScript",
            "Swift",
            "Kotlin",
            "Ruby",
            "PHP",
            "C#",
        ]
        search_combo.addItems(items)
        parent_layout.addWidget(search_combo)
        parent_layout.addSpacing(20)

    def _demoSearchableMultiCombo(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "09. pyqt5_ela_pro - ElaSearchMultiBox 可搜索多选下拉框"
            )
        )
        self._addInfoText("可搜索多选下拉框组件，支持中文拼音搜索", parent_layout)
        combo_layout = QHBoxLayout()
        combo_layout.setSpacing(15)
        searchable_multi_combo = ElaSearchMultiBox(self)
        searchable_multi_combo.setFixedWidth(300)
        items = [
            "Python",
            "JavaScript",
            "C++",
            "Java",
            "Go",
            "Rust",
            "TypeScript",
            "上海",
            "北京",
            "深圳",
        ]
        searchable_multi_combo.addItems(items)
        searchable_multi_combo.setCurrentSelection(["Python", "上海"])
        combo_layout.addWidget(searchable_multi_combo)
        combo_layout.addStretch()
        parent_layout.addLayout(combo_layout)
        parent_layout.addSpacing(20)

    def _demoPrimaryButton(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("01. PyQt5ElaWidgetTools - ElaPushButton 按钮")
        )
        self._addInfoText("按钮组件", parent_layout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        primary_btn = ElaPushButton("按钮", self)
        primary_btn.setFixedWidth(120)
        primary_btn.clicked.connect(
            lambda: QMessageBox.information(self, "提示", "按钮 clicked")
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
            self._createSectionHeader("01. ela_ext - ElaPrimaryBtn 主要按钮")
        )
        self._addInfoText(
            "使用 Primary 主题色的按钮，与 ElaToggleButton ON 状态外观一致",
            parent_layout,
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        primary_btn = ElaPrimaryBtn(self)
        primary_btn.setText("主要按钮")
        primary_btn.setFixedWidth(120)
        primary_btn.clicked.connect(
            lambda: QMessageBox.information(self, "提示", "ElaPrimaryBtn clicked")
        )
        btn_layout.addWidget(primary_btn)
        primary_btn_icon = ElaPrimaryBtn(self)
        primary_btn_icon.setText("带图标")
        primary_btn_icon.setFixedWidth(120)
        primary_btn_icon.setElaIcon(ElaIconType.IconName.FloppyDisk, 16)
        btn_layout.addWidget(primary_btn_icon)
        primary_btn_disabled = ElaPrimaryBtn(self)
        primary_btn_disabled.setText("禁用状态")
        primary_btn_disabled.setFixedWidth(120)
        primary_btn_disabled.setEnabled(False)
        btn_layout.addWidget(primary_btn_disabled)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

        parent_layout.addWidget(
            self._createSectionHeader("02. ela_ext - ElaLongPressBtn 长按按钮")
        )
        self._addInfoText(
            "按住按钮一段时间后才能触发点击事件，适合危险操作防误触", parent_layout
        )
        btn_layout2 = QHBoxLayout()
        btn_layout2.setSpacing(15)
        self._longPressBtn = ElaLongPressBtn(self, duration=800)
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
        QMessageBox.information(self, "提示", "长按触发成功！")

    def _demoToolButtonExt(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("03. ela_ext - ElaToolBtn 图标文字并排按钮")
        )
        self._addInfoText(
            "ToolButton 样式设置为文字在图标旁边，适合工具栏使用", parent_layout
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        tool_btn = ElaToolBtn(self)
        tool_btn.setText("保存")
        tool_btn.setFixedWidth(100)
        tool_btn.setElaIcon(ElaIconType.IconName.FloppyDisk)
        tool_btn.clicked.connect(
            lambda: QMessageBox.information(self, "提示", "保存 clicked")
        )
        btn_layout.addWidget(tool_btn)
        tool_btn_icon = ElaToolBtn(self)
        tool_btn_icon.setText("编辑")
        tool_btn_icon.setFixedWidth(100)
        tool_btn_icon.setElaIcon(ElaIconType.IconName.Pencil)
        tool_btn_icon.clicked.connect(
            lambda: QMessageBox.information(self, "提示", "编辑 clicked")
        )
        btn_layout.addWidget(tool_btn_icon)
        tool_btn_disabled = ElaToolBtn(self)
        tool_btn_disabled.setText("禁用")
        tool_btn_disabled.setFixedWidth(100)
        tool_btn_disabled.setEnabled(False)
        btn_layout.addWidget(tool_btn_disabled)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)
