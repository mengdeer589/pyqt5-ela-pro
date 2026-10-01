"""回归测试：``animation.py`` 的 ``widget.destroyed`` lambda 导致进程崩溃。

``destroyed`` 在 C++ 对象析构**之后**才发出，此时 lambda 里的
``widget in _animation_registry`` / ``_animation_registry[widget]`` 会对
**已失效的 PyQt 包装器取哈希**。全量测试下实测 6/6 必崩
（``0xC0000005`` 访问冲突，栈落在 ``animation.py`` 的 lambda 里，由一个与动画
毫不相干的 markdown 测试的 ``QTest.qWait`` 触发）。

另外 lambda 捕获 ``widget`` 会形成 ``widget -> destroyed 信号 -> lambda ->
widget`` 的引用环，让包装器永远不被回收。
"""

from __future__ import annotations

import inspect
from weakref import WeakKeyDictionary

from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro import animation as A


class TestNoDestroyedLambdaOnRegistry:
    """不得在 widget.destroyed 上做注册表键运算。"""

    def test_fade_in_has_no_destroyed_connection(self):

        src = inspect.getsource(A.fade_in)
        assert "widget.destroyed.connect" not in src, (
            "fade_in 不能连 widget.destroyed：析构后再拿失效包装器做字典键会崩"
        )

    def test_fade_out_has_no_destroyed_connection(self):

        src = inspect.getsource(A.fade_out)
        assert "widget.destroyed.connect" not in src

    def test_no_destroyed_lambda_registered_at_runtime(self, qapp):
        """运行期检查：destroyed 信号上不应再挂 Python 回调。"""

        w = QWidget()
        w.resize(120, 80)
        w.show()
        qapp.processEvents()
        A.fade_in(w, duration=5000)
        assert w in A._animation_registry
        # destroyed 上只允许有 C++ 内部连接，不应有额外的 Python 可调用
        receivers = w.receivers(w.destroyed)
        assert receivers <= 1, (
            f"destroyed 上有 {receivers} 个连接，析构期回调是崩溃来源"
        )
        w.close()
        w.deleteLater()
        qapp.processEvents()

    def test_registry_is_still_weak(self):

        assert isinstance(A._animation_registry, WeakKeyDictionary)


class TestShakeSurvivesDeletedAnimation:
    """``shake_window`` 复用一个带 DeleteWhenStopped 的动画，必须防已删除。"""

    def test_source_guards_deleted_animation(self):

        src = inspect.getsource(A.shake_window)
        assert "sip.isdeleted" in src, (
            "shake_window 必须用 sip.isdeleted 守卫上一次的动画对象"
        )

    def test_shake_many_times_while_alive(self, qapp):
        """连续抖动：每次都要先安全处理上一次的动画对象。"""

        w = QWidget()
        w.resize(120, 80)
        w.show()
        qapp.processEvents()
        for _ in range(6):
            A.shake_window(w, duration=8, loop_count=1)
            qapp.processEvents()
        w.close()
        w.deleteLater()
        qapp.processEvents()


class TestRegistryLifecycle:
    def test_entry_added_and_removed(self, qapp):

        w = QWidget()
        w.resize(120, 80)
        w.show()
        qapp.processEvents()
        A.fade_in(w, duration=20)
        assert w in A._animation_registry
        # 需要真实推进 Qt 时钟，processEvents 不会让动画走完
        QTest.qWait(200)
        qapp.processEvents()
        assert w not in A._animation_registry
        w.close()
        w.deleteLater()
        qapp.processEvents()

    def test_destroy_while_animating_is_silent(self, qapp):
        """动画进行中销毁控件：不能崩，也不能抛到事件循环里。"""

        for _ in range(6):
            w = QWidget()
            w.resize(120, 80)
            w.show()
            qapp.processEvents()
            A.fade_out(w, duration=5000)
            assert w in A._animation_registry
            w.deleteLater()
            for _ in range(6):
                qapp.processEvents()
