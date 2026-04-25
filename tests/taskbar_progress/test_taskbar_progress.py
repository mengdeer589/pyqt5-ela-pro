"""Tests for taskbar_progress module: ElaTaskbarProgress."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget


class TestElaTaskbarProgressImport:
    """Test cases for ElaTaskbarProgress import behavior."""

    def test_taskbar_progress_module_imports(self):
        """Test that taskbar_progress module can be imported."""
        from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress
        assert ElaTaskbarProgress is not None

    def test_has_valueChanged_signal(self):
        """Test ElaTaskbarProgress has valueChanged signal."""
        from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

        assert hasattr(ElaTaskbarProgress, 'valueChanged')
        sig = getattr(ElaTaskbarProgress, 'valueChanged')
        assert isinstance(sig, pyqtSignal)

    def test_has_pausedChanged_signal(self):
        """Test ElaTaskbarProgress has pausedChanged signal."""
        from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

        assert hasattr(ElaTaskbarProgress, 'pausedChanged')
        sig = getattr(ElaTaskbarProgress, 'pausedChanged')
        assert isinstance(sig, pyqtSignal)

    def test_has_stoppedChanged_signal(self):
        """Test ElaTaskbarProgress has stoppedChanged signal."""
        from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

        assert hasattr(ElaTaskbarProgress, 'stoppedChanged')
        sig = getattr(ElaTaskbarProgress, 'stoppedChanged')
        assert isinstance(sig, pyqtSignal)

    def test_has_visibilityChanged_signal(self):
        """Test ElaTaskbarProgress has visibilityChanged signal."""
        from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

        assert hasattr(ElaTaskbarProgress, 'visibilityChanged')
        sig = getattr(ElaTaskbarProgress, 'visibilityChanged')
        assert isinstance(sig, pyqtSignal)


class TestElaTaskbarProgressMethods:
    """Test cases for ElaTaskbarProgress methods with mocked Win32."""

    def test_initialization_stores_window(self):
        """Test initialization stores the window reference."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            assert tb._window is window

            window.deleteLater()

    def test_initial_button_is_none(self):
        """Test initial _button is None before attachment."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            assert tb._button is None

            window.deleteLater()

    def test_initial_progress_is_none(self):
        """Test initial _progress is None before attachment."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            assert tb._progress is None

            window.deleteLater()

    def test_initial_attached_is_false(self):
        """Test initial _attached is False."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            assert tb._attached is False

            window.deleteLater()

    def test_value_property_returns_zero_when_no_progress(self):
        """Test value property returns 0 when _progress is None."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            assert tb.value == 0

            window.deleteLater()

    def test_minimum_property_returns_zero_when_no_progress(self):
        """Test minimum property returns 0 when _progress is None."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            assert tb.minimum == 0

            window.deleteLater()

    def test_maximum_property_returns_zero_when_no_progress(self):
        """Test maximum property returns 0 when _progress is None."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            assert tb.maximum == 0

            window.deleteLater()

    def test_isPaused_returns_false_when_no_progress(self):
        """Test isPaused returns False when _progress is None."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            assert tb.isPaused is False

            window.deleteLater()

    def test_isVisible_returns_false_when_no_progress(self):
        """Test isVisible returns False when _progress is None."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            assert tb.isVisible is False

            window.deleteLater()

    def test_isStopped_returns_false_when_no_progress(self):
        """Test isStopped returns False when _progress is None."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            assert tb.isStopped is False

            window.deleteLater()

    def test_setRange_is_noop_when_no_win_extras(self):
        """Test setRange is no-op when WinExtras not available."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            tb.setRange(0, 100)

            window.deleteLater()

    def test_ensure_attached_noop_when_window_is_none(self):
        """Test _ensure_attached is no-op when window is None."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            tb = ElaTaskbarProgress(None)
            tb._ensure_attached()
            assert tb._attached is False

    def test_setValue_is_noop_when_no_win_extras(self):
        """Test setValue is no-op when WinExtras not available."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            tb.setValue(50)

            window.deleteLater()

    def test_show_is_noop_when_no_win_extras(self):
        """Test show is no-op when WinExtras not available."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            tb.show()

            window.deleteLater()

    def test_hide_is_noop_when_no_progress(self):
        """Test hide is no-op when _progress is None."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            tb.hide()

            window.deleteLater()

    def test_pause_is_noop_when_no_win_extras(self):
        """Test pause is no-op when WinExtras not available."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            tb.pause()

            window.deleteLater()

    def test_resume_is_noop_when_no_win_extras(self):
        """Test resume is no-op when WinExtras not available."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            tb.resume()

            window.deleteLater()

    def test_stop_is_noop_when_no_win_extras(self):
        """Test stop is no-op when WinExtras not available."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            tb.stop()

            window.deleteLater()

    def test_reset_is_noop_when_no_progress(self):
        """Test reset is no-op when _progress is None."""
        with patch('pyqt5_ela_pro.taskbar_progress.QWinTaskbarButton', None):
            from pyqt5_ela_pro.taskbar_progress import ElaTaskbarProgress

            window = QWidget()
            tb = ElaTaskbarProgress(window)

            tb.reset()

            window.deleteLater()