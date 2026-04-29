
import os
import sys

from PyQt5ElaWidgetTools.ElaWidgetTools import ElaScrollPage, ElaScrollArea, ElaScrollPageArea
from pyqt5_ela_pro import ElaThemeWidget

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.fonts.warning=false"

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QWidget)
from PyQt5ElaWidgetTools import (ElaPushButton, ElaText, ElaWindow, eApp)


class DemoWindow(ElaWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        # # ── 页面1: ElaScrollPage ─────────────────────────────
        # page1 = ElaScrollPage(self)
        # content1 = QWidget()
        # lay1 = QVBoxLayout(content1)
        # for i in range(50):
        #     btn = ElaPushButton(f"ElaScrollPage 按钮 {i}")
        #     lay1.addWidget(btn)
        # lay1.addStretch()
        # page1.addCentralWidget(content1)
        # self.addPageNode("ElaScrollPage", page1)
        #
        # ── 页面2: ElaScrollArea ─────────────────────────────
        page2 = ElaThemeWidget(self)
        lay2 = QVBoxLayout(page2)
        lay2.setContentsMargins(0, 0, 0, 0)
        area = ElaScrollArea(self)
        inner = ElaThemeWidget(self)
        inner_lay = QVBoxLayout(inner)
        for i in range(30):
            btn = ElaPushButton(f"ElaScrollArea 按钮 {i}")
            inner_lay.addWidget(btn)
        inner_lay.addStretch()
        area.setWidget(inner)
        area.setWidgetResizable(True)
        lay2.addWidget(area)
        self.addPageNode("ElaScrollArea", page2)

        # # ── 页面3: ElaScrollPageArea ──────────────────────────
        # page3 = ElaThemeWidget(self)
        # lay3 = QVBoxLayout(page3)
        # for i in range(20):
        #     spa = ElaScrollPageArea(self)
        #     spa_lay = QVBoxLayout(spa)
        #     label = ElaText(f"ElaScrollPageArea 区块 {i + 1}", spa)
        #     label.setTextPixelSize(14)
        #     spa_lay.addWidget(label)
        #     desc = ElaText("这是 ElaScrollPageArea，用于在滚动页面中分组内容。", spa)
        #     desc.setTextPixelSize(12)
        #     spa_lay.addWidget(desc)
        #     lay3.addWidget(spa)
        # lay3.addStretch()
        # self.addPageNode("ElaScrollPageArea", page3)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    eApp.init()
    window = DemoWindow()
    window.show()
    app.exec_()
