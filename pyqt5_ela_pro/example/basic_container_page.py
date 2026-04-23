"""
[pyqt5_ela_pro] 基础组件与容器展示页面

合并了以下来源的组件:
- PyQt5ElaWidgetTools: 输入、基础、导航、容器、展示组件
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import (
    QImage,
    QPixmap,
    QStandardItemModel,
    QStandardItem,
    QPalette,
    QColor,
    QFont,
)
from PyQt5ElaWidgetTools import (
    ElaText,
    ElaLineEdit,
    ElaPlainTextEdit,
    ElaSpinBox,
    ElaDoubleSpinBox,
    ElaSlider,
    ElaCalendar,
    ElaCalendarPicker,
    ElaLCDNumber,
    ElaCheckBox,
    ElaRadioButton,
    ElaToggleSwitch,
    ElaToggleButton,
    ElaIconButton,
    ElaMessageButton,
    ElaMessageBarType,
    ElaScrollBar,
    ElaProgressBar,
    ElaPushButton,
    ElaToolButton,
    ElaToolBar,
    ElaIconType,
    ElaBreadcrumbBar,
    ElaPivot,
    ElaTabBar,
    ElaTabWidget,
    ElaDialog,
    ElaDrawerArea,
    ElaScrollArea,
    ElaTreeView,
    ElaTableView,
    ElaListView,
    ElaToggleSwitch,
    ElaCheckBox,
    ElaProgressRing,
    ElaProgressRingType,
    ElaImageCard,
    ElaInteractiveCard,
    ElaPopularCard,
    ElaPromotionCard,
    ElaReminderCard,
    ElaAcrylicUrlCard,
    ElaKeyBinder,
    ElaColorDialog,
    ElaContentDialog,
    ElaMessageBar,
    ElaMenu,
    ElaMenuBar,
    ElaSuggestBox,
    ElaToolButton,
)
from pyqt5_ela_pro import ThemeWidget, create_ela_splitter, ElaSplitter
from .base_page import ExamplePage, _res


class BasicContainerPage(ExamplePage):
    """基础组件与容器展示页面"""

    PAGE_TITLE = "基础组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _setCardPixmap(self, card, filename):
        pixmap = QPixmap(_res(filename))
        if not pixmap.isNull():
            card.setCardPixmap(pixmap)

    def _setCardImage(self, card, filename):
        pixmap = QPixmap(_res(filename))
        if not pixmap.isNull():
            card.setCardImage(QImage(pixmap.toImage()))

    def _addDemoContent(self, main_layout):
        self._demoInput(main_layout)
        self._demoBasic(main_layout)
        self._demoNavigation(main_layout)
        self._demoContainer(main_layout)
        self._demoDisplay(main_layout)
        self._demoDialog(main_layout)
        self._demoMenu(main_layout)

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

    def _demoContainer(self, parent_layout):
        self._demoDrawerArea(parent_layout)
        self._demoScrollArea(parent_layout)
        self._demoSplitter(parent_layout)
        self._demoTreeView(parent_layout)
        self._demoTableView(parent_layout)
        self._demoListView(parent_layout)

    def _demoDisplay(self, parent_layout):
        self._demoProgressBar(parent_layout)
        self._demoProgressRing(parent_layout)
        self._demoImageCard(parent_layout)
        self._demoInteractiveCard(parent_layout)
        self._demoPopularCard(parent_layout)
        self._demoPromotionCard(parent_layout)
        self._demoReminderCard(parent_layout)
        self._demoAcrylicUrlCard(parent_layout)
        self._demoKeyBinder(parent_layout)

    def _demoDialog(self, parent_layout):
        self._demoColorDialog(parent_layout)
        self._demoContentDialog(parent_layout)

    def _demoMenu(self, parent_layout):
        self._demoMenu(parent_layout)
        self._demoMenuBar(parent_layout)
        self._demoSuggestBox(parent_layout)

    def _addInfoText(self, text, parent_layout):
        info = ElaText(text, self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

    def _demoLineEdit(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "01. PyQt5ElaWidgetTools - ElaLineEdit 单行输入框"
            )
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
        parent_layout.addWidget(
            self._createSectionHeader(
                "02. PyQt5ElaWidgetTools - ElaPlainTextEdit 多行文本编辑"
            )
        )
        self._addInfoText("多行文本编辑组件", parent_layout)
        text_edit = ElaPlainTextEdit(self)
        text_edit.setPlaceholderText("请输入多行文本...")
        text_edit.setFixedHeight(100)
        parent_layout.addWidget(text_edit)
        parent_layout.addSpacing(20)

    def _demoSpinBox(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("03. PyQt5ElaWidgetTools - ElaSpinBox 整数微调框")
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
        parent_layout.addWidget(
            self._createSectionHeader(
                "04. PyQt5ElaWidgetTools - ElaDoubleSpinBox 浮点数微调框"
            )
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
        parent_layout.addWidget(
            self._createSectionHeader("05. PyQt5ElaWidgetTools - ElaSlider 滑块")
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
        parent_layout.addWidget(
            self._createSectionHeader("06. PyQt5ElaWidgetTools - ElaCalendar 日历")
        )
        self._addInfoText("日历组件", parent_layout)
        calendar = ElaCalendar(self)
        calendar.setFixedWidth(280)
        parent_layout.addWidget(calendar)
        parent_layout.addSpacing(20)

    def _demoCalendarPicker(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "07. PyQt5ElaWidgetTools - ElaCalendarPicker 日期选择器"
            )
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
        parent_layout.addWidget(
            self._createSectionHeader(
                "08. PyQt5ElaWidgetTools - ElaLCDNumber LCD数字显示"
            )
        )
        self._addInfoText(
            "LCD数字显示组件，setIsUseAutoClock(True) 自动显示当前时间", parent_layout
        )
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
        parent_layout.addWidget(
            self._createSectionHeader("01. PyQt5ElaWidgetTools - ElaCheckBox 复选框")
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
        parent_layout.addWidget(
            self._createSectionHeader(
                "02. PyQt5ElaWidgetTools - ElaRadioButton 单选按钮"
            )
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
        parent_layout.addWidget(
            self._createSectionHeader("03. PyQt5ElaWidgetTools - ElaToggleSwitch 开关")
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
        parent_layout.addWidget(
            self._createSectionHeader(
                "04. PyQt5ElaWidgetTools - ElaToggleButton 切换按钮"
            )
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
        parent_layout.addWidget(
            self._createSectionHeader("05. PyQt5ElaWidgetTools - ElaPushButton 按钮")
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
        parent_layout.addWidget(
            self._createSectionHeader(
                "06. PyQt5ElaWidgetTools - ElaToolButton 工具按钮"
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
        parent_layout.addWidget(
            self._createSectionHeader(
                "07. PyQt5ElaWidgetTools - ElaIconButton 图标按钮"
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

    def _demoMessageButton(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "08. PyQt5ElaWidgetTools - ElaMessageButton 消息按钮"
            )
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
        parent_layout.addWidget(
            self._createSectionHeader("09. PyQt5ElaWidgetTools - ElaScrollBar 滚动条")
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
        parent_layout.addWidget(
            self._createSectionHeader("10. PyQt5ElaWidgetTools - ElaToolBar 工具栏")
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
        parent_layout.addWidget(
            self._createSectionHeader(
                "01. PyQt5ElaWidgetTools - ElaBreadcrumbBar 面包屑导航"
            )
        )
        self._addInfoText("面包屑导航组件，支持点击切换", parent_layout)
        breadcrumb = ElaBreadcrumbBar(self)
        breadcrumb_list = [f"项目{i}" for i in range(1, 8)]
        breadcrumb.setBreadcrumbList(breadcrumb_list)
        parent_layout.addWidget(breadcrumb)
        parent_layout.addSpacing(20)

    def _demoPivot(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("02. PyQt5ElaWidgetTools - ElaPivot Pivot标签")
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
        parent_layout.addWidget(
            self._createSectionHeader("03. PyQt5ElaWidgetTools - ElaTabBar 标签栏")
        )
        self._addInfoText("标签栏组件", parent_layout)
        tab_bar = ElaTabBar(self)
        tab_bar.addTab("标签1")
        tab_bar.addTab("标签2")
        tab_bar.addTab("标签3")
        parent_layout.addWidget(tab_bar)
        parent_layout.addSpacing(20)

    def _demoTabWidget(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("04. PyQt5ElaWidgetTools - ElaTabWidget 标签页")
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

    def _demoDrawerArea(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "01. PyQt5ElaWidgetTools - ElaDrawerArea 抽屉区域"
            )
        )
        self._addInfoText("点击开关展开/收起抽屉", parent_layout)
        self._drawer_area = ElaDrawerArea(self)
        self._drawer_area.setFixedHeight(200)
        header_widget = ThemeWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)
        header_title = ElaText("抽屉标题", header_widget)
        header_title.setTextPixelSize(14)
        header_layout.addWidget(header_title)
        self._drawer_switch = ElaToggleSwitch(header_widget)
        self._drawer_switch_text = ElaText("关", header_widget)
        self._drawer_switch_text.setTextPixelSize(14)

        def on_toggled(toggled):
            if toggled:
                self._drawer_switch_text.setText("开")
                self._drawer_area.expand()
            else:
                self._drawer_switch_text.setText("关")
                self._drawer_area.collapse()

        self._drawer_switch.toggled.connect(on_toggled)
        header_layout.addStretch()
        header_layout.addWidget(self._drawer_switch_text)
        header_layout.addWidget(self._drawer_switch)
        self._drawer_area.setDrawerHeader(header_widget)
        for i in range(3):
            drawer_widget = ThemeWidget()
            drawer_widget.setFixedHeight(75)
            drawer_layout = QHBoxLayout(drawer_widget)
            drawer_layout.setContentsMargins(60, 0, 10, 0)
            checkbox = ElaCheckBox(f"抽屉项目 {i + 1}", drawer_widget)
            drawer_layout.addWidget(checkbox)
            drawer_layout.addStretch()
            self._drawer_area.addDrawer(drawer_widget)
        parent_layout.addWidget(self._drawer_area)
        parent_layout.addSpacing(20)

    def _demoScrollArea(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "02. PyQt5ElaWidgetTools - ElaScrollArea 滚动区域"
            )
        )
        self._addInfoText("区域内包含多个组件，可滚动查看", parent_layout)
        scroll_area = ElaScrollArea(self)
        scroll_area.setFixedHeight(200)
        scroll_area.setWidgetResizable(True)
        scroll_content = ThemeWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        scroll_layout.setSpacing(10)
        for i in range(15):
            item = ElaText(f"滚动区域内的项目 {i + 1}", scroll_content)
            item.setTextPixelSize(14)
            scroll_layout.addWidget(item)
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        parent_layout.addWidget(scroll_area)
        parent_layout.addSpacing(20)

    def _demoSplitter(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("04. pyqt5_ela_pro - ElaSplitter 分隔器")
        )
        self._addInfoText(
            "ELA 主题风格的分割器，支持水平和垂直方向，自动响应主题切换",
            parent_layout,
        )
        self._addInfoText(
            "create_ela_splitter(widgets, orientation, handleThickness) 函数创建",
            parent_layout,
        )

        widget1 = ThemeWidget(self)
        widget1.setMinimumSize(50, 50)
        layout1 = QVBoxLayout(widget1)
        text1 = ElaText("面板 1", widget1)
        text1.setAlignment(Qt.AlignCenter)
        layout1.addWidget(text1)

        widget2 = ThemeWidget(self)
        widget2.setMinimumSize(50, 50)
        layout2 = QVBoxLayout(widget2)
        text2 = ElaText("面板 2", widget2)
        text2.setAlignment(Qt.AlignCenter)
        layout2.addWidget(text2)

        widget3 = ThemeWidget(self)
        widget3.setMinimumSize(50, 50)
        layout3 = QVBoxLayout(widget3)
        text3 = ElaText("面板 3", widget3)
        text3.setAlignment(Qt.AlignCenter)
        layout3.addWidget(text3)

        splitter = create_ela_splitter([widget1, widget2, widget3], Qt.Horizontal)
        splitter.setMinimumHeight(80)
        parent_layout.addWidget(splitter)
        parent_layout.addSpacing(20)

    def _demoTreeView(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("03. PyQt5ElaWidgetTools - ElaTreeView 树视图")
        )
        self._addInfoText("树视图组件，支持多层级展示", parent_layout)
        tree_view = ElaTreeView(self)
        tree_view.setFixedHeight(200)
        model = QStandardItemModel()
        root_item = model.invisibleRootItem()
        for i in range(3):
            parent_item = QStandardItem(f"文件夹 {i + 1}")
            for j in range(3):
                child_item = QStandardItem(f"文件 {j + 1}.txt")
                parent_item.appendRow(child_item)
            root_item.appendRow(parent_item)
        tree_view.setModel(model)
        parent_layout.addWidget(tree_view)
        parent_layout.addSpacing(20)

    def _demoTableView(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("04. PyQt5ElaWidgetTools - ElaTableView 表格视图")
        )
        self._addInfoText("表格视图组件，支持行列数据展示", parent_layout)
        table_view = ElaTableView(self)
        table_view.setFixedHeight(200)
        model = QStandardItemModel(5, 3)
        model.setHorizontalHeaderLabels(["姓名", "年龄", "城市"])
        data = [
            ["张三", "25", "北京"],
            ["李四", "30", "上海"],
            ["王五", "28", "广州"],
            ["赵六", "35", "深圳"],
            ["钱七", "22", "杭州"],
        ]
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QStandardItem(value)
                model.setItem(row, col, item)
        table_view.setModel(model)
        parent_layout.addWidget(table_view)
        parent_layout.addSpacing(20)

    def _demoListView(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("05. PyQt5ElaWidgetTools - ElaListView 列表视图")
        )
        self._addInfoText("列表视图组件", parent_layout)
        list_view = ElaListView(self)
        list_view.setFixedHeight(150)
        model = QStandardItemModel()
        for i in range(10):
            item = QStandardItem(f"列表项 {i + 1}")
            model.appendRow(item)
        list_view.setModel(model)
        parent_layout.addWidget(list_view)
        parent_layout.addSpacing(20)

    def _demoProgressBar(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("01. PyQt5ElaWidgetTools - ElaProgressBar 进度条")
        )
        self._addInfoText("水平进度条，显示当前操作进度", parent_layout)
        parent_layout.addSpacing(10)
        progress_bar = ElaProgressBar(self)
        progress_bar.setRange(0, 100)
        progress_bar.setValue(65)
        progress_bar.setFixedWidth(400)
        parent_layout.addWidget(progress_bar)
        parent_layout.addSpacing(30)

    def _demoProgressRing(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "02. PyQt5ElaWidgetTools - ElaProgressRing 环形进度"
            )
        )
        self._addInfoText("环形进度指示器，适用于等待状态", parent_layout)
        parent_layout.addSpacing(10)
        ring_container = QWidget(self)
        ring_layout = QHBoxLayout(ring_container)
        ring1 = ElaProgressRing(self)
        ring1.setValue(75)
        ring1.setIsDisplayValue(True)
        ring1.setValueDisplayMode(ElaProgressRingType.ValueDisplayMode.Percent)
        ring1.setFixedSize(100, 100)
        ring_layout.addWidget(ring1)
        ring2 = ElaProgressRing(self)
        ring2.setValue(50)
        ring2.setIsDisplayValue(True)
        ring2.setValueDisplayMode(ElaProgressRingType.ValueDisplayMode.Actual)
        ring2.setFixedSize(80, 80)
        ring_layout.addWidget(ring2)
        ring3 = ElaProgressRing(self)
        ring3.setIsBusying(True)
        ring3.setFixedSize(60, 60)
        ring_layout.addWidget(ring3)
        parent_layout.addWidget(ring_container)
        parent_layout.addSpacing(30)

    def _demoImageCard(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("03. PyQt5ElaWidgetTools - ElaImageCard 图片卡片")
        )
        self._addInfoText("带图片的卡片组件", parent_layout)
        parent_layout.addSpacing(10)
        card = ElaImageCard(self)
        card.setFixedSize(240, 180)
        card.setBorderRadius(8)
        self._setCardImage(card, "miku.png")
        parent_layout.addWidget(card)
        parent_layout.addSpacing(30)

    def _demoInteractiveCard(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "04. PyQt5ElaWidgetTools - ElaInteractiveCard 交互卡片"
            )
        )
        self._addInfoText("可交互的卡片组件，支持点击", parent_layout)
        parent_layout.addSpacing(10)
        card = ElaInteractiveCard(self)
        card.setTitle("热门文章")
        card.setSubTitle("点击查看详情")
        card.setBorderRadius(8)
        self._setCardPixmap(card, "miku.png")
        card.setCardPixmapSize(240, 120)
        card.setFixedSize(260, 200)
        parent_layout.addWidget(card)
        parent_layout.addSpacing(30)

    def _demoPopularCard(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "05. PyQt5ElaWidgetTools - ElaPopularCard 热门卡片"
            )
        )
        self._addInfoText("展示热门内容的卡片组件", parent_layout)
        parent_layout.addSpacing(10)
        card = ElaPopularCard(self)
        card.setTitle("STYX HELIX")
        card.setSubTitle("阅读量: 10,000+")
        card.setInteractiveTips("查看详情")
        card.setCardButtonText("立即阅读")
        card.setBorderRadius(8)
        self._setCardPixmap(card, "miku.png")
        card.setFixedSize(260, 220)
        parent_layout.addWidget(card)
        parent_layout.addSpacing(30)

    def _demoPromotionCard(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "06. PyQt5ElaWidgetTools - ElaPromotionCard 推广卡片"
            )
        )
        self._addInfoText("推广促销类卡片组件", parent_layout)
        parent_layout.addSpacing(10)
        card = ElaPromotionCard(self)
        card.setTitle("STYX HELIX")
        card.setSubTitle("Never close your eyes")
        card.setCardTitle("MiKu")
        card.setPromotionTitle("SONG~")
        card.setBorderRadius(10)
        self._setCardPixmap(card, "miku.png")
        card.setHorizontalCardPixmapRatio(0.5)
        card.setFixedSize(340, 180)
        parent_layout.addWidget(card)
        parent_layout.addSpacing(30)

    def _demoReminderCard(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "07. PyQt5ElaWidgetTools - ElaReminderCard 提醒卡片"
            )
        )
        self._addInfoText("提醒通知类卡片组件", parent_layout)
        parent_layout.addSpacing(10)
        card = ElaReminderCard(self)
        card.setTitle("会议提醒")
        card.setSubTitle("下午3点有一场会议")
        card.setBorderRadius(8)
        self._setCardPixmap(card, "miku.png")
        card.setFixedSize(320, 100)
        parent_layout.addWidget(card)
        parent_layout.addSpacing(30)

    def _demoAcrylicUrlCard(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "08. PyQt5ElaWidgetTools - ElaAcrylicUrlCard 亚克力URL卡片"
            )
        )
        self._addInfoText("带亚克力效果的URL链接卡片", parent_layout)
        parent_layout.addSpacing(10)
        card = ElaAcrylicUrlCard(self)
        card.setTitle("访问网站")
        card.setSubTitle("点击打开链接")
        card.setUrl("https://example.com")
        card.setBorderRadius(8)
        self._setCardPixmap(card, "miku.png")
        card.setFixedSize(320, 120)
        parent_layout.addWidget(card)
        parent_layout.addSpacing(30)

    def _demoKeyBinder(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "09. PyQt5ElaWidgetTools - ElaKeyBinder 快捷键提示"
            )
        )
        self._addInfoText("显示快捷键绑定的标签组件", parent_layout)
        parent_layout.addSpacing(10)
        binder_container = QWidget(self)
        binder_layout = QHBoxLayout(binder_container)
        binder1 = ElaKeyBinder(self)
        binder1.setBinderKeyText("Ctrl + S")
        binder1.setBorderRadius(4)
        binder_layout.addWidget(binder1)
        binder2 = ElaKeyBinder(self)
        binder2.setBinderKeyText("Ctrl + C")
        binder2.setBorderRadius(4)
        binder_layout.addWidget(binder2)
        binder3 = ElaKeyBinder(self)
        binder3.setBinderKeyText("Ctrl + V")
        binder3.setBorderRadius(4)
        binder_layout.addWidget(binder3)
        parent_layout.addWidget(binder_container)
        parent_layout.addSpacing(20)

    def _demoColorDialog(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "01. PyQt5ElaWidgetTools - ElaColorDialog 颜色对话框"
            )
        )
        self._addInfoText("点击按钮打开颜色选择对话框", parent_layout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        color_btn = ElaPushButton("选择颜色", self)
        color_btn.setFixedWidth(120)
        color_btn.clicked.connect(self._onOpenColorDialog)
        btn_layout.addWidget(color_btn)
        self._colorFrame = QWidget(self)
        self._colorFrame.setFixedSize(60, 30)
        self._colorFrame.setAutoFillBackground(True)
        self._colorFrame.setStyleSheet("background-color: #808080;")
        btn_layout.addWidget(self._colorFrame)
        self._colorLabel = ElaText("#808080", self)
        self._colorLabel.setTextPixelSize(14)
        btn_layout.addWidget(self._colorLabel)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoContentDialog(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "02. PyQt5ElaWidgetTools - ElaContentDialog 内容对话框"
            )
        )
        self._addInfoText("点击按钮打开内容对话框", parent_layout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        open_btn = ElaPushButton("打开对话框", self)
        open_btn.setFixedWidth(120)
        open_btn.clicked.connect(self._onOpenContentDialog)
        btn_layout.addWidget(open_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _onOpenColorDialog(self):
        dialog = ElaColorDialog(self)
        dialog.colorSelected.connect(self._updatePreviewColor)
        dialog.exec_()

    def _updatePreviewColor(self, color: QColor):
        self._colorFrame.setStyleSheet(f"background-color: {color.name()};")

    def _onOpenContentDialog(self):
        dialog = ElaContentDialog(self)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_text = ElaText(
            "这是内容对话框的描述文本。\n可以在这里放置各种组件。", content_widget
        )
        content_text.setTextPixelSize(14)
        content_layout.addWidget(content_text)
        dialog.setCentralWidget(content_widget)
        dialog.setLeftButtonText("确定")
        dialog.setMiddleButtonText("取消")
        dialog.setRightButtonText("应用")
        dialog.leftButtonClicked.connect(lambda: print("点击了确定"))
        dialog.middleButtonClicked.connect(lambda: print("点击了取消"))
        dialog.rightButtonClicked.connect(lambda: print("点击了应用"))
        dialog.exec_()

    def _showMenuFeedback(self, action_text: str):
        ElaMessageBar.success(
            ElaMessageBarType.PositionPolicy.Top,
            "菜单反馈",
            f"点击了: {action_text}",
            2000,
        )

    def _demoMenu(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("01. PyQt5ElaWidgetTools - ElaMenu 菜单")
        )
        self._addInfoText("点击按钮打开菜单，点击菜单项可看到反馈", parent_layout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        menu_btn = ElaToolButton(self)
        menu_btn.setText("菜单")
        menu_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
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
        menu_btn.setMenu(menu)
        btn_layout.addWidget(menu_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoMenuBar(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("02. PyQt5ElaWidgetTools - ElaMenuBar 菜单栏")
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

    def _demoSuggestBox(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("03. PyQt5ElaWidgetTools - ElaSuggestBox 建议框")
        )
        self._addInfoText("输入时显示建议列表", parent_layout)
        suggest_box = ElaSuggestBox(self)
        suggest_box.setFixedWidth(300)
        suggest_box.addSuggestion("Python")
        suggest_box.addSuggestion("JavaScript")
        suggest_box.addSuggestion("C++")
        suggest_box.addSuggestion("Java")
        suggest_box.addSuggestion("Go")
        suggest_box.addSuggestion("Rust")
        suggest_box.addSuggestion("TypeScript")
        parent_layout.addWidget(suggest_box)
        parent_layout.addSpacing(20)
