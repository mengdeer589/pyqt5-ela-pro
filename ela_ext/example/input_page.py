"""
[ela_ext] 输入组件演示页面
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import (
    ElaText,
    ElaLineEdit,
    ElaPlainTextEdit,
    ElaSpinBox,
    ElaDoubleSpinBox,
    ElaSlider,
    ElaCalendar,
    ElaCalendarPicker,
    ElaComboBox,
    ElaMultiSelectComboBox,
    ElaLCDNumber,
)
from .base_page import ExamplePage


class InputComponentsPage(ExamplePage):
    """ela 输入组件演示页面"""

    PAGE_TITLE = "ela 输入组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoLineEdit(main_layout)
        self._demoPlainTextEdit(main_layout)
        self._demoSpinBox(main_layout)
        self._demoDoubleSpinBox(main_layout)
        self._demoSlider(main_layout)
        self._demoCalendar(main_layout)
        self._demoCalendarPicker(main_layout)
        self._demoComboBox(main_layout)
        self._demoMultiSelectComboBox(main_layout)
        self._demoLCDNumber(main_layout)

    def _demoLineEdit(self, parent_layout):
        section = ElaText("01. ElaLineEdit - 单行输入框", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("标准单行输入框组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        edit_layout = QHBoxLayout()
        edit_layout.setSpacing(15)

        line_edit = ElaLineEdit(self)
        line_edit.setPlaceholderText("请输入文本")
        line_edit.setFixedWidth(200)
        edit_layout.addWidget(line_edit)

        line_edit_disabled = ElaLineEdit(self)
        line_edit_disabled.setPlaceholderText("禁用状态")
        line_edit_disabled.setFixedWidth(200)
        line_edit_disabled.setEnabled(False)
        edit_layout.addWidget(line_edit_disabled)

        edit_layout.addStretch()
        parent_layout.addLayout(edit_layout)
        parent_layout.addSpacing(20)

    def _demoPlainTextEdit(self, parent_layout):
        section = ElaText("02. ElaPlainTextEdit - 多行文本编辑", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("多行文本编辑组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        text_edit = ElaPlainTextEdit(self)
        text_edit.setPlaceholderText("请输入多行文本...")
        text_edit.setFixedHeight(100)
        parent_layout.addWidget(text_edit)
        parent_layout.addSpacing(20)

    def _demoSpinBox(self, parent_layout):
        section = ElaText("03. ElaSpinBox - 整数微调框", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("整数微调框组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        spin_layout = QHBoxLayout()
        spin_layout.setSpacing(15)

        spin_box = ElaSpinBox(self)
        spin_box.setFixedWidth(150)
        spin_layout.addWidget(spin_box)

        spin_layout.addStretch()
        parent_layout.addLayout(spin_layout)
        parent_layout.addSpacing(20)

    def _demoDoubleSpinBox(self, parent_layout):
        section = ElaText("04. ElaDoubleSpinBox - 浮点数微调框", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("浮点数微调框组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        dspin_layout = QHBoxLayout()
        dspin_layout.setSpacing(15)

        dspin_box = ElaDoubleSpinBox(self)
        dspin_box.setFixedWidth(150)
        dspin_box.setDecimals(2)
        dspin_layout.addWidget(dspin_box)

        dspin_layout.addStretch()
        parent_layout.addLayout(dspin_layout)
        parent_layout.addSpacing(20)

    def _demoSlider(self, parent_layout):
        section = ElaText("05. ElaSlider - 滑块", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("滑块组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(15)

        slider = ElaSlider(self)
        slider.setFixedWidth(200)
        slider_layout.addWidget(slider)

        slider_layout.addStretch()
        parent_layout.addLayout(slider_layout)
        parent_layout.addSpacing(20)

    def _demoCalendar(self, parent_layout):
        section = ElaText("06. ElaCalendar - 日历", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("日历组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        calendar = ElaCalendar(self)
        calendar.setFixedWidth(280)
        parent_layout.addWidget(calendar)
        parent_layout.addSpacing(20)

    def _demoCalendarPicker(self, parent_layout):
        section = ElaText("07. ElaCalendarPicker - 日期选择器", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("日期选择器组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        picker_layout = QHBoxLayout()
        picker_layout.setSpacing(15)

        calendar_picker = ElaCalendarPicker(self)
        calendar_picker.setFixedWidth(150)
        picker_layout.addWidget(calendar_picker)

        picker_layout.addStretch()
        parent_layout.addLayout(picker_layout)
        parent_layout.addSpacing(20)

    def _demoComboBox(self, parent_layout):
        section = ElaText("08. ElaComboBox - 下拉框", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("下拉框组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        combo_layout = QHBoxLayout()
        combo_layout.setSpacing(15)

        combo = ElaComboBox(self)
        combo.addItems(["选项1", "选项2", "选项3", "选项4"])
        combo.setFixedWidth(150)
        combo_layout.addWidget(combo)

        combo_layout.addStretch()
        parent_layout.addLayout(combo_layout)
        parent_layout.addSpacing(20)

    def _demoMultiSelectComboBox(self, parent_layout):
        section = ElaText("09. ElaMultiSelectComboBox - 多选下拉框", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("多选下拉框组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        combo_layout = QHBoxLayout()
        combo_layout.setSpacing(15)

        multi_combo = ElaMultiSelectComboBox(self)
        items = ["Python", "JavaScript", "C++", "Java", "Go", "Rust", "TypeScript"]
        multi_combo.addItems(items)
        multi_combo.setCurrentSelection(["Python", "C++"])
        combo_layout.addWidget(multi_combo)

        combo_layout.addStretch()
        parent_layout.addLayout(combo_layout)
        parent_layout.addSpacing(20)

    def _demoLCDNumber(self, parent_layout):
        section = ElaText("10. ElaLCDNumber - LCD数字显示", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("LCD数字显示组件，支持自动时钟和透明背景", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        lcd_layout = QHBoxLayout()
        lcd_layout.setSpacing(15)

        lcd = ElaLCDNumber(self)
        lcd.setFixedHeight(100)
        lcd.setIsUseAutoClock(True)
        lcd.setIsTransparent(False)
        lcd_layout.addWidget(lcd)

        lcd_layout.addStretch()
        parent_layout.addLayout(lcd_layout)
        parent_layout.addSpacing(20)
