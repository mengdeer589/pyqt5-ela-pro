"""
[pyqt5_ela_pro] 终端输出展示示例页
"""

import random

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QHBoxLayout, QWidget
from PyQt5ElaWidgetTools import ElaIconType

from pyqt5_ela_pro import (
    ElaButton,
    ElaTerminalView,
    terminalThemes,
)
from pyqt5_ela_pro.example.base_page import ExamplePage

SAMPLE_ANSI = (
    "[32m✓[0m 编译 128 个文件        [2m2.31s[0m\n"
    "[32m✓[0m 链接 ela_pro.dll        [2m0.84s[0m\n"
    "[33m![0m 3 个警告：未使用的变量\n"
    "[31m✗[0m 1 个错误：expected ';' before '}'\n"
    "\n"
    "[36m▸[0m 基础色："
    "[30m黑[0m [31m红[0m [32m绿[0m [33m黄[0m "
    "[34m蓝[0m [35m品红[0m [36m青[0m [37m白[0m\n"
    "[36m▸[0m 亮色："
    "[90m黑[0m [91m红[0m [92m绿[0m [93m黄[0m "
    "[94m蓝[0m [95m品红[0m [96m青[0m [97m白[0m\n"
    "[36m▸[0m 256 色：[38;5;208m橙[0m "
    "[38;5;45m青绿[0m [38;5;129m紫[0m [38;5;196m玫红[0m "
    "[38;5;244m灰[0m\n"
    "[36m▸[0m 真彩：[38;2;255;160;60m橙[0m "
    "[38;2;90;200;220m天蓝[0m [38;2;200;120;220m藕紫[0m\n"
    "[36m▸[0m 样式：[1m加粗[0m [2m暗淡[0m [3m斜体[0m "
    "[4m下划线[0m [7m反显[0m [9m删除线[0m\n"
    "[36m▸[0m 背景：[41m  红色底  [0m[42m  绿色底  [0m"
    "[44m  蓝色底  [0m[47m  白色底  [0m\n"
    "\n"
    "[2m被丢弃的序列：OSC 设标题ESC ]0;tBEL、"
    "DCSESC P…ESC \\、字符集选择[0m\n"
)

STREAM_SCRIPT = [
    ("info", "resolving dependencies..."),
    ("info", "collected 87 items"),
    ("test", "tests/test_core.py::test_alpha PASSED"),
    ("test", "tests/test_core.py::test_beta PASSED"),
    ("test", "tests/test_io.py::test_read PASSED"),
    ("warn", "tests/test_io.py::test_write SKIPPED (需要 Win7)"),
    ("test", "tests/test_ui.py::test_render PASSED"),
    ("fail", "tests/test_ui.py::test_theme FAILED"),
    ("", ""),
    ("fail", "assert 3 == 4"),
    ("info", "3 passed, 1 skipped, 1 failed in 4.12s"),
]

_COLORS = {
    "info": "\x1b[36m",
    "test": "\x1b[32m",
    "warn": "\x1b[33m",
    "fail": "\x1b[31m",
}


