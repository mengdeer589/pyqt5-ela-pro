"""
[pyqt5_ela_pro] 窗口嵌入组件页面

展示 ElaWindowEmbedder 和 ElaBrowserEmbedder 的用法。
"""

from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QWidget
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import ElaText, ElaPushButton, ElaComboBox
from pyqt5_ela_pro import ThemeWidget, ElaWindowEmbedder, ElaPrimaryButton
from .base_page import ExamplePage

import win32gui
import win32con


class WindowEmbedderPage(ExamplePage):
    """窗口嵌入组件页面"""

    PAGE_TITLE = "窗口嵌入"

    def __init__(self, parent=None):
        self._embedder = None
        self._browserEmbedder = None
        self._windowsList = []
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoWindowEmbedder(main_layout)
        self._demoBrowserEmbedder(main_layout)

    def _getAllWindows(self):
        self._windowsList = []

        def enum_callback(hwnd, _):
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    class_name = win32gui.GetClassName(hwnd)
                    self._windowsList.append((hwnd, title, class_name))
            return True

        try:
            win32gui.EnumWindows(enum_callback, None)
        except Exception:
            pass
        self._windowsList.sort(key=lambda x: x[1].lower())

    def _demoWindowEmbedder(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("01. ElaWindowEmbedder - 窗口嵌入")
        )
        self._addInfoText(
            "将外部窗口嵌入到 QWidget 中，支持通过 hwnd、窗口标题或类名嵌入。",
            parent_layout,
        )

        self._getAllWindows()

        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(10)
        mode_label = ElaText("嵌入模式:", self)
        mode_label.setTextPixelSize(14)
        mode_layout.addWidget(mode_label)

        self._modeCombo = ElaComboBox(self)
        self._modeCombo.addItems(["按句柄 (Hwnd)", "按标题 (Title)", "按类名 (Class)"])
        self._modeCombo.setFixedWidth(150)
        self._modeCombo.currentIndexChanged.connect(self._onModeChanged)
        mode_layout.addWidget(self._modeCombo)

        self._windowCombo = ElaComboBox(self)
        self._windowCombo.setFixedWidth(300)
        self._refreshWindowCombo()
        self._windowCombo.currentIndexChanged.connect(self._onWindowSelected)
        mode_layout.addWidget(self._windowCombo)

        refresh_btn = ElaPushButton("刷新窗口列表", self)
        refresh_btn.setFixedWidth(100)
        refresh_btn.clicked.connect(self._refreshWindows)
        mode_layout.addWidget(refresh_btn)

        mode_layout.addStretch()
        parent_layout.addLayout(mode_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self._embedBtn = ElaPushButton("嵌入窗口", self)
        self._embedBtn.setFixedWidth(100)
        self._embedBtn.clicked.connect(self._embedCurrentWindow)
        btn_layout.addWidget(self._embedBtn)

        release_btn = ElaPushButton("释放窗口", self)
        release_btn.setFixedWidth(100)
        release_btn.clicked.connect(self._releaseWindow)
        btn_layout.addWidget(release_btn)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)

        self._embedderContainer = QWidget(self)
        self._embedderContainer.setFixedHeight(300)
        self._embedderContainer.setStyleSheet(
            "background: #2b2b2b; border: 1px solid #444;"
        )
        parent_layout.addWidget(self._embedderContainer)

        self._embedder = ElaWindowEmbedder(self._embedderContainer)
        self._embedder.window_embedded.connect(self._onWindowEmbedded)
        self._embedder.window_released.connect(self._onWindowReleased)
        self._embedder.window_not_found.connect(self._onWindowNotFound)
        self._embedder.embed_error.connect(self._onEmbedError)
        self._embedder.embed_timeout.connect(self._onEmbedTimeout)

        self._infoText = ElaText(
            '嵌入区域 - 从下拉框选择窗口后点击"嵌入窗口"',
            self._embedderContainer,
        )
        self._infoText.setAlignment(Qt.AlignCenter)
        self._infoText.setStyleSheet("color: #888; border: none;")
        self._infoText.setFixedSize(350, 30)

        parent_layout.addSpacing(30)

    def _onModeChanged(self, index):
        self._refreshWindowCombo()

    def _refreshWindowCombo(self):
        self._windowCombo.clear()
        mode = self._modeCombo.currentIndex()

        if mode == 0:
            for hwnd, title, class_name in self._windowsList:
                display_text = f"0x{hwnd:X} | {title} | {class_name}"
                self._windowCombo.addItem(display_text, hwnd)
        elif mode == 1:
            seen_titles = set()
            for hwnd, title, class_name in self._windowsList:
                if title not in seen_titles:
                    seen_titles.add(title)
                    self._windowCombo.addItem(title, (title, None))
        elif mode == 2:
            seen_classes = set()
            for hwnd, title, class_name in self._windowsList:
                if class_name not in seen_classes:
                    seen_classes.add(class_name)
                    self._windowCombo.addItem(class_name, (class_name, None))

    def _refreshWindows(self):
        self._getAllWindows()
        self._refreshWindowCombo()
        self._showStatus("窗口列表已刷新")

    def _onWindowSelected(self, index):
        pass

    def _embedCurrentWindow(self):
        index = self._windowCombo.currentIndex()
        if index < 0:
            self._showStatus("请先选择要嵌入的窗口")
            return

        mode = self._modeCombo.currentIndex()

        if mode == 0:
            hwnd = self._windowCombo.currentData()
            if hwnd:
                self._embedder.embed_by_hwnd(hwnd)
        elif mode == 1:
            title = self._windowCombo.currentText()
            if title:
                self._embedder.embed_by_title(title)
        elif mode == 2:
            class_name = self._windowCombo.currentText()
            if class_name:
                self._embedder.embed_by_class(class_name)

    def _releaseWindow(self):
        if self._embedder.has_embedded_window:
            self._embedder.release()
        else:
            self._showStatus("没有嵌入的窗口")

    def _showStatus(self, msg):
        self._infoText.setText(msg)
        self._infoText.adjustSize()

    def _onWindowEmbedded(self, hwnd):
        self._showStatus(f"窗口已嵌入: 0x{hwnd:X}")

    def _onWindowReleased(self, hwnd):
        self._showStatus(f"窗口已释放: 0x{hwnd:X}")

    def _onWindowNotFound(self, msg):
        self._showStatus(msg)

    def _onEmbedError(self, msg):
        self._showStatus(f"错误: {msg}")

    def _onEmbedTimeout(self):
        self._showStatus("嵌入超时")

    def _demoBrowserEmbedder(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("02. ElaBrowserEmbedder - 浏览器嵌入")
        )
        self._addInfoText(
            "嵌入浏览器窗口，支持 CDP 控制。继承自 ElaWindowEmbedder，额外依赖 psutil 和 websocket-client。",
            parent_layout,
        )
        self._addInfoText(
            "提示: 请通过 'from pyqt5_ela_pro import ElaBrowserEmbedder' 导入",
            parent_layout,
        )

        info_text = (
            "ElaBrowserEmbedder 功能:\n"
            "  - 基于 Chrome DevTools Protocol (CDP) 控制浏览器\n"
            "  - 支持页面加载监控 (load_started / load_finished 信号)\n"
            "  - 支持 JavaScript 执行 (run_js)\n"
            "  - 支持页面导航 (navigate / reload)\n"
            "  - 自动管理浏览器进程生命周期"
        )
        self._addInfoText(info_text, parent_layout)
        parent_layout.addSpacing(20)
