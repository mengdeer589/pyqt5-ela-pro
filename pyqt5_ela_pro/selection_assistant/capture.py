"""剪贴板取词（``pyqt5_ela_pro.selection_assistant``）。

通过模拟 ``Ctrl+C`` + 剪贴板文本变化读取当前选区文本，全程异步（QTimer），
不阻塞 UI：

1. 延迟 ``captureDelayMs``（先让事件循环处理完挂起的剪贴板更新，同时等源
   应用处理完 mouse-up）；
2. 记录基准文本（**不写剪贴板**，避免污染 / 丢失用户剪贴板——Qt/Windows
   下写入空探针会导致后续写入丢失）；
3. 发送 Ctrl+C，以 ``pollMs`` 轮询：文本非空且不同于基准 → 取词成功；
4. 超时（``clipboardTimeoutMs``）视为没有选区，剪贴板从未被改动；
5. 成功后按 ``restoreClipboard``（默认开启）延迟 ``restoreDelayMs`` 恢复
   基准文本（基准为空时 ``clear()``）。

信号：``captured(text)`` / ``failed()``。恢复只还原文本，非文本格式
（图片等）不保留。若选中文本与用户原剪贴板内容完全相同，无法与「未复制」
区分，将视为无选区（已知限制）。

命名规范与库内一致（``camelCase``）。
"""

from __future__ import annotations

import time
from typing import Optional

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication

from ._native import send_copy

#: 默认发送 Ctrl+C 前的等待（毫秒，等源应用处理完 mouse-up）
_DEFAULT_CAPTURE_DELAY_MS = 80
#: 默认剪贴板轮询间隔（毫秒）
_DEFAULT_POLL_MS = 10
#: 默认取词超时（毫秒）
_DEFAULT_TIMEOUT_MS = 250
#: 默认取词成功后恢复剪贴板的延迟（毫秒）
_DEFAULT_RESTORE_DELAY_MS = 120


