from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro.ela_dropdown_button import ElaDropDownButton
from PyQt5ElaWidgetTools import ElaIconType, ElaMenu


class TestElaDropDownButtonInit:
    def test_initialization_with_defaults(self):
        btn = ElaDropDownButton()
        assert btn._text == ""
        assert btn._icon == ElaIconType.IconName.None_
        btn.deleteLater()

    def test_initialization_with_text(self):
        btn = ElaDropDownButton(text="操作")
        assert btn.text() == "操作"
        btn.deleteLater()

    def test_initialization_with_icon(self):
        btn = ElaDropDownButton(icon=ElaIconType.IconName.Gear)
        assert btn.elaIcon() == ElaIconType.IconName.Gear
        btn.deleteLater()

    def test_initialization_with_text_and_icon(self):
        btn = ElaDropDownButton(text="操作", icon=ElaIconType.IconName.Gear)
        assert btn.text() == "操作"
        assert btn.elaIcon() == ElaIconType.IconName.Gear
        btn.deleteLater()
        assert btn._border_radius == 6
        assert btn._menu is None
        assert btn._is_hover is False
        assert btn._is_pressed is False
        btn.deleteLater()

    def test_fixed_height(self):
        btn = ElaDropDownButton()
        assert btn.height() == 35
        btn.deleteLater()

    def test_mouse_tracking_enabled(self):
        btn = ElaDropDownButton()
        assert btn.hasMouseTracking() is True
        btn.deleteLater()


class TestElaDropDownButtonText:
    def test_set_text(self):
        btn = ElaDropDownButton()
        btn.setText("操作")
        assert btn.text() == "操作"
        btn.deleteLater()

    def test_set_text_empty(self):
        btn = ElaDropDownButton()
        btn.setText("")
        assert btn.text() == ""
        btn.deleteLater()


class TestElaDropDownButtonIcon:
    def test_set_icon(self):
        btn = ElaDropDownButton()
        btn.setElaIcon(ElaIconType.IconName.Gear)
        assert btn.elaIcon() == ElaIconType.IconName.Gear
        btn.deleteLater()

    def test_icon_default(self):
        btn = ElaDropDownButton()
        assert btn.elaIcon() == ElaIconType.IconName.None_
        btn.deleteLater()


class TestElaDropDownButtonBorderRadius:
    def test_border_radius_default(self):
        btn = ElaDropDownButton()
        assert btn.borderRadius() == 6
        btn.deleteLater()

    def test_set_border_radius(self):
        btn = ElaDropDownButton()
        btn.setBorderRadius(12)
        assert btn.borderRadius() == 12
        btn.deleteLater()


class TestElaDropDownButtonMenu:
    def test_set_menu(self):
        btn = ElaDropDownButton()
        parent = QWidget()
        menu = ElaMenu(parent)
        btn.setMenu(menu)
        assert btn.menu() is menu
        parent.deleteLater()
        btn.deleteLater()

    def test_menu_default_none(self):
        btn = ElaDropDownButton()
        assert btn.menu() is None
        btn.deleteLater()


class TestElaDropDownButtonEvents:
    def test_leave_resets_hover_and_press(self):
        btn = ElaDropDownButton()
        btn._is_hover = True
        btn._is_pressed = True
        from PyQt5.QtCore import QEvent
        btn.leaveEvent(QEvent(QEvent.Type.Leave))
        assert btn._is_hover is False
        assert btn._is_pressed is False
        btn.deleteLater()

    def test_mouse_press_sets_pressed(self):
        btn = ElaDropDownButton()
        from PyQt5.QtCore import QEvent, QPoint
        from PyQt5.QtGui import QMouseEvent
        event = QMouseEvent(QEvent.Type.MouseButtonPress, QPoint(10, 10),
                            Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
                            Qt.KeyboardModifier.NoModifier)
        btn.mousePressEvent(event)
        assert btn._is_pressed is True
        btn.deleteLater()


class TestElaDropDownButtonTheme:
    def test_on_theme_changed_updates_mode(self):
        btn = ElaDropDownButton()
        from PyQt5ElaWidgetTools import ElaThemeType
        btn._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert btn._theme_mode == ElaThemeType.ThemeMode.Dark
        btn.deleteLater()


class TestElaDropDownButtonDeleteLater:
    def test_delete_later_cleans_up(self):
        btn = ElaDropDownButton()
        btn.deleteLater()
