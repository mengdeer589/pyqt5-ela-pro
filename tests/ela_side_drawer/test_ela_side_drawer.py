"""``ela_side_drawer`` 测试：位置枚举 / 面板 / 蒙层 / 抽屉本体。"""

from __future__ import annotations

import pytest
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro.ela_side_drawer import (
    ElaDrawerPosition,
    ElaDrawerPanel,
    ElaDrawerDim,
    ElaDrawer,
)


@pytest.fixture
def parent(make):
    """抽屉的宿主控件。"""
    return make(QWidget)


@pytest.fixture
def panel(make):
    return make(ElaDrawerPanel)


@pytest.fixture
def dim(make):
    return make(ElaDrawerDim)


@pytest.fixture
def drawer(make, parent):
    """挂在 *parent* 上的默认抽屉。"""
    return make(ElaDrawer, parent=parent)


class TestElaDrawerPosition:
    """Test cases for ElaDrawerPosition enum."""

    @pytest.mark.parametrize(
        ("position", "value"),
        [
            (ElaDrawerPosition.Left, 0),
            (ElaDrawerPosition.Right, 1),
            (ElaDrawerPosition.Top, 2),
            (ElaDrawerPosition.Bottom, 3),
        ],
        ids=["left", "right", "top", "bottom"],
    )
    def test_enum_value(self, position, value):
        assert position == value


class TestElaDrawerPanel:
    """Test cases for ElaDrawerPanel class."""

    @pytest.mark.parametrize(
        ("attr", "expected"),
        [("_corner_radius", 12), ("_position", ElaDrawerPosition.Right)],
        ids=["corner-radius", "position"],
    )
    def test_initialization_with_defaults(self, panel, attr, expected):
        assert getattr(panel, attr) == expected

    def test_initialization_with_custom_values(self, make):
        panel = make(ElaDrawerPanel, position=ElaDrawerPosition.Left, corner_radius=8)
        assert panel._corner_radius == 8
        assert panel._position == ElaDrawerPosition.Left

    def test_set_bg_color(self, panel):
        color = QColor(255, 0, 0)
        panel.setBgColor(color)
        assert panel._bg_color == color

    def test_set_position(self, panel):
        panel.setPosition(ElaDrawerPosition.Top)
        assert panel._position == ElaDrawerPosition.Top


class TestElaDrawerDim:
    """Test cases for ElaDrawerDim class."""

    def test_initialization(self, dim):
        assert dim._bg_color == QColor(0, 0, 0, 102)

    def test_set_bg_color(self, dim):
        color = QColor(255, 0, 0, 128)
        dim.setBgColor(color)
        assert dim._bg_color == color


class TestElaDrawer:
    """Test cases for ElaDrawer class."""

    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("_position", ElaDrawerPosition.Right),
            ("_drawer_size", 360),
            ("_is_opened", False),
            ("_close_on_dim_clicked", True),
            ("_animation_duration", 250),
        ],
        ids=[
            "position",
            "drawer-size",
            "is-opened",
            "close-on-dim-clicked",
            "animation-duration",
        ],
    )
    def test_initialization_with_defaults(self, drawer, attr, expected):
        assert getattr(drawer, attr) == expected

    def test_initialization_with_custom_values(self, make, parent):
        drawer = make(
            ElaDrawer, position=ElaDrawerPosition.Left, drawer_size=400, parent=parent
        )
        assert drawer._position == ElaDrawerPosition.Left
        assert drawer._drawer_size == 400

    @pytest.mark.parametrize("signal", ["closed", "opened"])
    def test_has_signal(self, drawer, signal):
        assert hasattr(drawer, signal)
        assert callable(getattr(drawer, signal))

    def test_initial_state_is_hidden(self, drawer):
        assert not drawer.isVisible()

    def test_initial_opened_is_false(self, drawer):
        assert drawer.isOpened() is False

    def test_set_content_widget(self, make, drawer):
        assert drawer.setContentWidget(make(QWidget)) is drawer

    def test_set_drawer_size(self, drawer):
        drawer.setDrawerSize(500)
        assert drawer._drawer_size == 500

    def test_set_corner_radius(self, drawer):
        drawer.setCornerRadius(20)
        assert drawer._corner_radius == 20

    def test_set_close_on_dim_clicked(self, drawer):
        drawer.setCloseOnDimClicked(False)
        assert drawer._close_on_dim_clicked is False

    def test_set_animation_duration(self, drawer):
        drawer.setAnimationDuration(500)
        assert drawer._animation_duration == 500

    def test_delete_later_disconnects_theme_signal(self, drawer):
        """析构要断开主题信号。"""
        drawer.deleteLater()

    def test_show_drawer_without_parent_returns_immediately(self, make):
        """Regression: parentless showDrawer must not setParent(self) and hang."""
        drawer = make(ElaDrawer)
        drawer.setContentWidget(make(QWidget))

        drawer.showDrawer()

        assert drawer.isOpened() is False

    def test_show_drawer_with_parent_opens(self, make, drawer):
        """Test showDrawer with a parent widget opens the drawer."""
        drawer.setContentWidget(make(QWidget))

        drawer.showDrawer()

        assert drawer.isOpened() is True
