"""[pyqt5_ela_pro] 划词助手示例页面。"""

from __future__ import annotations

from datetime import datetime

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QCursor, QTextCursor
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QWidget,
)
from PyQt5ElaWidgetTools import (
    ElaCheckBox,
    ElaComboBox,
    ElaIconType,
    ElaPlainTextEdit,
    ElaText,
    ElaToggleSwitch,
)

from pyqt5_ela_pro import (
    ElaButton,
    ElaMenuItem,
    ElaSelectionAssistant,
)

from .base_page import ExamplePage

#: 日志最大行数
_MAX_LOG_LINES = 200


class SelectionAssistantPage(ExamplePage):
    """划词助手：全局划词监听、动作条与事件演示。"""

    PAGE_TITLE = "[ela_ext] 划词助手"

    #: 助手启用状态变化（供托盘菜单等外部入口回写文案用）
    assistantStateChanged = pyqtSignal(bool)

    def _addDemoContent(self, main_layout):
        self._assistant = None
        self._action_boxes = {}
        self._demo_actions = ()
        self._log = None
        self._updating_switch = False

        main_layout.addLayout(
            self._createHeaderRow("01. 启用与参数", self._demoSettings)
        )
        self._demoSettings(main_layout)

        main_layout.addLayout(
            self._createHeaderRow("02. 动作配置（纯信号）", self._demoActions)
        )
        self._demoActions(main_layout)

        main_layout.addLayout(
            self._createHeaderRow("03. 事件日志与宿主实现", self._demoEvents)
        )
        self._demoEvents(main_layout)

    # -- 分区 01：启用与参数 -------------------------------------------------

    def _demoSettings(self, main_layout):
        info = ElaText(
            "在任意应用拖选文本（或双击选词），动作条会出现在光标附近；"
            "取词通过模拟 Ctrl+C 完成，默认会恢复原剪贴板。",
            self,
        )
        info.setTextPixelSize(14)
        main_layout.addWidget(info)

        row = QWidget(self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(ElaText("启用", row))
        self._enable_switch = ElaToggleSwitch(row)
        self._enable_switch.toggled.connect(self._on_enable_toggled)
        layout.addWidget(self._enable_switch)
        layout.addSpacing(12)

        layout.addWidget(ElaText("紧凑模式", row))
        self._compact_switch = ElaToggleSwitch(row)
        self._compact_switch.toggled.connect(self._on_compact_toggled)
        layout.addWidget(self._compact_switch)
        layout.addSpacing(12)

        layout.addWidget(ElaText("恢复剪贴板", row))
        self._restore_switch = ElaToggleSwitch(row)
        self._restore_switch.setIsToggled(True)
        self._restore_switch.toggled.connect(self._on_restore_toggled)
        layout.addWidget(self._restore_switch)
        layout.addSpacing(12)

        layout.addWidget(ElaText("最小长度", row))
        self._length_combo = ElaComboBox(row)
        for value in (1, 2, 3, 5):
            self._length_combo.addItem(f"{value} 个字符", value)
        self._length_combo.currentIndexChanged.connect(self._on_length_changed)
        layout.addWidget(self._length_combo)
        layout.addStretch(1)

        self._manual_button = ElaButton(
            "手动弹出动作条", variant="outlined", size="small", parent=row
        )
        self._manual_button.clicked.connect(self._on_manual_show)
        layout.addWidget(self._manual_button)
        main_layout.addWidget(row)

    def _on_enable_toggled(self, checked: bool) -> None:
        if self._updating_switch:
            return
        self._log_line(f"启用划词助手：{checked}")
        assistant = self._ensure_assistant()
        if checked and not assistant.setEnabled(True):
            self._updating_switch = True
            self._enable_switch.setIsToggled(False)
            self._updating_switch = False
            self._log_line("启用失败：请查看错误日志（非 Windows 或钩子安装失败）")
            return
        assistant.setEnabled(checked)

    def isAssistantEnabled(self) -> bool:
        """助手当前是否启用（**不会**顺带创建助手，供外部入口读状态用）。"""
        return bool(self._assistant is not None and self._assistant.isEnabled())

    def toggleAssistantFromTray(self) -> bool:
        """供托盘菜单等外部入口调用的开关入口（与页面内开关双向同步）。

        :returns: 切换后的**实际**启用状态（启用失败时为 ``False``，
            此时页面开关已自动回滚）
        """
        assistant = self._ensure_assistant()
        target = not assistant.isEnabled()
        # 复用开关那条路径，保证失败回滚与日志只写一处
        self._updating_switch = True
        try:
            self._enable_switch.setIsToggled(target)
        finally:
            self._updating_switch = False
        if self._enable_switch.getIsToggled() == target:
            self._on_enable_toggled(target)
        return self.isAssistantEnabled()

    def _on_compact_toggled(self, checked: bool) -> None:
        if self._assistant is not None:
            # 外观配置走 popup() 句柄，助手只负责手势编排
            self._assistant.popup().setCompactMode(checked)
        self._log_line(f"紧凑模式：{checked}")

    def _on_restore_toggled(self, checked: bool) -> None:
        if self._assistant is not None:
            # 取词参数走 capture() 句柄（注入自定义后端时同样有效）
            self._assistant.capture().setRestoreClipboard(checked)
        self._log_line(f"恢复剪贴板：{checked}")

    def _on_length_changed(self, _index: int) -> None:
        length = self._length_combo.currentData() or 1
        if self._assistant is not None:
            self._assistant.setMinSelectionLength(int(length))
        self._log_line(f"最小长度：{length}")

    def _on_manual_show(self) -> None:
        assistant = self._ensure_assistant()
        assistant.showFor("这是手动弹出的示例文本", QCursor.pos())
        self._log_line("手动弹出动作条（不经全局钩子）")

    # -- 分区 02：动作配置 ---------------------------------------------------

    def _demoActions(self, main_layout):
        """动作条菜单项由宿主定义（示例：6 个动作；组件本身不内置）。"""
        self._demo_actions = (
            ElaMenuItem(id="copy", label="复制", icon=ElaIconType.IconName.Copy),
            ElaMenuItem(
                id="translate", label="翻译", icon=ElaIconType.IconName.Language
            ),
            ElaMenuItem(
                id="explain", label="解释", icon=ElaIconType.IconName.CommentQuestion
            ),
            ElaMenuItem(
                id="summary", label="总结", icon=ElaIconType.IconName.FileLines
            ),
            ElaMenuItem(
                id="search", label="搜索", icon=ElaIconType.IconName.MagnifyingGlass
            ),
            ElaMenuItem(id="quote", label="引用", icon=ElaIconType.IconName.QuoteLeft),
        )

        info = ElaText(
            "菜单项完全由宿主定义（下面每组「名称 + id + 图标」就是一个菜单项），"
            "动作条只发 actionTriggered(actionId, text, pos) 信号，"
            "复制 / 搜索 / 翻译等行为全部由宿主实现（本页演示 copy）。",
            self,
        )
        info.setTextPixelSize(14)
        main_layout.addWidget(info)

        row = QWidget(self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        for action in self._demo_actions:
            box = ElaCheckBox(f"{action.label}（{action.id}）", row)
            box.setChecked(action.enabled)
            box.stateChanged.connect(self._on_action_toggled)
            self._action_boxes[action.id] = box
            layout.addWidget(box)
        layout.addStretch(1)
        main_layout.addWidget(row)

    def _on_action_toggled(self, _state: int) -> None:
        if self._assistant is not None:
            self._apply_actions()
        enabled = [key for key, box in self._action_boxes.items() if box.isChecked()]
        self._log_line(f"动作列表更新：{', '.join(enabled) or '（空）'}")

    def _apply_actions(self) -> None:
        actions = [
            ElaMenuItem(
                id=action.id,
                label=action.label,
                icon=action.icon,
                tooltip=action.tooltip,
                enabled=self._action_boxes[action.id].isChecked(),
            )
            for action in self._demo_actions
        ]
        self._assistant.setActions(actions)

    # -- 分区 03：事件日志 ---------------------------------------------------

    def _demoEvents(self, main_layout):
        info = ElaText(
            "selectionCaptured / actionTriggered / popupShown / popupHidden / "
            "errorOccurred 信号都会记录在下方；宿主实现示例：copy 动作写剪贴板。",
            self,
        )
        info.setTextPixelSize(14)
        main_layout.addWidget(info)

        self._log = ElaPlainTextEdit(self)
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(180)
        self._log.setPlaceholderText("事件日志…")
        main_layout.addWidget(self._log)

        clear_row = QWidget(self)
        clear_layout = QHBoxLayout(clear_row)
        clear_layout.setContentsMargins(0, 0, 0, 0)
        clear_layout.addStretch(1)
        clear_btn = ElaButton(
            "清空日志", variant="text", size="small", parent=clear_row
        )
        clear_btn.clicked.connect(lambda: self._log.clear())
        clear_layout.addWidget(clear_btn)
        main_layout.addWidget(clear_row)
        self._log_line("就绪：勾选「启用」后可在任意应用划词")

    # -- 助手与事件 ----------------------------------------------------------

    def _ensure_assistant(self) -> ElaSelectionAssistant:
        if self._assistant is None:
            assistant = ElaSelectionAssistant(self)
            assistant.selectionCaptured.connect(self._on_selection_captured)
            assistant.actionTriggered.connect(self._on_action_triggered)
            assistant.popupShown.connect(self._on_popup_shown)
            assistant.popupHidden.connect(lambda: self._log_line("popupHidden"))
            assistant.errorOccurred.connect(self._on_error)
            assistant.popup().setCompactMode(self._compact_switch.getIsToggled())
            assistant.capture().setRestoreClipboard(self._restore_switch.getIsToggled())
            assistant.setMinSelectionLength(int(self._length_combo.currentData() or 1))
            assistant.enabledChanged.connect(self._on_assistant_state_changed)
            self._assistant = assistant
            self._apply_actions()
        return self._assistant

    def _on_assistant_state_changed(self, enabled: bool) -> None:
        self.assistantStateChanged.emit(bool(enabled))

    def _on_selection_captured(self, text: str, pos) -> None:
        preview = text.strip().replace("\n", " ")[:40]
        self._log_line(f"selectionCaptured：{preview!r} @ ({pos.x()}, {pos.y()})")

    def _on_popup_shown(self, text: str, pos) -> None:
        self._log_line(f"popupShown：{len(text)} 字 @ ({pos.x()}, {pos.y()})")

    def _on_error(self, message: str) -> None:
        self._log_line(f"errorOccurred：{message}")

    def _on_action_triggered(self, actionId: str, text: str, pos) -> None:
        self._log_line(f"actionTriggered：{actionId} ← {text.strip()[:30]!r}")
        if actionId == "copy":
            QApplication.clipboard().setText(text)
            self._log_line("  宿主实现：已写入剪贴板")

    def _log_line(self, message: str) -> None:
        if self._log is None:
            return
        stamp = datetime.now().strftime("%H:%M:%S")
        self._log.appendPlainText(f"[{stamp}] {message}")
        document = self._log.document()
        if document.blockCount() > _MAX_LOG_LINES:
            cursor = self._log.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.movePosition(
                QTextCursor.MoveOperation.Down,
                QTextCursor.MoveMode.KeepAnchor,
                document.blockCount() - _MAX_LOG_LINES,
            )
            cursor.removeSelectedText()
        self._log.verticalScrollBar().setValue(self._log.verticalScrollBar().maximum())

    # -- 生命周期 ------------------------------------------------------------

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt 命名)
        if self._assistant is not None:
            self._assistant.setEnabled(False)
        super().closeEvent(event)
