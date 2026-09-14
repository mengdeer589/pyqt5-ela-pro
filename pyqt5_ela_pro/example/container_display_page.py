"""
[pyqt5_ela_pro] 容器与展示组件页面

合并了以下来源的组件:
- PyQt5ElaWidgetTools: 容器、展示、对话框、菜单组件
"""

from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap, QStandardItemModel, QStandardItem, QColor
from PyQt5ElaWidgetTools import (
    ElaText, ElaPushButton, ElaCheckBox, ElaToggleSwitch, ElaScrollArea, ElaTreeView, ElaTableView, ElaListView,
    ElaProgressBar, ElaProgressRing, ElaProgressRingType,
    ElaImageCard, ElaInteractiveCard, ElaPopularCard, ElaPromotionCard,
    ElaReminderCard, ElaAcrylicUrlCard, ElaKeyBinder,
    ElaColorDialog, ElaContentDialog, ElaMessageBar, ElaMessageBarType,
    ElaMenu, ElaMenuBar, ElaSuggestBox,
)
from pyqt5_ela_pro import ElaDrawerArea, ElaThemeWidget
from .base_page import ExamplePage, _res


class ContainerDisplayPage(ExamplePage):
    """容器与展示组件页面"""

    PAGE_TITLE = "容器展示"

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
        self._demoContainer(main_layout)
        self._demoDisplay(main_layout)
        self._demoDialog(main_layout)
        self._demoMenu(main_layout)

    def _demoContainer(self, parent_layout):
        self._demoDrawerArea(parent_layout)
        self._demoScrollArea(parent_layout)
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
        self._demoElaMenu(parent_layout)
        self._demoMenuBar(parent_layout)
        self._demoSuggestBox(parent_layout)

    def _demoDrawerArea(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("01. PyQt5ElaWidgetTools - ElaDrawerArea 抽屉区域", self._demoDrawerArea)
        )
        self._addInfoText("点击标题栏或开关展开/收起抽屉", parent_layout)
        self._drawer_area = ElaDrawerArea(self)
        self._drawer_area.setHeaderHeight(50)
        header_widget = ElaThemeWidget(self._drawer_area)
        header_layout = QHBoxLayout(header_widget)
        header_title = ElaText("抽屉标题", header_widget)
        header_title.setTextPixelSize(14)
        header_layout.addWidget(header_title)
        self._drawer_switch = ElaToggleSwitch(header_widget)
        self._drawer_switch_text = ElaText("关", header_widget)
        self._drawer_switch_text.setTextPixelSize(14)

        def on_toggled(toggled):
            # setIsToggled 同步开关时原生会回发 toggled，状态一致时跳过避免回声
            if toggled == self._drawer_area.getIsExpand():
                return
            if toggled:
                self._drawer_area.expand()
            else:
                self._drawer_area.collapse()

        def on_expand_state_changed(is_expand):
            # 点击标题栏切换时，回向同步开关与文字（setIsToggled 值不变时不发信号，无循环）
            self._drawer_switch_text.setText("开" if is_expand else "关")
            self._drawer_switch.setIsToggled(is_expand)

        self._drawer_switch.toggled.connect(on_toggled)
        self._drawer_area.expandStateChanged.connect(on_expand_state_changed)
        header_layout.addWidget(self._drawer_switch_text)
        header_layout.addWidget(self._drawer_switch)
        self._drawer_area.setDrawerHeader(header_widget)
        drawer_widget = ElaThemeWidget(self._drawer_area)
        drawer_layout = QHBoxLayout(drawer_widget)
        for i in range(3):
            checkbox = ElaCheckBox(f"抽屉项目 {i + 1}", drawer_widget)
            drawer_layout.addWidget(checkbox)
        self._drawer_area.addDrawer(drawer_widget)
        parent_layout.addWidget(self._drawer_area)

    def _demoScrollArea(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("02. PyQt5ElaWidgetTools - ElaScrollArea 滚动区域", self._demoScrollArea)
        )
        self._addInfoText("区域内包含多个组件，可滚动查看", parent_layout)
        scroll_area = ElaScrollArea(self)
        scroll_area.setFixedHeight(200)
        scroll_area.setWidgetResizable(True)
        scroll_content = ElaThemeWidget()
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

    def _demoTreeView(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("03. PyQt5ElaWidgetTools - ElaTreeView 树视图", self._demoTreeView)
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
        parent_layout.addLayout(
            self._createHeaderRow("04. PyQt5ElaWidgetTools - ElaTableView 表格视图", self._demoTableView)
        )
        self._addInfoText("表格视图组件，支持行列数据展示", parent_layout)
        from PyQt5.QtCore import Qt
        table_view = ElaTableView(self)
        table_view.setFixedHeight(200)
        model = QStandardItemModel(5, 3)
        model.setHorizontalHeaderLabels(["姓名", "年龄", "城市"])
        hh = table_view.horizontalHeader()
        if hh:
            hh.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
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
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                model.setItem(row, col, item)
        table_view.setModel(model)
        parent_layout.addWidget(table_view)
        parent_layout.addSpacing(20)

    def _demoListView(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("05. PyQt5ElaWidgetTools - ElaListView 列表视图", self._demoListView)
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
        parent_layout.addLayout(
            self._createHeaderRow("01. PyQt5ElaWidgetTools - ElaProgressBar 进度条", self._demoProgressBar)
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
        parent_layout.addLayout(
            self._createHeaderRow("02. PyQt5ElaWidgetTools - ElaProgressRing 环形进度", self._demoProgressRing)
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
        parent_layout.addLayout(
            self._createHeaderRow("03. PyQt5ElaWidgetTools - ElaImageCard 图片卡片", self._demoImageCard)
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
        parent_layout.addLayout(
            self._createHeaderRow("04. PyQt5ElaWidgetTools - ElaInteractiveCard 交互卡片", self._demoInteractiveCard)
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
        parent_layout.addLayout(
            self._createHeaderRow("05. PyQt5ElaWidgetTools - ElaPopularCard 热门卡片", self._demoPopularCard)
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
        parent_layout.addLayout(
            self._createHeaderRow("06. PyQt5ElaWidgetTools - ElaPromotionCard 推广卡片", self._demoPromotionCard)
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
        parent_layout.addLayout(
            self._createHeaderRow("07. PyQt5ElaWidgetTools - ElaReminderCard 提醒卡片", self._demoReminderCard)
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
        parent_layout.addLayout(
            self._createHeaderRow("08. PyQt5ElaWidgetTools - ElaAcrylicUrlCard 亚克力URL卡片", self._demoAcrylicUrlCard)
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
        parent_layout.addLayout(
            self._createHeaderRow("09. PyQt5ElaWidgetTools - ElaKeyBinder 快捷键提示", self._demoKeyBinder)
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
        parent_layout.addLayout(
            self._createHeaderRow("01. PyQt5ElaWidgetTools - ElaColorDialog 颜色对话框", self._demoColorDialog)
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
        parent_layout.addLayout(
            self._createHeaderRow("02. PyQt5ElaWidgetTools - ElaContentDialog 内容对话框", self._demoContentDialog)
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

    def _demoElaMenu(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("01. PyQt5ElaWidgetTools - ElaMenu 菜单", self._demoElaMenu)
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
        menu_btn.clicked.connect(lambda: menu.popup(menu_btn.mapToGlobal(QPoint(0, menu_btn.height()))))
        btn_layout.addWidget(menu_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoMenuBar(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("02. PyQt5ElaWidgetTools - ElaMenuBar 菜单栏", self._demoMenuBar)
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
        parent_layout.addLayout(
            self._createHeaderRow("03. PyQt5ElaWidgetTools - ElaSuggestBox 建议框", self._demoSuggestBox)
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
