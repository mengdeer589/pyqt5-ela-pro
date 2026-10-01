"""``ElaDropDownButton`` 测试：初值 / 文本 / 图标 / 圆角 / 菜单 / 鼠标事件。"""

from __future__ import annotations

import pytest
from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget
from PyQt5ElaWidgetTools import ElaIconType, ElaMenu, ElaThemeType

from pyqt5_ela_pro.ela_dropdown_button import ElaDropDownButton


@pytest.fixture
def btn(make):
    """默认构造的下拉按钮。"""
    return make(ElaDropDownButton)


class TestElaDropDownButtonInit:
    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("_text", ""),
            ("_icon", ElaIconType.IconName.None_),
            ("_border_radius", 6),
            ("_menu", None),
            ("_is_hover", False),
            ("_is_pressed", False),
        ],
        ids=["text", "icon", "border-radius", "menu", "hover", "pressed"],
    )
    def test_initialization_with_defaults(self, btn, attr, expected):
        assert getattr(btn, attr) == expected

    def test_initialization_with_text(self, make):
        assert make(ElaDropDownButton, text="操作").text() == "操作"

    def test_initialization_with_icon(self, make):
        assert make(ElaDropDownButton, icon=ElaIconType.IconName.Gear).elaIcon() == (
            ElaIconType.IconName.Gear
        )

    def test_initialization_with_text_and_icon(self, make):
        btn = make(ElaDropDownButton, text="操作", icon=ElaIconType.IconName.Gear)
        assert btn.text() == "操作"
        assert btn.elaIcon() == ElaIconType.IconName.Gear

    def test_fixed_height(self, btn):
        assert btn.height() == 35

    def test_mouse_tracking_enabled(self, btn):
        assert btn.hasMouseTracking() is True


class TestElaDropDownButtonText:
    @pytest.mark.parametrize("text", ["操作", ""], ids=["non-empty", "empty"])
    def test_set_text_roundtrip(self, btn, text):
        btn.setText(text)
        assert btn.text() == text


class TestElaDropDownButtonIcon:
    def test_set_icon(self, btn):
        btn.setElaIcon(ElaIconType.IconName.Gear)
        assert btn.elaIcon() == ElaIconType.IconName.Gear

    def test_icon_default(self, btn):
        assert btn.elaIcon() == ElaIconType.IconName.None_


class TestElaDropDownButtonBorderRadius:
    def test_border_radius_default(self, btn):
        assert btn.borderRadius() == 6

    def test_set_border_radius(self, btn):
        btn.setBorderRadius(12)
        assert btn.borderRadius() == 12


class TestElaDropDownButtonMenu:
    def test_set_menu(self, make):
        btn = make(ElaDropDownButton)
        parent = make(QWidget)
        menu = make(ElaMenu, parent)

        btn.setMenu(menu)

        assert btn.menu() is menu

    def test_menu_default_none(self, btn):
        assert btn.menu() is None


class TestElaDropDownButtonEvents:
    @pytest.mark.parametrize(
        "attr", ["_is_hover", "_is_pressed"], ids=["hover", "pressed"]
    )
    def test_leave_resets_state(self, btn, attr):
        setattr(btn, attr, True)

        btn.leaveEvent(QEvent(QEvent.Type.Leave))

        assert getattr(btn, attr) is False

    def test_mouse_press_sets_pressed(self, btn):
        btn.mousePressEvent(
            QMouseEvent(
                QEvent.Type.MouseButtonPress,
                QPoint(10, 10),
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier,
            )
        )
        assert btn._is_pressed is True


class TestElaDropDownButtonTheme:
    def test_on_theme_changed_updates_mode(self, btn):
        btn._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert btn._theme_mode == ElaThemeType.ThemeMode.Dark


class TestElaDropDownButtonDeleteLater:
    def test_delete_later_cleans_up(self, btn):
        btn.deleteLater()
