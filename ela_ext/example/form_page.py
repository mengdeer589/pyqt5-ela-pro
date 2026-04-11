"""
[ela_ext] 表单组件演示页面
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import ElaText, ElaPushButton
from ela_ext import (
    ThemeWidget,
    ElaCapsuleLineEdit,
    ElaCapsuleComboBox,
    ElaMultiSelectComboBox,
    ElaSingleSelectComboBox,
    ElaSearchableComboBox,
)
from .base_page import ExamplePage


class FormComponentsPage(ExamplePage):
    """表单组件演示页面"""

    PAGE_TITLE = "[ela_ext] 表单组件"

    def __init__(self, parent=None):
        self._nameEdit = None
        self._passwordEdit = None
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoCapsuleLineEdit(main_layout)
        self._demoCapsuleComboBox(main_layout)
        self._demoMultiSelectCombo(main_layout)
        self._demoSingleSelectCombo(main_layout)
        self._demoSearchableCombo(main_layout)

    def _demoCapsuleLineEdit(self, parent_layout):
        section = ElaText("01. ElaCapsuleLineEdit - 具名输入框", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText(
            "带有标题标签的输入框组件，支持主题适配和错误状态",
            self,
        )
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        edit_layout = QVBoxLayout()
        edit_layout.setSpacing(15)

        self._nameEdit = ElaCapsuleLineEdit(self, title="用户名")
        self._nameEdit.setFixedWidth(300)
        self._nameEdit.setText("admin")
        edit_layout.addWidget(self._nameEdit)

        self._passwordEdit = ElaCapsuleLineEdit(self, title="密码")
        self._passwordEdit.setFixedWidth(300)
        self._passwordEdit.setEchoMode(2)
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
        section = ElaText("02. ElaCapsuleComboBox - 具名组合框", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("带有标题标签的组合框，只读模式", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        combo_layout = QHBoxLayout()
        combo_layout.setSpacing(15)

        combo_readonly = ElaCapsuleComboBox(self, title="语言")
        combo_readonly.setFixedWidth(200)
        combo_readonly.addItems(["Python", "C++", "JavaScript", "Rust", "Go"])
        combo_layout.addWidget(combo_readonly)

        combo_disabled = ElaCapsuleComboBox(self, title="禁用")
        combo_disabled.setFixedWidth(200)
        combo_disabled.setEnabled(False)
        combo_disabled.addItems(["Python", "C++", "JavaScript"])
        combo_layout.addWidget(combo_disabled)

        combo_layout.addStretch()
        parent_layout.addLayout(combo_layout)
        parent_layout.addSpacing(20)

    def _demoMultiSelectCombo(self, parent_layout):
        section = ElaText("03. ElaMultiSelectComboBox - 多选组合框", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        multi_combo = ElaMultiSelectComboBox(self)
        items = ["Python", "JavaScript", "C++", "Java", "Go", "Rust", "TypeScript"]
        multi_combo.addItems(items)
        multi_combo.setCurrentSelection(["Python", "C++"])
        parent_layout.addWidget(multi_combo)
        parent_layout.addSpacing(20)

    def _demoSingleSelectCombo(self, parent_layout):
        section = ElaText("04. ElaSingleSelectComboBox - 单选组合框", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        single_combo = ElaSingleSelectComboBox(self)
        items = ["Windows", "macOS", "Linux", "iOS", "Android"]
        single_combo.addItems(items)
        parent_layout.addWidget(single_combo)
        parent_layout.addSpacing(20)

    def _demoSearchableCombo(self, parent_layout):
        section = ElaText("05. ElaSearchableComboBox - 可搜索组合框", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        search_combo = ElaSearchableComboBox(self)
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
