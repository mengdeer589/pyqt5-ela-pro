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
from pyqt5_ela_pro.example import (
    BasicContainerPage,
    FormButtonPage,
    TableChartPage,
    DrawerTooltipPage,
    AnimationIconPage,
    ComboBoxPage,
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


if __name__ == "__main__":
    try:
        QT_VERSION_STR = "5.14.0"
    except Exception:
        QT_VERSION_STR = "6.8.3"

    if QT_VERSION_STR < "6.0.0":
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        if QT_VERSION_STR >= "5.14.0":
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )

    app = QApplication(sys.argv)
    eApp.init()
    window = ExampleWindow()
    window.show()
    sys.exit(app.exec_())
