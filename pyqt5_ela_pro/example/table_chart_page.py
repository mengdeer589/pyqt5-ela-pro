"""
[pyqt5_ela_pro] 表格与图表组件页面

合并了以下来源的组件:
- pyqt5_ela_pro: 表格、图表组件
"""

import random
import math

from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QFileDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from PyQt5ElaWidgetTools import ElaText, ElaPushButton, ElaLineEdit, ElaComboBox, ElaCheckBox, ElaSlider, ElaGraphicsScene, ElaGraphicsView
from pyqt5_ela_pro import ElaDataTable, ElaTrendChart, ElaPlotWidget, ElaDashboardGauge
from .base_page import ExamplePage

try:
    import pyqtgraph  # noqa: F401
    _HAS_PYQTGRAPH = True
except ImportError:
    _HAS_PYQTGRAPH = False

try:
    import matplotlib  # noqa: F401
    _HAS_MATPLOTLIB = True
except ImportError:
    _HAS_MATPLOTLIB = False


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
        self._demoGraphicsView(main_layout)

    def _demoTable(self, parent_layout):
        self._demoBasicTable(parent_layout)
        self._demoAsyncTable(parent_layout)
        self._demoStyleTable(parent_layout)
        self._demoSortTable(parent_layout)
        self._demoParquetTable(parent_layout)

    def _demoChart(self, parent_layout):
        self._demoTrendChart(parent_layout)
        parent_layout.addSpacing(20)
        self._demoPyqtgraphChart(parent_layout)
        parent_layout.addSpacing(20)
        self._demoFigureCanvas(parent_layout)
        parent_layout.addSpacing(20)
        self._demoDashboardGauge(parent_layout)
        parent_layout.addSpacing(20)

    def _demoBasicTable(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("01. ela_ext - ElaDataTable 基础表格", self._demoBasicTable)
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
        parent_layout.addLayout(
            self._createHeaderRow("02. ela_ext - ElaDataTable 异步加载", self._demoAsyncTable)
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
        parent_layout.addLayout(
            self._createHeaderRow("03. ela_ext - ElaDataTable 单元格样式", self._demoStyleTable)
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
        parent_layout.addLayout(
            self._createHeaderRow("04. ela_ext - ElaDataTable 表头排序", self._demoSortTable)
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

    def _demoParquetTable(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("05. ela_ext - ElaParquetTable Parquet 文件查看", self._demoParquetTable)
        )
        self._addInfoText(
            "分页浏览 Parquet 文件，显示列统计信息。需要安装 polars",
            parent_layout,
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        open_btn = ElaPushButton("打开 Parquet 文件", self)
        open_btn.setFixedWidth(130)
        open_btn.clicked.connect(self._onOpenParquet)
        btn_layout.addWidget(open_btn)
        size_label = ElaText("每页行数:", self)
        size_label.setTextPixelSize(14)
        btn_layout.addWidget(size_label)
        for s in [50, 100, 200, 500, 1000, 2000]:
            btn = ElaPushButton(str(s), self)
            btn.setFixedWidth(50)
            btn.clicked.connect(lambda checked, x=s: self._onSetParquetPageSize(x))
            btn_layout.addWidget(btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(10)

        from pyqt5_ela_pro import ElaParquetTable
        try:
            self._parquet_table = ElaParquetTable(page_size=50, parent=self)
            self._parquet_table.setFixedHeight(350)
            self._parquet_table.setVisible(False)
            parent_layout.addWidget(self._parquet_table)
            self._parquet_available = True
        except ImportError:
            self._parquet_table = None
            self._parquet_available = False

        self._parquet_info = ElaText("请点击上方按钮选择 .parquet 文件", self)
        self._parquet_info.setTextPixelSize(14)
        parent_layout.addWidget(self._parquet_info)
        parent_layout.addSpacing(20)

    def _onOpenParquet(self):
        if not self._parquet_available:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 Parquet 文件", "", "Parquet (*.parquet);;所有文件 (*)"
        )
        if not path:
            return
        try:
            self._parquet_table.loadData(path)
            self._parquet_table.setVisible(True)
            if self._parquet_info:
                self._parquet_info.deleteLater()
                self._parquet_info = None
        except ImportError as e:
            from PyQt5ElaWidgetTools import ElaMessageBar, ElaMessageBarType
            ElaMessageBar.error(
                ElaMessageBarType.PositionPolicy.Top,
                "缺少依赖",
                f"需要 polars 库: {e}",
                5000, self,
            )
        except Exception as e:
            from PyQt5ElaWidgetTools import ElaMessageBar, ElaMessageBarType
            ElaMessageBar.error(
                ElaMessageBarType.PositionPolicy.Top,
                "加载失败",
                str(e),
                5000, self,
            )

    def _onSetParquetPageSize(self, size):
        if self._parquet_table and self._parquet_available:
            self._parquet_table.setPageSize(size)

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
        parent_layout.addLayout(
            self._createHeaderRow("02. ela_ext - ElaTrendChart 趋势图", self._demoTrendChart)
        )
        self._addInfoText(
            "支持多曲线绘制、主题切换、网格线显示、交互式指示器\n"
            "启用交互后，左键拖拽平移，滚轮缩放，双击重置视图",
            parent_layout,
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
        data_count_label = ElaText("数据点数:", self)
        data_count_label.setTextPixelSize(14)
        btn_layout.addWidget(data_count_label)
        self._data_count_input = ElaLineEdit(self)
        self._data_count_input.setFixedWidth(80)
        self._data_count_input.setText("100")
        btn_layout.addWidget(self._data_count_input)
        self._interact_btn = ElaPushButton("启用交互", self)
        self._interact_btn.setFixedWidth(100)
        self._interact_btn.clicked.connect(self._toggleChartInteraction)
        btn_layout.addWidget(self._interact_btn)
        png_btn = ElaPushButton("导出PNG", self)
        png_btn.setFixedWidth(80)
        png_btn.clicked.connect(self._exportPng)
        btn_layout.addWidget(png_btn)
        svg_btn = ElaPushButton("导出SVG", self)
        svg_btn.setFixedWidth(80)
        svg_btn.clicked.connect(self._exportSvg)
        type_label = ElaText("图表类型:", self)
        type_label.setTextPixelSize(14)
        btn_layout.addWidget(type_label)
        self._chart_type_combo = ElaComboBox(self)
        self._chart_type_combo.setFixedWidth(120)
        self._chart_type_combo.addItems(["折线图", "散点图"])
        btn_layout.addWidget(self._chart_type_combo)
        btn_layout.addStretch()
        parent_layout.addWidget(self._trendChart)
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoPyqtgraphChart(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("03. ela_ext - ElaPlotWidget 实时波形图 (pyqtgraph)", self._demoPyqtgraphChart)
        )
        if not _HAS_PYQTGRAPH:
            self._addInfoText(
                "ElaPlotWidget 需要 pyqtgraph，请运行: pip install pyqtgraph",
                parent_layout,
            )
            return
        self._addInfoText(
            "基于 pyqtgraph 的高性能实时绘图，支持主题自适应\n"
            "使用 ``setDownsampling`` 自动降采样以处理大量数据点",
            parent_layout,
        )

        self._pg_widget = ElaPlotWidget(self)
        self._pg_widget.setFixedSize(600, 300)

        self._pg_plot = self._pg_widget.plot(title="实时波形 (pyqtgraph)")
        self._pg_plot.showGrid(x=True, y=True, alpha=0.5)
        self._pg_plot.setLabel("left", "幅度")
        self._pg_plot.setLabel("bottom", "sample")
        self._pg_plot.setDownsampling(mode="peak")

        self._pg_total = 40000
        self._pg_data_x = list(range(self._pg_total))
        self._pg_data_y = [0.0] * self._pg_total
        self._pg_t = 0.0
        self._pg_index = 0
        self._pg_curve = self._pg_plot.plot([], [], pen="b")

        # 数据生成 timer
        self._pg_sim_timer = QTimer(self)
        self._pg_sim_timer.setInterval(1)
        self._pg_sim_timer.timeout.connect(self._onPgGenerateData)

        # UI 刷新 timer
        self._pg_ui_timer = QTimer(self)
        self._pg_ui_timer.setInterval(30)
        self._pg_ui_timer.timeout.connect(self._onPgUpdatePlot)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self._pg_toggle_btn = ElaPushButton("开始实时", self)
        self._pg_toggle_btn.setFixedWidth(100)
        self._pg_toggle_btn.clicked.connect(self._onTogglePyqtgraphRealtime)
        btn_layout.addWidget(self._pg_toggle_btn)
        reset_btn = ElaPushButton("重置数据", self)
        reset_btn.setFixedWidth(100)
        reset_btn.clicked.connect(self._onPgReset)
        btn_layout.addWidget(reset_btn)
        gen_label = ElaText("生成(ms):", self)
        gen_label.setTextPixelSize(14)
        btn_layout.addWidget(gen_label)
        self._pg_gen_input = ElaLineEdit(self)
        self._pg_gen_input.setFixedWidth(60)
        self._pg_gen_input.setText("1")
        btn_layout.addWidget(self._pg_gen_input)
        ui_label = ElaText("刷新(ms):", self)
        ui_label.setTextPixelSize(14)
        btn_layout.addWidget(ui_label)
        self._pg_ui_input = ElaLineEdit(self)
        self._pg_ui_input.setFixedWidth(60)
        self._pg_ui_input.setText("30")
        btn_layout.addWidget(self._pg_ui_input)
        self._pg_auto_scale_cb = ElaCheckBox("平移X轴", self)
        self._pg_auto_scale_cb.setChecked(True)
        btn_layout.addWidget(self._pg_auto_scale_cb)
        btn_layout.addStretch()
        parent_layout.addWidget(self._pg_widget)
        parent_layout.addLayout(btn_layout)

    def _onTogglePyqtgraphRealtime(self):
        running = self._pg_sim_timer.isActive()
        if running:
            self._pg_sim_timer.stop()
            self._pg_ui_timer.stop()
            self._pg_toggle_btn.setText("开始实时")
        else:
            try:
                gen_interval = max(1, int(self._pg_gen_input.text()))
            except ValueError:
                gen_interval = 1
            try:
                ui_interval = max(10, int(self._pg_ui_input.text()))
            except ValueError:
                ui_interval = 30
            self._pg_sim_timer.setInterval(gen_interval)
            self._pg_ui_timer.setInterval(ui_interval)
            self._pg_sim_timer.start()
            self._pg_ui_timer.start()
            self._pg_toggle_btn.setText("停止实时")

    def _onPgGenerateData(self):
        if self._pg_index >= self._pg_total:
            self._pg_sim_timer.stop()
            return
        val = (
            math.sin(self._pg_t * 0.02) * 50 + 50
            + 0.5 * math.sin(self._pg_t * 0.05) * 25
            + random.gauss(0, 1) * 5
        )
        self._pg_data_y[self._pg_index] = val
        self._pg_t += 1.0
        self._pg_index += 1

    def _onPgUpdatePlot(self):
        n = self._pg_index
        if n == 0:
            return
        self._pg_curve.setData(self._pg_data_x[:n], self._pg_data_y[:n])
        if self._pg_auto_scale_cb.isChecked():
            if n > 100:
                self._pg_plot.setXRange(max(0, n - 600), n + 100)
            else:
                self._pg_plot.setXRange(0, 1000)
        else:
            self._pg_plot.setXRange(0, max(n + 100, 1000))

    def _onPgReset(self):
        self._pg_sim_timer.stop()
        self._pg_ui_timer.stop()
        self._pg_toggle_btn.setText("开始实时")
        self._pg_data_y = [0.0] * self._pg_total
        self._pg_t = 0.0
        self._pg_index = 0
        self._pg_curve.setData([], [])
        self._pg_plot.setXRange(0, 1000)

    def _demoFigureCanvas(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("04. ela_ext - ElaFigureCanvas 图表 (matplotlib)", self._demoFigureCanvas)
        )
        if not _HAS_MATPLOTLIB:
            self._addInfoText(
                "ElaFigureCanvas 需要 matplotlib，请运行: pip install matplotlib",
                parent_layout,
            )
            return
        from pyqt5_ela_pro import ElaFigureCanvas
        from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
        self._addInfoText(
            "基于 matplotlib 的图表画布，支持主题自适应\n"
            "跟随 Ela 主题自动切换 Light/Dark 配色\n"
            "数据生成与 UI 刷新分离，使用两个 QTimer 实现流畅更新",
            parent_layout,
        )
        self._mpl_canvas = ElaFigureCanvas(self)
        self._mpl_canvas.setFixedSize(600, 300)
        self._mpl_toolbar = NavigationToolbar2QT(self._mpl_canvas, self)
        self._mpl_ax = self._mpl_canvas.figure.subplots()
        self._mpl_ax.set_xlim(0, 1000)
        self._mpl_ax.set_ylim(-2, 2)
        self._mpl_ax.set_xlabel("sample")
        self._mpl_ax.set_ylabel("value")
        self._mpl_ax.set_title("实时波形")
        self._mpl_ax.grid(True, alpha=0.7)
        self._mpl_canvas.figure.tight_layout()

        self._mpl_line, = self._mpl_ax.plot([], [], 'b-', lw=0.5)
        self._mpl_total = 40000
        self._mpl_data_x = list(range(self._mpl_total))
        self._mpl_data_y = [0.0] * self._mpl_total
        self._mpl_t = 0.0
        self._mpl_index = 0

        # 数据生成 timer（高频）
        self._mpl_sim_timer = QTimer(self)
        self._mpl_sim_timer.setInterval(1)
        self._mpl_sim_timer.timeout.connect(self._onMplGenerateData)

        # UI 刷新 timer（低频）
        self._mpl_ui_timer = QTimer(self)
        self._mpl_ui_timer.setInterval(30)
        self._mpl_ui_timer.timeout.connect(self._onMplUpdatePlot)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self._mpl_toggle_btn = ElaPushButton("开始实时", self)
        self._mpl_toggle_btn.setFixedWidth(100)
        self._mpl_toggle_btn.clicked.connect(self._onToggleMatplotlibRealtime)
        btn_layout.addWidget(self._mpl_toggle_btn)
        reset_btn = ElaPushButton("重置数据", self)
        reset_btn.setFixedWidth(100)
        reset_btn.clicked.connect(self._onMplReset)
        btn_layout.addWidget(reset_btn)
        gen_label = ElaText("生成(ms):", self)
        gen_label.setTextPixelSize(14)
        btn_layout.addWidget(gen_label)
        self._mpl_gen_input = ElaLineEdit(self)
        self._mpl_gen_input.setFixedWidth(60)
        self._mpl_gen_input.setText("1")
        btn_layout.addWidget(self._mpl_gen_input)
        ui_label = ElaText("刷新(ms):", self)
        ui_label.setTextPixelSize(14)
        btn_layout.addWidget(ui_label)
        self._mpl_ui_input = ElaLineEdit(self)
        self._mpl_ui_input.setFixedWidth(60)
        self._mpl_ui_input.setText("30")
        btn_layout.addWidget(self._mpl_ui_input)
        self._mpl_auto_scale_cb = ElaCheckBox("平移X轴", self)
        self._mpl_auto_scale_cb.setChecked(True)
        btn_layout.addWidget(self._mpl_auto_scale_cb)
        btn_layout.addStretch()
        parent_layout.addWidget(self._mpl_toolbar)
        parent_layout.addWidget(self._mpl_canvas)
        parent_layout.addLayout(btn_layout)

    def _onToggleMatplotlibRealtime(self):
        running = self._mpl_sim_timer.isActive()
        if running:
            self._mpl_sim_timer.stop()
            self._mpl_ui_timer.stop()
            self._mpl_toggle_btn.setText("开始实时")
        else:
            try:
                gen_interval = max(1, int(self._mpl_gen_input.text()))
            except ValueError:
                gen_interval = 1
            try:
                ui_interval = max(10, int(self._mpl_ui_input.text()))
            except ValueError:
                ui_interval = 30
            self._mpl_sim_timer.setInterval(gen_interval)
            self._mpl_ui_timer.setInterval(ui_interval)
            self._mpl_sim_timer.start()
            self._mpl_ui_timer.start()
            self._mpl_toggle_btn.setText("停止实时")

    def _onMplGenerateData(self):
        if self._mpl_index >= self._mpl_total:
            self._mpl_sim_timer.stop()
            return
        val = (
            math.sin(self._mpl_t * 0.02)
            + 0.5 * math.sin(self._mpl_t * 0.05)
            + random.gauss(0, 1) * 0.1
        )
        self._mpl_data_y[self._mpl_index] = val
        self._mpl_t += 1.0
        self._mpl_index += 1

    def _onMplUpdatePlot(self):
        n = self._mpl_index
        if n == 0:
            return
        self._mpl_line.set_data(self._mpl_data_x[:n], self._mpl_data_y[:n])
        if self._mpl_auto_scale_cb.isChecked():
            if n > 100:
                self._mpl_ax.set_xlim(max(0, n - 600), n + 100)
            else:
                self._mpl_ax.set_xlim(0, 1000)
        else:
            self._mpl_ax.set_xlim(0, max(n + 100, 1000))
        self._mpl_canvas.draw_idle()

    def _onMplReset(self):
        self._mpl_sim_timer.stop()
        self._mpl_ui_timer.stop()
        self._mpl_toggle_btn.setText("开始实时")
        self._mpl_data_y = [0.0] * self._mpl_total
        self._mpl_t = 0.0
        self._mpl_index = 0
        self._mpl_line.set_data([], [])
        self._mpl_ax.set_xlim(0, 1000)
        self._mpl_canvas.draw_idle()
        self._mpl_canvas.draw_idle()

    def _onRefreshMatplotlib(self):
        """更新一次静态数据（不再需要，保留兼容）"""
        pass

    def _demoDashboardGauge(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("05. ela_ext - ElaDashboardGauge 仪表盘", self._demoDashboardGauge)
        )
        self._addInfoText(
            "全 QPainter 自绘仪表盘，支持弧形刻度、指针、颜色分段和动画过渡",
            parent_layout,
        )

        self._gauge = ElaDashboardGauge(self)
        self._gauge.setMinimum(0)
        self._gauge.setMaximum(1000)
        self._gauge.setValue(0)
        self._gauge.setTitle("引擎转速")
        self._gauge.setUnit("r/min")
        self._gauge.setDangerPercent(0.9)
        self._gauge.setWarningPercent(0.7)

        gauge_layout = QHBoxLayout()
        gauge_layout.setSpacing(15)
        gauge_layout.addWidget(self._gauge)

        control_layout = QVBoxLayout()
        control_layout.setSpacing(8)

        val_label = ElaText("值: 0", self)
        val_label.setTextPixelSize(18)
        font = val_label.font()
        font.setBold(True)
        val_label.setFont(font)
        control_layout.addWidget(val_label)
        self._gauge_val_label = val_label

        self._gauge_slider = ElaSlider(Qt.Orientation.Horizontal, self)
        self._gauge_slider.setMinimum(0)
        self._gauge_slider.setMaximum(1000)
        self._gauge_slider.setValue(0)
        self._gauge_slider.setFixedWidth(200)
        self._gauge_slider.valueChanged.connect(self._onGaugeSliderChanged)
        control_layout.addWidget(self._gauge_slider)

        size_label = ElaText("表盘尺寸:", self)
        size_label.setTextPixelSize(14)
        control_layout.addWidget(size_label)

        btn_size = QHBoxLayout()
        btn_size.setSpacing(8)
        for s in [100, 150, 200, 260, 300, 350]:
            btn = ElaPushButton(str(s), self)
            btn.setFixedWidth(50)
            btn.clicked.connect(lambda checked, x=s: self._gauge.setFixedSize(x, x))
            btn_size.addWidget(btn)
        control_layout.addLayout(btn_size)

        btn_row2 = QHBoxLayout()
        btn_row2.setSpacing(8)
        self._gauge_auto_btn = ElaPushButton("自动扫描", self)
        self._gauge_auto_btn.setFixedWidth(100)
        self._gauge_auto_btn.clicked.connect(self._onToggleGaugeAuto)
        btn_row2.addWidget(self._gauge_auto_btn)
        reset_btn = ElaPushButton("归零", self)
        reset_btn.setFixedWidth(70)
        reset_btn.clicked.connect(lambda: self._onGaugeSetValue(0))
        btn_row2.addWidget(reset_btn)
        control_layout.addLayout(btn_row2)
        control_layout.addStretch()

        gauge_layout.addLayout(control_layout)
        gauge_layout.addStretch()
        parent_layout.addLayout(gauge_layout)

        self._gauge_timer = QTimer(self)
        self._gauge_timer.setInterval(50)
        self._gauge_timer.timeout.connect(self._onGaugeTick)
        self._gauge_tick_val = 0.0
        self._gauge_tick_dir = 1

    def _onGaugeSetValue(self, val):
        self._gauge.setValue(val)
        self._gauge_slider.setValue(val)
        self._gauge_val_label.setText(f"值: {int(val)}")

    def _onGaugeSliderChanged(self, val):
        self._gauge.setValue(val)
        self._gauge_val_label.setText(f"值: {int(val)}")

    def _onToggleGaugeAuto(self):
        if self._gauge_timer.isActive():
            self._gauge_timer.stop()
            self._gauge_auto_btn.setText("自动扫描")
        else:
            self._gauge_tick_val = self._gauge.value()
            self._gauge_tick_dir = 1
            self._gauge_timer.start()
            self._gauge_auto_btn.setText("停止扫描")

    def _onGaugeTick(self):
        self._gauge_tick_val += self._gauge_tick_dir * 10
        if self._gauge_tick_val >= self._gauge.maximum():
            self._gauge_tick_val = self._gauge.maximum()
            self._gauge_tick_dir = -1
        elif self._gauge_tick_val <= self._gauge.minimum():
            self._gauge_tick_val = self._gauge.minimum()
            self._gauge_tick_dir = 1
        self._gauge_val_label.setText(f"值: {int(self._gauge_tick_val)}")
        self._gauge_slider.setValue(int(self._gauge_tick_val))
        self._gauge.setValue(self._gauge_tick_val)

    def _toggleGrid(self):
        self._gridVisible = not self._gridVisible
        self._trendChart.setGridVisible(self._gridVisible)

    def _toggleLegend(self):
        self._legendVisible = not self._legendVisible
        self._trendChart.setLegendVisible(self._legendVisible)

    def _toggleChartInteraction(self):
        enabled = not self._trendChart.isInteractionEnabled()
        self._trendChart.setInteractionEnabled(enabled)
        self._interact_btn.setText("禁用交互" if enabled else "启用交互")

    def _exportPng(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "导出 PNG", "chart.png", "PNG 图片 (*.png)"
        )
        if path:
            self._trendChart.saveToPng(path)

    def _exportSvg(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "导出 SVG", "chart.svg", "SVG 矢量图 (*.svg)"
        )
        if path:
            self._trendChart.saveToSvg(path)

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
        text = self._data_count_input.text() if self._data_count_input else "100"
        try:
            count = max(1, int(text))
        except ValueError:
            count = 100
        x_data = list(range(count))
        y1_data = [random.uniform(50, 100) for _ in x_data]
        y2_data = [random.uniform(40, 80) for _ in x_data]
        y3_data = [random.uniform(60, 90) for _ in x_data]
        self._trendChart.clearCurves()

        chart_type = self._chart_type_combo.currentText() if self._chart_type_combo else "折线图"
        t = "scatter" if chart_type == "散点图" else "line"
        if t == "scatter":
            self._trendChart.addCurve(x=x_data, y=y1_data, name="圆形", curve_type=t, dot_shape="circle")
            self._trendChart.addCurve(x=x_data, y=y2_data, name="方块", curve_type=t, dot_shape="square")
            self._trendChart.addCurve(x=x_data, y=y3_data, name="菱形", curve_type=t, dot_shape="diamond")
        else:
            self._trendChart.addCurve(x=x_data, y=y1_data, name="实线", curve_type=t, line_style="solid")
            self._trendChart.addCurve(x=x_data, y=y2_data, name="虚线", curve_type=t, line_style="dash")
            self._trendChart.addCurve(x=x_data, y=y3_data, name="点线", curve_type=t, line_style="dot")
        self._trendChart.adjustViewRect()

    def _demoGraphicsView(self, parent_layout):
        from PyQt5.QtGui import QColor, QBrush, QPen

        parent_layout.addLayout(
            self._createHeaderRow("06. PyQt5ElaWidgetTools - ElaGraphicsScene / ElaGraphicsView 图形视图", self._demoGraphicsView)
        )
        self._addInfoText(
            "Ela 主题的图形视图框架，支持场景中放置可交互的图形项", parent_layout
        )
        scene = ElaGraphicsScene(self)
        scene.setSceneRect(-200, -200, 400, 400)
        view = ElaGraphicsView(self)
        view.setScene(scene)
        view.setFixedHeight(300)
        view.setDragMode(ElaGraphicsView.DragMode.ScrollHandDrag)

        rect = view.scene().addRect(-60, -60, 120, 120, QPen(QColor("#1677ff"), 2), QBrush(QColor("#e6f4ff")))
        rect.setFlag(rect.GraphicsItemFlag.ItemIsMovable, True)
        rect.setFlag(rect.GraphicsItemFlag.ItemIsSelectable, True)

        circle = view.scene().addEllipse(-50, -50, 100, 100, QPen(QColor("#52c41a"), 2), QBrush(QColor("#f6ffed")))
        circle.setPos(150, 0)
        circle.setFlag(circle.GraphicsItemFlag.ItemIsMovable, True)
        circle.setFlag(circle.GraphicsItemFlag.ItemIsSelectable, True)

        from PyQt5.QtGui import QPainterPath
        tp = QPainterPath()
        tp.moveTo(0, -50)
        tp.lineTo(50, 50)
        tp.lineTo(-50, 50)
        tp.closeSubpath()
        triangle = view.scene().addPath(tp, QPen(QColor("#fa8c16"), 2), QBrush(QColor("#fff7e6")))
        triangle.setPos(-150, 100)
        triangle.setFlag(triangle.GraphicsItemFlag.ItemIsMovable, True)
        triangle.setFlag(triangle.GraphicsItemFlag.ItemIsSelectable, True)

        parent_layout.addWidget(view)
        parent_layout.addSpacing(20)
