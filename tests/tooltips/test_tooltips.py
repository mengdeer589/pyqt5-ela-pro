"""Tests for tooltips module: ElaToolTip, ElaStateToolTip, set_tooltip, remove_tooltip."""

from __future__ import annotations

from PyQt5.QtCore import QEvent, QObject, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QHelpEvent, QPalette
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5ElaWidgetTools import ElaThemeType, eTheme

import pyqt5_ela_pro.tooltips as tooltips_module
from pyqt5_ela_pro.tooltips import (
    TOOLTIP_BORDER_RADIUS,
    ElaStateToolTip,
    ElaToolTip,
    ElaToolTipPosition,
    _filter_dict,
    _tooltip_dict,
    remove_tooltip,
    set_tooltip,
)


class TestToolTip:
    """Test cases for ElaToolTip class."""

    def test_tooltip_initialization(self):
        """Test ElaToolTip initializes with text."""
        tooltip = ElaToolTip("Test tooltip")

        assert tooltip._text == "Test tooltip"

        tooltip.deleteLater()

    def test_tooltip_has_frameless_window_flag(self):
        """Test ElaToolTip uses frameless window."""
        tooltip = ElaToolTip()

        flags = tooltip.windowFlags()
        assert flags & Qt.FramelessWindowHint

        tooltip.deleteLater()

    def test_tooltip_has_tool_window_flag(self):
        """Test ElaToolTip uses Tool window type."""
        tooltip = ElaToolTip()

        flags = tooltip.windowFlags()
        assert flags & Qt.Tool

        tooltip.deleteLater()

    def test_tooltip_has_stays_on_top_flag(self):
        """Test ElaToolTip stays on top of other windows."""
        tooltip = ElaToolTip()

        flags = tooltip.windowFlags()
        assert flags & Qt.WindowStaysOnTopHint

        tooltip.deleteLater()

    def test_tooltip_set_text(self):
        """Test setText updates tooltip text."""
        tooltip = ElaToolTip()
        tooltip.setText("New text")

        assert tooltip._text == "New text"
        assert tooltip._label.text() == "New text"

        tooltip.deleteLater()

    def test_tooltip_has_translucent_background(self):
        """Test ElaToolTip has translucent background."""
        tooltip = ElaToolTip()

        assert tooltip.testAttribute(Qt.WA_TranslucentBackground)

        tooltip.deleteLater()

    def test_tooltip_border_radius_constant(self):
        """Test TOOLTIP_BORDER_RADIUS is 8."""
        assert TOOLTIP_BORDER_RADIUS == 8


class TestElaToolTipPosition:
    """Test cases for ElaToolTipPosition enum."""

    def test_ela_tool_tip_position_has_top(self):
        """Test ElaToolTipPosition.Top exists."""
        assert ElaToolTipPosition.Top is not None

    def test_ela_tool_tip_position_has_bottom(self):
        """Test ElaToolTipPosition.Bottom exists."""
        assert ElaToolTipPosition.Bottom is not None

    def test_ela_tool_tip_position_has_left(self):
        """Test ElaToolTipPosition.Left exists."""
        assert ElaToolTipPosition.Left is not None

    def test_ela_tool_tip_position_has_right(self):
        """Test ElaToolTipPosition.Right exists."""
        assert ElaToolTipPosition.Right is not None

    def test_ela_tool_tip_position_has_all_8_positions(self):
        """Test all 8 positions exist."""
        assert len(ElaToolTipPosition) == 8

        positions = [
            ElaToolTipPosition.Top,
            ElaToolTipPosition.Bottom,
            ElaToolTipPosition.Left,
            ElaToolTipPosition.Right,
            ElaToolTipPosition.TopLeft,
            ElaToolTipPosition.TopRight,
            ElaToolTipPosition.BottomLeft,
            ElaToolTipPosition.BottomRight,
        ]

        for pos in positions:
            assert pos is not None


