"""
[ela_ext] 容器组件演示页面 - PyQt5ElaWidgetTools
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem
from PyQt5ElaWidgetTools import (
    ElaText,
    ElaPushButton,
    ElaDialog,
    ElaDrawerArea,
    ElaScrollArea,
    ElaTreeView,
    ElaTableView,
    ElaListView,
    ElaToggleSwitch,
    ElaCheckBox,
)
from ela_ext import ThemeWidget
from .base_page import ExamplePage


class ContainerComponentsPage(ExamplePage):
    """ela 容器组件演示页面"""

    PAGE_TITLE = "ela 容器组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoDialog(main_layout)
        self._demoDrawerArea(main_layout)
        self._demoScrollArea(main_layout)
        self._demoTreeView(main_layout)
        self._demoTableView(main_layout)
        self._demoListView(main_layout)

    def _demoDialog(self, parent_layout):
        section = ElaText("01. ElaDialog - 对话框", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("点击按钮打开对话框", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        open_btn = ElaPushButton("打开对话框", self)
        open_btn.setFixedWidth(120)
        open_btn.clicked.connect(self._onOpenDialog)
        btn_layout.addWidget(open_btn)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _onOpenDialog(self):
        dialog = ElaDialog(self)
        dialog.setWindowTitle("对话框标题")
        dialog.resize(400, 300)
        dialog.setAttribute(99, True)
        dialog.accepted.connect(lambda: print("对话框已确认"))
        dialog.rejected.connect(lambda: print("对话框已取消"))
        dialog.closeButtonClicked.connect(dialog.close)
        dialog.exec_()

    def _demoDrawerArea(self, parent_layout):
        section = ElaText("02. ElaDrawerArea - 抽屉区域", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("点击开关展开/收起抽屉", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

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
        section = ElaText("03. ElaScrollArea - 滚动区域", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("区域内包含多个组件，可滚动查看", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

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

    def _demoTreeView(self, parent_layout):
        section = ElaText("04. ElaTreeView - 树视图", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("树视图组件，支持多层级展示", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

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
        section = ElaText("05. ElaTableView - 表格视图", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("表格视图组件，支持行列数据展示", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

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
        section = ElaText("06. ElaListView - 列表视图", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("列表视图组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        list_view = ElaListView(self)
        list_view.setFixedHeight(150)

        model = QStandardItemModel()
        for i in range(10):
            item = QStandardItem(f"列表项 {i + 1}")
            model.appendRow(item)

        list_view.setModel(model)
        parent_layout.addWidget(list_view)
        parent_layout.addSpacing(20)
