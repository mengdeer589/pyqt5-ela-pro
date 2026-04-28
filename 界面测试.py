
import sys
import os

from pyqt5_ela_pro import ElaPrimaryButton, ElaThemeWidget

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.fonts.warning=false"

from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QToolButton
from PyQt5ElaWidgetTools import eApp, ElaWindow, ElaText, eTheme, ElaThemeType, ElaToolButton, ElaPushButton


class DemoWindow(ElaWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._browser = None
        self._setup_ui()

    def _setup_ui(self):


        central = ElaThemeWidget(self)
        self.addPageNode("浏览器示例",central)
        # self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        self.btn=ElaPrimaryButton(text="测试", parent=self)
        layout.addWidget(self.btn)
        self.btn.clicked.connect(lambda: central.alert("你好",'error'))





if __name__ == "__main__":

    app = QApplication(sys.argv)
    eApp.init()

    window = DemoWindow()
    window.show()
    app.exec_()
