"""
[pyqt5_ela_pro] 下拉框组件页面

展示所有 8 个下拉框组件:
- PyQt5ElaWidgetTools 自带: ElaComboBox, ElaMultiSelectComboBox
- pyqt5_ela_pro 封装: ElaSearchBox, ElaSearchMultiBox,
                     ElaTagBox, ElaTagMultiBox,
                     ElaTagSearchBox, ElaTagSearchMultiBox
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

from PyQt5ElaWidgetTools import (
    ElaComboBox,
    ElaMultiSelectComboBox,
    ElaPushButton,
    ElaText,
)
from pyqt5_ela_pro import (
    ElaThemeWidget,
    ElaSearchBox,
    ElaSearchMultiBox,
    ElaTagBox,
    ElaTagMultiBox,
    ElaTagSearchBox,
    ElaTagSearchMultiBox,
    ElaMessageDialog,
)
from .base_page import ExamplePage


COMBO_BOX_ITEMS = [
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
    "广州",
    "杭州",
    "成都",
]


class ComboBoxPage(ExamplePage):
    """下拉框组件页面"""

    PAGE_TITLE = "下拉框组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoElaComboBox(main_layout)
        self._demoElaMultiSelectComboBox(main_layout)
        self._demoSearchableComboBox(main_layout)
        self._demoSearchableMultiComboBox(main_layout)
        self._demoCapsuleComboBox(main_layout)
        self._demoCapsuleMultiComboBox(main_layout)
        self._demoCapsuleSearchableComboBox(main_layout)
        self._demoCapsuleSearchableMultiComboBox(main_layout)
        self._demoEmptyCombos(main_layout)

    def _createRowLayout(self, parent_layout):
        row_layout = QHBoxLayout()
        row_layout.setSpacing(15)
        parent_layout.addLayout(row_layout)
        return row_layout

    def _demoElaComboBox(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "01. PyQt5ElaWidgetTools - ElaComboBox 基础单选下拉框"
            )
        )
        self._addInfoText("PyQt5ElaWidgetTools 原生提供的单选下拉框组件", parent_layout)
        row = self._createRowLayout(parent_layout)
        combo = ElaComboBox(self)
        combo.addItems(COMBO_BOX_ITEMS)
        combo.setFixedWidth(250)
        row.addWidget(combo)
        btn = ElaPushButton("显示选中", self)
        btn.setFixedWidth(100)
        btn.clicked.connect(
            lambda: ElaMessageDialog.show(
                self, "当前选中", f"当前选中: {combo.currentText()}"
            )
        )
        row.addWidget(btn)
        row.addSpacing(20)
        combo_disabled = ElaComboBox(self)
        combo_disabled.addItems(COMBO_BOX_ITEMS)
        combo_disabled.setFixedWidth(250)
        combo_disabled.setEnabled(False)
        row.addWidget(combo_disabled)
        row.addStretch()
        parent_layout.addSpacing(30)

    def _demoElaMultiSelectComboBox(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "02. PyQt5ElaWidgetTools - ElaMultiSelectComboBox 基础多选下拉框"
            )
        )
        self._addInfoText("PyQt5ElaWidgetTools 原生提供的多选下拉框组件", parent_layout)
        row = self._createRowLayout(parent_layout)
        multi = ElaMultiSelectComboBox(self)
        multi.addItems(COMBO_BOX_ITEMS)
        multi.setFixedWidth(300)
        multi.setCurrentSelection(["Python", "上海"])
        row.addWidget(multi)
        btn = ElaPushButton("显示选中", self)
        btn.setFixedWidth(100)
        btn.clicked.connect(
            lambda: ElaMessageDialog.show(
                self, "当前选中", f"当前选中: {multi.getCurrentSelection()}"
            )
        )
        row.addWidget(btn)
        row.addStretch()
        parent_layout.addSpacing(30)

    def _demoSearchableComboBox(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "03. pyqt5_ela_pro - ElaSearchBox 可搜索单选下拉框"
            )
        )
        self._addInfoText(
            "基于 ElaComboBox 的可搜索下拉框，支持中文拼音首字母搜索",
            parent_layout,
        )
        row = self._createRowLayout(parent_layout)
        combo = ElaSearchBox(self)
        combo.addItems(COMBO_BOX_ITEMS)
        combo.setFixedWidth(250)
        row.addWidget(combo)
        btn = ElaPushButton("显示选中", self)
        btn.setFixedWidth(100)
        btn.clicked.connect(
            lambda: ElaMessageDialog.show(
                self, "当前选中", f"当前选中: {combo.currentText()}"
            )
        )
        row.addWidget(btn)
        row.addStretch()
        parent_layout.addSpacing(30)

    def _demoSearchableMultiComboBox(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "04. pyqt5_ela_pro - ElaSearchMultiBox 可搜索多选下拉框"
            )
        )
        self._addInfoText(
            "基于 ElaMultiSelectComboBox 的可搜索多选下拉框，支持中文拼音首字母搜索",
            parent_layout,
        )
        row = self._createRowLayout(parent_layout)
        multi = ElaSearchMultiBox(self)
        multi.addItems(COMBO_BOX_ITEMS)
        multi.setFixedWidth(300)
        multi.setCurrentSelection(["Python", "上海"])
        row.addWidget(multi)
        btn = ElaPushButton("显示选中", self)
        btn.setFixedWidth(100)
        btn.clicked.connect(
            lambda: ElaMessageDialog.show(
                self, "当前选中", f"当前选中: {multi.getCurrentSelection()}"
            )
        )
        row.addWidget(btn)
        row.addStretch()
        parent_layout.addSpacing(30)

    def _demoCapsuleComboBox(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "05. pyqt5_ela_pro - ElaTagBox 标签样式单选下拉框"
            )
        )
        self._addInfoText(
            "带有标题标签的标签样式组合框，展开时显示底部主题色横条动画",
            parent_layout,
        )
        row = self._createRowLayout(parent_layout)
        combo = ElaTagBox(self, title="语言")
        combo.addItems(COMBO_BOX_ITEMS)
        combo.setFixedWidth(250)
        row.addWidget(combo)
        btn = ElaPushButton("显示选中", self)
        btn.setFixedWidth(100)
        btn.clicked.connect(
            lambda: ElaMessageDialog.show(
                self, "当前选中", f"当前选中: {combo.currentText()}"
            )
        )
        row.addWidget(btn)
        row.addSpacing(20)
        combo_disabled = ElaTagBox(self, title="禁用")
        combo_disabled.setEnabled(False)
        combo_disabled.addItems(COMBO_BOX_ITEMS)
        combo_disabled.setFixedWidth(250)
        row.addWidget(combo_disabled)
        row.addStretch()
        parent_layout.addSpacing(30)

    def _demoCapsuleMultiComboBox(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "06. pyqt5_ela_pro - ElaTagMultiBox 标签样式多选下拉框"
            )
        )
        self._addInfoText(
            "带有标题标签的标签样式多选下拉框，底部横条宽度根据选中数量动态变化",
            parent_layout,
        )
        row = self._createRowLayout(parent_layout)
        multi = ElaTagMultiBox(self, title="语言")
        multi.addItems(COMBO_BOX_ITEMS)
        multi.setFixedWidth(300)
        multi.setCurrentSelection(["Python", "上海", "C++"])
        row.addWidget(multi)
        btn = ElaPushButton("显示选中", self)
        btn.setFixedWidth(100)
        btn.clicked.connect(
            lambda: ElaMessageDialog.show(
                self, "当前选中", f"当前选中: {multi.getCurrentSelection()}"
            )
        )
        row.addWidget(btn)
        row.addStretch()
        parent_layout.addSpacing(30)

    def _demoCapsuleSearchableComboBox(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "07. pyqt5_ela_pro - ElaTagSearchBox 标签样式可搜索单选下拉框"
            )
        )
        self._addInfoText(
            "带有标题标签的标签样式可搜索单选下拉框，结合了搜索和动画效果",
            parent_layout,
        )
        row = self._createRowLayout(parent_layout)
        combo = ElaTagSearchBox(self, title="语言")
        combo.addItems(COMBO_BOX_ITEMS)
        combo.setFixedWidth(250)
        row.addWidget(combo)
        btn = ElaPushButton("显示选中", self)
        btn.setFixedWidth(100)
        btn.clicked.connect(
            lambda: ElaMessageDialog.show(
                self, "当前选中", f"当前选中: {combo.currentText()}"
            )
        )
        row.addWidget(btn)
        row.addStretch()
        parent_layout.addSpacing(30)

    def _demoCapsuleSearchableMultiComboBox(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "08. pyqt5_ela_pro - ElaTagSearchMultiBox 标签样式可搜索多选下拉框"
            )
        )
        self._addInfoText(
            "带有标题标签的标签样式可搜索多选下拉框，支持拼音搜索和多选",
            parent_layout,
        )
        row = self._createRowLayout(parent_layout)
        multi = ElaTagSearchMultiBox(self, title="语言")
        multi.addItems(COMBO_BOX_ITEMS)
        multi.setFixedWidth(300)
        multi.setCurrentSelection(["Python", "上海"])
        row.addWidget(multi)
        btn = ElaPushButton("显示选中", self)
        btn.setFixedWidth(100)
        btn.clicked.connect(
            lambda: ElaMessageDialog.show(
                self, "当前选中", f"当前选中: {multi.getCurrentSelection()}"
            )
        )
        row.addWidget(btn)
        row.addStretch()
        parent_layout.addSpacing(30)

    def _demoEmptyCombos(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "09. 空选项状态 — 无选项时的外观"
            )
        )
        self._addInfoText(
            "所有 6 个自定义下拉框在无选项时的显示效果，点击触发按钮不弹出空白菜单",
            parent_layout,
        )
        row = self._createRowLayout(parent_layout)
        # ElaSearchBox (empty)
        empty_search = ElaSearchBox(self)
        empty_search.setFixedWidth(180)
        row.addWidget(empty_search)
        # ElaSearchMultiBox (empty)
        empty_search_multi = ElaSearchMultiBox(self)
        empty_search_multi.setFixedWidth(180)
        row.addWidget(empty_search_multi)
        # ElaTagBox (empty)
        empty_tag = ElaTagBox(self, title="单选")
        empty_tag.setFixedWidth(150)
        row.addWidget(empty_tag)
        # ElaTagMultiBox (empty)
        empty_tag_multi = ElaTagMultiBox(self, title="多选")
        empty_tag_multi.setFixedWidth(150)
        row.addWidget(empty_tag_multi)
        # ElaTagSearchBox (empty)
        empty_tag_search = ElaTagSearchBox(self, title="搜索")
        empty_tag_search.setFixedWidth(150)
        row.addWidget(empty_tag_search)
        # ElaTagSearchMultiBox (empty)
        empty_tag_search_multi = ElaTagSearchMultiBox(self, title="搜索多选")
        empty_tag_search_multi.setFixedWidth(150)
        row.addWidget(empty_tag_search_multi)
        row.addStretch()
        parent_layout.addSpacing(20)
