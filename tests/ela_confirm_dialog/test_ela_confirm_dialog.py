from __future__ import annotations

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro.ela_confirm_dialog import ElaConfirmDialog, _ElaConfirmButton


class TestElaConfirmDialogInit:
    def test_initialization_with_defaults(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        assert dlg._title == "标题"
        assert dlg._content == ""
        assert dlg._border_radius == 8
        assert dlg._position == "bottom"
        assert dlg._title_pixel_size == 15
        assert dlg._content_pixel_size == 13
        parent.deleteLater()
        dlg.deleteLater()

    def test_initialization_with_position_top(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent, position="top")
        assert dlg._position == "top"
        parent.deleteLater()
        dlg.deleteLater()

    def test_minimum_size(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        assert dlg.minimumWidth() == 280
        assert dlg.minimumHeight() == 150
        parent.deleteLater()
        dlg.deleteLater()

    def test_has_confirm_and_cancel_buttons(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        assert hasattr(dlg, '_confirm_btn')
        assert hasattr(dlg, '_cancel_btn')
        parent.deleteLater()
        dlg.deleteLater()

    def test_frameless_window_hint(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        flags = dlg.windowFlags()
        assert flags & Qt.FramelessWindowHint
        parent.deleteLater()
        dlg.deleteLater()

    def test_translucent_background(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        assert dlg.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        parent.deleteLater()
        dlg.deleteLater()


class TestElaConfirmDialogSignals:
    def test_has_confirmed_signal(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        assert hasattr(dlg, "confirmed")
        assert callable(dlg.confirmed)
        parent.deleteLater()
        dlg.deleteLater()

    def test_has_cancelled_signal(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        assert hasattr(dlg, "cancelled")
        assert callable(dlg.cancelled)
        parent.deleteLater()
        dlg.deleteLater()


class TestElaConfirmDialogTitle:
    def test_set_title(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        dlg.setTitle("确认删除？")
        assert dlg.title() == "确认删除？"
        parent.deleteLater()
        dlg.deleteLater()

    def test_set_title_empty(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        dlg.setTitle("")
        assert dlg.title() == ""
        parent.deleteLater()
        dlg.deleteLater()


class TestElaConfirmDialogContent:
    def test_set_content(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        dlg.setContent("确定要删除此项目吗？")
        assert dlg.content() == "确定要删除此项目吗？"
        parent.deleteLater()
        dlg.deleteLater()

    def test_set_content_empty(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        dlg.setContent("")
        assert dlg.content() == ""
        parent.deleteLater()
        dlg.deleteLater()


class TestElaConfirmDialogBorderRadius:
    def test_border_radius_default(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        assert dlg.borderRadius() == 8
        parent.deleteLater()
        dlg.deleteLater()

    def test_set_border_radius(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        dlg.setBorderRadius(16)
        assert dlg.borderRadius() == 16
        parent.deleteLater()
        dlg.deleteLater()


class TestElaConfirmDialogPosition:
    def test_position_default(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        assert dlg.position() == "bottom"
        parent.deleteLater()
        dlg.deleteLater()

    def test_set_position_top(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        dlg.setPosition("top")
        assert dlg.position() == "top"
        parent.deleteLater()
        dlg.deleteLater()

    def test_set_position_bottom(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        dlg.setPosition("bottom")
        assert dlg.position() == "bottom"
        parent.deleteLater()
        dlg.deleteLater()


class TestElaConfirmDialogActions:
    def test_on_confirm_emits_confirmed(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        received = []
        dlg.confirmed.connect(lambda: received.append(True))
        dlg._onConfirm()
        assert received == [True]
        parent.deleteLater()
        dlg.deleteLater()

    def test_on_cancel_emits_cancelled(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        received = []
        dlg.cancelled.connect(lambda: received.append(True))
        dlg._onCancel()
        assert received == [True]
        parent.deleteLater()
        dlg.deleteLater()


class TestElaConfirmDialogTheme:
    def test_on_theme_changed_updates_mode(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        from PyQt5ElaWidgetTools import ElaThemeType
        dlg._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert dlg._theme_mode == ElaThemeType.ThemeMode.Dark
        parent.deleteLater()
        dlg.deleteLater()


class TestElaConfirmButton:
    def test_confirm_button_type(self):
        btn = _ElaConfirmButton(_ElaConfirmButton.TYPE_CONFIRM)
        assert btn._type == _ElaConfirmButton.TYPE_CONFIRM
        assert btn._is_hovered is False
        assert btn._is_pressed is False
        btn.deleteLater()

    def test_cancel_button_type(self):
        btn = _ElaConfirmButton(_ElaConfirmButton.TYPE_CANCEL)
        assert btn._type == _ElaConfirmButton.TYPE_CANCEL
        btn.deleteLater()

    def test_button_has_clicked_signal(self):
        btn = _ElaConfirmButton(_ElaConfirmButton.TYPE_CONFIRM)
        assert hasattr(btn, "clicked")
        btn.deleteLater()

    def test_button_has_hand_cursor(self):
        btn = _ElaConfirmButton(_ElaConfirmButton.TYPE_CONFIRM)
        assert btn.cursor().shape() == Qt.CursorShape.PointingHandCursor
        btn.deleteLater()

    def test_button_fixed_height(self):
        btn = _ElaConfirmButton(_ElaConfirmButton.TYPE_CONFIRM)
        assert btn.height() == 40
        btn.deleteLater()

    def test_button_enter_leave_events(self):
        btn = _ElaConfirmButton(_ElaConfirmButton.TYPE_CONFIRM)
        from PyQt5.QtCore import QEvent, QPoint
        btn._is_hovered = False
        btn.enterEvent(QEvent(QEvent.Type.Enter))
        assert btn._is_hovered is True
        btn.leaveEvent(QEvent(QEvent.Type.Leave))
        assert btn._is_hovered is False
        btn.deleteLater()


class TestElaConfirmDialogDeleteLater:
    def test_delete_later_cleans_up(self):
        parent = QWidget()
        dlg = ElaConfirmDialog(parent)
        dlg.deleteLater()
        parent.deleteLater()