class TerminalPage(ExamplePage):
    """终端输出展示组件示例页。"""

    PAGE_TITLE = "[ela_ext] 终端输出"

    def __init__(self, parent=None):
        self._timers = []
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._addStaticDemo(main_layout)
        self._addProgressDemo(main_layout)
        self._addStreamDemo(main_layout)
        self._addPaletteDemo(main_layout)

    # ── 1. 静态 ANSI 样例 ──────────────────────────────────────────
    def _addStaticDemo(self, main_layout):
        main_layout.addLayout(self._createHeaderRow("ANSI 色彩渲染", self._demoStatic))
        self._addInfoText(
            "组件解析 SGR（16 色 / 256 色 / truecolor / 粗体 / 暗淡 / 斜体 / "
            "下划线 / 反显 / 删除线）、CSI K 擦行、CSI 2J 清屏、"
            "CSI C/D/G 光标移动；BEL / OSC / DCS 一律丢弃。",
            main_layout,
        )

        view = ElaTerminalView(maxLines=200, parent=self)
        view.setMinimumHeight(300)
        view.append(SAMPLE_ANSI)
        main_layout.addWidget(view)

    def _demoStatic(self):
        """静态 ANSI 样例：把带转义序列的原始文本喂给 append。"""

    # ── 2. 进度条 ──────────────────────────────────────────────────
    def _addProgressDemo(self, main_layout):
        main_layout.addLayout(
            self._createHeaderRow(
                "\\r 整行重绘（进度条 / spinner）", self._demoProgress
            )
        )
        self._addInfoText(
            "pip / git clone / docker pull 这类工具靠 \\r 把光标拉回行首重画整行。"
            "组件把 \\r 后的第一次写入视为整行重绘，所以反复刷新不会把一行"
            "撑成上百个片段。",
            main_layout,
        )

        view = ElaTerminalView(maxLines=100, parent=self)
        view.setMinimumHeight(110)
        main_layout.addWidget(view)

        row = QWidget(self)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        start_btn = ElaButton(
            "开始",
            icon=ElaIconType.IconName.Play,
            variant="solid",
            color="primary",
            parent=row,
        )
        stop_btn = ElaButton(
            "停止",
            icon=ElaIconType.IconName.Stop,
            variant="outlined",
            color="danger",
            parent=row,
        )
        row_layout.addWidget(start_btn)
        row_layout.addWidget(stop_btn)
        row_layout.addStretch(1)
        main_layout.addWidget(row)

        state = {"percent": 0, "timer": None}

        def tick():
            percent = state["percent"] + random.randint(3, 11)
            if percent >= 100:
                percent = 100
            state["percent"] = percent
            bar = "█" * (percent // 5) + "░" * (20 - percent // 5)
            view.append(f"\r\x1b[36m{bar}\x1b[0m {percent:3d}%")
            if percent >= 100:
                self._stop_timer(state)
                view.append("\n\x1b[32m✓\x1b[0m 下载完成\n")
            else:
                view.append("\n")

        def start():
            state["percent"] = 0
            view.clear()
            self._stop_timer(state)
            state["timer"] = QTimer(row)
            state["timer"].timeout.connect(tick)
            state["timer"].start(60)
            self._timers.append(state["timer"])

        def stop():
            self._stop_timer(state)

        start_btn.clicked.connect(start)
        stop_btn.clicked.connect(stop)

    def _demoProgress(self):
        """进度条：用 \\r 让同一行被反复重画。"""

    # ── 3. 伪流式输出 ──────────────────────────────────────────────
    def _addStreamDemo(self, main_layout):
        main_layout.addLayout(
            self._createHeaderRow("流式输出 + 搜索 / 过滤", self._demoStream)
        )
        self._addInfoText(
            "append 可以按 read() 的粒度高频调用，内部按帧合并，同一帧内多次"
            "append 只重排一次。搜索框过滤出不匹配行（数据模型原样保留，"
            "导出与行数统计不受影响），F3 / Shift+F3 在命中之间跳转。",
            main_layout,
        )

        view = ElaTerminalView(maxLines=500, parent=self)
        view.setMinimumHeight(280)
        main_layout.addWidget(view)

        row = QWidget(self)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)
        stream_btn = ElaButton(
            "开始推流",
            icon=ElaIconType.IconName.Play,
            variant="solid",
            color="primary",
            parent=row,
        )
        row_layout.addWidget(stream_btn)
        row_layout.addStretch(1)
        main_layout.addWidget(row)

        state = {"index": 0, "timer": None}

        def tick():
            kind, text = STREAM_SCRIPT[state["index"] % len(STREAM_SCRIPT)]
            state["index"] += 1
            color = _COLORS.get(kind, "")
            view.append(f"{color}{text}\x1b[0m\n" if color else f"{text}\n")
            if state["index"] > len(STREAM_SCRIPT) * 4:
                self._stop_timer(state)

        def start():
            self._stop_timer(state)
            state["index"] = 0
            view.clear()
            state["timer"] = QTimer(row)
            state["timer"].timeout.connect(tick)
            state["timer"].start(120)
            self._timers.append(state["timer"])

        stream_btn.clicked.connect(start)

    def _demoStream(self):
        """流式输出：QTimer 逐行喂 append，配合搜索框过滤。"""

    # ── 4. 调色板 ──────────────────────────────────────────────────
    def _addPaletteDemo(self, main_layout):
        main_layout.addLayout(self._createHeaderRow("调色板切换", self._demoPalette))
        self._addInfoText(
            "内置 one-dark / solarized / classic 三套，各带亮暗两档。"
            "应用主题切换时自动跟随，实例级可用 setPaletteName() 单独指定，"
            "也可以 registerTerminalTheme() 注册自己的配色。",
            main_layout,
        )

        view = ElaTerminalView(maxLines=100, parent=self)
        view.setMinimumHeight(200)
        view.append(
            "\x1b[1mAa Bb Cc\x1b[0m 0123456789\n"
            "\x1b[31m████\x1b[32m████\x1b[33m████\x1b[34m████\x1b[0m\n"
            "\x1b[36m中文回退测试：编译输出 / 构建产物\x1b[0m\n"
        )
        main_layout.addWidget(view)

        row = QWidget(self)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)
        for name in terminalThemes():
            btn = ElaButton(
                name,
                variant="outlined",
                color="primary",
                parent=row,
            )
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.clicked.connect(lambda _c=False, n=name: view.setPaletteName(n))
            row_layout.addWidget(btn)
        row_layout.addStretch(1)
        main_layout.addWidget(row)

    def _demoPalette(self):
        """调色板：setPaletteName 在内置配色之间切换。"""

    # ── 清理 ──────────────────────────────────────────────────────

    def _stop_timer(self, state):
        timer = state.get("timer")
        if timer is not None:
            timer.stop()
            state["timer"] = None

    def closeEvent(self, event):  # noqa: N802 (Qt 命名)
        for state_timer in list(self._timers):
            state_timer.stop()
        self._timers.clear()
        super().closeEvent(event)