class TestSetTooltip:
    """Test cases for set_tooltip function."""

    def test_set_tooltip_accepts_widget_and_text(self, qapp):
        """Test set_tooltip accepts widget and text parameters."""
        widget = QWidget()

        set_tooltip(widget, "Test tooltip")

        widget.deleteLater()
        qapp.processEvents()

    def test_set_tooltip_accepts_position_parameter(self, qapp):
        """Test set_tooltip accepts position parameter."""
        widget = QWidget()

        set_tooltip(widget, "Test", position=ElaToolTipPosition.Top)

        widget.deleteLater()
        qapp.processEvents()

    def test_set_tooltip_does_not_crash_on_widget_destroyed(self, qapp):
        """Test tooltip cleanup does not crash when widget is destroyed."""
        widget = QWidget()
        set_tooltip(widget, "No crash test")

        # deleteLater + defer should not raise
        widget.deleteLater()
        qapp.processEvents()

    def test_remove_tooltip_cleans_up_entries(self, qapp):
        """Test remove_tooltip cleans up global dict entries."""

        widget = QWidget()
        set_tooltip(widget, "Cleanup test")

        assert widget in _tooltip_dict
        assert widget in _filter_dict

        remove_tooltip(widget)

        assert widget not in _tooltip_dict
        assert widget not in _filter_dict

        widget.deleteLater()

    def test_custom_tooltip_suppresses_native_tooltip(self, qapp):
        """绑定自定义提示后吞掉 QEvent.ToolTip，避免原生 QToolTip 双提示。"""

        widget = QWidget()
        widget.setToolTip("提示")
        set_tooltip(widget, "提示")
        tooltip = _filter_dict[widget]

        enter = QHelpEvent(QEvent.Type.ToolTip, QPoint(1, 1), QPoint(10, 10))
        assert tooltip.eventFilter(widget, enter) is True

        remove_tooltip(widget)
        widget.deleteLater()


class TestRemoveTooltip:
    """Test cases for remove_tooltip function."""

    def test_remove_tooltip_accepts_widget(self, qapp):
        """Test remove_tooltip accepts widget parameter."""
        widget = QWidget()

        remove_tooltip(widget)

        widget.deleteLater()
        qapp.processEvents()

    def test_remove_tooltip_does_not_raise_on_unregistered_widget(self, qapp):
        """Test remove_tooltip doesn't raise on widget without tooltip."""
        widget = QWidget()

        remove_tooltip(widget)

        widget.deleteLater()
        qapp.processEvents()


class TestToolTipClamp:
    """提示框越界收敛 / 翻转测试。"""

    def _child(self, qapp):
        parent = QWidget()
        parent.setWindowFlags(Qt.Window)
        parent.setGeometry(320, 240, 260, 200)
        parent.show()
        child = QWidget(parent)
        child.setGeometry(20, 20, 60, 24)
        qapp.processEvents()
        return parent, child

    def test_show_at_keeps_inside_screen(self, qapp):

        area = QApplication.primaryScreen().availableGeometry()
        parent, child = self._child(qapp)
        for position in (
            ElaToolTipPosition.Top,
            ElaToolTipPosition.Bottom,
            ElaToolTipPosition.Left,
            ElaToolTipPosition.Right,
        ):
            tooltip = ElaToolTip("提示")
            tooltip.showAt(child, position)
            assert area.contains(tooltip.frameGeometry())
            tooltip.hide()
            tooltip.deleteLater()
        parent.close()
        parent.deleteLater()
        qapp.processEvents()

    def test_flip_below_when_no_room_above(self, qapp):

        area = QApplication.primaryScreen().availableGeometry()
        parent, child = self._child(qapp)
        tooltip = ElaToolTip("提示")
        y = area.top() - 50
        _, clamped = tooltip._clamp_to_screen(area.left() + 100, y, child, above=True)
        assert clamped >= area.top()
        assert clamped >= child.mapToGlobal(QPoint(0, 0)).y()
        tooltip.deleteLater()
        parent.close()
        parent.deleteLater()
        qapp.processEvents()

    def test_flip_above_when_no_room_below(self, qapp):

        area = QApplication.primaryScreen().availableGeometry()
        parent, child = self._child(qapp)
        tooltip = ElaToolTip("提示")
        y = area.bottom() - 5
        _, clamped = tooltip._clamp_to_screen(area.left() + 100, y, child, above=False)
        assert clamped <= area.bottom() - tooltip.height() + 1
        assert clamped + tooltip.height() <= child.mapToGlobal(QPoint(0, 0)).y() + 1
        tooltip.deleteLater()
        parent.close()
        parent.deleteLater()
        qapp.processEvents()

    def test_horizontal_clamped_to_right_edge(self, qapp):

        area = QApplication.primaryScreen().availableGeometry()
        parent, child = self._child(qapp)
        tooltip = ElaToolTip("提示")
        x, _ = tooltip._clamp_to_screen(
            area.right() + 200, area.top() + 50, child, above=False
        )
        assert x + tooltip.width() <= area.right() + 1
        assert x >= area.left()
        tooltip.deleteLater()
        parent.close()
        parent.deleteLater()
        qapp.processEvents()


