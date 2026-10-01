"""Tests for taskbar_progress module: ElaTaskbarProgress."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

# 所有公开方法都写着 `if self._progress is not None`，所以「没有 QtWinExtras」
# 时它们必须是**可断言的空操作**：不能挂上 button、不能置 _attached。
# 原来这批用例只有「调用没抛」没有断言，等于什么都没验。
NOOP_METHODS = [
    "setRange",
    "setValue",
    "show",
    "pause",
    "resume",
    "stop",
    "reset",
    "hide",
]


@pytest.fixture
def no_win_extras():
    """模拟「没装 pywin32 扩展」的环境。

    注意 patch 打的是已导入模块的属性，所以模块级的 ``ElaTaskbarProgress``
    引用照样有效 —— 原先在 ``with`` 块里重复 import 一次纯属噪音。
    """
    with patch("pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton", None):
        yield


@pytest.fixture
def window(make):
    return make(QWidget)


@pytest.fixture
def tb(make, window, no_win_extras):
    return make(ElaTaskbarProgress, window)


def test_module_imports():
    assert ElaTaskbarProgress is not None


@pytest.mark.parametrize(
    "signal_name",
    ["valueChanged", "pausedChanged", "stoppedChanged", "visibilityChanged"],
)
def test_declares_signal(signal_name):
    assert isinstance(getattr(ElaTaskbarProgress, signal_name), pyqtSignal)


def test_has_on_window_handle_created_method():
    assert hasattr(ElaTaskbarProgress, "_on_window_handle_created")


def test_initialization_stores_window(tb, window):
    assert tb._window is window


@pytest.mark.parametrize(
    ("attr", "expected"),
    [
        ("_button", None),
        ("_progress", None),
        ("_attached", False),
        ("_attach_timer", None),
    ],
)
def test_initial_state_before_attachment(tb, attr, expected):
    assert getattr(tb, attr) == expected


@pytest.mark.parametrize(
    ("prop", "expected"),
    [
        ("value", 0),
        ("minimum", 0),
        ("maximum", 0),
        ("isPaused", False),
        ("isVisible", False),
        ("isStopped", False),
    ],
)
def test_property_falls_back_when_no_progress(tb, prop, expected):
    assert getattr(tb, prop) == expected


@pytest.mark.parametrize("method", NOOP_METHODS)
def test_public_methods_are_noop_without_win_extras(tb, method):
    """无 QtWinExtras 时调用公开方法不得产生任何副作用。"""
    if method == "setRange":
        tb.setRange(0, 100)
    elif method == "setValue":
        tb.setValue(50)
    else:
        getattr(tb, method)()

    assert tb._button is None
    assert tb._progress is None
    assert tb._attached is False
    assert tb._attach_timer is None


def test_ensure_attached_noop_when_window_is_none(make, no_win_extras):
    tb = make(ElaTaskbarProgress, None)
    tb._ensure_attached()
    assert tb._attached is False


def test_on_window_handle_created_noop_without_window_handle(tb):
    tb._button = MagicMock()
    tb._attached = False

    tb._on_window_handle_created()

    assert tb._attached is False  # no handle, no attachment


def test_ensure_attached_without_handle_starts_polling(make, window):
    """回归：QWidget 在 Qt5 没有 windowHandleChanged 信号。

    窗口 show() 之前调 setter 不能抛 AttributeError，改用轮询重试挂接。
    """
    with patch("pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton", MagicMock()):
        tb = make(ElaTaskbarProgress, window)
        tb.setValue(5)  # 旧实现在这里抛 AttributeError

        assert tb._attached is False
        assert tb._attach_timer is not None
        assert tb._attach_timer.isActive() is True

        tb.deleteLater()


def test_on_window_handle_created_attaches_and_stops_polling(make, window):
    with patch("pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton", MagicMock()):
        tb = make(ElaTaskbarProgress, window)
        tb.setValue(5)
        fake_handle = MagicMock()
        window.windowHandle = lambda: fake_handle

        tb._on_window_handle_created()

        assert tb._attached is True
        tb._button.setWindow.assert_called_once_with(fake_handle)
        assert tb._attach_timer.isActive() is False

        tb.deleteLater()
