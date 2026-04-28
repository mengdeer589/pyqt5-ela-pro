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
    TableChartPage,
    DrawerTooltipPage,
    AnimationIconPage,
    ComboBoxPage,
    WindowEmbedderPage,
    ApplicationComponentsPage,
    AdvancedComponentsPage,
    GraphicsComponentsPage,
    BrowserExamplePage,
)


class ExampleWindow(ElaWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyqt5_ela_pro 组件示例")
        self.resize(1200, 800)

        self.setUserInfoCardTitle("组件演示")
        self.setUserInfoCardSubTitle("pyqt5_ela_pro@example.com")

        self.addPageNode("基础组件", BasicContainerPage(self))
        self.addPageNode("表单与按钮", FormButtonPage(self))
        self.addPageNode("下拉框组件", ComboBoxPage(self))
        self.addPageNode("表格与图表", TableChartPage(self))
        self.addPageNode("抽屉与提示", DrawerTooltipPage(self))
        self.addPageNode("动画与图标", AnimationIconPage(self))
        self.addPageNode("窗口嵌入", WindowEmbedderPage(self))
        self.addPageNode("ela 应用级组件", ApplicationComponentsPage(self))
        self.addPageNode("高级组件", AdvancedComponentsPage(self))
        self.addPageNode("图形组件", GraphicsComponentsPage(self))
        self.addPageNode("浏览器嵌入", BrowserExamplePage(self))


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
