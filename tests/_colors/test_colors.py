from __future__ import annotations

import pytest
from PyQt5.QtGui import QColor
from PyQt5ElaWidgetTools import ElaThemeType

from pyqt5_ela_pro._colors import (
    resolve_color,
    get_color_scheme,
    get_accent_color,
    _COLOR_PALETTE,
    _COLOR_ALIAS,
)


class TestColorsPalette:
    def test_palette_has_all_colors(self):
        expected = {
            "blue", "danger", "purple", "cyan", "green", "magenta",
            "red", "orange", "yellow", "volcano", "geekblue", "lime", "gold",
        }
        assert set(_COLOR_PALETTE.keys()) == expected

    def test_each_color_has_light_and_dark(self):
        for name, schemes in _COLOR_PALETTE.items():
            assert "light" in schemes, f"{name} missing light"
            assert "dark" in schemes, f"{name} missing dark"

    def test_each_scheme_has_required_keys(self):
        required = {"accent", "accentHover", "accentActive", "accentBg", "accentBgHover", "textColor"}
        for cname, schemes in _COLOR_PALETTE.items():
            for mode in ("light", "dark"):
                keys = set(schemes[mode].keys())
                assert keys == required, f"{cname}/{mode} missing {required - keys}"

    def test_all_hex_colors_are_valid(self):
        import re
        for cname, schemes in _COLOR_PALETTE.items():
            for mode in ("light", "dark"):
                for key, val in schemes[mode].items():
                    assert re.match(r"^#[0-9a-fA-F]{6}$", val), f"{cname}/{mode}/{key}: {val}"

    def test_each_color_palette_value_parsable_as_qcolor(self):
        for cname, schemes in _COLOR_PALETTE.items():
            for mode in ("light", "dark"):
                for key, val in schemes[mode].items():
                    color = QColor(val)
                    assert color.isValid(), f"{cname}/{mode}/{key}: {val}"


class TestColorsAlias:
    def test_alias_has_expected_mappings(self):
        assert _COLOR_ALIAS == {"default": "blue", "primary": "blue", "pink": "magenta"}

    def test_resolve_color_returns_alias(self):
        assert resolve_color("default") == "blue"
        assert resolve_color("primary") == "blue"
        assert resolve_color("pink") == "magenta"

    def test_resolve_color_returns_self_for_unknown(self):
        assert resolve_color("nonexistent") == "nonexistent"

    def test_resolve_color_returns_self_for_direct_name(self):
        assert resolve_color("blue") == "blue"
        assert resolve_color("danger") == "danger"


class TestColorsGetColorScheme:
    def test_get_color_scheme_returns_dict_of_qcolors(self):
        scheme = get_color_scheme("blue", ElaThemeType.ThemeMode.Light)
        assert isinstance(scheme, dict)
        for k, v in scheme.items():
            assert isinstance(v, QColor), f"{k} is not QColor"

    def test_get_color_scheme_has_6_keys(self):
        scheme = get_color_scheme("primary", ElaThemeType.ThemeMode.Light)
        assert len(scheme) == 6

    def test_get_color_scheme_light_vs_dark_differ(self):
        light = get_color_scheme("blue", ElaThemeType.ThemeMode.Light)
        dark = get_color_scheme("blue", ElaThemeType.ThemeMode.Dark)
        assert light["accent"].name() != dark["accent"].name()

    def test_get_color_scheme_resolves_alias(self):
        direct = get_color_scheme("blue", ElaThemeType.ThemeMode.Light)
        aliased = get_color_scheme("primary", ElaThemeType.ThemeMode.Light)
        assert direct["accent"].name() == aliased["accent"].name()

    def test_get_color_scheme_unknown_raises_keyerror(self):
        with pytest.raises(KeyError):
            get_color_scheme("nonexistent", ElaThemeType.ThemeMode.Light)


class TestColorsGetAccentColor:
    def test_get_accent_color_returns_qcolor(self):
        color = get_accent_color("blue", ElaThemeType.ThemeMode.Light)
        assert isinstance(color, QColor)

    def test_get_accent_color_light_value(self):
        color = get_accent_color("blue", ElaThemeType.ThemeMode.Light)
        assert color.name() == "#1677ff"

    def test_get_accent_color_dark_value(self):
        color = get_accent_color("blue", ElaThemeType.ThemeMode.Dark)
        assert color.name() == "#1668dc"

    def test_get_accent_color_resolves_alias(self):
        direct = get_accent_color("blue", ElaThemeType.ThemeMode.Light)
        aliased = get_accent_color("primary", ElaThemeType.ThemeMode.Light)
        assert direct.name() == aliased.name()

    def test_get_accent_color_unknown_raises_keyerror(self):
        with pytest.raises(KeyError):
            get_accent_color("nonexistent", ElaThemeType.ThemeMode.Light)
