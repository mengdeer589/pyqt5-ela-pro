"""Tests for ela_drawer_area module: ElaDrawerArea click-to-toggle fix."""

from __future__ import annotations

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget

from PyQt5ElaWidgetTools import ElaText, ElaToggleSwitch

from pyqt5_ela_pro.ela_drawer_area import ElaDrawerArea
from pyqt5_ela_pro.widget_base import ElaThemeWidget


def _click(qapp, widget: QWidget, pos: QPoint) -> None:
    """向 *widget* 发送一次左键点击（按下 + 释放）。"""
    press = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        pos,
        widget.mapToGlobal(pos),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    release = QMouseEvent(
        QEvent.Type.MouseButtonRelease,
        pos,
        widget.mapToGlobal(pos),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )
    qapp.sendEvent(widget, press)
    qapp.sendEvent(widget, release)
    qapp.processEvents()


def _make_area(qapp) -> tuple[QWidget, ElaDrawerArea, QWidget]:
    parent = QWidget()
    parent.resize(400, 300)
    area = ElaDrawerArea(parent)
    area.setGeometry(0, 0, 400, 300)
    area.addDrawer(QWidget(area))
    parent.show()
    qapp.processEvents()
    header = area.findChild(QWidget, "ElaDrawerHeader")
    assert header is not None
    return parent, area, header


class TestElaDrawerAreaApi:
    def test_is_native_subclass(self, qapp):
        from PyQt5ElaWidgetTools import ElaDrawerArea as NativeDrawerArea

        assert issubclass(ElaDrawerArea, NativeDrawerArea)

    def test_toggle_method(self, qapp):
        parent, area, _ = _make_area(qapp)

        area.toggle()
        assert area.getIsExpand() is True
        area.toggle()
        assert area.getIsExpand() is False

        parent.close()
        parent.deleteLater()

    def test_expand_collapse_idempotent(self, qapp):
        """Regression: 重复 expand/collapse 不重复发信号（开关回声防护）。"""
        parent, area, _ = _make_area(qapp)
        states = []
        area.expandStateChanged.connect(states.append)

        area.expand()
        area.expand()
        assert states == [True]

        area.collapse()
        area.collapse()
        assert states == [True, False]

        parent.close()
        parent.deleteLater()


class TestElaDrawerAreaClickToggle:
    def test_click_empty_header_toggles_once(self, qapp):
        parent, area, header = _make_area(qapp)
        states = []
        area.expandStateChanged.connect(states.append)

        _click(qapp, header, header.rect().center())

        assert area.getIsExpand() is True
        assert states == [True]
        parent.close()
        parent.deleteLater()

    def test_click_empty_header_twice_collapses(self, qapp):
        parent, area, header = _make_area(qapp)

        _click(qapp, header, header.rect().center())
        _click(qapp, header, header.rect().center())

        assert area.getIsExpand() is False
        parent.close()
        parent.deleteLater()

    def test_click_custom_header_label_toggles(self, qapp):
        parent, area, _ = _make_area(qapp)
        header_widget = ElaThemeWidget(area)
        layout = QHBoxLayout(header_widget)
        label = ElaText("抽屉标题", header_widget)
        layout.addWidget(label)
        layout.addStretch()
        area.setDrawerHeader(header_widget)
        qapp.processEvents()

        _click(qapp, label, label.rect().center())

        assert area.getIsExpand() is True
        parent.close()
        parent.deleteLater()

    def test_click_custom_header_background_toggles(self, qapp):
        parent, area, _ = _make_area(qapp)
        header_widget = ElaThemeWidget(area)
        layout = QHBoxLayout(header_widget)
        layout.addWidget(ElaText("抽屉标题", header_widget))
        layout.addStretch()
        area.setDrawerHeader(header_widget)
        qapp.processEvents()

        background_pos = QPoint(header_widget.width() - 5, 5)
        _click(qapp, header_widget, background_pos)

        assert area.getIsExpand() is True
        parent.close()
        parent.deleteLater()

    def test_click_interactive_button_does_not_toggle(self, qapp):
        parent, area, _ = _make_area(qapp)
        header_widget = ElaThemeWidget(area)
        layout = QHBoxLayout(header_widget)
        button = QPushButton("点我", header_widget)
        layout.addWidget(button)
        layout.addStretch()
        area.setDrawerHeader(header_widget)
        qapp.processEvents()

        _click(qapp, button, button.rect().center())

        assert area.getIsExpand() is False
        parent.close()
        parent.deleteLater()

    def test_header_click_syncs_toggle_switch(self, qapp):
        """Regression: 示例中标题栏点击后右侧开关必须跟随切换。"""
        from PyQt5ElaWidgetTools import ElaToggleSwitch

        parent, area, _ = _make_area(qapp)
        header_widget = ElaThemeWidget(area)
        layout = QHBoxLayout(header_widget)
        switch = ElaToggleSwitch(header_widget)
        layout.addWidget(switch)
        layout.addStretch()
        area.setDrawerHeader(header_widget)
        area.expandStateChanged.connect(switch.setIsToggled)
        qapp.processEvents()

        _click(qapp, header_widget, QPoint(header_widget.width() - 5, 5))

        assert area.getIsExpand() is True
        assert switch.getIsToggled() is True

        _click(qapp, header_widget, QPoint(header_widget.width() - 5, 5))

        assert area.getIsExpand() is False
        assert switch.getIsToggled() is False
        parent.close()
        parent.deleteLater()

    def test_click_toggle_switch_does_not_toggle_drawer(self, qapp):
        """Regression: 交互开关自处理点击，不应被当成"点击标题栏"。"""
        parent, area, _ = _make_area(qapp)
        header_widget = ElaThemeWidget(area)
        layout = QHBoxLayout(header_widget)
        switch = ElaToggleSwitch(header_widget)
        layout.addWidget(switch)
        layout.addStretch()
        area.setDrawerHeader(header_widget)
        qapp.processEvents()

        _click(qapp, switch, switch.rect().center())

        assert switch.getIsToggled() is True
        assert area.getIsExpand() is False
        parent.close()
        parent.deleteLater()

    def test_switch_click_with_bidirectional_wiring_no_flap(self, qapp):
        """Regression: 示例双向接线（开关↔抽屉）下单击开关只切换一次。"""
        parent, area, _ = _make_area(qapp)
        header_widget = ElaThemeWidget(area)
        layout = QHBoxLayout(header_widget)
        switch = ElaToggleSwitch(header_widget)
        layout.addWidget(switch)
        layout.addStretch()
        area.setDrawerHeader(header_widget)

        def on_toggled(state):
            area.expand() if state else area.collapse()

        switch.toggled.connect(on_toggled)
        area.expandStateChanged.connect(switch.setIsToggled)
        qapp.processEvents()

        _click(qapp, switch, switch.rect().center())

        assert switch.getIsToggled() is True
        assert area.getIsExpand() is True
        parent.close()
        parent.deleteLater()
