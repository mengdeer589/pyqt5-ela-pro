"""pytest configuration and fixtures for pyqt5_ela_pro tests."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget


@pytest.fixture(scope="session")
def qapp():
    """Provide QApplication instance for all tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_e_theme(mocker):
    """Mock PyQt5ElaWidgetTools.eTheme for isolated testing."""
    mock = mocker.patch("PyQt5ElaWidgetTools.eTheme")
    mock_theme_mode = MagicMock()
    mock_theme_mode.value = 0
    mock.getThemeMode.return_value = mock_theme_mode
    mock.getThemeColor.return_value = "#FFFFFF"
    mock.themeModeChanged = MagicMock()
    return mock


@pytest.fixture
def widget(qapp):
    """Provide a basic QWidget for testing."""
    w = QWidget()
    yield w
    w.deleteLater()


@pytest.fixture
def window_widget(qapp):
    """Provide a widget that can be shown (for animation tests)."""
    w = QWidget()
    w.setWindowFlags(Qt.Window)
    w.resize(400, 300)
    yield w
    if w.isVisible():
        w.close()
    w.deleteLater()