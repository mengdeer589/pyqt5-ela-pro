
import os
import sys

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.fonts.warning=false"

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5ElaWidgetTools import (
    eApp,
    ElaWindow,
    ElaDockWidget,
    ElaText,
    ElaListView,
    ElaPlainTextEdit,
    ElaPushButton,
ElaMessageBar
)


class DockDemoWindow(ElaWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ElaDockWidget 演示")
        self.resize(1000, 700)
        self.setUserInfoCardTitle("Dock 演示")
        self.setUserInfoCardSubTitle("ElaDockWidget@example.com")

        # 添加一个空白页面
        from PyQt5.QtWidgets import QWidget, QVBoxLayout
        page = QWidget()
        layout = QVBoxLayout(page)
        info = ElaText("右侧两个 DockWidget 可拖拽分离或重新停靠\n\n选中一个标签页拖动即可分离为浮动窗口\n拖回边缘即可重新停靠")
        info.setTextPixelSize(14)
        layout.addWidget(info)
        layout.addStretch()
        self.addPageNode("首页", page)

        # ── ElaDockWidget 演示 ────────────────────────

        # Dock 1: 列表
        dock1 = ElaDockWidget("组件列表", self)
        dock1.setObjectName("DockList")
        list_view = ElaListView()
        model = QStandardItemModel()
        for name in ["基础控件", "增强按钮", "下拉框", "表格与图表", "弹窗与提示"]:
            model.appendRow(QStandardItem(name))
        list_view.setModel(model)
        dock1.setWidget(list_view)
        dock1.setMinimumWidth(180)
        self.addDockWidget(Qt.RightDockWidgetArea, dock1)

        # Dock 2: 日志
        dock2 = ElaDockWidget("日志输出", self)
        dock2.setObjectName("DockLog")
        log = ElaPlainTextEdit()
        log.setReadOnly(True)
        log.appendPlainText("欢迎使用 ElaDockWidget")
        log.appendPlainText("拖拽标签页可分离为独立窗口")
        log.appendPlainText("拖回边缘可恢复停靠")
        dock2.setWidget(log)
        dock2.setMinimumWidth(180)
        self.addDockWidget(Qt.RightDockWidgetArea, dock2)

        # 合并为标签页
        self.tabifyDockWidget(dock1, dock2)
        dock1.raise_()

        # Dock 3: 底部
        dock3 = ElaDockWidget("快捷操作", self)
        dock3.setObjectName("DockActions")
        from PyQt5.QtWidgets import QHBoxLayout, QWidget
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        for text in ["保存", "导出", "刷新"]:
            btn = ElaPushButton(text)
            btn_layout.addWidget(btn)
        btn_layout.addStretch()
        dock3.setWidget(btn_widget)
        dock3.setMinimumHeight(50)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock3)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    eApp.init()
    window = DockDemoWindow()
    window.show()
    sys.exit(app.exec_())
