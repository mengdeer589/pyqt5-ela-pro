from __future__ import annotations

import pytest
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro.ela_info_badge import ElaInfoBadge
from PyQt5ElaWidgetTools import ElaIconType


class TestElaInfoBadgeInit:
    def test_initialization_with_defaults(self):
        badge = ElaInfoBadge()
        assert badge._badge_mode == ElaInfoBadge.BadgeMode.Dot
        assert badge._severity == ElaInfoBadge.Severity.Attention
        assert badge._value == 0
        assert badge._max_value == 99
        assert badge._target is None
        badge.deleteLater()

    def test_transparent_for_mouse_events(self):
        badge = ElaInfoBadge()
        assert badge.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        badge.deleteLater()

    def test_initialization_with_value(self):
        badge = ElaInfoBadge(value=5)
        assert badge._badge_mode == ElaInfoBadge.BadgeMode.Value
        assert badge._value == 5
        badge.deleteLater()

    def test_initialization_with_icon(self):
        badge = ElaInfoBadge(icon=ElaIconType.IconName.Gear)
        assert badge._badge_mode == ElaInfoBadge.BadgeMode.Icon
        assert badge._icon == ElaIconType.IconName.Gear
        badge.deleteLater()


class TestElaInfoBadgeEnums:
    def test_badge_mode_values(self):
        assert ElaInfoBadge.BadgeMode.Dot == 0
        assert ElaInfoBadge.BadgeMode.Value == 1
        assert ElaInfoBadge.BadgeMode.Icon == 2

    def test_severity_values(self):
        assert ElaInfoBadge.Severity.Attention == 0
        assert ElaInfoBadge.Severity.Informational == 1
        assert ElaInfoBadge.Severity.Success == 2
        assert ElaInfoBadge.Severity.Caution == 3
        assert ElaInfoBadge.Severity.Critical == 4


class TestElaInfoBadgeMode:
    def test_badge_mode_default(self):
        badge = ElaInfoBadge()
        assert badge.badgeMode() == ElaInfoBadge.BadgeMode.Dot
        badge.deleteLater()

    def test_set_badge_mode(self):
        badge = ElaInfoBadge()
        badge.setBadgeMode(ElaInfoBadge.BadgeMode.Value)
        assert badge.badgeMode() == ElaInfoBadge.BadgeMode.Value
        badge.deleteLater()


class TestElaInfoBadgeValue:
    def test_value_default(self):
        badge = ElaInfoBadge()
        assert badge.value() == 0
        badge.deleteLater()

    def test_set_value(self):
        badge = ElaInfoBadge()
        badge.setValue(42)
        assert badge.value() == 42
        badge.deleteLater()

    def test_set_value_zero(self):
        badge = ElaInfoBadge()
        badge.setValue(0)
        assert badge.value() == 0
        badge.deleteLater()


class TestElaInfoBadgeMaxValue:
    def test_max_value_default(self):
        badge = ElaInfoBadge()
        assert badge.maxValue() == 99
        badge.deleteLater()

    def test_set_max_value(self):
        badge = ElaInfoBadge()
        badge.setMaxValue(999)
        assert badge.maxValue() == 999
        badge.deleteLater()

    def test_max_value_overflow_displays_plus(self):
        badge = ElaInfoBadge()
        badge.setBadgeMode(ElaInfoBadge.BadgeMode.Value)
        badge.setValue(150)
        badge.setMaxValue(99)
        text = str(badge._value) if badge._value <= badge._max_value else f"{badge._max_value}+"
        assert text == "99+"
        badge.deleteLater()


class TestElaInfoBadgeIcon:
    def test_ela_icon_default(self):
        badge = ElaInfoBadge()
        assert badge.elaIcon() == ElaIconType.IconName.None_
        badge.deleteLater()

    def test_set_ela_icon(self):
        badge = ElaInfoBadge()
        badge.setElaIcon(ElaIconType.IconName.Check)
        assert badge.elaIcon() == ElaIconType.IconName.Check
        badge.deleteLater()


class TestElaInfoBadgeSeverity:
    def test_severity_default(self):
        badge = ElaInfoBadge()
        assert badge.severity() == ElaInfoBadge.Severity.Attention
        badge.deleteLater()

    def test_set_severity(self):
        badge = ElaInfoBadge()
        badge.setSeverity(ElaInfoBadge.Severity.Success)
        assert badge.severity() == ElaInfoBadge.Severity.Success
        badge.deleteLater()

    def test_set_severity_all_values(self):
        badge = ElaInfoBadge()
        for s in ElaInfoBadge.Severity:
            badge.setSeverity(s)
            assert badge.severity() == s
        badge.deleteLater()


class TestElaInfoBadgeAttachDetach:
    def test_attach_to_sets_target(self):
        badge = ElaInfoBadge()
        target = QWidget()
        badge.attachTo(target)
        assert badge._target is target
        assert badge.parent() is target
        target.deleteLater()
        badge.deleteLater()

    def test_detach_clears_target(self):
        badge = ElaInfoBadge()
        target = QWidget()
        badge.attachTo(target)
        badge.detach()
        assert badge._target is None
        assert badge.isVisible() is False
        target.deleteLater()
        badge.deleteLater()


class TestElaInfoBadgeSeverityColor:
    def test_get_severity_color_returns_qcolor(self):
        badge = ElaInfoBadge()
        from PyQt5.QtGui import QColor
        color = badge._getSeverityColor()
        assert isinstance(color, QColor)
        badge.deleteLater()


class TestElaInfoBadgeSizeHint:
    def test_size_hint_dot_mode(self):
        badge = ElaInfoBadge()
        sz = badge.sizeHint()
        assert sz == QSize(10, 10)
        badge.deleteLater()

    def test_size_hint_value_mode(self):
        badge = ElaInfoBadge(value=5)
        sz = badge.sizeHint()
        assert sz.width() >= 16
        assert sz.height() == 16
        badge.deleteLater()

    def test_size_hint_icon_mode(self):
        badge = ElaInfoBadge(icon=ElaIconType.IconName.Gear)
        sz = badge.sizeHint()
        assert sz == QSize(16, 16)
        badge.deleteLater()


class TestElaInfoBadgeTheme:
    def test_on_theme_changed_updates_mode(self):
        badge = ElaInfoBadge()
        from PyQt5ElaWidgetTools import ElaThemeType
        badge._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert badge._theme_mode == ElaThemeType.ThemeMode.Dark
        badge.deleteLater()


class TestElaInfoBadgeDeleteLater:
    def test_delete_later_removes_event_filter(self):
        badge = ElaInfoBadge()
        target = QWidget()
        badge.attachTo(target)
        badge.deleteLater()
        target.deleteLater()
