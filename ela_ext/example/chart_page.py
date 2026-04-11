"""
[ela_ext] 图表组件演示页面
"""

import random

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import ElaText, ElaPushButton
from ela_ext import ElaTrendChart, ElaDataTable
from .base_page import ExamplePage


class ChartComponentsPage(ExamplePage):
    """图表组件演示页面"""

    PAGE_TITLE = "[ela_ext] 图表组件"

    def __init__(self, parent=None):
        self._trendChart = None
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoTrendChart(main_layout)

    def _demoTrendChart(self, parent_layout):
        section = ElaText("01. ElaTrendChart - 趋势图", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText(
            "支持多曲线绘制、主题切换、网格线显示、交互式指示器",
            self,
        )
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        self._trendChart = ElaTrendChart(self)
        self._trendChart.setFixedSize(600, 300)

        x_data = list(range(100))
        y1_data = [50 + 30 * ((i % 10) / 10) + random.random() * 10 for i in x_data]
        y2_data = [40 + 20 * ((i % 8) / 8) + random.random() * 15 for i in x_data]
        y3_data = [60 + 25 * ((i % 12) / 12) + random.random() * 8 for i in x_data]

        self._trendChart.addCurve(x=x_data, y=y1_data, name="系列A")
        self._trendChart.addCurve(x=x_data, y=y2_data, name="系列B")
        self._trendChart.addCurve(x=x_data, y=y3_data, name="系列C")
        self._trendChart.adjustViewRect()

        self._trendChart.setOnPointClicked(
            lambda name, x, y: QMessageBox.information(
                self, "点击", f"{name}\nx={x:.2f}, y={y:.2f}"
            )
        )

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        grid_btn = ElaPushButton("切换网格线", self)
        grid_btn.setFixedWidth(100)
        grid_btn.clicked.connect(
            lambda: self._trendChart.setGridVisible(
                not self._trendChart.isGridVisible()
            )
        )
        btn_layout.addWidget(grid_btn)

        legend_btn = ElaPushButton("切换图例", self)
        legend_btn.setFixedWidth(100)
        legend_btn.clicked.connect(
            lambda: self._trendChart.setLegendVisible(
                not self._trendChart.isLegendVisible()
            )
        )
        btn_layout.addWidget(legend_btn)

        refresh_btn = ElaPushButton("刷新数据", self)
        refresh_btn.setFixedWidth(100)
        refresh_btn.clicked.connect(self._onRefreshChartData)
        btn_layout.addWidget(refresh_btn)

        btn_layout.addStretch()

        parent_layout.addWidget(self._trendChart)
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _onRefreshChartData(self):
        if not self._trendChart:
            return
        x_data = list(range(100))
        y1_data = [50 + random.random() * 50 for _ in x_data]
        y2_data = [40 + random.random() * 40 for _ in x_data]
        y3_data = [60 + random.random() * 30 for _ in x_data]

        self._trendChart.clearCurves()
        self._trendChart.addCurve(x=x_data, y=y1_data, name="系列A")
        self._trendChart.addCurve(x=x_data, y=y2_data, name="系列B")
        self._trendChart.addCurve(x=x_data, y=y3_data, name="系列C")
        self._trendChart.adjustViewRect()
