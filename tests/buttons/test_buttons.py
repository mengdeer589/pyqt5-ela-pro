"""Tests for buttons modules: ElaLongPressBtn, ElaProgressButton."""

from __future__ import annotations


from pyqt5_ela_pro.ela_long_press_button import ElaLongPressButton as ElaLongPressBtn
from pyqt5_ela_pro.ela_progress_button import ElaProgressButton


class TestElaLongPressBtn:
    """Test cases for ElaLongPressBtn class."""

    def test_initialization_with_defaults(self):
        """Test long press button initializes with default duration."""
        btn = ElaLongPressBtn()

        assert btn._duration == 500
        assert btn._progress == 0.0
        assert btn._triggered is False

        btn.deleteLater()

    def test_initialization_with_custom_duration(self):
        """Test long press button accepts custom duration."""
        btn = ElaLongPressBtn(duration=800)

        assert btn._duration == 800

        btn.deleteLater()

    def test_has_long_pressed_signal(self):
        """Test long press button has longPressed signal."""
        btn = ElaLongPressBtn()
        assert hasattr(btn, 'longPressed')
        btn.deleteLater()

    def test_has_progress_changed_signal(self):
        """Test long press button has progressChanged signal."""
        btn = ElaLongPressBtn()
        assert hasattr(btn, 'progressChanged')
        btn.deleteLater()

    def test_set_duration(self):
        """Test setDuration updates duration."""
        btn = ElaLongPressBtn()
        btn.set_duration(1000)

        assert btn._duration == 1000

        btn.deleteLater()

    def test_duration_returns_value(self):
        """Test duration returns current value."""
        btn = ElaLongPressBtn()
        btn.set_duration(2000)

        assert btn.duration() == 2000

        btn.deleteLater()

    def test_set_duration_ignores_zero_or_negative(self):
        """Test setDuration ignores invalid values."""
        btn = ElaLongPressBtn()
        btn.set_duration(0)

        assert btn._duration == 500

        btn.deleteLater()

    def test_progress_initially_zero(self):
        """Test progress is initially 0."""
        btn = ElaLongPressBtn()

        assert btn.progress() == 0.0

        btn.deleteLater()

    def test_delete_later_stops_timers(self):
        """Test deleteLater stops mouse pressed timer."""
        btn = ElaLongPressBtn()
        btn._mouse_pressed_timer.start()

        btn.deleteLater()

    def test_step_length_calculation(self):
        """Test _stepLength returns correct increment."""
        btn = ElaLongPressBtn(duration=500)

        step = btn._stepLength()

        assert step > 0
        assert step <= 1.0


class TestElaProgressButton:
    """Test cases for ElaProgressButton class."""

    def test_initialization_with_defaults(self):
        """Test progress button initializes correctly."""
        btn = ElaProgressButton()

        assert btn._progress == 0.0
        assert btn._custom_progress_color is False

        btn.deleteLater()

    def test_initialization_with_text(self):
        """Test progress button accepts text parameter."""
        btn = ElaProgressButton(text="下载")

        assert btn.text() == "下载"

        btn.deleteLater()

    def test_initialization_with_custom_color(self):
        """Test progress button accepts custom color."""
        from PyQt5.QtGui import QColor

        btn = ElaProgressButton(getProgressColor=QColor(255, 0, 0))

        assert btn._custom_progress_color is True

        btn.deleteLater()

    def test_has_progress_changed_signal(self):
        """Test progress button has progressChanged signal."""
        btn = ElaProgressButton()
        assert hasattr(btn, 'progressChanged')
        btn.deleteLater()

    def test_set_progress_emits_signal(self):
        """Test setProgress emits progressChanged signal."""
        btn = ElaProgressButton()

        received = []
        btn.progressChanged.connect(lambda v: received.append(v))

        btn.setProgress(50)

        assert 50 in received

        btn.deleteLater()

    def test_delete_later_disconnects_theme(self):
        """Test deleteLater disconnects theme signal."""
        btn = ElaProgressButton()
        btn.deleteLater()