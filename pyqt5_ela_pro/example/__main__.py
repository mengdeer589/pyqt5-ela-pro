"""
pyqt5_ela_pro 模块示例脚本
"""

import sys
import os

from pyqt5_ela_pro import ElaSplashScreen

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.fonts.warning=false"

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5ElaWidgetTools import (
    eApp,
    ElaWindow,
    ElaDockWidget,
    ElaText,
    ElaListView,
    ElaIconType,
)
from pyqt5_ela_pro.example import (
    BasicContainerPage,
    ContainerDisplayPage,
    ExtensionComponentsPage,
    FormButtonPage,
    ComboBoxPage,
    TableChartPage,
    DrawerTooltipPage,
    AnimationIconPage,
    WindowEmbedderPage,
    BrowserExamplePage,
    ApplicationComponentsPage,
    AdvancedComponentsPage,
    ApplicationUtilitiesPage,
)


class ExampleWindow(ElaWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyqt5_ela_pro 组件示例")
        self.resize(1200, 800)

        self.setUserInfoCardTitle("组件演示")
        self.setUserInfoCardSubTitle("pyqt5_ela_pro@example.com")

        # ════════════════════════════════════════════
        # PyQt5ElaWidgetTools 原生组件
        # ════════════════════════════════════════════
        self.addPageNode("基础控件", BasicContainerPage(self), ElaIconType.IconName.House)
        self.addPageNode("容器展示", ContainerDisplayPage(self), ElaIconType.IconName.Square)
        self.addPageNode("扩展组件", ExtensionComponentsPage(self), ElaIconType.IconName.Puzzle)
        self.addPageNode("应用框架", ApplicationComponentsPage(self), ElaIconType.IconName.Grid)

        # ════════════════════════════════════════════
        # pyqt5_ela_pro 扩展组件
        # ════════════════════════════════════════════
        self.addPageNode("增强按钮", FormButtonPage(self), ElaIconType.IconName.Pen)
        self.addPageNode("下拉框组件", ComboBoxPage(self), ElaIconType.IconName.List)
        self.addPageNode("表格与图表", TableChartPage(self), ElaIconType.IconName.Table)
        self.addPageNode("弹窗与提示", DrawerTooltipPage(self), ElaIconType.IconName.Bell)
        self.addPageNode("动画与图标", AnimationIconPage(self), ElaIconType.IconName.Play)
        self.addPageNode("应用辅助", ApplicationUtilitiesPage(self), ElaIconType.IconName.Sitemap)
        self.addPageNode("Office 文档预览", AdvancedComponentsPage(self), ElaIconType.IconName.FileWord)
        self.addPageNode("窗口嵌入", WindowEmbedderPage(self), ElaIconType.IconName.WindowRestore)
        self.addPageNode("浏览器嵌入", BrowserExamplePage(self), ElaIconType.IconName.Globe)

        # ── DockWidget 停靠面板演示 ────────────────────
        dock1 = ElaDockWidget("页面导航", self)
        dock1.setObjectName("DockPageNav")
        nav_list = ElaListView()
        nav_model = QStandardItemModel()
        for name in ["基础控件", "增强按钮", "下拉框组件", "表格与图表", "弹窗与提示"]:
            nav_model.appendRow(QStandardItem(name))
        nav_list.setModel(nav_model)
        dock1.setWidget(nav_list)
        dock1.setMinimumWidth(180)
        self.addDockWidget(Qt.RightDockWidgetArea, dock1)

        dock2 = ElaDockWidget("说明", self)
        dock2.setObjectName("DockInfo")
        info_text = ElaText(
            "pyqt5_ela_pro 组件示例\n\n"
            "左侧导航栏切换页面，\n"
            "右侧面板可拖拽分离或重新停靠。\n\n"
            "所有演示代码位于:\npyqt5_ela_pro/example/",
        )
        info_text.setTextPixelSize(13)
        info_text.setWordWrap(True)
        info_text.setMinimumWidth(180)
        dock2.setWidget(info_text)
        self.addDockWidget(Qt.RightDockWidgetArea, dock2)
        self.tabifyDockWidget(dock1, dock2)
        dock1.raise_()


if __name__ == "__main__":
    from PyQt5.QtCore import QT_VERSION_STR

    if QT_VERSION_STR < "6.0.0":
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        if QT_VERSION_STR >= "5.14.0":
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )

    app = QApplication(sys.argv)
    eApp.init()
    #
    splash = ElaSplashScreen()
    splash.setTitle("pyqt5_ela_pro")
    splash.setSubTitle("组件示例")
    splash.show()

    messages = [
        "正在加载组件...",
        "正在初始化主题...",
        "正在构建页面...",
        "正在准备就绪...",
    ]
    step = [0]
    timer = QTimer()
    timer.setInterval(100)

    def next_step():
        if step[0] < len(messages):
            splash.setValue(int((step[0] + 1) / len(messages) * 100))
            splash.setStatusText(messages[step[0]])
            step[0] += 1
        else:
            timer.stop()
            window = ExampleWindow()
            app.processEvents()
            splash.finish(window)

    timer.timeout.connect(next_step)
    timer.start()
    # window = ExampleWindow()
    # window.show()
    sys.exit(app.exec_())
