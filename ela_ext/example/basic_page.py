"""
[ela_ext] 基础组件演示页面 - PyQt5ElaWidgetTools
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import (
    ElaText,
    ElaCheckBox,
    ElaRadioButton,
    ElaToggleSwitch,
    ElaToggleButton,
    ElaIconButton,
    ElaMessageButton,
    ElaMessageBarType,
    ElaScrollBar,
    ElaScrollArea,
    ElaProgressBar,
    ElaIconType,
)
from .base_page import ExamplePage


class BasicComponentsPage(ExamplePage):
    """ela 基础组件演示页面"""

    PAGE_TITLE = "ela 基础组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoCheckBox(main_layout)
        self._demoRadioButton(main_layout)
        self._demoToggleSwitch(main_layout)
        self._demoToggleButton(main_layout)
        self._demoIconButton(main_layout)
        self._demoMessageButton(main_layout)
        self._demoScrollBar(main_layout)

    def _demoCheckBox(self, parent_layout):
        section = ElaText("01. ElaCheckBox - 复选框", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("复选框组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        checkbox_layout = QHBoxLayout()
        checkbox_layout.setSpacing(15)

        checkbox = ElaCheckBox("复选框", self)
        checkbox_layout.addWidget(checkbox)

        checkbox_disabled = ElaCheckBox("禁用", self)
        checkbox_disabled.setEnabled(False)
        checkbox_layout.addWidget(checkbox_disabled)

        checkbox_layout.addStretch()
        parent_layout.addLayout(checkbox_layout)
        parent_layout.addSpacing(20)

    def _demoRadioButton(self, parent_layout):
        section = ElaText("02. ElaRadioButton - 单选按钮", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("单选按钮组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(15)

        radio1 = ElaRadioButton("选项1", self)
        radio_layout.addWidget(radio1)

        radio2 = ElaRadioButton("选项2", self)
        radio2.setChecked(True)
        radio_layout.addWidget(radio2)

        radio_disabled = ElaRadioButton("禁用", self)
        radio_disabled.setEnabled(False)
        radio_layout.addWidget(radio_disabled)

        radio_layout.addStretch()
        parent_layout.addLayout(radio_layout)
        parent_layout.addSpacing(20)

    def _demoToggleSwitch(self, parent_layout):
        section = ElaText("03. ElaToggleSwitch - 开关", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("开关组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        switch_layout = QHBoxLayout()
        switch_layout.setSpacing(15)

        toggle_switch = ElaToggleSwitch(self)
        switch_layout.addWidget(toggle_switch)

        switch_disabled = ElaToggleSwitch(self)
        switch_disabled.setEnabled(False)
        switch_layout.addWidget(switch_disabled)

        switch_layout.addStretch()
        parent_layout.addLayout(switch_layout)
        parent_layout.addSpacing(20)

    def _demoToggleButton(self, parent_layout):
        section = ElaText("04. ElaToggleButton - 切换按钮", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("切换按钮组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        toggle_btn = ElaToggleButton("ToggleButton", self)
        toggle_btn.setFixedWidth(120)
        btn_layout.addWidget(toggle_btn)

        toggle_btn_disabled = ElaToggleButton("禁用", self)
        toggle_btn_disabled.setFixedWidth(120)
        toggle_btn_disabled.setEnabled(False)
        btn_layout.addWidget(toggle_btn_disabled)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoIconButton(self, parent_layout):
        section = ElaText("05. ElaIconButton - 图标按钮", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("图标按钮组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

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

    def _demoMessageButton(self, parent_layout):
        section = ElaText("06. ElaMessageButton - 消息按钮", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("消息按钮组件，点击显示消息条", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        success_btn = ElaMessageButton("Success", self)
        success_btn.setBarTitle("Success")
        success_btn.setBarText("操作成功完成！")
        btn_layout.addWidget(success_btn)

        info_btn = ElaMessageButton("Info", self)
        info_btn.setBarTitle("Information")
        info_btn.setBarText("这是一条信息提示")
        info_btn.setMessageMode(ElaMessageBarType.MessageMode.Information)
        info_btn.setPositionPolicy(ElaMessageBarType.PositionPolicy.TopLeft)
        btn_layout.addWidget(info_btn)

        warning_btn = ElaMessageButton("Warning", self)
        warning_btn.setBarTitle("Warning")
        warning_btn.setBarText("警告，请注意！")
        warning_btn.setMessageMode(ElaMessageBarType.MessageMode.Warning)
        warning_btn.setPositionPolicy(ElaMessageBarType.PositionPolicy.BottomLeft)
        btn_layout.addWidget(warning_btn)

        error_btn = ElaMessageButton("Error", self)
        error_btn.setBarTitle("Error")
        error_btn.setBarText("发生错误！")
        error_btn.setMessageMode(ElaMessageBarType.MessageMode.Error)
        error_btn.setPositionPolicy(ElaMessageBarType.PositionPolicy.BottomRight)
        btn_layout.addWidget(error_btn)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoScrollBar(self, parent_layout):
        section = ElaText("07. ElaScrollBar - 滚动条", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("滚动条组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        scroll_layout = QHBoxLayout()
        scroll_layout.setSpacing(15)

        scroll_bar = ElaScrollBar(self)
        scroll_bar.setFixedHeight(100)
        scroll_layout.addWidget(scroll_bar)

        scroll_layout.addStretch()
        parent_layout.addLayout(scroll_layout)
        parent_layout.addSpacing(20)
