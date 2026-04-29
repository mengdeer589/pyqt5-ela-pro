"""
pyqt5_ela_pro 模块示例脚本
"""

import sys
import os

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.fonts.warning=false"

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5ElaWidgetTools import (
    eApp,
    ElaWindow,
)
from pyqt5_ela_pro import ElaSplashScreen
from pyqt5_ela_pro.example import (
    BasicContainerPage,
    FormButtonPage,
    ComboBoxPage,
    TableChartPage,
    DrawerTooltipPage,
    AnimationIconPage,
    WindowEmbedderPage,
    ApplicationComponentsPage,
    AdvancedComponentsPage,
    BrowserExamplePage,
    ApplicationUtilitiesPage,
    GraphicsComponentsPage,
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
        self.addPageNode("基础控件", BasicContainerPage(self))
        self.addPageNode("应用框架", ApplicationComponentsPage(self))

        # ════════════════════════════════════════════
        # pyqt5_ela_pro 扩展组件
        # ════════════════════════════════════════════
        self.addPageNode("增强按钮", FormButtonPage(self))
        self.addPageNode("下拉框组件", ComboBoxPage(self))
        self.addPageNode("表格与图表", TableChartPage(self))
        self.addPageNode("弹窗与提示", DrawerTooltipPage(self))
        self.addPageNode("动画与图标", AnimationIconPage(self))
        self.addPageNode("应用辅助", ApplicationUtilitiesPage(self))
        self.addPageNode("Office 文档预览", AdvancedComponentsPage(self))
        self.addPageNode("窗口嵌入", WindowEmbedderPage(self))
        self.addPageNode("浏览器嵌入", BrowserExamplePage(self))
        self.addPageNode("其他组件", GraphicsComponentsPage(self))


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

    splash = ElaSplashScreen(
        title="pyqt5_ela_pro",
        subtitle="组件示例",
        width=500,
        height=350,
    )
    splash.show()
    splash.showMessage("正在加载组件...")
    app.processEvents()

    window = ExampleWindow()

    splash.showMessage("正在启动...")
    splash.setProgress(0.8)
    app.processEvents()

    splash.showMessage("加载完成")
    splash.setProgress(1.0)
    app.processEvents()

    splash.finish(window)
    window.show()
    sys.exit(app.exec_())
