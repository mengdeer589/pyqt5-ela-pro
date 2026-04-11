"""
窗口淡入淡出动画模块。

提供两种使用方式：
1. 模块级函数：fade_in() / fade_out()，一行调用
2. AnimatedMixin：继承获得 fade_in() / fade_out() 实例方法
"""

from __future__ import annotations

import weakref
from typing import Optional, Callable

from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtWidgets import QWidget

from ._internal import catch_error, safe_call


_animation_registry: dict[int, QPropertyAnimation] = {}


def fade_in(widget: QWidget, duration: int = 1000) -> None:
    """让窗口淡入（opacity: 0 → 1）。

    如果窗口尚未显示，会先设置 opacity=0，再 show，再启动动画。
    动画进行中再次调用会忽略新请求。

    :param widget: 目标窗口控件
    :param duration: 动画时长（毫秒），默认 1000ms
    """
    if not widget.isVisible():
        widget.setWindowOpacity(0)
        widget.show()

    key = id(widget)
    if key in _animation_registry:
        existing = _animation_registry[key]
        if existing and existing.state() == QPropertyAnimation.State.Running:
            return

    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(duration)
    animation.setStartValue(0)
    animation.setEndValue(1)

    @catch_error
    def _cleanup():
        if key in _animation_registry and _animation_registry[key] is animation:
            _animation_registry.pop(key, None)

    animation.finished.connect(_cleanup)
    _animation_registry[key] = animation
    animation.start()


def fade_out(
    widget: QWidget,
    duration: int = 1000,
    on_finished: Optional[Callable[[], None]] = None,
) -> None:
    """让窗口淡出（opacity: 1 → 0）。

    仅将透明度渐变到0，不会自动关闭窗口。动画结束后调用 on_finished 回调。
    动画进行中再次调用会忽略新请求。

    :param widget: 目标窗口控件
    :param duration: 动画时长（毫秒），默认 1000ms
    """
    key = id(widget)
    if key in _animation_registry:
        existing = _animation_registry[key]
        if existing and existing.state() == QPropertyAnimation.State.Running:
            return

    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(duration)
    animation.setStartValue(1)
    animation.setEndValue(0)

    @catch_error
    def _on_finished():
        if key in _animation_registry and _animation_registry[key] is animation:
            _animation_registry.pop(key, None)
        if on_finished is not None:
            safe_call(on_finished)

    animation.finished.connect(_on_finished)
    _animation_registry[key] = animation
    animation.start()


class ElaAnimatedMixin:
    """给窗口/对话框添加淡入淡出动画能力的混入类。

    继承此 Mixin 后，实例自动获得 fade_in() / fade_out() 方法。
    动画实例被自身持有，每次调用会复用同一个实例（停止旧动画再启动新动画）。

    Example::

        class MyDialog(AnimatedMixin, QDialog):
            def show_with_animation(self):
                self.fade_in()

            def close_with_animation(self):
                self.fade_out(on_finished=self.close)
    """

    _fade_animation: Optional[QPropertyAnimation] = None

    def fade_in(self, duration: int = 1000) -> None:
        """让窗口淡入（opacity: 0 → 1）。

        如果窗口尚未显示，会先设置 opacity=0，再 show，再启动动画。
        动画进行中再次调用会忽略新请求。

        :param duration: 动画时长（毫秒），默认 1000ms
        """
        if not self.isVisible():
            self.setWindowOpacity(0)
            self.show()

        if (
            self._fade_animation
            and self._fade_animation.state() == QPropertyAnimation.State.Running
        ):
            return

        self._fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self._fade_animation.setDuration(duration)
        self._fade_animation.setStartValue(0)
        self._fade_animation.setEndValue(1)
        self._fade_animation.start()

    def fade_out(
        self,
        duration: int = 1000,
        on_finished: Optional[Callable[[], None]] = None,
    ) -> None:
        """让窗口淡出（opacity: 1 → 0）。

        仅将透明度渐变到0，不会自动关闭窗口。动画结束后调用 on_finished 回调。
        动画进行中再次调用会忽略新请求。

        :param duration: 动画时长（毫秒），默认 1000ms
        :param on_finished: 动画完成后的回调函数
        """
        if (
            self._fade_animation
            and self._fade_animation.state() == QPropertyAnimation.State.Running
        ):
            return

        self._fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self._fade_animation.setDuration(duration)
        self._fade_animation.setStartValue(1)
        self._fade_animation.setEndValue(0)

        @catch_error
        def _on_finished():
            if on_finished is not None:
                safe_call(on_finished)

        self._fade_animation.finished.connect(_on_finished)
        self._fade_animation.start()
