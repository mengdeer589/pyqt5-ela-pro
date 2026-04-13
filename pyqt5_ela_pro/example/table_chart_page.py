"""
[pyqt5_ela_pro] 表格与图表组件页面

合并了以下来源的组件:
- pyqt5_ela_pro: 表格、图表组件
"""

import random

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt
from PyQt5ElaWidgetTools import ElaText, ElaPushButton
from pyqt5_ela_pro import ElaDataTable, ElaTrendChart
from .base_page import ExamplePage


class TableChartPage(ExamplePage):
    """表格与图表组件页面"""

    PAGE_TITLE = "表格与图表"

    def __init__(self, parent=None):
        self._trendChart = None
        self._gridVisible = True
        self._legendVisible = True
        self._basicTable = None
        self._asyncTable = None
        self._styleTable = None
        self._sortTable = None
        self._sortingEnabled = False
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoTable(main_layout)
        self._demoChart(main_layout)

    def _demoTable(self, parent_layout):
        self._demoBasicTable(parent_layout)
        self._demoAsyncTable(parent_layout)
        self._demoStyleTable(parent_layout)
        self._demoSortTable(parent_layout)

    def _demoChart(self, parent_layout):
        self._demoTrendChart(parent_layout)

    def _addInfoText(self, text, parent_layout):
        info = ElaText(text, self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

    def _demoBasicTable(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("01. ela_ext - ElaDataTable 基础表格")
        )
        self._addInfoText(
            "使用 setTableData() 填充静态数据，支持列表和字典两种格式", parent_layout
        )
        self._basicTable = ElaDataTable(self)
        self._basicTable.setFixedHeight(200)
        data = [
            ["姓名", "年龄", "城市", "职业"],
            ["张三", "28", "北京", "工程师"],
            ["李四", "34", "上海", "设计师"],
            ["王五", "25", "广州", "产品经理"],
            ["赵六", "31", "深圳", "数据分析师"],
        ]
        self._basicTable.setTableData(data, center_columns={1})
        self._basicTable.setColumnWidths({0: 120, 1: 80, 2: 100})
        parent_layout.addWidget(self._basicTable)
        parent_layout.addSpacing(30)

    def _demoAsyncTable(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("02. ela_ext - ElaDataTable 异步加载")
        )
        self._addInfoText(
            "使用 setTableDataAsync() 在后台线程加载大量数据", parent_layout
        )
        self._asyncTable = ElaDataTable(self)
        self._asyncTable.setFixedHeight(200)
        large_data = [
            ["行号", "数据", "状态", "金额"],
        ]
        for i in range(100):
            large_data.append(
                [
                    str(i + 1),
                    f"数据项_{i}",
                    "正常" if i % 3 != 0 else "异常",
                    f"{1000 + i * 50:.2f}",
                ]
            )
        self._asyncTable.setTableDataAsync(large_data, callback=self._onAsyncLoaded)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        refresh_btn = ElaPushButton("重新加载", self)
        refresh_btn.setFixedWidth(100)
        refresh_btn.clicked.connect(self._onRefreshAsyncTable)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        parent_layout.addWidget(self._asyncTable)
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(30)

    def _demoStyleTable(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("03. ela_ext - ElaDataTable 单元格样式")
        )
        self._addInfoText(
            "设置前景色、背景色、字体、对齐方式、行背景高亮", parent_layout
        )
        self._styleTable = ElaDataTable(self)
        self._styleTable.setFixedHeight(250)
        data = [
            ["商品", "销量", "库存", "状态"],
            ["iPhone 15", "1250", "320", "热销"],
            ["MacBook Pro", "480", "85", "热销"],
            ["iPad Air", "720", "150", "正常"],
            ["Apple Watch", "360", "210", "滞销"],
            ["AirPods Pro", "890", "95", "热销"],
        ]
        self._styleTable.setTableData(data, center_columns={1, 2})
        self._styleTable.setColumnWidths({0: 150, 1: 100, 2: 100, 3: 100})
        for row in range(1, self._styleTable.rowCount() + 1):
            status_item = self._styleTable.item(row, 3)
            if status_item:
                status_text = status_item.text()
                if status_text == "热销":
                    self._styleTable.setItemForeground(row, 3, QColor(255, 87, 34))
                    self._styleTable.setItem(row, 3, "🔴 热销", center=True)
                elif status_text == "滞销":
                    self._styleTable.setItemForeground(row, 3, QColor(76, 175, 80))
                    self._styleTable.setItem(row, 3, "🟢 滞销", center=True)
                else:
                    self._styleTable.setItem(row, 3, "🟡 正常", center=True)
        self._styleTable.setRowBackground(1, QColor(255, 243, 224))
        self._styleTable.setRowBackground(4, QColor(232, 245, 233))
        bold_font = QFont()
        bold_font.setBold(True)
        self._styleTable.setItemFont(0, 0, bold_font)
        self._styleTable.setItemFont(1, 0, bold_font)
        for row in range(1, self._styleTable.rowCount() + 1):
            sales_item = self._styleTable.item(row, 1)
            if sales_item:
                sales_value = int(sales_item.text())
                if sales_value > 1000:
                    self._styleTable.setItemForeground(row, 1, QColor(255, 87, 34))
        parent_layout.addWidget(self._styleTable)
        parent_layout.addSpacing(20)

    def _demoSortTable(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("04. ela_ext - ElaDataTable 表头排序")
        )
        self._addInfoText(
            "点击表头可排序，再次点击切换升序/降序，支持对齐方式设置", parent_layout
        )
        self._sortTable = ElaDataTable(self)
        self._sortTable.setFixedHeight(250)
        data = [
            ["姓名", "年龄", "城市", "销量"],
            ["张三", "28", "北京", "1250"],
            ["李四", "34", "上海", "890"],
            ["王五", "25", "广州", "720"],
            ["赵六", "31", "深圳", "1100"],
            ["孙七", "29", "杭州", "650"],
            ["周八", "33", "成都", "980"],
        ]
        self._sortTable.setTableData(data)
        self._sortTable.setColumnWidths({0: 100, 1: 80, 2: 100, 3: 80})
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        self._sortToggleBtn = ElaPushButton("开启排序", self)
        self._sortToggleBtn.setFixedWidth(100)
        self._sortToggleBtn.clicked.connect(self._onToggleSort)
        btn_layout.addWidget(self._sortToggleBtn)
        self._sortInfoLabel = ElaText("排序功能: 关闭", self)
        self._sortInfoLabel.setTextPixelSize(14)
        btn_layout.addWidget(self._sortInfoLabel)
        btn_layout.addSpacing(20)
        self._alignLabel = ElaText("第0列对齐:", self)
        self._alignLabel.setTextPixelSize(14)
        btn_layout.addWidget(self._alignLabel)
        align_left_btn = ElaPushButton("靠左", self)
        align_left_btn.setFixedWidth(60)
        align_left_btn.clicked.connect(lambda: self._onSetAlignment(0, Qt.AlignLeft))
        btn_layout.addWidget(align_left_btn)
        align_center_btn = ElaPushButton("居中", self)
        align_center_btn.setFixedWidth(60)
        align_center_btn.clicked.connect(
            lambda: self._onSetAlignment(0, Qt.AlignCenter)
        )
        btn_layout.addWidget(align_center_btn)
        align_right_btn = ElaPushButton("靠右", self)
        align_right_btn.setFixedWidth(60)
        align_right_btn.clicked.connect(lambda: self._onSetAlignment(0, Qt.AlignRight))
        btn_layout.addWidget(align_right_btn)
        btn_layout.addStretch()
        parent_layout.addWidget(self._sortTable)
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _onToggleSort(self):
        self._sortingEnabled = not self._sortingEnabled
        self._sortTable.setSortingEnabled(self._sortingEnabled)
        self._sortToggleBtn.setText("关闭排序" if self._sortingEnabled else "开启排序")
        self._sortInfoLabel.setText(
            f"排序功能: {'开启' if self._sortingEnabled else '关闭'}"
        )

    def _onSetAlignment(self, column: int, alignment: Qt.AlignmentFlag):
        self._sortTable.setColumnAlignment(column, alignment)

    def _onAsyncLoaded(self):
        self._asyncTable.setColumnWidths({0: 80, 1: 150, 2: 100, 3: 120})

    def _onRefreshAsyncTable(self):
        large_data = [
            ["行号", "数据", "状态", "金额"],
        ]
        for i in range(100):
            large_data.append(
                [
                    str(i + 1),
                    f"数据项_{i}_{random.randint(1000, 9999)}",
                    "正常" if random.randint(0, 2) != 0 else "异常",
                    f"{random.uniform(500, 5000):.2f}",
                ]
            )
        self._asyncTable.setTableDataAsync(large_data, callback=self._onAsyncLoaded)

    def _demoTrendChart(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("01. ela_ext - ElaTrendChart 趋势图")
        )
        self._addInfoText(
            "支持多曲线绘制、主题切换、网格线显示、交互式指示器", parent_layout
        )
        self._trendChart = ElaTrendChart(self)
        self._trendChart.setFixedSize(600, 300)
        x_data = list(range(100))
        y1_data = self._generateWaveData(100, base=50, amplitude=30, phase=10)
        y2_data = self._generateWaveData(100, base=40, amplitude=20, phase=15)
        y3_data = self._generateWaveData(100, base=60, amplitude=25, phase=8)
        self._trendChart.addCurve(x=x_data, y=y1_data, name="系列A")
        self._trendChart.addCurve(x=x_data, y=y2_data, name="系列B")
        self._trendChart.addCurve(x=x_data, y=y3_data, name="系列C")
        self._trendChart.adjustViewRect()
        self._trendChart.setGridVisible(self._gridVisible)
        self._trendChart.setLegendVisible(self._legendVisible)
        self._trendChart.setOnPointClicked(self._onChartPointClicked)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        grid_btn = ElaPushButton("切换网格线", self)
        grid_btn.setFixedWidth(100)
        grid_btn.clicked.connect(self._toggleGrid)
        btn_layout.addWidget(grid_btn)
        legend_btn = ElaPushButton("切换图例", self)
        legend_btn.setFixedWidth(100)
        legend_btn.clicked.connect(self._toggleLegend)
        btn_layout.addWidget(legend_btn)
        refresh_btn = ElaPushButton("刷新数据", self)
        refresh_btn.setFixedWidth(100)
        refresh_btn.clicked.connect(self._onRefreshChartData)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        parent_layout.addWidget(self._trendChart)
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _toggleGrid(self):
        self._gridVisible = not self._gridVisible
        self._trendChart.setGridVisible(self._gridVisible)

    def _toggleLegend(self):
        self._legendVisible = not self._legendVisible
        self._trendChart.setLegendVisible(self._legendVisible)

    def _generateWaveData(self, count, base=50, amplitude=10, phase=5):
        data = []
        for i in range(count):
            value = base + amplitude * (i / count) + random.random() * phase
            data.append(value)
        return data

    def _onChartPointClicked(self, name: str, x: float, y: float):
        print(f"点击: {name}, x={x:.2f}, y={y:.2f}")

    def _onRefreshChartData(self):
        if not self._trendChart:
            return
        x_data = list(range(100))
        y1_data = [random.uniform(50, 100) for _ in x_data]
        y2_data = [random.uniform(40, 80) for _ in x_data]
        y3_data = [random.uniform(60, 90) for _ in x_data]
        self._trendChart.clearCurves()
        self._trendChart.addCurve(x=x_data, y=y1_data, name="系列A")
        self._trendChart.addCurve(x=x_data, y=y2_data, name="系列B")
        self._trendChart.addCurve(x=x_data, y=y3_data, name="系列C")
        self._trendChart.adjustViewRect()
