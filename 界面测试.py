"""下拉框底部弹出测试 — 将全部 6 种下拉框置于窗口底部。"""

import os
import sys

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.fonts.warning=false"

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5ElaWidgetTools import eApp, ElaText

from pyqt5_ela_pro import (
    ElaTagBox,
    ElaTagMultiBox,
    ElaTagSearchBox,
    ElaTagSearchMultiBox,
    ElaSearchBox,
    ElaSearchMultiBox,
)

ITEMS = [
    "Python", "C++", "JavaScript", "Rust", "Go", "Java",
    "TypeScript", "Kotlin", "Swift", "Ruby", "PHP", "C#",
    "Scala", "Perl", "Haskell", "Lua", "Dart", "Elixir",
]


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("下拉框底部弹出测试")
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 顶部说明
        info = ElaText("将窗口拖到屏幕底部，点击各下拉框确认弹窗不超出屏幕", self)
        info.setTextPixelSize(14)
        layout.addWidget(info)

        layout.addStretch()  # 把组件全部顶到底部

        # 第一行：3 个单选框
        row1 = QHBoxLayout()
        row1.setSpacing(15)
        row1.addWidget(self._make_combo(ElaTagBox, "ElaTagBox"))
        row1.addWidget(self._make_combo(ElaTagSearchBox, "ElaTagSearchBox"))
        row1.addWidget(self._make_combo(ElaSearchBox, "ElaSearchBox", has_title=False))
        layout.addLayout(row1)

        # 第二行：3 个多选框
        row2 = QHBoxLayout()
        row2.setSpacing(15)
        row2.addWidget(self._make_combo(ElaTagMultiBox, "ElaTagMultiBox"))
        row2.addWidget(self._make_combo(ElaTagSearchMultiBox, "ElaTagSearchMultiBox"))
        row2.addWidget(self._make_combo(ElaSearchMultiBox, "ElaSearchMultiBox", has_title=False))
        layout.addLayout(row2)

    def _make_combo(self, cls, label, has_title=True):
        container = QWidget()
        clayout = QVBoxLayout(container)
        clayout.setContentsMargins(0, 0, 0, 0)
        clayout.setSpacing(4)

        lbl = ElaText(label, container)
        lbl.setTextPixelSize(10)
        clayout.addWidget(lbl)

        if has_title:
            combo = cls(title=label, parent=container)
        else:
            combo = cls(parent=container)
        combo.addItems(ITEMS)
        combo.setFixedWidth(200)
        clayout.addWidget(combo)

        return container


if __name__ == "__main__":
    app = QApplication(sys.argv)
    eApp.init()
    window = Window()
    window.show()
    sys.exit(app.exec_())
