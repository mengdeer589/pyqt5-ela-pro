"""Tests for notify_popup module: ElaNotifyPopup and show_notify."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro.notify_popup import ElaNotifyPopup, ElaNotifyManager, show_notify


class TestElaNotifyPopup:
    """Test cases for ElaNotifyPopup class."""

    def test_ela_notify_popup_initialization(self):
        """Test ElaNotifyPopup initializes with correct default values."""
        popup = ElaNotifyPopup(title="Test", content="Content", timeout=5000)

        assert popup._title == "Test"
        assert popup._content == "Content"
        assert popup._timeout == 5000
        assert popup._is_showing is False

        popup.deleteLater()

    def test_ela_notify_popup_has_closed_signal(self):
        """Test ElaNotifyPopup has closed signal."""
        popup = ElaNotifyPopup()
        assert hasattr(popup, "closed")
        popup.deleteLater()

    def test_ela_notify_popup_set_title(self):
        """Test setTitle method updates title."""
        popup = ElaNotifyPopup()
        popup.setTitle("New Title")

        assert popup._title == "New Title"

        popup.deleteLater()

    def test_ela_notify_popup_set_content(self):
        """Test setContent method updates content."""
        popup = ElaNotifyPopup()
        popup.setContent("New Content")

        assert popup._content == "New Content"

        popup.deleteLater()

    def test_ela_notify_popup_set_timeout(self):
        """Test setTimeout method updates timeout."""
        popup = ElaNotifyPopup()
        popup.setTimeout(3000)

        assert popup._timeout == 3000

        popup.deleteLater()

    def test_ela_notify_popup_has_width_constraint(self):
        """Test ElaNotifyPopup has width constraint."""
        popup = ElaNotifyPopup()
        popup.show()
        assert popup.width() == 300
        popup.deleteLater()

    def test_ela_notify_popup_has_frameless_window(self):
        """Test ElaNotifyPopup uses frameless window flags."""
        popup = ElaNotifyPopup()

        flags = popup.windowFlags()
        assert flags & Qt.FramelessWindowHint

        popup.deleteLater()

    def test_ela_notify_popup_has_translucent_background(self):
        """Test ElaNotifyPopup has translucent background attribute."""
        popup = ElaNotifyPopup()

        assert popup.testAttribute(Qt.WA_TranslucentBackground)

        popup.deleteLater()


class TestElaNotifyManager:
    """Test cases for ElaNotifyManager singleton."""

    def test_ela_notify_manager_is_singleton(self):
        """Test ElaNotifyManager returns same instance."""
        manager1 = ElaNotifyManager()
        manager2 = ElaNotifyManager()

        assert manager1 is manager2

    def test_show_notify_is_ela_manager_show(self):
        """Test show_notify is bound to ElaNotifyManager.show method."""
        assert show_notify == ElaNotifyManager().show

    def test_ela_notify_manager_show_creates_popup(self):
        """Test show method creates and shows popup."""
        manager = ElaNotifyManager()
        manager._popups.clear()

        manager.show(title="Test", content="Message", timeout=100)

        assert len(manager._popups) == 1
        popup = manager._popups[0]
        assert isinstance(popup, ElaNotifyPopup)

        popup.deleteLater()

    def test_ela_notify_manager_removes_closed_popup(self):
        """Test _on_popup_closed removes popup from list."""
        manager = ElaNotifyManager()
        manager._popups.clear()

        popup = ElaNotifyPopup(title="Test", timeout=100)
        manager._popups.append(popup)

        manager._on_popup_closed(popup)

        assert popup not in manager._popups

        popup.deleteLater()