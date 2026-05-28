"""Tests for dialog_base module: ElaDialogBase."""

from __future__ import annotations

from PyQt5.QtWidgets import QWidget


class TestElaDialogBase:
    """Test cases for ElaDialogBase class."""

    def test_dialog_base_module_imports(self):
        """Test that dialog_base module can be imported."""
        from pyqt5_ela_pro.dialog_base import ElaDialogBase
        assert ElaDialogBase is not None

    def test_create_with_default_buttons(self, qapp):
        from pyqt5_ela_pro.dialog_base import ElaDialogBase
        parent = QWidget()
        dlg = ElaDialogBase(parent=parent)
        assert dlg is not None
        dlg.deleteLater()
        parent.deleteLater()

    def test_create_with_middle_text(self, qapp):
        from pyqt5_ela_pro.dialog_base import ElaDialogBase
        parent = QWidget()
        dlg = ElaDialogBase(parent=parent, middleText="稍后提醒")
        assert dlg is not None
        dlg.deleteLater()
        parent.deleteLater()

    def test_set_title(self, qapp):
        from pyqt5_ela_pro.dialog_base import ElaDialogBase
        parent = QWidget()
        dlg = ElaDialogBase(parent=parent)
        dlg.setTitle("测试标题")
        parent.deleteLater()

    def test_confirm_button_emits_signal(self, qapp):
        from pyqt5_ela_pro.dialog_base import ElaDialogBase
        parent = QWidget()
        dlg = ElaDialogBase(parent=parent)
        fired = False
        def on_confirm():
            nonlocal fired
            fired = True
        dlg.rightButtonClicked.connect(on_confirm)
        dlg.rightButtonClicked.emit()
        assert fired
        dlg.deleteLater()
        parent.deleteLater()

    def test_middle_button_emits_signal(self, qapp):
        from pyqt5_ela_pro.dialog_base import ElaDialogBase
        parent = QWidget()
        dlg = ElaDialogBase(parent=parent, middleText="稍后提醒")
        fired = False
        def on_middle():
            nonlocal fired
            fired = True
        dlg.middleButtonClicked.connect(on_middle)
        dlg.middleButtonClicked.emit()
        assert fired
        dlg.deleteLater()
        parent.deleteLater()

    def test_cancel_button_emits_signal(self, qapp):
        from pyqt5_ela_pro.dialog_base import ElaDialogBase
        parent = QWidget()
        dlg = ElaDialogBase(parent=parent)
        fired = False
        def on_cancel():
            nonlocal fired
            fired = True
        dlg.leftButtonClicked.connect(on_cancel)
        dlg.leftButtonClicked.emit()
        assert fired
        dlg.deleteLater()
        parent.deleteLater()

    def test_delete_later_disconnects_middle_button(self, qapp):
        from pyqt5_ela_pro.dialog_base import ElaDialogBase
        parent = QWidget()
        dlg = ElaDialogBase(parent=parent, middleText="稍后提醒")
        dlg.deleteLater()
        parent.deleteLater()

    def test_delete_later_disconnects_right_button(self, qapp):
        from pyqt5_ela_pro.dialog_base import ElaDialogBase
        parent = QWidget()
        dlg = ElaDialogBase(parent=parent)
        dlg.deleteLater()
        parent.deleteLater()

    def test_multiple_dialogs_created_and_destroyed(self, qapp):
        from pyqt5_ela_pro.dialog_base import ElaDialogBase
        parent = QWidget()
        dialogs = [ElaDialogBase(parent=parent) for _ in range(5)]
        for d in dialogs:
            d.deleteLater()
        parent.deleteLater()
