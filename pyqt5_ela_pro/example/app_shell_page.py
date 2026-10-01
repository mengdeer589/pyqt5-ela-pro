"""启动与托盘

应用外壳：启动画面（`ElaSplashScreen`）、任务栏进度（`ElaTaskbarProgress`）、
系统托盘（`ElaTrayIcon` / `ElaTrayHost`）。

这三样此前分散在「应用辅助」（2 个组件）和「托盘图标」两页，而它们回答的是
同一个问题：**我的程序怎么在系统里露出存在**。合到一页后这个问题有一个
地方可查，而不是让用户在侧边栏里凭标题猜。

托盘菜单**不许出现 checkable 项** —— `ElaMenu` 的图标列与勾选框互斥，
一旦有 checkable 项，所有项的 ElaAwesome 图标都不再绘制；开关状态要写进
文案并换图标（见 `tray_host.py` 的 `_syncToggleItem`）。
"""

from __future__ import annotations

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QHBoxLayout, QWidget
from PyQt5ElaWidgetTools import (
    ElaIconType,
    ElaMenu,
    ElaPlainTextEdit,
    ElaPushButton,
    ElaText,
)
from pyqt5_ela_pro import (
    ElaButton,
    ElaMenuItem,
    ElaSplashScreen,
    ElaTaskbarProgress,
    ElaTrayIcon,
)
from .base_page import ExamplePage
from datetime import datetime
from PyQt5.QtGui import QColor, QIcon, QPainter, QPixmap
from .selection_page import SelectionAssistantPage
from .tray_host import ElaTrayHost, QUIT_ID, SEPARATOR, TOGGLE_WINDOW_ID


def _dot(color: str) -> QIcon:
    """画一个纯色圆点当托盘图标（示例不依赖外部资源文件）。"""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(color))
    painter.drawEllipse(2, 2, 28, 28)
    painter.end()
    return QIcon(pixmap)


