"""pytest configuration and fixtures for pyqt5_ela_pro tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from _qthelpers import WidgetFactory
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget


@pytest.fixture(scope="session", autouse=True)
def qapp():
    """Provide QApplication instance for all tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    # ``eApp.init()`` **必须在创建任何 ElaWindow 之前**调用（AGENTS.md 的硬约束），
    # 少了这一步 `ElaWindow()` 直接 access violation，且崩在构造那一行、看不出
    # 跟 init 有关。凡是碰 ElaWindow / ElaAppBar 的用例都靠这一行兜住。
    from PyQt5ElaWidgetTools import eApp

    eApp.init()
    yield app


@pytest.fixture(autouse=True)
def qt_cleanup(qapp):
    """每个用例的收尾：回收 ``make()`` 登记的控件 + 冲刷 ``deleteLater`` 队列。

    AGENTS.md 约定「``deleteLater()`` 后必须跟 ``qapp.processEvents()``
    才真正销毁」。这条以前靠一千多处人工 ``processEvents()`` 维持，漏写就跨
    测试泄漏控件；现在统一由本 fixture 兜底，所以测试体里不再需要写收尾样板。

    产出的就是 :class:`~_qthelpers.WidgetFactory`，``make`` fixture 是它的别名。
    """
    factory = WidgetFactory(qapp)
    yield factory
    factory.destroy_all()


@pytest.fixture
def make(qt_cleanup):
    """控件工厂：``make(ElaButton, "ok")``，造出来的控件由 ``qt_cleanup`` 统一销毁。

    取代测试体里的 ``w = X(...)`` … ``w.deleteLater()`` 样板。
    """
    return qt_cleanup


@pytest.fixture
def mock_e_theme(mocker):
    """Mock PyQt5ElaWidgetTools.eTheme for isolated testing."""
    mock = mocker.patch("PyQt5ElaWidgetTools.eTheme")
    mock_theme_mode = MagicMock()
    mock_theme_mode.value = 0
    mock.getThemeMode.return_value = mock_theme_mode
    mock.getThemeColor.return_value = "#FFFFFF"
    mock.themeModeChanged = MagicMock()
    return mock


@pytest.fixture
def widget(qapp):
    """Provide a basic QWidget for testing."""
    w = QWidget()
    yield w
    w.deleteLater()


@pytest.fixture
def window_widget(qapp):
    """Provide a widget that can be shown (for animation tests)."""
    w = QWidget()
    w.setWindowFlags(Qt.Window)
    w.resize(400, 300)
    yield w
    if w.isVisible():
        w.close()
    w.deleteLater()
