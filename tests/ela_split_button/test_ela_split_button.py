from __future__ import annotations

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro.ela_split_button import ElaSplitButton
from PyQt5ElaWidgetTools import ElaIconType, ElaMenu


class TestElaSplitButtonInit:
    def test_initialization_with_defaults(self):
        btn = ElaSplitButton()
        assert btn._text == ""
        assert btn._icon == ElaIconType.IconName.None_
        btn.deleteLater()

    def test_initialization_with_text(self):
        btn = ElaSplitButton(text="保存")
        assert btn.text() == "保存"
        btn.deleteLater()

    def test_initialization_with_icon(self):
        btn = ElaSplitButton(icon=ElaIconType.IconName.FloppyDisk)
        assert btn.elaIcon() == ElaIconType.IconName.FloppyDisk
        btn.deleteLater()

    def test_initialization_with_text_and_icon(self):
        btn = ElaSplitButton(text="保存", icon=ElaIconType.IconName.FloppyDisk)
        assert btn.text() == "保存"
        assert btn.elaIcon() == ElaIconType.IconName.FloppyDisk
        btn.deleteLater()
        assert btn._border_radius == 3
        assert btn._dropdown_width == 30
        assert btn._menu is None
        assert btn._is_left_hovered is False
        assert btn._is_right_hovered is False
        assert btn._is_left_pressed is False
        assert btn._is_right_pressed is False
        btn.deleteLater()

    def test_fixed_height(self):
        btn = ElaSplitButton()
        assert btn.height() == 35
        btn.deleteLater()

    def test_mouse_tracking_enabled(self):
        btn = ElaSplitButton()
        assert btn.hasMouseTracking() is True
        btn.deleteLater()

    def test_has_clicked_signal(self):
        btn = ElaSplitButton()
        assert hasattr(btn, "clicked")
        assert callable(btn.clicked)
        btn.deleteLater()


class TestElaSplitButtonText:
    def test_set_text(self):
        btn = ElaSplitButton()
        btn.setText("保存")
        assert btn.text() == "保存"
        btn.deleteLater()

    def test_set_text_empty(self):
        btn = ElaSplitButton()
        btn.setText("")
        assert btn.text() == ""
        btn.deleteLater()


class TestElaSplitButtonIcon:
    def test_set_icon(self):
        btn = ElaSplitButton()
        btn.setElaIcon(ElaIconType.IconName.FloppyDisk)
        assert btn.elaIcon() == ElaIconType.IconName.FloppyDisk
        btn.deleteLater()

    def test_icon_default(self):
        btn = ElaSplitButton()
        assert btn.elaIcon() == ElaIconType.IconName.None_
        btn.deleteLater()


class TestElaSplitButtonBorderRadius:
    def test_border_radius_default(self):
        btn = ElaSplitButton()
        assert btn.borderRadius() == 3
        btn.deleteLater()

    def test_set_border_radius(self):
        btn = ElaSplitButton()
        btn.setBorderRadius(12)
        assert btn.borderRadius() == 12
        btn.deleteLater()


class TestElaSplitButtonMenu:
    def test_set_menu(self):
        btn = ElaSplitButton()
        parent = QWidget()
        menu = ElaMenu(parent)
        btn.setMenu(menu)
        assert btn.menu() is menu
        parent.deleteLater()
        btn.deleteLater()

    def test_menu_default_none(self):
        btn = ElaSplitButton()
        assert btn.menu() is None
        btn.deleteLater()


class TestElaSplitButtonLeaveEvent:
    def test_leave_resets_hover_and_press(self):
        btn = ElaSplitButton()
        btn._is_left_hovered = True
        btn._is_right_pressed = True
        from PyQt5.QtCore import QEvent
        btn.leaveEvent(QEvent(QEvent.Type.Leave))
        assert btn._is_left_hovered is False
        assert btn._is_right_hovered is False
        assert btn._is_left_pressed is False
        assert btn._is_right_pressed is False
        btn.deleteLater()


class TestElaSplitButtonTheme:
    def test_on_theme_changed_updates_mode(self):
        btn = ElaSplitButton()
        from PyQt5ElaWidgetTools import ElaThemeType
        btn._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert btn._theme_mode == ElaThemeType.ThemeMode.Dark
        btn.deleteLater()


class TestElaSplitButtonDeleteLater:
    def test_delete_later_cleans_up(self):
        btn = ElaSplitButton()
        btn.deleteLater()
