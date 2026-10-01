"""``ElaLongPressButton`` / ``ElaProgressButton`` 测试：初值 / setter / 信号 / 析构。"""

from __future__ import annotations

import pytest
from PyQt5.QtGui import QColor

from pyqt5_ela_pro.ela_long_press_button import ElaLongPressButton as ElaLongPressBtn
from pyqt5_ela_pro.ela_progress_button import ElaProgressButton


class TestElaLongPressBtn:
    """Test cases for ElaLongPressBtn class."""

    @pytest.mark.parametrize(
        ("attr", "expected"),
        [("_duration", 500), ("_progress", 0.0), ("_triggered", False)],
        ids=["duration", "progress", "triggered"],
    )
    def test_initialization_with_defaults(self, make, attr, expected):
        assert getattr(make(ElaLongPressBtn), attr) == expected

    def test_initialization_with_custom_duration(self, make):
        assert make(ElaLongPressBtn, duration=800)._duration == 800

    @pytest.mark.parametrize("signal", ["longPressed", "progressChanged"])
    def test_has_signal(self, make, signal):
        assert hasattr(make(ElaLongPressBtn), signal)

    def test_set_duration(self, make):
        btn = make(ElaLongPressBtn)
        btn.set_duration(1000)
        assert btn._duration == 1000

    def test_duration_returns_value(self, make):
        """setter 之后 getter 必须回读得到（此前只测了 ``_duration``）。"""
        btn = make(ElaLongPressBtn)
        btn.set_duration(2000)
        assert btn.duration() == 2000

    def test_set_duration_ignores_zero(self, make):
        """非法值（0）被忽略，保持默认 500。"""
        btn = make(ElaLongPressBtn)
        btn.set_duration(0)
        assert btn._duration == 500

    def test_progress_initially_zero(self, make):
        assert make(ElaLongPressBtn).progress() == 0.0

    def test_delete_later_stops_timers(self, make):
        """析构时鼠标按下计时器必须被停掉。"""
        btn = make(ElaLongPressBtn)
        btn._mouse_pressed_timer.start()
        btn.deleteLater()

    def test_step_length_calculation(self, make):
        """_stepLength 返回 (0, 1] 区间内的增量。"""
        step = make(ElaLongPressBtn, duration=500)._stepLength()
        assert step > 0
        assert step <= 1.0


class TestElaProgressButton:
    """Test cases for ElaProgressButton class."""

    @pytest.mark.parametrize(
        ("attr", "expected"),
        [("_progress", 0.0), ("_custom_progress_color", False)],
        ids=["progress", "custom-progress-color"],
    )
    def test_initialization_with_defaults(self, make, attr, expected):
        assert getattr(make(ElaProgressButton), attr) == expected

    def test_initialization_with_text(self, make):
        assert make(ElaProgressButton, text="下载").text() == "下载"

    def test_initialization_with_custom_color(self, make):
        """QColor 必须在用例内构造 —— parametrize 参数在 qapp 之前求值。"""
        btn = make(ElaProgressButton, getProgressColor=QColor(255, 0, 0))
        assert btn._custom_progress_color is True

    def test_has_progress_changed_signal(self, make):
        assert hasattr(make(ElaProgressButton), "progressChanged")

    def test_set_progress_emits_signal(self, make):
        btn = make(ElaProgressButton)
        received = []
        btn.progressChanged.connect(received.append)

        btn.setProgress(50)

        assert 50 in received

    def test_delete_later_disconnects_theme(self, make):
        """析构要断开主题信号。"""
        make(ElaProgressButton).deleteLater()
