"""Tests for splash_screen module: ElaSplashScreen."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QSplashScreen

from pyqt5_ela_pro.splash_screen import ElaSplashScreen


class TestElaSplashScreen:
    """Test cases for ElaSplashScreen class."""

    def test_inherits_from_qsplashscreen(self):
        """Test ElaSplashScreen inherits from QSplashScreen."""
        splash = ElaSplashScreen()
        assert isinstance(splash, QSplashScreen)
        splash.close()

    def test_initialization_with_defaults(self):
        """Test splash screen initializes with default values."""
        splash = ElaSplashScreen()

        assert splash._title == "ElaWidgetTools"
        assert splash._subtitle == "Fluent UI For QWidget"
        assert splash._width == 500
        assert splash._height == 350

        splash.close()

    def test_initialization_with_custom_values(self):
        """Test splash screen accepts custom title, subtitle, size."""
        splash = ElaSplashScreen(
            title="My App",
            subtitle="Loading...",
            width=400,
            height=300
        )

        assert splash._title == "My App"
        assert splash._subtitle == "Loading..."
        assert splash._width == 400
        assert splash._height == 300

        splash.close()

    @patch('pyqt5_ela_pro.splash_screen.QSplashScreen.show')
    def test_show_calls_super_show(self, mock_show):
        """Test show calls super().show() and processes events."""
        splash = ElaSplashScreen()

        splash.show()

        mock_show.assert_called_once()
        splash.close()

    def test_initialization_calls_build_base_pixmap(self):
        """Test init calls _build_base_pixmap internally during parent __init__."""
        splash = ElaSplashScreen()
        assert splash._base_pixmap is not None
        assert splash._base_pixmap.width() == 500
        assert splash._base_pixmap.height() == 350
        splash.close()

    def test_build_progress_pixmap_returns_pixmap(self):
        """Test _build_progress_pixmap returns a valid QPixmap."""
        splash = ElaSplashScreen()
        pixmap = splash._build_progress_pixmap()
        assert pixmap is not None
        assert pixmap.width() == splash._width
        assert pixmap.height() == splash._height
        splash.close()

    def test_show_message_uses_super(self):
        """Test showMessage delegates to QSplashScreen.showMessage."""
        splash = ElaSplashScreen()

        with patch.object(QSplashScreen, 'showMessage') as mock_show_msg:
            splash.showMessage("Loading...")
            mock_show_msg.assert_called_once()

        splash.close()

    def test_finish_calls_super_finish(self):
        """Test finish delegates to QSplashScreen.finish without extra close."""
        splash = ElaSplashScreen()

        with patch.object(QSplashScreen, 'finish') as mock_finish, \
             patch.object(QSplashScreen, 'close') as mock_close:
            mock_widget = MagicMock()
            splash.finish(mock_widget)

            mock_finish.assert_called_once_with(mock_widget)
            mock_close.assert_not_called()

    def test_set_progress_updates_progress(self):
        """Test setProgress updates internal progress value."""
        splash = ElaSplashScreen()

        splash.setProgress(0.5)
        assert splash._progress == 0.5

        splash.setProgress(1.0)
        assert splash._progress == 1.0

        splash.setProgress(-0.1)
        assert splash._progress == 0.0

        splash.setProgress(1.5)
        assert splash._progress == 1.0

        splash.close()

    def test_set_progress_reuses_base_pixmap(self):
        """Test setProgress does not recreate the base pixmap."""
        splash = ElaSplashScreen()
        original_base = splash._base_pixmap

        splash.setProgress(0.5)
        assert splash._base_pixmap is original_base

        splash.setProgress(1.0)
        assert splash._base_pixmap is original_base

        splash.close()

    def test_close_calls_super_close(self):
        """Test close delegates to QSplashScreen.close."""
        splash = ElaSplashScreen()

        with patch.object(QSplashScreen, 'close') as mock_close:
            splash.close()

            mock_close.assert_called_once()