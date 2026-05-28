from __future__ import annotations

from PyQt5.QtGui import QColor

from pyqt5_ela_pro.ela_chip import ElaChip


class TestElaChipInit:
    def test_initialization_with_defaults(self):
        chip = ElaChip()
        assert chip._text == ""
        assert chip._border_radius == 4
        assert chip._is_closable is False
        assert chip._is_checkable is False
        assert chip._is_checked is False
        assert chip._chip_color == ElaChip.Color.Default
        chip.deleteLater()

    def test_initialization_with_text(self):
        chip = ElaChip(text="标签")
        assert chip.text() == "标签"
        chip.deleteLater()


class TestElaChipText:
    def test_set_text(self):
        chip = ElaChip()
        chip.setText("新标签")
        assert chip.text() == "新标签"
        chip.deleteLater()

    def test_set_text_empty(self):
        chip = ElaChip(text="旧标签")
        chip.setText("")
        assert chip.text() == ""
        chip.deleteLater()


class TestElaChipBorderRadius:
    def test_border_radius_default(self):
        chip = ElaChip()
        assert chip.borderRadius() == 4
        chip.deleteLater()

    def test_set_border_radius(self):
        chip = ElaChip()
        chip.setBorderRadius(12)
        assert chip.borderRadius() == 12
        chip.deleteLater()

    def test_set_border_radius_zero(self):
        chip = ElaChip()
        chip.setBorderRadius(0)
        assert chip.borderRadius() == 0
        chip.deleteLater()


class TestElaChipClosable:
    def test_closable_default_false(self):
        chip = ElaChip()
        assert chip.isClosable() is False
        chip.deleteLater()

    def test_set_closable(self):
        chip = ElaChip()
        chip.setClosable(True)
        assert chip.isClosable() is True
        chip.deleteLater()

    def test_set_closable_toggle(self):
        chip = ElaChip()
        chip.setClosable(True)
        chip.setClosable(False)
        assert chip.isClosable() is False
        chip.deleteLater()


class TestElaChipCheckable:
    def test_checkable_default_false(self):
        chip = ElaChip()
        assert chip.isCheckable() is False
        chip.deleteLater()

    def test_set_checkable(self):
        chip = ElaChip()
        chip.setCheckable(True)
        assert chip.isCheckable() is True
        chip.deleteLater()

    def test_checked_default_false(self):
        chip = ElaChip()
        assert chip.isChecked() is False
        chip.deleteLater()

    def test_set_checked(self):
        chip = ElaChip()
        chip.setChecked(True)
        assert chip.isChecked() is True
        chip.deleteLater()

    def test_set_checked_while_checkable(self):
        chip = ElaChip()
        chip.setCheckable(True)
        chip.setChecked(True)
        assert chip.isChecked() is True
        chip.deleteLater()


class TestElaChipColor:
    def test_color_default(self):
        chip = ElaChip()
        assert chip.color() == ElaChip.Color.Default
        chip.deleteLater()

    def test_set_color_primary(self):
        chip = ElaChip()
        chip.setColor(ElaChip.Color.Primary)
        assert chip.color() == ElaChip.Color.Primary
        chip.deleteLater()

    def test_set_color_all_values(self):
        chip = ElaChip()
        for c in ElaChip.Color:
            chip.setColor(c)
            assert chip.color() == c
        chip.deleteLater()


class TestElaChipSignals:
    def test_has_closed_signal(self):
        chip = ElaChip()
        assert hasattr(chip, "closed")
        assert callable(chip.closed)
        chip.deleteLater()

    def test_has_clicked_signal(self):
        chip = ElaChip()
        assert hasattr(chip, "clicked")
        chip.deleteLater()

    def test_has_checked_changed_signal(self):
        chip = ElaChip()
        assert hasattr(chip, "checkedChanged")
        chip.deleteLater()


class TestElaChipColorHelpers:
    def test_get_background_color_returns_qcolor(self):
        chip = ElaChip()
        bg = chip._getBackgroundColor()
        assert isinstance(bg, QColor)
        chip.deleteLater()

    def test_get_foreground_color_returns_qcolor(self):
        chip = ElaChip()
        fg = chip._getForegroundColor()
        assert isinstance(fg, QColor)
        chip.deleteLater()


class TestElaChipDeleteLater:
    def test_delete_later_cleans_up(self):
        chip = ElaChip()
        chip.deleteLater()
