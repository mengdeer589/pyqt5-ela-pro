"""
[ela_ext] 应用级组件演示页面 - PyQt5ElaWidgetTools
"""

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QApplication
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import (
    ElaText,
    ElaAppBar,
    ElaStatusBar,
    ElaTheme,
    ElaEventBus,
    ElaPushButton,
)
from pyqt5_ela_pro import ElaSplashScreen, ElaTaskbarProgress, ElaPrimaryButton
from .base_page import ExamplePage


class ApplicationComponentsPage(ExamplePage):
    """ela 应用级组件演示页面"""

    PAGE_TITLE = "ela 应用级组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoAppBar(main_layout)
        self._demoStatusBar(main_layout)
        self._demoTheme(main_layout)
        self._demoEventBus(main_layout)
        self._demoSplashScreen(main_layout)
        self._demoTaskbarProgress(main_layout)

    def _demoAppBar(self, parent_layout):
        section = ElaText("01. ElaAppBar - 应用栏", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("应用栏组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        app_bar = ElaAppBar(self)
        app_bar.setFixedHeight(50)
        parent_layout.addWidget(app_bar)
        parent_layout.addSpacing(20)

    def _demoStatusBar(self, parent_layout):
        section = ElaText("02. ElaStatusBar - 状态栏", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("状态栏组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        status_bar = ElaStatusBar(self)
        parent_layout.addWidget(status_bar)
        parent_layout.addSpacing(20)

    def _demoTheme(self, parent_layout):
        section = ElaText("03. ElaTheme - 主题管理", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("主题管理组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        parent_layout.addSpacing(20)

    def _demoEventBus(self, parent_layout):
        section = ElaText("04. ElaEventBus - 事件总线", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("事件总线组件", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        parent_layout.addSpacing(20)

    def _demoSplashScreen(self, parent_layout):
        section = ElaText("05. ElaSplashScreen - 启动画面", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText(
            "应用程序启动画面，支持渐变背景、标题、副标题和加载进度显示", self
        )
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        show_btn = ElaPushButton("显示启动画面", self)
        show_btn.setFixedWidth(120)
        show_btn.clicked.connect(self._showSplashDemo)
        btn_layout.addWidget(show_btn)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _showSplashDemo(self):
        splash = ElaSplashScreen(
            title="pyqt5_ela_pro",
            subtitle="Fluent UI For QWidget",
            width=500,
            height=350,
        )
        splash.show()
        splash.showMessage("正在加载组件...")

        messages = [
            "正在加载组件...",
            "正在初始化主题...",
            "正在启动应用程序...",
        ]
        self._splash_step = 0

        def next_step():
            if self._splash_step < len(messages):
                progress = (self._splash_step + 1) / len(messages)
                splash.setProgress(progress)
                splash.showMessage(messages[self._splash_step])
                self._splash_step += 1
            else:
                self._splash_timer.stop()
                splash.finish(self.window())

        self._splash_timer = QTimer(self)
        self._splash_timer.timeout.connect(next_step)
        self._splash_timer.start(800)

    def _demoTaskbarProgress(self, parent_layout):
        section = ElaText("06. ElaTaskbarProgress - 任务栏进度条", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText(
            "在 Windows 任务栏图标上显示进度条，支持暂停/恢复/停止/不确定状态。", self
        )
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        start_btn = ElaPrimaryButton("开始下载", parent=self)
        start_btn.setFixedWidth(100)
        start_btn.clicked.connect(self._startTaskbarDemo)
        btn_layout.addWidget(start_btn)

        pause_btn = ElaPrimaryButton("暂停", parent=self)
        pause_btn.setFixedWidth(80)
        pause_btn.clicked.connect(self._pauseTaskbarDemo)
        btn_layout.addWidget(pause_btn)

        resume_btn = ElaPrimaryButton("继续", parent=self)
        resume_btn.setFixedWidth(80)
        resume_btn.clicked.connect(self._resumeTaskbarDemo)
        btn_layout.addWidget(resume_btn)

        stop_btn = ElaPrimaryButton("停止", parent=self)
        stop_btn.setFixedWidth(80)
        stop_btn.clicked.connect(self._stopTaskbarDemo)
        btn_layout.addWidget(stop_btn)

        indeterminate_btn = ElaPrimaryButton("不确定状态", parent=self)
        indeterminate_btn.setFixedWidth(100)
        indeterminate_btn.clicked.connect(self._indeterminateTaskbarDemo)
        btn_layout.addWidget(indeterminate_btn)

        reset_btn = ElaPrimaryButton("重置", parent=self)
        reset_btn.setFixedWidth(80)
        reset_btn.clicked.connect(self._resetTaskbarDemo)
        btn_layout.addWidget(reset_btn)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)

        self._taskbar_progress = None
        self._taskbar_running = False
        self._taskbar_paused = False
        self._taskbar_value = 0
        self._taskbar_timer = None

        from PyQt5.QtCore import QTimer

        self._taskbar_timer = QTimer(self)
        self._taskbar_timer.timeout.connect(self._updateTaskbarProgress)

        info2 = ElaText(
            "提示: 任务栏进度条仅在 Windows 平台有效，且需要关联到窗口", self
        )
        info2.setTextPixelSize(12)
        parent_layout.addWidget(info2)
        parent_layout.addSpacing(20)

    def _ensureTaskbarProgress(self):
        if self._taskbar_progress is None:
            window = self.window()
            if window:
                self._taskbar_progress = ElaTaskbarProgress(window)
        return self._taskbar_progress is not None

    def _startTaskbarDemo(self):
        if not self._ensureTaskbarProgress():
            return

        self._taskbar_running = True
        self._taskbar_paused = False
        self._taskbar_value = 0

        self._taskbar_progress.set_range(0, 100)
        self._taskbar_progress.set_value(0)
        self._taskbar_progress.show()
        self._taskbar_timer.start(50)

    def _pauseTaskbarDemo(self):
        if self._taskbar_progress and self._taskbar_running:
            self._taskbar_progress.pause()
            self._taskbar_paused = True
            self._taskbar_timer.stop()

    def _resumeTaskbarDemo(self):
        if self._taskbar_progress and self._taskbar_paused:
            self._taskbar_progress.resume()
            self._taskbar_paused = False
            self._taskbar_timer.start(50)

    def _stopTaskbarDemo(self):
        self._taskbar_timer.stop()
        self._taskbar_running = False
        if self._taskbar_progress:
            self._taskbar_progress.stop()

    def _indeterminateTaskbarDemo(self):
        if not self._ensureTaskbarProgress():
            return

        self._taskbar_progress.show()
        self._taskbar_progress.set_range(0, 0)
        self._taskbar_progress.set_value(0)

    def _resetTaskbarDemo(self):
        self._taskbar_timer.stop()
        self._taskbar_running = False
        self._taskbar_paused = False
        self._taskbar_value = 0

        if self._taskbar_progress:
            self._taskbar_progress.reset()
            self._taskbar_progress.hide()

    def _updateTaskbarProgress(self):
        if not self._taskbar_running or self._taskbar_paused:
            return

        self._taskbar_value += 1
        if self._taskbar_progress:
            self._taskbar_progress.set_value(self._taskbar_value)

        if self._taskbar_value >= 100:
            self._taskbar_timer.stop()
            self._taskbar_running = False
            if self._taskbar_progress:
                self._taskbar_progress.hide()
