"""下拉框底部弹出测试 — 将全部 6 种下拉框置于窗口底部。"""

import os
import sys

from PyQt5ElaWidgetTools.ElaWidgetTools import ElaCheckBox, ElaText

from pyqt5_ela_pro import ElaThemeWidget

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.fonts.warning=false"

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5ElaWidgetTools import eApp, ElaDrawerArea



class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("下拉框底部弹出测试")
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        widget=ElaDrawerArea(self)
        layout.addWidget(widget)
        draw=ElaThemeWidget(self)
        draw_lay=QVBoxLayout(draw)
        draw_lay.addWidget(ElaCheckBox('选项1',draw))
        widget.addDrawer(draw)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    eApp.init()
    window = Window()
    window.show()
    sys.exit(app.exec_())
