"""``ElaChip`` 测试：初值 / 文本 / 圆角 / 关闭 / 选择 / 颜色 / 信号。"""

from __future__ import annotations

import pytest
from PyQt5.QtGui import QColor

from pyqt5_ela_pro.ela_chip import ElaChip


@pytest.fixture
def chip(make):
    return make(ElaChip)


class TestElaChipInit:
    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("_text", ""),
            ("_border_radius", 4),
            ("_is_closable", False),
            ("_is_checkable", False),
            ("_is_checked", False),
            ("_chip_color", ElaChip.Color.Default),
        ],
    )
    def test_initialization_with_defaults(self, chip, attr, expected):
        assert getattr(chip, attr) == expected

    def test_initialization_with_text(self, make):
        assert make(ElaChip, text="标签").text() == "标签"


class TestElaChipText:
    @pytest.mark.parametrize(
        ("initial", "new", "expected"),
        [("", "新标签", "新标签"), ("旧标签", "", "")],
        ids=["set-new", "clear"],
    )
    def test_set_text(self, make, initial, new, expected):
        chip = make(ElaChip, text=initial)
        chip.setText(new)
        assert chip.text() == expected


class TestElaChipBorderRadius:
    def test_border_radius_default(self, chip):
        assert chip.borderRadius() == 4

    @pytest.mark.parametrize("radius", [12, 0], ids=["12", "0"])
    def test_set_border_radius(self, chip, radius):
        chip.setBorderRadius(radius)
        assert chip.borderRadius() == radius


class TestElaChipClosable:
    def test_closable_default_false(self, chip):
        assert chip.isClosable() is False

    def test_set_closable(self, chip):
        chip.setClosable(True)
        assert chip.isClosable() is True

    def test_set_closable_toggle(self, chip):
        chip.setClosable(True)
        chip.setClosable(False)
        assert chip.isClosable() is False


class TestElaChipCheckable:
    def test_checkable_default_false(self, chip):
        assert chip.isCheckable() is False

    def test_set_checkable(self, chip):
        chip.setCheckable(True)
        assert chip.isCheckable() is True

    def test_checked_default_false(self, chip):
        assert chip.isChecked() is False

    def test_set_checked(self, chip):
        chip.setChecked(True)
        assert chip.isChecked() is True

    def test_set_checked_while_checkable(self, chip):
        chip.setCheckable(True)
        chip.setChecked(True)
        assert chip.isChecked() is True


class TestElaChipColor:
    def test_color_default(self, chip):
        assert chip.color() == ElaChip.Color.Default

    def test_set_color_primary(self, chip):
        chip.setColor(ElaChip.Color.Primary)
        assert chip.color() == ElaChip.Color.Primary

    def test_set_color_all_values(self, chip):
        for c in ElaChip.Color:
            chip.setColor(c)
            assert chip.color() == c


class TestElaChipSignals:
    @pytest.mark.parametrize("name", ["closed", "clicked", "checkedChanged"])
    def test_has_signal(self, chip, name):
        assert hasattr(chip, name)

    def test_closed_signal_is_callable(self, chip):
        assert callable(chip.closed)


class TestElaChipColorHelpers:
    @pytest.mark.parametrize(
        "getter",
        [ElaChip._getBackgroundColor, ElaChip._getForegroundColor],
        ids=["background", "foreground"],
    )
    def test_color_helper_returns_qcolor(self, chip, getter):
        assert isinstance(getter(chip), QColor)


class TestElaChipDeleteLater:
    def test_delete_later_cleans_up(self, chip):
        chip.deleteLater()