class TestToolTipTheme:
    """提示框文字颜色跟随主题（深色背景下必须变亮）。"""

    def test_label_text_color_follows_theme(self, qapp):

        light = eTheme.getThemeColor(
            ElaThemeType.ThemeMode.Light, ElaThemeType.ThemeColor.BasicText
        ).name()
        dark = eTheme.getThemeColor(
            ElaThemeType.ThemeMode.Dark, ElaThemeType.ThemeColor.BasicText
        ).name()
        assert light != dark

        tooltip = ElaToolTip("提示")
        tooltip._onThemeChanged(ElaThemeType.ThemeMode.Light)
        assert tooltip._label.palette().color(QPalette.ColorRole.WindowText).name() == light
        tooltip._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert tooltip._label.palette().color(QPalette.ColorRole.WindowText).name() == dark
        assert tooltip._currentTheme == ElaThemeType.ThemeMode.Dark
        assert tooltip._label.font().pixelSize() == 12
        tooltip.deleteLater()
        qapp.processEvents()

    def test_theme_signal_reconnects_text_color(self, qapp, monkeypatch):

        class _FakeTheme(QObject):
            themeModeChanged = pyqtSignal(object)

            def getThemeMode(self):
                return ElaThemeType.ThemeMode.Light

            def getThemeColor(self, mode, _role):
                return (
                    QColor("#ff0000")
                    if mode == ElaThemeType.ThemeMode.Dark
                    else QColor("#00ff00")
                )

        fake = _FakeTheme()
        monkeypatch.setattr(tooltips_module, "eTheme", fake)
        tooltip = tooltips_module.ElaToolTip("提示")
        assert (
            tooltip._label.palette().color(QPalette.ColorRole.WindowText).name()
            == "#00ff00"
        )

        fake.themeModeChanged.emit(ElaThemeType.ThemeMode.Dark)
        assert (
            tooltip._label.palette().color(QPalette.ColorRole.WindowText).name()
            == "#ff0000"
        )
        tooltip.deleteLater()
        qapp.processEvents()


class TestStateToolTip:
    """Test cases for ElaStateToolTip class."""

    def test_state_tooltip_initialization(self):
        """Test ElaStateToolTip initializes with title and content."""
        st = ElaStateToolTip("Title", "Content")

        assert st._title == "Title"
        assert st._content == "Content"

        st.deleteLater()

    def test_state_tooltip_has_closed_signal(self):
        """Test ElaStateToolTip has closed signal (was closedSignal)."""
        st = ElaStateToolTip()
        assert hasattr(st, "closed")
        st.deleteLater()

    def test_state_tooltip_has_title_and_content_labels(self):
        """Test ElaStateToolTip has title and content labels."""
        st = ElaStateToolTip("Title", "Content")

        assert hasattr(st, "_titleLabel")
        assert hasattr(st, "_contentLabel")

        st.deleteLater()


class TestStateToolTipTimerLifecycle:
    """复用同一个 tooltip（hide 之后再 show）必须重启 loading spinner。"""

    def test_rotate_timer_restarts_after_hide_show(self, qapp):
        tip = ElaStateToolTip()
        tip.resize(200, 60)
        tip.show()
        qapp.processEvents()
        assert tip._rotateTimer.isActive() is True

        tip.hide()
        qapp.processEvents()
        assert tip._rotateTimer.isActive() is False

        tip.show()
        qapp.processEvents()
        assert tip._rotateTimer.isActive() is True, "hide -> show 后 spinner 必须重启"

        tip.close()
        tip.deleteLater()
        qapp.processEvents()

    def test_rotate_timer_stays_off_after_real_close(self, qapp):
        tip = ElaStateToolTip()
        tip.show()
        qapp.processEvents()
        tip.close()
        qapp.processEvents()
        assert tip._rotateTimer.isActive() is False
        tip.deleteLater()
        qapp.processEvents()
