"""测试公用工具：事件循环等待、控件回收。

统一原因（历史重复）：

* ``_wait_until`` 曾在 11 个测试文件里各抄一份，只有超时与轮询间隔不同；
  ``test_md_export_media.py`` 还另有一个签名不同的 ``_wait``。
* ``X.deleteLater()`` 后必须跟一次 ``qapp.processEvents()`` 才真正销毁
  （本仓库约定，见 AGENTS.md）。这条纪律以前靠人工，现在由
  ``conftest.py`` 的 ``qt_teardown`` autouse fixture 在每个用例后统一兜底。
"""

from __future__ import annotations

import time
from typing import Callable, List, TypeVar

from PyQt5 import sip
from PyQt5.QtCore import QObject
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

T = TypeVar("T", bound=QObject)


def wait_until(
    qapp: QApplication | None,
    predicate: Callable[[], bool],
    timeout_ms: int = 3000,
    interval_ms: int = 10,
    use_qwait: bool = False,
) -> bool:
    """跑事件循环直到 ``predicate()`` 为真或超时。

    Args:
        qapp: ``QApplication`` 实例；``None`` 时回落到 ``QApplication.instance()``。
        predicate: 无参可调用对象，返回真值即视为满足。
        timeout_ms: 超时毫秒数。
        interval_ms: 两轮之间的间隔。
        use_qwait: 用 ``QTest.qWait`` 代替 ``time.sleep`` 等待。
            两者都会转事件循环，但 ``qWait`` 是 Qt 自己的等待器，
            在 mermaid 那类靠内部定时器推进的测试里更稳。

    Returns:
        谓词最终是否成立（超时返回最后一次求值结果）。
    """
    if qapp is None:
        qapp = QApplication.instance()
    deadline = time.monotonic() + timeout_ms / 1000.0
    while time.monotonic() < deadline:
        qapp.processEvents()
        if predicate():
            return True
        if use_qwait:
            QTest.qWait(interval_ms)
        else:
            time.sleep(interval_ms / 1000.0)
    return predicate()


def flush_events(qapp: QApplication | None = None, rounds: int = 2) -> None:
    """冲刷 ``deleteLater`` 队列（连跑 ``rounds`` 轮，兼容级联 deleteLater）。"""
    if qapp is None:
        qapp = QApplication.instance()
    for _ in range(rounds):
        qapp.processEvents()


class WidgetFactory:
    """登记式控件工厂：造出来的控件统一在 fixture teardown 里销毁。

    用途是把 ``w = X(); ...; w.deleteLater()`` 收敛成 ``w = make(X)``，
    销毁时机交给 ``conftest.qt_teardown``，测试体内不再出现样板。

    >>> def test_x(make):
    ...     btn = make(ElaButton, "ok")
    ...     assert btn.text() == "ok"
    """

    def __init__(self, qapp: QApplication) -> None:
        self._qapp = qapp
        self._created: List[QObject] = []

    def __call__(self, cls: type[T], *args, **kwargs) -> T:
        # **空 kwargs 不能传给 sip 类**：``PyQt5ElaWidgetTools`` 的生成绑定在
        # 「位置参数没填满 + 带 kwargs」时会 access violation（实测 0.11.1 /
        # 0.12.1 都有，``ElaText("x", **{})`` / ``ElaPushButton("x", **{})``
        # 一跑就崩，``ElaText("x", None, **{})`` 反而正常）。空 kwargs 时走
        # 纯位置参数路径即可绕开；非空 kwargs 仍是坏的（上游绑定问题，真正
        # 修复要改 PyElaWidgetTools 的 sip 生成再重编译）。
        if kwargs:
            widget = cls(*args, **kwargs)
        else:
            widget = cls(*args)
        self._created.append(widget)
        return widget

    def track(self, widget: T) -> T:
        """把外部已建好的控件纳入统一回收（用于库内部创建的返回值）。"""
        self._created.append(widget)
        return widget

    @property
    def created(self) -> List[QObject]:
        return list(self._created)

    def destroy_all(self) -> None:
        """逆序 ``deleteLater()`` 再冲刷事件循环，保证真正析构。

        必须逐个用 ``sip.isdeleted()`` 判存活：控件常被库内部重新挂到别的
        parent 下（``create_ela_splitter`` 就把子控件 reparent 给 splitter），
        父控件析构会连带销毁子控件，此时再调 ``deleteLater()`` 抛
        ``RuntimeError: wrapped C/C++ object has been deleted``。
        """
        for widget in reversed(self._created):
            if widget is None:
                continue
            try:
                if sip.isdeleted(widget):
                    continue
                widget.deleteLater()
            except RuntimeError:  # 已销毁 / 无 deleteLater 的裸 QObject
                continue
        self._created.clear()
        flush_events(self._qapp)
