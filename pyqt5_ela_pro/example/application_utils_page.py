"""
[pyqt5_ela_pro] 应用辅助组件演示页面
"""

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5ElaWidgetTools import ElaText, ElaPushButton
from pyqt5_ela_pro import ElaSplashScreen, ElaTaskbarProgress, ElaButton
from .base_page import ExamplePage


class ApplicationUtilitiesPage(ExamplePage):
    """应用辅助组件演示页面"""

    PAGE_TITLE = "辅助组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoSplashScreen(main_layout)
        self._demoTaskbarProgress(main_layout)

    def _demoSplashScreen(self, parent_layout):
        parent_layout.addLayout(self._createHeaderRow("01. ElaSplashScreen - 启动画面", self._demoSplashScreen))
        self._addInfoText(
            "应用程序启动画面，支持渐变背景、标题、副标题和加载进度显示", parent_layout
        )

        def _show_splash():
            splash = ElaSplashScreen(self)
            splash.setTitle("pyqt5_ela_pro")
            splash.setSubTitle("Fluent UI For QWidget")
            splash.show()
            splash.setStatusText("正在加载组件...")

            messages = [
                "正在加载组件...",
                "正在初始化主题...",
                "正在启动应用程序...",
            ]
            step = [0]

            def next_step():
                if step[0] < len(messages):
                    splash.setValue(int((step[0] + 1) / len(messages) * 100))
                    splash.setStatusText(messages[step[0]])
                    step[0] += 1
                else:
                    splash.finish(self.window())

            timer = QTimer(self)
            timer.timeout.connect(next_step)
            timer.start(800)

        splash_btn = ElaPushButton("显示启动画面", self)
        splash_btn.setFixedWidth(120)
        splash_btn.clicked.connect(_show_splash)
        parent_layout.addWidget(splash_btn)
        parent_layout.addSpacing(20)

    def _demoTaskbarProgress(self, parent_layout):
        parent_layout.addLayout(self._createHeaderRow("02. ElaTaskbarProgress - 任务栏进度条", self._demoTaskbarProgress))
        self._addInfoText(
            "在 Windows 任务栏图标上显示进度条，支持暂停/恢复/停止/不确定状态。", parent_layout
        )

        self._taskbar_progress = None
        self._taskbar_running = False
        self._taskbar_paused = False
        self._taskbar_value = 0
        self._taskbar_timer = None

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        start_btn = ElaButton("开始下载", variant="solid", color="primary", parent=self)
        start_btn.setFixedWidth(100)
        start_btn.clicked.connect(self._startTaskbarDemo)
        btn_layout.addWidget(start_btn)

        pause_btn = ElaButton("暂停", variant="solid", color="primary", parent=self)
        pause_btn.setFixedWidth(80)
        pause_btn.clicked.connect(self._pauseTaskbarDemo)
        btn_layout.addWidget(pause_btn)

        resume_btn = ElaButton("继续", variant="solid", color="primary", parent=self)
        resume_btn.setFixedWidth(80)
        resume_btn.clicked.connect(self._resumeTaskbarDemo)
        btn_layout.addWidget(resume_btn)

        stop_btn = ElaButton("停止", variant="solid", color="primary", parent=self)
        stop_btn.setFixedWidth(80)
        stop_btn.clicked.connect(self._stopTaskbarDemo)
        btn_layout.addWidget(stop_btn)

        reset_btn = ElaButton("重置", variant="solid", color="primary", parent=self)
        reset_btn.setFixedWidth(80)
        reset_btn.clicked.connect(self._resetTaskbarDemo)
        btn_layout.addWidget(reset_btn)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)

        info = ElaText("提示: 任务栏进度条仅在 Windows 平台有效，且需要关联到窗口", self)
        info.setTextPixelSize(12)
        parent_layout.addWidget(info)
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
        self._taskbar_progress.setRange(0, 100)
        self._taskbar_progress.setValue(0)
        self._taskbar_progress.show()
        self._taskbar_timer = QTimer(self)
        self._taskbar_timer.timeout.connect(self._updateTaskbarProgress)
        self._taskbar_timer.start(50)

    def _pauseTaskbarDemo(self):
        if self._taskbar_progress and self._taskbar_running:
            self._taskbar_progress.pause()
            self._taskbar_paused = True
            if self._taskbar_timer:
                self._taskbar_timer.stop()

    def _resumeTaskbarDemo(self):
        if self._taskbar_progress and self._taskbar_paused:
            self._taskbar_progress.resume()
            self._taskbar_paused = False
            if self._taskbar_timer:
                self._taskbar_timer.start(50)

    def _stopTaskbarDemo(self):
        if self._taskbar_timer:
            self._taskbar_timer.stop()
        self._taskbar_running = False
        if self._taskbar_progress:
            self._taskbar_progress.stop()

    def _resetTaskbarDemo(self):
        if self._taskbar_timer:
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
            self._taskbar_progress.setValue(self._taskbar_value)
        if self._taskbar_value >= 100:
            if self._taskbar_timer:
                self._taskbar_timer.stop()
            self._taskbar_running = False
            if self._taskbar_progress:
                self._taskbar_progress.hide()
