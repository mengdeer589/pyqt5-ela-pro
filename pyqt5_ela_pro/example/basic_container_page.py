"""
[pyqt5_ela_pro] 基础组件页面

包含 PyQt5ElaWidgetTools 的输入、基础交互、导航组件。
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5ElaWidgetTools import (
    ElaText, ElaLineEdit, ElaPlainTextEdit, ElaSpinBox, ElaDoubleSpinBox,
    ElaSlider, ElaCalendar, ElaCalendarPicker, ElaLCDNumber,
    ElaCheckBox, ElaRadioButton, ElaToggleSwitch, ElaToggleButton,
    ElaPushButton, ElaToolButton, ElaIconButton, ElaMessageButton,
    ElaMessageBarType, ElaScrollBar, ElaToolBar,
    ElaBreadcrumbBar, ElaPivot, ElaTabBar, ElaTabWidget,
    ElaIconType,
)
from .base_page import ExamplePage


class BasicContainerPage(ExamplePage):
    """基础组件页面"""

    PAGE_TITLE = "基础组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoInput(main_layout)
        self._demoBasic(main_layout)
        self._demoNavigation(main_layout)

    def _demoInput(self, parent_layout):
        self._demoLineEdit(parent_layout)
        self._demoPlainTextEdit(parent_layout)
        self._demoSpinBox(parent_layout)
        self._demoDoubleSpinBox(parent_layout)
        self._demoSlider(parent_layout)
        self._demoCalendar(parent_layout)
        self._demoCalendarPicker(parent_layout)
        self._demoLCDNumber(parent_layout)

    def _demoBasic(self, parent_layout):
        self._demoCheckBox(parent_layout)
        self._demoRadioButton(parent_layout)
        self._demoToggleSwitch(parent_layout)
        self._demoToggleButton(parent_layout)
        self._demoPushButton(parent_layout)
        self._demoToolButton(parent_layout)
        self._demoIconButton(parent_layout)
        self._demoMessageButton(parent_layout)
        self._demoScrollBar(parent_layout)
        self._demoToolBar(parent_layout)

    def _demoNavigation(self, parent_layout):
        self._demoBreadcrumbBar(parent_layout)
        self._demoPivot(parent_layout)
        self._demoTabBar(parent_layout)
        self._demoTabWidget(parent_layout)

    def _demoLineEdit(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("01. PyQt5ElaWidgetTools - ElaLineEdit 单行输入框", self._demoLineEdit)
        )
        self._addInfoText("标准单行输入框组件", parent_layout)
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
        parent_layout.addLayout(
            self._createHeaderRow("02. PyQt5ElaWidgetTools - ElaPlainTextEdit 多行文本编辑", self._demoPlainTextEdit)
        )
        self._addInfoText("多行文本编辑组件", parent_layout)
        text_edit = ElaPlainTextEdit(self)
        text_edit.setPlaceholderText("请输入多行文本...")
        text_edit.setFixedHeight(100)
        parent_layout.addWidget(text_edit)
        parent_layout.addSpacing(20)

    def _demoSpinBox(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("03. PyQt5ElaWidgetTools - ElaSpinBox 整数微调框", self._demoSpinBox)
        )
        self._addInfoText("整数微调框组件", parent_layout)
        spin_layout = QHBoxLayout()
        spin_layout.setSpacing(15)
        spin_box = ElaSpinBox(self)
        spin_box.setFixedWidth(150)
        spin_layout.addWidget(spin_box)
        spin_layout.addStretch()
        parent_layout.addLayout(spin_layout)
        parent_layout.addSpacing(20)

    def _demoDoubleSpinBox(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("04. PyQt5ElaWidgetTools - ElaDoubleSpinBox 浮点数微调框", self._demoDoubleSpinBox)
        )
        self._addInfoText("浮点数微调框组件", parent_layout)
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
        parent_layout.addLayout(
            self._createHeaderRow("05. PyQt5ElaWidgetTools - ElaSlider 滑块", self._demoSlider)
        )
        self._addInfoText("滑块组件，支持 valueChanged 信号实时反馈", parent_layout)
        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(15)
        self._slider = ElaSlider(self)
        self._slider.setFixedWidth(200)
        self._slider.setRange(0, 100)
        self._slider.setValue(50)
        self._slider.valueChanged.connect(self._onSliderValueChanged)
        slider_layout.addWidget(self._slider)
        self._sliderValueLabel = ElaText("50", self)
        self._sliderValueLabel.setTextPixelSize(14)
        self._sliderValueLabel.setFixedWidth(40)
        slider_layout.addWidget(self._sliderValueLabel)
        slider_layout.addStretch()
        parent_layout.addLayout(slider_layout)
        parent_layout.addSpacing(20)

    def _onSliderValueChanged(self, value):
        self._sliderValueLabel.setText(str(value))

    def _demoCalendar(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("06. PyQt5ElaWidgetTools - ElaCalendar 日历", self._demoCalendar)
        )
        self._addInfoText("日历组件", parent_layout)
        calendar = ElaCalendar(self)
        calendar.setFixedWidth(280)
        parent_layout.addWidget(calendar)
        parent_layout.addSpacing(20)

    def _demoCalendarPicker(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("07. PyQt5ElaWidgetTools - ElaCalendarPicker 日期选择器", self._demoCalendarPicker)
        )
        self._addInfoText("日期选择器组件", parent_layout)
        picker_layout = QHBoxLayout()
        picker_layout.setSpacing(15)
        calendar_picker = ElaCalendarPicker(self)
        calendar_picker.setFixedWidth(150)
        picker_layout.addWidget(calendar_picker)
        picker_layout.addStretch()
        parent_layout.addLayout(picker_layout)
        parent_layout.addSpacing(20)

    def _demoLCDNumber(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("08. PyQt5ElaWidgetTools - ElaLCDNumber LCD数字显示", self._demoLCDNumber)
        )
        self._addInfoText("LCD数字显示组件，setIsUseAutoClock(True) 自动显示当前时间", parent_layout)
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

    def _demoCheckBox(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("01. PyQt5ElaWidgetTools - ElaCheckBox 复选框", self._demoCheckBox)
        )
        self._addInfoText("复选框组件", parent_layout)
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
        parent_layout.addLayout(
            self._createHeaderRow("02. PyQt5ElaWidgetTools - ElaRadioButton 单选按钮", self._demoRadioButton)
        )
        self._addInfoText("单选按钮组件", parent_layout)
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
        parent_layout.addLayout(
            self._createHeaderRow("03. PyQt5ElaWidgetTools - ElaToggleSwitch 开关", self._demoToggleSwitch)
        )
        self._addInfoText("开关组件", parent_layout)
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
        parent_layout.addLayout(
            self._createHeaderRow("04. PyQt5ElaWidgetTools - ElaToggleButton 切换按钮", self._demoToggleButton)
        )
        self._addInfoText("切换按钮组件", parent_layout)
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

    def _demoPushButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("05. PyQt5ElaWidgetTools - ElaPushButton 按钮", self._demoPushButton)
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
            self._createHeaderRow("06. PyQt5ElaWidgetTools - ElaToolButton 工具按钮", self._demoToolButton)
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
            self._createHeaderRow("07. PyQt5ElaWidgetTools - ElaIconButton 图标按钮", self._demoIconButton)
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

    def _demoMessageButton(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("08. PyQt5ElaWidgetTools - ElaMessageButton 消息按钮", self._demoMessageButton)
        )
        self._addInfoText("消息按钮组件，点击显示消息条", parent_layout)
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
        parent_layout.addLayout(
            self._createHeaderRow("09. PyQt5ElaWidgetTools - ElaScrollBar 滚动条", self._demoScrollBar)
        )
        self._addInfoText("滚动条组件", parent_layout)
        scroll_layout = QHBoxLayout()
        scroll_layout.setSpacing(15)
        scroll_bar = ElaScrollBar(self)
        scroll_bar.setFixedHeight(100)
        scroll_layout.addWidget(scroll_bar)
        scroll_layout.addStretch()
        parent_layout.addLayout(scroll_layout)
        parent_layout.addSpacing(20)

    def _demoToolBar(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("10. PyQt5ElaWidgetTools - ElaToolBar 工具栏", self._demoToolBar)
        )
        self._addInfoText("工具栏组件，可在工具栏中添加各种组件", parent_layout)
        parent_layout.addSpacing(10)
        toolbar = ElaToolBar(self)
        for i in range(5):
            tool_btn = ElaToolButton(self)
            tool_btn.setText(f"工具{i + 1}")
            tool_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            toolbar.addWidget(tool_btn)
        toolbar.addSeparator()
        for i in range(3):
            tool_btn = ElaToolButton(self)
            tool_btn.setText(f"操作{i + 1}")
            tool_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            toolbar.addWidget(tool_btn)
        parent_layout.addWidget(toolbar)
        parent_layout.addSpacing(20)

    def _demoBreadcrumbBar(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("01. PyQt5ElaWidgetTools - ElaBreadcrumbBar 面包屑导航", self._demoBreadcrumbBar)
        )
        self._addInfoText("面包屑导航组件，支持点击切换", parent_layout)
        breadcrumb = ElaBreadcrumbBar(self)
        breadcrumb_list = [f"项目{i}" for i in range(1, 8)]
        breadcrumb.setBreadcrumbList(breadcrumb_list)
        parent_layout.addWidget(breadcrumb)
        parent_layout.addSpacing(20)

    def _demoPivot(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("02. PyQt5ElaWidgetTools - ElaPivot Pivot标签", self._demoPivot)
        )
        self._addInfoText("Pivot标签组件，适合切换视图", parent_layout)
        pivot = ElaPivot(self)
        pivot.setPivotSpacing(8)
        pivot.setMarkWidth(75)
        pivot.appendPivot("本地歌曲")
        pivot.appendPivot("下载歌曲")
        pivot.appendPivot("下载视频")
        pivot.appendPivot("正在下载")
        pivot.setCurrentIndex(0)
        parent_layout.addWidget(pivot)
        parent_layout.addSpacing(20)

    def _demoTabBar(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("03. PyQt5ElaWidgetTools - ElaTabBar 标签栏", self._demoTabBar)
        )
        self._addInfoText("标签栏组件", parent_layout)
        tab_bar = ElaTabBar(self)
        tab_bar.addTab("标签1")
        tab_bar.addTab("标签2")
        tab_bar.addTab("标签3")
        parent_layout.addWidget(tab_bar)
        parent_layout.addSpacing(20)

    def _demoTabWidget(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("04. PyQt5ElaWidgetTools - ElaTabWidget 标签页", self._demoTabWidget)
        )
        self._addInfoText("标签页组件，包含多个页面", parent_layout)
        tab_widget = ElaTabWidget(self)
        tab_widget.setFixedHeight(200)
        tab_widget.setIsTabTransparent(True)
        page1 = ElaText("新标签页1", self)
        page1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_page = page1.font()
        font_page.setPixelSize(32)
        page1.setFont(font_page)
        page2 = ElaText("新标签页2", self)
        page2.setFont(font_page)
        page2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page3 = ElaText("新标签页3", self)
        page3.setFont(font_page)
        page3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab_widget.addTab(page1, "新标签页1")
        tab_widget.addTab(page2, "新标签页2")
        tab_widget.addTab(page3, "新标签页3")
        parent_layout.addWidget(tab_widget)
        parent_layout.addSpacing(20)
