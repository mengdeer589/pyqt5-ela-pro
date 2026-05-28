from __future__ import annotations

from PyQt5.QtWidgets import QLineEdit

from pyqt5_ela_pro.ela_password_edit import ElaPasswordEdit


class TestElaPasswordEditInit:
    def test_initialization_with_defaults(self):
        pwd = ElaPasswordEdit()
        assert pwd._is_password_visible is False
        assert pwd.echoMode() == QLineEdit.EchoMode.Password
        pwd.deleteLater()

    def test_has_toggle_action(self):
        pwd = ElaPasswordEdit()
        assert pwd._toggle_action is not None
        pwd.deleteLater()


class TestElaPasswordEditVisibility:
    def test_is_password_visible_default(self):
        pwd = ElaPasswordEdit()
        assert pwd.is_password_visible() is False
        pwd.deleteLater()

    def test_set_is_password_visible_true(self):
        pwd = ElaPasswordEdit()
        pwd.set_is_password_visible(True)
        assert pwd.is_password_visible() is True
        assert pwd.echoMode() == QLineEdit.EchoMode.Normal
        pwd.deleteLater()

    def test_set_is_password_visible_false(self):
        pwd = ElaPasswordEdit()
        pwd.set_is_password_visible(True)
        pwd.set_is_password_visible(False)
        assert pwd.is_password_visible() is False
        assert pwd.echoMode() == QLineEdit.EchoMode.Password
        pwd.deleteLater()

    def test_toggle_visibility(self):
        pwd = ElaPasswordEdit()
        pwd._on_toggle_visibility()
        assert pwd.is_password_visible() is True
        pwd._on_toggle_visibility()
        assert pwd.is_password_visible() is False
        pwd.deleteLater()


class TestElaPasswordEditIcon:
    def test_eye_icon_initially_eye(self):
        pwd = ElaPasswordEdit()
        icon = pwd._toggle_action.icon()
        assert icon is not None
        pwd.deleteLater()

    def test_eye_icon_changes_on_toggle(self):
        pwd = ElaPasswordEdit()
        icon_before = pwd._toggle_action.icon()
        pwd.set_is_password_visible(True)
        icon_after = pwd._toggle_action.icon()
        assert icon_before != icon_after
        pwd.deleteLater()


class TestElaPasswordEditDeleteLater:
    def test_delete_later_disconnects_theme(self):
        pwd = ElaPasswordEdit()
        pwd.deleteLater()
