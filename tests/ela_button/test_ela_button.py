"""``ElaButton`` 测试：初值 / 变体 / 配色 / 尺寸 / 图标 / 禁用 / 主题。"""

from __future__ import annotations

import pytest
from PyQt5ElaWidgetTools import ElaIconType, ElaThemeType

from pyqt5_ela_pro.ela_button import ElaButton

VARIANTS = ["solid", "dashed", "filled", "text", "link"]

COLORS = [
    "default",
    "primary",
    "danger",
    "blue",
    "purple",
    "cyan",
    "green",
    "magenta",
    "pink",
    "red",
    "orange",
    "yellow",
    "volcano",
    "geekblue",
    "lime",
    "gold",
]

# size -> (height, borderRadius)
SIZES = {"small": (28, 4), "middle": (38, 6), "large": (46, 8)}


@pytest.fixture
def btn(make):
    return make(ElaButton)


class TestElaButtonInit:
    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("_variant", "outlined"),
            ("_color_name", "default"),
            ("_danger", False),
            ("_border_radius", 6),
            ("_icon_name", None),
            ("_hovered", False),
        ],
    )
    def test_initialization_with_defaults(self, btn, attr, expected):
        assert getattr(btn, attr) == expected

    def test_default_text_empty(self, btn):
        assert btn.text() == ""

    def test_initialization_with_text(self, make):
        assert make(ElaButton, text="提交").text() == "提交"

    def test_initialization_with_icon(self, make):
        b = make(ElaButton, icon=ElaIconType.IconName.House)
        assert b._icon_name == ElaIconType.IconName.House

    def test_initialization_with_all_params(self, make):
        b = make(
            ElaButton,
            text="删除",
            variant="solid",
            color="danger",
            danger=True,
            size="small",
            parent=None,
        )
        assert b._variant == "solid"
        assert b._color_name == "danger"
        assert b._danger is True
        assert b._border_radius == 4

    def test_initial_sizes_increase(self, make):
        heights = [
            make(ElaButton, size=name).height() for name in ("small", "middle", "large")
        ]
        assert heights[0] < heights[1] < heights[2]


class TestElaButtonVariant:
    @pytest.mark.parametrize("variant", VARIANTS)
    def test_set_variant_roundtrip(self, btn, variant):
        btn.setVariant(variant)
        assert btn.variant() == variant

    def test_default_variant(self, btn):
        assert btn.variant() == "outlined"


class TestElaButtonColor:
    @pytest.mark.parametrize("color", COLORS)
    def test_set_color_roundtrip(self, btn, color):
        btn.setColor(color)
        assert btn.color() == color
        assert btn._color_name == color

    def test_default_color(self, btn):
        assert btn.color() == "default"


class TestElaButtonDanger:
    def test_danger_default_false(self, btn):
        assert btn.isDanger() is False

    def test_set_danger(self, btn):
        btn.setDanger(True)
        assert btn.isDanger() is True

    @pytest.mark.parametrize(
        ("kwargs", "danger", "expected"),
        [
            ({}, True, "danger"),  # 构造参数
            ({"color": "primary"}, True, "danger"),  # danger 覆盖 color
            ({"color": "primary"}, False, "primary"),  # 未开 danger 时保留 color
        ],
        ids=["ctor-danger", "danger-overrides", "keeps-color"],
    )
    def test_effective_color(self, make, kwargs, danger, expected):
        b = make(ElaButton, **kwargs)
        b.setDanger(danger)
        assert b._effective_color() == expected


class TestElaButtonSize:
    @pytest.mark.parametrize(("name", "expected"), SIZES.items())
    def test_set_button_size(self, make, name, expected):
        b = make(ElaButton)
        b.setButtonSize(name)
        assert b.height() == expected[0]
        assert b.buttonSize() == name

    def test_size_variant_does_not_affect_set_border_radius(self, btn):
        btn.setButtonSize("small")
        btn.setBorderRadius(12)
        assert btn.borderRadius() == 12


class TestElaButtonBorderRadius:
    @pytest.mark.parametrize("radius", [0, 12, 50])
    def test_set_border_radius(self, btn, radius):
        btn.setBorderRadius(radius)
        assert btn.borderRadius() == radius

    def test_border_radius_default(self, btn):
        assert btn.borderRadius() == 6

    def test_border_radius_varies_by_size(self, make):
        radii = tuple(
            make(ElaButton, size=name).borderRadius()
            for name in ("small", "middle", "large")
        )
        assert radii == (4, 6, 8)


class TestElaButtonIcon:
    def test_set_ela_icon(self, btn):
        btn.setElaIcon(ElaIconType.IconName.Pencil)
        assert btn._icon_name == ElaIconType.IconName.Pencil

    def test_set_icon_updates_icon_size(self, btn):
        btn.setElaIcon(ElaIconType.IconName.House, iconSize=20)
        assert btn._icon_size == 20

    def test_icon_only_button_icon_centered(self, make, qapp):
        """纯图标按钮：图标绘制在按钮正中（回归：曾保留文字间距导致左偏）。"""
        b = make(
            ElaButton,
            icon=ElaIconType.IconName.ArrowUp,
            iconSize=16,
            variant="solid",
            color="primary",
        )
        b.setFixedSize(28, 28)
        b.show()
        qapp.processEvents()
        image = b.grab().toImage()

        xs, ys = [], []
        for y in range(image.height()):
            for x in range(image.width()):
                color = image.pixelColor(x, y)
                if color.red() > 200 and color.green() > 200 and color.blue() > 200:
                    xs.append(x)
                    ys.append(y)
        assert xs, "未找到图标像素"
        center_x = (min(xs) + max(xs) + 1) / 2
        center_y = (min(ys) + max(ys) + 1) / 2
        assert abs(center_x - image.width() / 2) <= 2.0
        assert abs(center_y - image.height() / 2) <= 2.0
        b.close()

    def test_icon_with_text_keeps_spacing(self, make):
        """图标 + 文字：宽度包含间距（纯图标时不加间距）。"""
        icon = make(ElaButton, icon=ElaIconType.IconName.House, size="middle")
        icon.setFixedHeight(28)
        with_text = make(
            ElaButton, text="首页", icon=ElaIconType.IconName.House, size="middle"
        )
        with_text.setFixedHeight(28)
        assert with_text.sizeHint().width() > icon.sizeHint().width()


class TestElaButtonDisabled:
    def test_enabled_by_default(self, btn):
        assert btn.isEnabled() is True

    def test_set_disabled(self, btn):
        btn.setEnabled(False)
        assert btn.isEnabled() is False


class TestElaButtonTheme:
    def test_on_theme_changed_updates_mode(self, btn):
        btn._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert btn._theme_mode == ElaThemeType.ThemeMode.Dark


class TestElaButtonDeleteLater:
    def test_delete_later_cleans_up(self, btn):
        btn.deleteLater()
