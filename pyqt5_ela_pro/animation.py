"""
窗口淡入淡出动画模块。

提供两种使用方式：
1. 模块级函数：fade_in() / fade_out()，一行调用
2. AnimatedMixin：继承获得 fade_in() / fade_out() 实例方法
"""

from __future__ import annotations

import weakref
from typing import Callable, Optional

from PyQt5.QtCore import QPropertyAnimation, QPoint
from PyQt5.QtWidgets import QWidget
from PyQt5 import sip

from ._internal import catch_error, safe_call


_animation_registry: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()


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

    if widget in _animation_registry:
        existing = _animation_registry[widget]
        if existing and existing.state() == QPropertyAnimation.State.Running:
            return

    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(duration)
    animation.setStartValue(0)
    animation.setEndValue(1)

    @catch_error
    def _cleanup():
        if widget in _animation_registry and _animation_registry[widget] is animation:
            del _animation_registry[widget]

    animation.finished.connect(_cleanup)
    # 故意**不**连 widget.destroyed：
    #   1) destroyed 在 C++ 对象析构之后才发出，此时 lambda 里任何
    #      ``widget in _animation_registry`` / ``_animation_registry[widget]``
    #      都要对已失效的 PyQt 包装器取哈希 —— 全量测试下实测 6/6 必崩
    #      （0xC0000005 访问冲突，栈就落在本模块的 lambda）。
    #   2) lambda 捕获 widget 会形成 widget -> destroyed 信号 -> lambda -> widget
    #      的引用环，包装器永远不被回收。
    # 条目清理由 WeakKeyDictionary 自身负责（包装器回收时自动移除），
    # 目标控件析构时 Qt 也会自动停止作用于它的 QPropertyAnimation。
    _animation_registry[widget] = animation
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
    if widget in _animation_registry:
        existing = _animation_registry[widget]
        if existing and existing.state() == QPropertyAnimation.State.Running:
            return

    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(duration)
    animation.setStartValue(1)
    animation.setEndValue(0)

    @catch_error
    def _on_finished():
        if widget in _animation_registry and _animation_registry[widget] is animation:
            del _animation_registry[widget]
        if on_finished is not None:
            safe_call(on_finished)

    animation.finished.connect(_on_finished)
    # 同 fade_in： destroyed 在 C++ 析构后才发出，此时对已失效的控件包装器做
    # 字典键运算会触发 0xC0000005 访问冲突；且 lambda 捕获 widget 会造成引用环。
    # 目标析构时 Qt 会自动停止 QPropertyAnimation，无需在此清理。
    _animation_registry[widget] = animation
    animation.start()


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
        # 上一次抖动用的动画带 DeleteWhenStopped，C++ 可能已被删除；
        # 对已删除对象取 state() 会抛 RuntimeError（进而 0xC0000409）。
        try:
            if existing is not None and not sip.isdeleted(existing):
                if existing.state() == QPropertyAnimation.State.Running:
                    return
        except RuntimeError:
            pass

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
    animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fade_animation = None

    def fade_in(self, duration: int = 1000) -> None:
        """让窗口淡入（opacity: 0 → 1）。

        如果窗口尚未显示，会先设置 opacity=0，再 show，再启动动画。
        动画进行中再次调用会忽略新请求。

        :param duration: 动画时长（毫秒），默认 1000ms
        """
        if not self.isVisible():  # type: ignore[attr-defined]
            self.setWindowOpacity(0)  # type: ignore[attr-defined]
            self.show()  # type: ignore[attr-defined]

        if (
            self._fade_animation
            and self._fade_animation.state() == QPropertyAnimation.State.Running
        ):
            return

        self._fade_animation = QPropertyAnimation(self, b"windowOpacity")  # type: ignore[arg-type]
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

        self._fade_animation = QPropertyAnimation(self, b"windowOpacity")  # type: ignore[arg-type]
        self._fade_animation.setDuration(duration)
        self._fade_animation.setStartValue(1)
        self._fade_animation.setEndValue(0)

        @catch_error
        def _on_finished():
            if on_finished is not None:
                safe_call(on_finished)

        self._fade_animation.finished.connect(_on_finished)
        self._fade_animation.start()
