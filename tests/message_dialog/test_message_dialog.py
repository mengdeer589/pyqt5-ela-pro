"""Tests for message_dialog module: ElaMessageDialog."""

from __future__ import annotations

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QWidget

from pyside6_ela_pro.dialog_base import ElaDialogBase
from pyside6_ela_pro.message_dialog import ElaMessageDialog


class TestElaMessageDialog:
    """Test cases for ElaMessageDialog class."""

    def test_message_dialog_module_imports(self):
        """Test that message_dialog module can be imported."""
        assert ElaMessageDialog is not None

    def test_message_dialog_has_show_method(self):
        """Test that show method exists."""
        assert hasattr(ElaMessageDialog, "show")
        assert callable(ElaMessageDialog.show)

    def test_message_dialog_inherits_from_dialog_base(self):
        """Test that ElaMessageDialog inherits from ElaDialogBase."""
        assert issubclass(ElaMessageDialog, ElaDialogBase)

    def test_set_param_widget_survives_set_message(self, qapp):
        """Regression: setMessage must not delete user content from setParamWidget."""
        import shiboken6

        parent = QWidget()
        dlg = ElaMessageDialog(parent=parent)
        content = QWidget()
        dlg.setParamWidget(content)

        dlg.setMessage("hello")
        QCoreApplication.sendPostedEvents(content, QEvent.DeferredDelete)
        qapp.processEvents()

        assert shiboken6.isValid(content)
        assert dlg._paramLay.indexOf(content) != -1
        assert dlg._message_widget is not None
        dlg.deleteLater()
        parent.deleteLater()

    def test_set_message_replaces_previous_message_widget(self, qapp):
        """Regression: setMessage must replace only its own message widget."""
        import shiboken6

        parent = QWidget()
        dlg = ElaMessageDialog(parent=parent)
        first = dlg._message_widget

        dlg.setMessage("second")
        QCoreApplication.sendPostedEvents(first, QEvent.DeferredDelete)
        qapp.processEvents()

        assert first is not dlg._message_widget
        assert not shiboken6.isValid(first)
        assert shiboken6.isValid(dlg._message_widget)
        assert dlg._paramLay.indexOf(dlg._message_widget) != -1
        dlg.deleteLater()
        parent.deleteLater()
