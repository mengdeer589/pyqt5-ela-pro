from __future__ import annotations

import pytest
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro.ela_group_box import ElaGroupBox


class TestElaGroupBoxInit:
    def test_initialization_with_defaults(self):
        gb = ElaGroupBox()
        assert gb._title == ""
        assert gb._border_radius == 6
        assert gb._title_pixel_size == 14
        gb.deleteLater()

    def test_initialization_with_title(self):
        gb = ElaGroupBox(title="基本信息")
        assert gb.title() == "基本信息"
        gb.deleteLater()

    def test_initialization_with_custom_radius(self):
        gb = ElaGroupBox(border_radius=12)
        assert gb.borderRadius() == 12
        gb.deleteLater()


class TestElaGroupBoxTitle:
    def test_set_title(self):
        gb = ElaGroupBox()
        gb.setTitle("高级设置")
        assert gb.title() == "高级设置"
        gb.deleteLater()

    def test_set_title_empty(self):
        gb = ElaGroupBox(title="旧标题")
        gb.setTitle("")
        assert gb.title() == ""
        gb.deleteLater()


class TestElaGroupBoxBorderRadius:
    def test_border_radius_default(self):
        gb = ElaGroupBox()
        assert gb.borderRadius() == 6
        gb.deleteLater()

    def test_set_border_radius(self):
        gb = ElaGroupBox()
        gb.setBorderRadius(16)
        assert gb.borderRadius() == 16
        gb.deleteLater()


class TestElaGroupBoxSizeHint:
    def test_size_hint(self):
        gb = ElaGroupBox()
        sz = gb.sizeHint()
        assert sz.width() == 160
        assert sz.height() > 0
        gb.deleteLater()


class TestElaGroupBoxTheme:
    def test_on_theme_changed_updates_mode(self):
        gb = ElaGroupBox()
        from PyQt5ElaWidgetTools import ElaThemeType
        gb._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert gb._theme_mode == ElaThemeType.ThemeMode.Dark
        gb.deleteLater()


class TestElaGroupBoxDeleteLater:
    def test_delete_later_cleans_up(self):
        gb = ElaGroupBox()
        gb.deleteLater()
