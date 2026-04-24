"""Tests for message_dialog module: ElaMessageDialog."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch


class TestElaMessageDialog:
    """Test cases for ElaMessageDialog class."""

    def test_message_dialog_module_imports(self):
        """Test that message_dialog module can be imported."""
        from pyqt5_ela_pro.message_dialog import ElaMessageDialog
        assert ElaMessageDialog is not None

    def test_message_dialog_has_show_method(self):
        """Test that show method exists."""
        from pyqt5_ela_pro.message_dialog import ElaMessageDialog
        assert hasattr(ElaMessageDialog, 'show')
        assert callable(ElaMessageDialog.show)

    def test_message_dialog_inherits_from_dialog_base(self):
        """Test that ElaMessageDialog inherits from ElaDialogBase."""
        from pyqt5_ela_pro.message_dialog import ElaMessageDialog
        from pyqt5_ela_pro.dialog_base import ElaDialogBase
        assert issubclass(ElaMessageDialog, ElaDialogBase)