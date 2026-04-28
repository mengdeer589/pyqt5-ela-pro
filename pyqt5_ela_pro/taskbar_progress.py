"""
Windows 任务栏进度条组件。

基于 QWinTaskbarButton / QWinTaskbarProgress 封装，
在 Windows 任务栏图标上展示进度条（暂停/恢复/停止/不确定状态等）。
仅 Windows 平台有效，非 Windows 环境下所有方法为空操作。
"""

from __future__ import annotations

import sys

from typing import Optional

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWinExtras import QWinTaskbarButton, QWinTaskbarProgress


class ElaTaskbarProgress(QObject):
    """Windows 任务栏进度条组件。

    在 Windows 任务栏图标上展示进度条，支持暂停/恢复/停止/不确定状态。

    使用方式::

        from pyqt5_ela_pro import TaskbarProgress

        tb = TaskbarProgress(my_window)
        tb.setRange(0, 100)
        tb.setValue(0)
        tb.show()
        for i in range(100):
            tb.setValue(i)
            # ...
        tb.hide()

    :param window: 要关联进度的窗口控件
    :type window: QWidget
    """

    valueChanged = pyqtSignal(int)
    pausedChanged = pyqtSignal(bool)
    stoppedChanged = pyqtSignal(bool)
    visibilityChanged = pyqtSignal(bool)

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self._window = window
        self._button: Optional[QWinTaskbarButton] = None
        self._progress: Optional[QWinTaskbarProgress] = None
        self._attached = False

    def _connect_signals(self) -> None:
        if self._progress is not None:
            self._progress.valueChanged.connect(self.valueChanged)
            self._progress.pausedChanged.connect(self.pausedChanged)
            self._progress.stoppedChanged.connect(self.stoppedChanged)
            self._progress.visibilityChanged.connect(self.visibilityChanged)

    def _ensure_attached(self) -> None:
        if self._attached or self._window is None:
            return

        if not self._is_win_extras_available():
            return

        self._button = QWinTaskbarButton(self._window)
        self._progress = self._button.progress()
        self._connect_signals()

        wh = self._window.windowHandle()
        if wh is not None:
            self._button.setWindow(wh)
            self._attached = True
        else:
            self._window.windowHandleChanged.connect(self._on_window_handle_created)

    def _on_window_handle_created(self) -> None:
        wh = self._window.windowHandle()
        if wh is not None:
            try:
                self._window.windowHandleChanged.disconnect(self._on_window_handle_created)
            except (TypeError, RuntimeError):
                pass
            self._button.setWindow(wh)
            self._attached = True

    def _is_win_extras_available(self) -> bool:
        return QWinTaskbarButton is not None and callable(QWinTaskbarButton)

    @property
    def value(self) -> int:
        if self._progress is None:
            return 0
        return self._progress.value()

    @property
    def minimum(self) -> int:
        if self._progress is None:
            return 0
        return self._progress.minimum()

    @property
    def maximum(self) -> int:
        if self._progress is None:
            return 0
        return self._progress.maximum()

    @property
    def isPaused(self) -> bool:
        if self._progress is None:
            return False
        return self._progress.isPaused()

    @property
    def isVisible(self) -> bool:
        if self._progress is None:
            return False
        return self._progress.isVisible()

    @property
    def isStopped(self) -> bool:
        if self._progress is None:
            return False
        return self._progress.isStopped()

    def setRange(self, min_val: int, max_val: int) -> None:
        """设置进度条范围。

        :param min_val: 最小值
        :param max_val: 最大值
        """
        self._ensure_attached()
        if self._progress is not None:
            self._progress.setRange(min_val, max_val)

    def setValue(self, value: int) -> None:
        """设置进度条当前值。

        :param value: 当前值
        """
        self._ensure_attached()
        if self._progress is not None:
            self._progress.setValue(value)

    def show(self) -> None:
        """显示任务栏进度条。"""
        self._ensure_attached()
        if self._progress is not None:
            self._progress.show()

    def hide(self) -> None:
        """隐藏任务栏进度条。"""
        if self._progress is not None:
            self._progress.hide()

    def pause(self) -> None:
        """暂停进度条。"""
        self._ensure_attached()
        if self._progress is not None:
            self._progress.pause()

    def resume(self) -> None:
        """恢复暂停的进度条。"""
        self._ensure_attached()
        if self._progress is not None:
            self._progress.resume()

    def stop(self) -> None:
        """停止进度条。"""
        self._ensure_attached()
        if self._progress is not None:
            self._progress.stop()

    def reset(self) -> None:
        """重置进度条。"""
        if self._progress is not None:
            self._progress.reset()
