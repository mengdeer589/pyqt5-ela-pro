from __future__ import annotations

import pytest
from PyQt5.QtCore import Qt

from pyqt5_ela_pro.ela_divider import ElaDivider


class TestElaDividerInit:
    def test_initialization_with_defaults(self):
        d = ElaDivider()
        assert d._text == ""
        assert d._orientation == "center"
        assert d._variant == "solid"
        assert d._vertical is False
        d.deleteLater()

    def test_initialization_with_text(self):
        d = ElaDivider(text="OR")
        assert d.text() == "OR"
        d.deleteLater()

    def test_initialization_with_orientation_left(self):
        d = ElaDivider(orientation="left")
        assert d.orientation() == "left"
        d.deleteLater()

    def test_initialization_with_orientation_right(self):
        d = ElaDivider(orientation="right")
        assert d.orientation() == "right"
        d.deleteLater()

    def test_initialization_with_variant_dashed(self):
        d = ElaDivider(variant="dashed")
        assert d.variant() == "dashed"
        d.deleteLater()

    def test_initialization_with_vertical(self):
        d = ElaDivider(vertical=True)
        assert d.isVertical() is True
        d.deleteLater()

    def test_initialization_with_all_params(self):
        d = ElaDivider(text="分隔", orientation="left", variant="dashed", vertical=False)
        assert d.text() == "分隔"
        assert d.orientation() == "left"
        assert d.variant() == "dashed"
        assert d.isVertical() is False
        d.deleteLater()


class TestElaDividerText:
    def test_set_text(self):
        d = ElaDivider()
        d.setText("新文字")
        assert d.text() == "新文字"
        d.deleteLater()

    def test_set_text_empty(self):
        d = ElaDivider(text="旧文字")
        d.setText("")
        assert d.text() == ""
        d.deleteLater()


class TestElaDividerOrientation:
    def test_set_orientation_left(self):
        d = ElaDivider()
        d.setOrientation("left")
        assert d.orientation() == "left"
        d.deleteLater()

    def test_set_orientation_center(self):
        d = ElaDivider()
        d.setOrientation("center")
        assert d.orientation() == "center"
        d.deleteLater()

    def test_set_orientation_right(self):
        d = ElaDivider()
        d.setOrientation("right")
        assert d.orientation() == "right"
        d.deleteLater()

    def test_set_orientation_top(self):
        d = ElaDivider(vertical=True)
        d.setOrientation("top")
        assert d.orientation() == "top"
        d.deleteLater()

    def test_set_orientation_bottom(self):
        d = ElaDivider(vertical=True)
        d.setOrientation("bottom")
        assert d.orientation() == "bottom"
        d.deleteLater()


class TestElaDividerVariant:
    def test_set_variant_solid(self):
        d = ElaDivider()
        d.setVariant("solid")
        assert d.variant() == "solid"
        d.deleteLater()

    def test_set_variant_dashed(self):
        d = ElaDivider()
        d.setVariant("dashed")
        assert d.variant() == "dashed"
        d.deleteLater()


class TestElaDividerVertical:
    def test_set_vertical_true(self):
        d = ElaDivider()
        d.setVertical(True)
        assert d.isVertical() is True
        d.deleteLater()

    def test_set_vertical_false(self):
        d = ElaDivider(vertical=True)
        d.setVertical(False)
        assert d.isVertical() is False
        d.deleteLater()


class TestElaDividerDeleteLater:
    def test_delete_later_cleans_up(self):
        d = ElaDivider()
        d.deleteLater()
