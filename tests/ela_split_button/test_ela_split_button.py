"""``ElaSplitButton`` 测试：初值 / 文本 / 图标 / 圆角 / 菜单 / 事件。"""

from __future__ import annotations

import pytest
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QWidget
from PyQt5ElaWidgetTools import ElaIconType, ElaMenu, ElaThemeType

from pyqt5_ela_pro.ela_split_button import ElaSplitButton


@pytest.fixture
def btn(make):
    """默认构造的 split button。"""
    return make(ElaSplitButton)


class TestElaSplitButtonInit:
    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("_text", ""),
            ("_icon", ElaIconType.IconName.None_),
            ("_border_radius", 3),
            ("_dropdown_width", 30),
            ("_menu", None),
            ("_is_left_hovered", False),
            ("_is_right_hovered", False),
            ("_is_left_pressed", False),
            ("_is_right_pressed", False),
        ],
        ids=[
            "text",
            "icon",
            "border-radius",
            "dropdown-width",
            "menu",
            "left-hovered",
            "right-hovered",
            "left-pressed",
            "right-pressed",
        ],
    )
    def test_initialization_with_defaults(self, btn, attr, expected):
        assert getattr(btn, attr) == expected

    def test_initialization_with_text(self, make):
        assert make(ElaSplitButton, text="保存").text() == "保存"

    def test_initialization_with_icon(self, make):
        icon = ElaIconType.IconName.FloppyDisk
        assert make(ElaSplitButton, icon=icon).elaIcon() == icon

    def test_initialization_with_text_and_icon(self, make):
        icon = ElaIconType.IconName.FloppyDisk
        btn = make(ElaSplitButton, text="保存", icon=icon)
        assert btn.text() == "保存"
        assert btn.elaIcon() == icon

    def test_fixed_height(self, btn):
        assert btn.height() == 35

    def test_mouse_tracking_enabled(self, btn):
        assert btn.hasMouseTracking() is True

    def test_has_clicked_signal(self, btn):
        assert hasattr(btn, "clicked")
        assert callable(btn.clicked)


class TestElaSplitButtonText:
    @pytest.mark.parametrize("text", ["保存", ""], ids=["non-empty", "empty"])
    def test_set_text_roundtrip(self, btn, text):
        btn.setText(text)
        assert btn.text() == text


class TestElaSplitButtonIcon:
    def test_set_icon(self, btn):
        btn.setElaIcon(ElaIconType.IconName.FloppyDisk)
        assert btn.elaIcon() == ElaIconType.IconName.FloppyDisk

    def test_icon_default(self, btn):
        assert btn.elaIcon() == ElaIconType.IconName.None_


class TestElaSplitButtonBorderRadius:
    def test_border_radius_default(self, btn):
        assert btn.borderRadius() == 3

    def test_set_border_radius(self, btn):
        btn.setBorderRadius(12)
        assert btn.borderRadius() == 12


class TestElaSplitButtonMenu:
    def test_set_menu(self, make):
        btn = make(ElaSplitButton)
        parent = make(QWidget)
        menu = make(ElaMenu, parent)

        btn.setMenu(menu)

        assert btn.menu() is menu

    def test_menu_default_none(self, btn):
        assert btn.menu() is None


class TestElaSplitButtonLeaveEvent:
    @pytest.mark.parametrize(
        "attr",
        [
            "_is_left_hovered",
            "_is_right_hovered",
            "_is_left_pressed",
            "_is_right_pressed",
        ],
        ids=["left-hovered", "right-hovered", "left-pressed", "right-pressed"],
    )
    def test_leave_resets_state(self, btn, attr):
        setattr(btn, attr, True)

        btn.leaveEvent(QEvent(QEvent.Type.Leave))

        assert getattr(btn, attr) is False


class TestElaSplitButtonTheme:
    def test_on_theme_changed_updates_mode(self, btn):
        btn._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert btn._theme_mode == ElaThemeType.ThemeMode.Dark


class TestElaSplitButtonDeleteLater:
    def test_delete_later_cleans_up(self, btn):
        btn.deleteLater()