class AppShellPage(ExamplePage):
    """启动与托盘示例页。"""

    PAGE_TITLE = "启动与托盘"

    def __init__(self, parent=None):
        # 托盘 / 宿主 / 日志在 demo 方法里**延迟创建**（点按钮才建），
        # 但「先写日志再创日志控件」的顺序在真实使用里很常见
        # （_demoHost 结束时要写一行，_demoEvents 才建 ElaPlainTextEdit），
        # 所以这里先给 None，让 _log_line 能提前判空返回。
        self._tray = None
        self._host = None
        self._log = None
        self._taskbar_progress = None
        self._taskbar_timer = None
        self._taskbar_running = False
        self._taskbar_paused = False
        self._taskbar_value = 0
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoSplashScreen(main_layout)
        self._demoTaskbarProgress(main_layout)
        self._demoTray(main_layout)
        self._demoHost(main_layout)
        self._demoEvents(main_layout)

    def _demoSplashScreen(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "01. ElaSplashScreen - 启动画面", self._demoSplashScreen
            )
        )
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

    def _pauseTaskbarDemo(self):
        if self._taskbar_progress and self._taskbar_running:
            self._taskbar_progress.pause()
            self._taskbar_paused = True
            if self._taskbar_timer:
                self._taskbar_timer.stop()

    def _resetTaskbarDemo(self):
        if self._taskbar_timer:
            self._taskbar_timer.stop()
        self._taskbar_running = False
        self._taskbar_paused = False
        self._taskbar_value = 0
        if self._taskbar_progress:
            self._taskbar_progress.reset()
            self._taskbar_progress.hide()

    def _resumeTaskbarDemo(self):
        if self._taskbar_progress and self._taskbar_paused:
            self._taskbar_progress.resume()
            self._taskbar_paused = False
            if self._taskbar_timer:
                self._taskbar_timer.start(50)

    def _ensureTaskbarProgress(self):
        if self._taskbar_progress is None:
            window = self.window()
            if window:
                self._taskbar_progress = ElaTaskbarProgress(window)
        return self._taskbar_progress is not None

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

    def _stopTaskbarDemo(self):
        if self._taskbar_timer:
            self._taskbar_timer.stop()
        self._taskbar_running = False
        if self._taskbar_progress:
            self._taskbar_progress.stop()

    def _demoTaskbarProgress(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "02. ElaTaskbarProgress - 任务栏进度条", self._demoTaskbarProgress
            )
        )
        self._addInfoText(
            "在 Windows 任务栏图标上显示进度条，支持暂停/恢复/停止/不确定状态。",
            parent_layout,
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

        info = ElaText(
            "提示: 任务栏进度条仅在 Windows 平台有效，且需要关联到窗口", self
        )
        info.setTextPixelSize(12)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(20)

    def _buildTrayMenu(self):
        """裸 ElaMenu 直接 setContextMenu 即可（托盘菜单只认原生 QMenu 体系）。

        注意 ElaMenu 的父对象必须是 **QWidget**（ElaTrayIcon 是 QObject，不行），
        所以挂到页面自身。
        """
        menu = ElaMenu(self)
        menu.setMenuItemHeight(28)
        menu.addElaIconAction(ElaIconType.IconName.Gear, "设置…")
        menu.addSeparator()
        menu.addElaIconAction(ElaIconType.IconName.Info, "关于")
        return menu

    def _log_line(self, text):
        if self._log is None:
            return
        stamp = datetime.now().strftime("%H:%M:%S")
        self._log.appendPlainText(f"[{stamp}] {text}")

    def _on_notify(self):
        ok = self._tray.notify(
            "通知标题",
            "这是一条来自托盘的气泡通知。",
            ElaTrayIcon.TrayState.Normal,
            3000,
        )
        self._log_line(
            "notify() 返回 "
            + ("True（已弹气泡）" if ok else "False（该环境不支持，已降级）")
        )

    def _on_tray_error(self, message):
        """``notify()`` 的降级路径：不支持气泡的 Win7 上组件发信号而不崩。"""
        self._log_line(f"托盘通知失败：{message}")

    def _on_tray_toggle(self):
        window = self.window()
        if window is None:
            return
        window.setVisible(not window.isVisible())
        self._log_line("主窗口 -> " + ("显示" if window.isVisible() else "隐藏"))

    def _demoTray(self, main_layout):
        info = ElaText(
            "托盘由 Explorer 绘制，QIcon 不吃 eTheme，组件不做主题自动适配——"
            "深浅两版图标需宿主自行准备。Win7 等环境可能不支持气泡通知，"
            "notify() 会降级为发 errorOccurred 而不崩。",
            self,
        )
        info.setTextPixelSize(14)
        main_layout.addWidget(info)

        self._tray = ElaTrayIcon(_dot("#4f9dff"), "pyqt5_ela_pro 托盘演示", self)
        self._tray.setIcons(
            normal=_dot("#4f9dff"),
            warning=_dot("#f0a13a"),
            critical=_dot("#e5484d"),
        )
        self._tray.setMenu(self._buildTrayMenu())
        self._tray.errorOccurred.connect(self._on_tray_error)

        row = QWidget(self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        for label, state in (
            ("正常", ElaTrayIcon.TrayState.Normal),
            ("警告", ElaTrayIcon.TrayState.Warning),
            ("错误", ElaTrayIcon.TrayState.Critical),
        ):
            btn = ElaButton(
                label, variant="outlined", color="primary", size="small", parent=row
            )
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.clicked.connect(lambda _c=False, s=state: self._tray.setState(s))
            layout.addWidget(btn)

        layout.addSpacing(12)
        notify_btn = ElaButton(
            "发气泡通知",
            icon=ElaIconType.IconName.Bell,
            variant="solid",
            color="primary",
            size="small",
            parent=row,
        )
        notify_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        notify_btn.clicked.connect(self._on_notify)
        layout.addWidget(notify_btn)

        toggle_btn = ElaButton(
            "显示 / 隐藏托盘",
            icon=ElaIconType.IconName.Eye,
            variant="outlined",
            size="small",
            parent=row,
        )
        toggle_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        toggle_btn.clicked.connect(self._on_tray_toggle)
        layout.addWidget(toggle_btn)
        layout.addStretch(1)
        main_layout.addWidget(row)

    def _find_selection_page(self):
        """定位划词助手页面。

        ``ElaWindow`` **没有**「按 widget 查页面」的 API（只有
        ``navigation(pageKey)``），但 ``addPageNode`` 会把页面 reparent 进
        内容区，所以页面就是主窗口的子控件，用 ``findChildren`` 找。
        """
        window = self.window()
        if window is None:
            return None
        pages = window.findChildren(SelectionAssistantPage)
        return pages[0] if pages else None

    # -- 分区 03：日志 -----------------------------------------------------

    def _on_host_action(self, actionId):  # noqa: N803 (Qt 命名)
        if actionId == TOGGLE_WINDOW_ID:
            self._host.toggleWindow()
        elif actionId == "selection":
            # 页面提供的对外入口（复用页面内开关那条路径，失败回滚只写一处）。
            # 注意**不是** setAssistantEnabled —— 划词页没这个方法，
            # 外部入口是 toggleAssistantFromTray()。
            page = self._find_selection_page()
            if page is None:
                return
            enabled = page.toggleAssistantFromTray()
            self._log_line("划词助手 -> " + ("开" if enabled else "关"))
        else:
            self._log_line(f"未处理的动作：{actionId}")

    def _on_quit_requested(self):
        """退出**交给宿主**：``ElaTrayHost.shutdown()`` 自己管窗口与进程，
        页面只发信号 + 记日志（直接 ``QApplication.quit()`` 会跳过宿主的
        清理顺序，托盘图标会留一个点不动的灰图标）。"""
        self._log_line("宿主请求退出")
        self._host.shutdown()

    def _sync_selection_item(self, enabled):
        self._host.updateItem(
            "selection",
            label=f"划词助手：{'开' if enabled else '关'}",
            icon=(
                ElaIconType.IconName.Highlighter
                if enabled
                else ElaIconType.IconName.Circle
            ),
        )

    def _on_selection_state_changed(self, enabled):
        # 划词页开关 -> 托盘文案（双向同步的另一半）
        self._sync_selection_item(enabled)

    def _on_window_visibility(self, visible):
        window = self.window()
        if window is not None:
            window.setVisible(bool(visible))
        self._log_line("宿主请求主窗口" + ("显示" if visible else "隐藏"))

    def _demoHost(self, main_layout):
        info = ElaText(
            "ElaTrayHost 是应用级宿主骨架（放在 example/ 而非组件库）："
            "托盘 + 主窗口显隐 + 退出。菜单项复用 ElaMenuItem；"
            "「显隐主窗口」不用勾选框而用文案+图标表达状态——"
            "ElaMenu 里只要有 checkable 项，所有项的图标都会消失。",
            self,
        )
        info.setTextPixelSize(14)
        main_layout.addWidget(info)

        self._host = ElaTrayHost(
            self.window(), _dot("#52c41a"), "pyqt5_ela_pro 宿主演示", self
        )
        self._host.setItems(
            [
                ElaMenuItem(TOGGLE_WINDOW_ID, "隐藏主窗口", ElaIconType.IconName.Eye),
                SEPARATOR,
                ElaMenuItem("selection", "划词助手：关", ElaIconType.IconName.Circle),
                SEPARATOR,
                ElaMenuItem(QUIT_ID, "退出", ElaIconType.IconName.PowerOff),
            ]
        )
        self._host.actionTriggered.connect(self._on_host_action)
        self._host.windowVisibilityRequested.connect(self._on_window_visibility)
        self._host.quitRequested.connect(self._on_quit_requested)
        self._host.show()
        # 初始文案对齐划词页的真实状态（不预设为「开」——助手可能尚未创建）
        page = self._find_selection_page()
        self._sync_selection_item(page.isAssistantEnabled() if page else False)
        if page is not None:
            # 页面内开关变化时同步回来（双向同步的另一半）
            page.assistantStateChanged.connect(self._on_selection_state_changed)

        row = QWidget(self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        for label, slot in (
            ("显示托盘", self._host.show),
            ("隐藏托盘", self._host.hide),
            ("切换主窗口显隐", self._host.toggleWindow),
        ):
            btn = ElaButton(label, variant="outlined", size="small", parent=row)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.clicked.connect(slot)
            layout.addWidget(btn)
        layout.addStretch(1)
        main_layout.addWidget(row)

        self._log_line("托盘宿主已启动：右键托盘看菜单，单击图标切换主窗口显隐")

    def _demoEvents(self, main_layout):
        info = ElaText("托盘与宿主的全部信号出口。", self)
        info.setTextPixelSize(14)
        main_layout.addWidget(info)

        self._log = ElaPlainTextEdit(self)
        self._log.setReadOnly(True)
        self._log.setMinimumHeight(140)
        main_layout.addWidget(self._log)

    # -- 信号回调（这些是**槽**，抽取时不会被依赖闭包带上，必须显式声明）----
    # 依赖闭包只认 `self._x(...)`；`btn.clicked.connect(self._on_x)` 这种
    # 裸引用不匹配，早期版本漏掉它们，症状是运行期 AttributeError 而 lint 全绿。

    # -- 信号回调（这些是**槽**，抽取时不会被依赖闭包带上，必须显式声明）----
    # 依赖闭包只认 `self._x(...)`；`btn.clicked.connect(self._on_x)` 这种
    # 裸引用不匹配，早期版本漏掉它们，症状是运行期 AttributeError 而 lint 全绿。