class ElaClipboardCapture(QObject):
    """模拟 Ctrl+C 的异步取词器（不阻塞 UI，不预先改动剪贴板）。

    :param parent: 父对象
    """

    #: 取词成功（参数：选中文本）
    captured = pyqtSignal(str)
    #: 取词失败 / 无选区
    failed = pyqtSignal()
    #: 剪贴板**未被还原** —— 因为用户在延时窗口里复制了新的内容（宿主可据此提示）
    restoreSkipped = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._restore = True
        self._capture_delay_ms = _DEFAULT_CAPTURE_DELAY_MS
        self._poll_ms = _DEFAULT_POLL_MS
        self._timeout_ms = _DEFAULT_TIMEOUT_MS
        self._restore_delay_ms = _DEFAULT_RESTORE_DELAY_MS

        self._active = False
        self._need_restore = False
        self._old_text = ""
        # 取词链路放进剪贴板的那份内容；恢复时用它判断「有没有被用户改过」
        self._captured_text = ""
        self._deadline = 0.0

        self._delay_timer = QTimer(self)
        self._delay_timer.setSingleShot(True)
        self._delay_timer.timeout.connect(self._on_send_copy)

        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(self._poll_ms)
        self._poll_timer.timeout.connect(self._poll)

        self._restore_timer = QTimer(self)
        self._restore_timer.setSingleShot(True)
        self._restore_timer.timeout.connect(self._restore_clipboard)

    # -- 配置 --------------------------------------------------------------

    def setRestoreClipboard(self, on: bool) -> None:
        """设置取词成功后是否恢复原剪贴板（默认开启）。"""
        self._restore = bool(on)

    def restoreClipboard(self) -> bool:
        """取词成功后是否恢复原剪贴板。"""
        return self._restore

    def setCaptureDelayMs(self, ms: int) -> None:
        """设置发送 Ctrl+C 前的等待毫秒数。"""
        self._capture_delay_ms = max(0, int(ms))

    def captureDelayMs(self) -> int:
        """发送 Ctrl+C 前的等待毫秒数。"""
        return self._capture_delay_ms

    def setPollMs(self, ms: int) -> None:
        """设置剪贴板轮询间隔毫秒数。"""
        self._poll_ms = max(1, int(ms))
        self._poll_timer.setInterval(self._poll_ms)

    def pollMs(self) -> int:
        """剪贴板轮询间隔毫秒数。"""
        return self._poll_ms

    def setTimeoutMs(self, ms: int) -> None:
        """设置取词超时毫秒数。"""
        self._timeout_ms = max(1, int(ms))

    def timeoutMs(self) -> int:
        """取词超时毫秒数。"""
        return self._timeout_ms

    def setRestoreDelayMs(self, ms: int) -> None:
        """设置成功取词后恢复剪贴板的延迟毫秒数。"""
        self._restore_delay_ms = max(0, int(ms))

    def restoreDelayMs(self) -> int:
        """成功取词后恢复剪贴板的延迟毫秒数。"""
        return self._restore_delay_ms

    # -- 流程 --------------------------------------------------------------

    def isCapturing(self) -> bool:
        """是否正在取词。"""
        return self._active

    def capture(self) -> None:
        """开始一次异步取词（进行中重复调用会先取消上一次）。"""
        # 上一次取词可能已经排了「恢复原剪贴板」的延时定时器。若不先结算就
        # 重置 _old_text=""，那次定时器触发时 _restore_clipboard() 会走
        # clipboard.clear() 分支，把用户原有的剪贴板内容清掉且无法恢复。
        if self._need_restore:
            self._restore_timer.stop()
            self._restore_clipboard()
        if self._active:
            self.cancel()
        self._active = True
        self._old_text = ""
        self._captured_text = ""
        self._deadline = time.monotonic() + self._timeout_ms / 1000.0
        self._delay_timer.start(self._capture_delay_ms)

    def cancel(self) -> None:
        """取消进行中的取词（剪贴板从未被改动，无需恢复）。"""
        if not self._active:
            return
        self._active = False
        self._delay_timer.stop()
        self._poll_timer.stop()
        self._restore_timer.stop()

    # -- 内部 --------------------------------------------------------------

    def _on_send_copy(self) -> None:
        if not self._active:
            return
        self._old_text = QApplication.clipboard().text()
        try:
            send_copy()
        except Exception:
            self._finish("", ok=False)
            return
        self._poll_timer.start()
        self._poll()

    def _poll(self) -> None:
        if not self._active:
            return
        text = QApplication.clipboard().text()
        if text and text != self._old_text:
            self._finish(text, ok=True)
        elif time.monotonic() >= self._deadline:
            self._finish("", ok=False)

    def _finish(self, text: str, ok: bool) -> None:
        self._active = False
        self._delay_timer.stop()
        self._poll_timer.stop()
        if ok and self._restore:
            self._need_restore = True
            # 记下「我们自己放进剪贴板的那份」，供恢复时判断有没有被用户改过
            self._captured_text = text
            self._restore_timer.start(self._restore_delay_ms)
        if ok:
            self.captured.emit(text)
        else:
            self.failed.emit()

    def _restore_clipboard(self) -> None:
        """把剪贴板还原成取词**之前**的内容。

        **只在剪贴板还是「我们自己放进去的那份」时才还原**。延时窗口
        （``restoreDelayMs``，默认几百毫秒）里用户完全可能又复制了别的东西 ——
        比如切到资源管理器按了 Ctrl+C。原先无条件写回 ``_old_text``，于是那次
        复制**被静默丢弃**，用户按 Ctrl+V 拿到的是几百毫秒前的旧内容。
        这种数据丢失比「剪贴板没还原」更糟，所以宁可留着用户新复制的那份。

        判据用**纯文本比较**而不是序列号（Windows 剪贴板序列号要 ``user32``
        ``GetClipboardSequenceNumber``，而本模块的平台/环境分支里刻意不引
        win32 —— 见 AGENTS.md「Import 约定」）：取词链路本来就只看纯文本，
        用户新复制的内容若与取词结果**文本相同**，是否还原在语义上无差别。
        """
        if not self._need_restore:
            return
        self._need_restore = False
        clipboard = QApplication.clipboard()
        if clipboard.text() != self._captured_text:
            # 用户已经复制了新的东西 —— 不要覆盖
            self.restoreSkipped.emit()
            return
        if self._old_text:
            clipboard.setText(self._old_text)
        else:
            clipboard.clear()


__all__ = ["ElaClipboardCapture"]
