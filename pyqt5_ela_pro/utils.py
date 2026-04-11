"""
窗口动画和工具函数模块。

提供 shake_window 函数用于窗口抖动动画。
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from PyQt5.QtCore import QPropertyAnimation, QPoint
from PyQt5.QtWidgets import QWidget

from ._internal import catch_error, safe_call


def shake_window(
    widget: QWidget,
    duration: int = 200,
    loop_count: int = 2,
    on_finished: Optional[Callable[[], None]] = None,
) -> None:
    """让窗口抖动动画（左右+上下晃动画回到原位）。

    动画进行中再次调用会忽略新请求。

    :param widget: 目标窗口控件
    :param duration: 动画总时长（毫秒），默认 200ms
    :param loop_count: 抖动循环次数，默认 2
    :param on_finished: 动画完成后的回调函数
    """
    if hasattr(widget, "_shake_animation"):
        existing = widget._shake_animation
        if existing and existing.state() == QPropertyAnimation.State.Running:
            return

    animation = QPropertyAnimation(widget, b"pos", widget)
    widget._shake_animation = animation

    pos = widget.pos()
    x, y = pos.x(), pos.y()

    animation.setDuration(duration)
    animation.setLoopCount(loop_count)
    animation.setKeyValueAt(0, QPoint(x, y))
    animation.setKeyValueAt(0.09, QPoint(x + 2, y - 2))
    animation.setKeyValueAt(0.18, QPoint(x + 4, y - 4))
    animation.setKeyValueAt(0.27, QPoint(x + 2, y - 6))
    animation.setKeyValueAt(0.36, QPoint(x, y - 8))
    animation.setKeyValueAt(0.45, QPoint(x - 2, y - 10))
    animation.setKeyValueAt(0.54, QPoint(x - 4, y - 8))
    animation.setKeyValueAt(0.63, QPoint(x - 6, y - 6))
    animation.setKeyValueAt(0.72, QPoint(x - 8, y - 4))
    animation.setKeyValueAt(0.81, QPoint(x - 6, y - 2))
    animation.setKeyValueAt(0.90, QPoint(x - 4, y))
    animation.setKeyValueAt(0.99, QPoint(x - 2, y + 2))
    animation.setEndValue(QPoint(x, y))

    @catch_error
    def _cleanup():
        if hasattr(widget, "_shake_animation"):
            try:
                delattr(widget, "_shake_animation")
            except AttributeError:
                pass
        if on_finished is not None:
            safe_call(on_finished)

    animation.finished.connect(_cleanup)
    animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)  # type: ignore[attr-defined]
