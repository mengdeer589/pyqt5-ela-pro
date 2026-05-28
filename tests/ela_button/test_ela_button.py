from __future__ import annotations


from pyqt5_ela_pro.ela_button import ElaButton


class TestElaButtonInit:
    def test_initialization_with_defaults(self):
        btn = ElaButton()
        assert btn._variant == "outlined"
        assert btn._color_name == "default"
        assert btn._danger is False
        assert btn._border_radius == 3
        assert btn._icon_name is None
        assert btn._hovered is False
        assert btn.text() == ""
        btn.deleteLater()

    def test_initialization_with_text(self):
        btn = ElaButton(text="提交")
        assert btn.text() == "提交"
        btn.deleteLater()

    def test_initialization_with_icon(self):
        from PyQt5ElaWidgetTools import ElaIconType
        btn = ElaButton(icon=ElaIconType.IconName.House)
        assert btn._icon_name == ElaIconType.IconName.House
        btn.deleteLater()

    def test_initialization_with_all_params(self):
        btn = ElaButton(
            text="删除", variant="solid", color="danger",
            danger=True, size="small", parent=None,
        )
        assert btn._variant == "solid"
        assert btn._color_name == "danger"
        assert btn._danger is True
        assert btn._border_radius == 3
        btn.deleteLater()

    def test_initial_sizes_vary_by_size_param(self):
        small = ElaButton(size="small")
        middle = ElaButton(size="middle")
        large = ElaButton(size="large")
        assert small.height() < middle.height() < large.height()
        small.deleteLater()
        middle.deleteLater()
        large.deleteLater()


class TestElaButtonVariant:
    def test_set_variant(self):
        btn = ElaButton()
        btn.setVariant("solid")
        assert btn.variant() == "solid"
        btn.deleteLater()

    def test_set_variant_dashed(self):
        btn = ElaButton()
        btn.setVariant("dashed")
        assert btn.variant() == "dashed"
        btn.deleteLater()

    def test_set_variant_filled(self):
        btn = ElaButton()
        btn.setVariant("filled")
        assert btn.variant() == "filled"
        btn.deleteLater()

    def test_set_variant_text(self):
        btn = ElaButton()
        btn.setVariant("text")
        assert btn.variant() == "text"
        btn.deleteLater()

    def test_set_variant_link(self):
        btn = ElaButton()
        btn.setVariant("link")
        assert btn.variant() == "link"
        btn.deleteLater()


class TestElaButtonColor:
    def test_set_color(self):
        btn = ElaButton()
        btn.setColor("primary")
        assert btn.color() == "primary"
        btn.deleteLater()

    def test_set_color_primary(self):
        btn = ElaButton()
        btn.setColor("primary")
        assert btn._color_name == "primary"
        btn.deleteLater()

    def test_set_color_all_16(self):
        btn = ElaButton()
        for c in ["default", "primary", "danger", "blue", "purple", "cyan",
                   "green", "magenta", "pink", "red", "orange", "yellow",
                   "volcano", "geekblue", "lime", "gold"]:
            btn.setColor(c)
            assert btn.color() == c
        btn.deleteLater()


class TestElaButtonDanger:
    def test_danger_default_false(self):
        btn = ElaButton()
        assert btn.isDanger() is False
        btn.deleteLater()

    def test_set_danger(self):
        btn = ElaButton()
        btn.setDanger(True)
        assert btn.isDanger() is True
        btn.deleteLater()

    def test_danger_overrides_color(self):
        btn = ElaButton(color="primary")
        btn.setDanger(True)
        assert btn._effective_color() == "danger"
        btn.deleteLater()

    def test_danger_false_keeps_color(self):
        btn = ElaButton(color="primary")
        assert btn._effective_color() == "primary"
        btn.deleteLater()


class TestElaButtonSize:
    def test_set_button_size_small(self):
        btn = ElaButton()
        btn.setButtonSize("small")
        assert btn.height() == 28
        btn.deleteLater()

    def test_set_button_size_middle(self):
        btn = ElaButton()
        btn.setButtonSize("middle")
        assert btn.height() == 38
        btn.deleteLater()

    def test_set_button_size_large(self):
        btn = ElaButton()
        btn.setButtonSize("large")
        assert btn.height() == 46
        btn.deleteLater()

    def test_button_size_returns_name(self):
        btn = ElaButton()
        btn.setButtonSize("small")
        assert btn.buttonSize() == "small"
        btn.deleteLater()


class TestElaButtonBorderRadius:
    def test_border_radius_default(self):
        btn = ElaButton()
        assert btn.borderRadius() == 3
        btn.deleteLater()

    def test_set_border_radius(self):
        btn = ElaButton()
        btn.setBorderRadius(12)
        assert btn.borderRadius() == 12
        btn.deleteLater()

    def test_set_border_radius_zero(self):
        btn = ElaButton()
        btn.setBorderRadius(0)
        assert btn.borderRadius() == 0
        btn.deleteLater()

    def test_set_border_radius_large(self):
        btn = ElaButton()
        btn.setBorderRadius(50)
        assert btn.borderRadius() == 50
        btn.deleteLater()


class TestElaButtonIcon:
    def test_set_ela_icon(self):
        from PyQt5ElaWidgetTools import ElaIconType
        btn = ElaButton()
        btn.setElaIcon(ElaIconType.IconName.Pencil)
        assert btn._icon_name == ElaIconType.IconName.Pencil
        btn.deleteLater()

    def test_set_icon_updates_icon_size(self):
        from PyQt5ElaWidgetTools import ElaIconType
        btn = ElaButton()
        btn.setElaIcon(ElaIconType.IconName.House, iconSize=20)
        assert btn._icon_size == 20
        btn.deleteLater()


class TestElaButtonDisabled:
    def test_disabled_by_default(self):
        btn = ElaButton()
        assert btn.isEnabled() is True
        btn.deleteLater()

    def test_set_disabled(self):
        btn = ElaButton()
        btn.setEnabled(False)
        assert btn.isEnabled() is False
        btn.deleteLater()


class TestElaButtonTheme:
    def test_effective_color_danger(self):
        btn = ElaButton(danger=True)
        assert btn._effective_color() == "danger"
        btn.deleteLater()

    def test_effective_color_normal(self):
        btn = ElaButton(color="primary")
        assert btn._effective_color() == "primary"
        btn.deleteLater()

    def test_on_theme_changed_updates_mode(self):
        btn = ElaButton()
        from PyQt5ElaWidgetTools import ElaThemeType
        btn._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert btn._theme_mode == ElaThemeType.ThemeMode.Dark
        btn.deleteLater()


class TestElaButtonDeleteLater:
    def test_delete_later_cleans_up(self):
        btn = ElaButton()
        btn.deleteLater()
