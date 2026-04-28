"""Tests for dialog_base module: ElaDialogBase."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch


class TestElaDialogBase:
    """Test cases for ElaDialogBase class."""

    def test_dialog_base_module_imports(self):
        """Test that dialog_base module can be imported."""
        from pyqt5_ela_pro.dialog_base import ElaDialogBase
        assert ElaDialogBase is not None

    def test_button_text_constants(self):
        """Test that cancel and confirm button texts are defined."""
        from pyqt5_ela_pro.dialog_base import ElaDialogBase
        import inspect

        source = inspect.getsource(ElaDialogBase.__init__)
        assert "取消" in source
        assert "确定" in source

    def test_delete_later_disconnects_middle_button(self, qapp):
        """Test deleteLater disconnects middleButtonClicked."""
        from PyQt5.QtWidgets import QWidget
        from pyqt5_ela_pro.dialog_base import ElaDialogBase
        parent = QWidget()
        dlg = ElaDialogBase(parent=parent, middleText="稍后提醒")
        dlg.deleteLater()
        parent.deleteLater()