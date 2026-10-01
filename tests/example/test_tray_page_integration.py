"""托盘示例页的接入行为测试。

守两个曾经坏掉的行为：
① 托盘菜单「划词助手」项要真能找到划词页并切换（曾依赖不存在的
   ``window._page_map``，导致该项永远打空）；
② 托盘菜单「退出」要真结束进程（曾只打日志）。

**刻意不构造完整 ``ExampleWindow``** —— 它会把浏览器嵌入等重页面一并建起来
（``concurrent.futures`` 线程 + 原生窗口），在 pytest 里实测 access violation。
这里用最小 ``ElaWindow`` 只挂这两个页面，``addPageNode`` 的 reparent 行为一致。

（原 ``tray_page.py`` 的 ``TrayIconPage`` 已并入 ``app_shell_page.py`` 的
``AppShellPage`` —— 启动画面 / 任务栏进度 / 托盘回答的是同一个问题：
「我的程序怎么在系统里露出存在」。）
"""

from __future__ import annotations

import pytest
from PyQt5ElaWidgetTools import ElaIconType, ElaWindow

from pyqt5_ela_pro.example.app_shell_page import AppShellPage
from pyqt5_ela_pro.example.selection_page import SelectionAssistantPage


@pytest.fixture(scope="module")
def env(qapp):
    """最小主窗口：只挂托盘页 + 划词页（够验证 reparent 后的 findChildren）。"""
    window = ElaWindow()
    sel = SelectionAssistantPage(window)
    tray = AppShellPage(window)
    window.addPageNode("划词助手", sel, ElaIconType.IconName.Highlighter)
    window.addPageNode("启动与托盘", tray, ElaIconType.IconName.Plug)
    window.show()
    qapp.processEvents()
    yield window, tray, sel
    window.deleteLater()
    qapp.processEvents()


def _labels(host):
    return [a.text() for a in host.trayIcon().menu().actions() if a.text()]


def _click(host, text):
    for action in host.trayIcon().menu().actions():
        if action.text() == text:
            action.trigger()
            return True
    return False


class TestSelectionToggle:
    def test_page_lookup_uses_find_children(self, env, qapp):
        """回归：不能用 ``window._page_map``（ElaWindow 根本没这个属性）。"""
        window, tray_page, sel = env
        assert not hasattr(window, "_page_map")
        assert tray_page._find_selection_page() is sel
        qapp.processEvents()

    def test_menu_has_selection_item(self, env):
        _window, tray_page, _sel = env
        labels = _labels(tray_page._host)
        assert any("划词助手" in t for t in labels), labels

    def test_toggle_from_tray_enables_assistant(self, env, qapp):
        _window, tray_page, sel = env
        host = tray_page._host
        # 先归零，保证与用例执行顺序无关
        if sel.isAssistantEnabled():
            _click(host, "划词助手：开")
            qapp.processEvents()
        assert sel.isAssistantEnabled() is False

        assert _click(host, "划词助手：关") is True
        qapp.processEvents()
        assert sel.isAssistantEnabled() is True
        # 页面内开关也跟着翻
        assert sel._enable_switch.getIsToggled() is True
        # 托盘文案同步
        assert any("划词助手：开" in t for t in _labels(host)), _labels(host)

    def test_label_syncs_back_from_page_switch(self, env, qapp):
        """页面内开关变化 -> 托盘文案回写（双向同步）。"""
        _window, tray_page, sel = env
        host = tray_page._host
        _click(host, "划词助手：关")
        qapp.processEvents()
        assert sel.isAssistantEnabled() is True

        # 从页面自身关掉
        sel._on_enable_toggled(False)
        qapp.processEvents()
        assert sel.isAssistantEnabled() is False
        assert any("划词助手：关" in t for t in _labels(host)), _labels(host)

    def test_state_relay_signal(self, env, qapp):
        _window, _tray_page, sel = env
        seen = []
        sel.assistantStateChanged.connect(seen.append)
        if not sel.isAssistantEnabled():
            sel._on_enable_toggled(True)
        qapp.processEvents()
        assert True in seen, seen

    def test_is_assistant_enabled_does_not_create(self, env, qapp):
        """读状态不该顺带把助手造出来（托盘初始化时会问一次）。"""
        _window, _tray_page, sel = env
        before = sel._assistant
        sel.isAssistantEnabled()
        assert sel._assistant is before


class TestQuitAction:
    def test_quit_requested_calls_shutdown(self, env, qapp, monkeypatch):
        """回归：点「退出」必须真调 shutdown()，不能只打日志。"""
        _window, tray_page, _sel = env
        called = []
        monkeypatch.setattr(tray_page._host, "shutdown", lambda: called.append(True))
        tray_page._on_quit_requested()
        assert called == [True]

    def test_quit_menu_item_emits_quit_requested(self, env, qapp):
        _window, tray_page, _sel = env
        seen = []
        tray_page._host.quitRequested.connect(lambda: seen.append(True))
        assert _click(tray_page._host, "退出") is True
        assert seen == [True]

    # 注意：不在这里跑 `qapp.exec_()` 验证真退出 —— 在 pytest 内重入事件循环
    # 会把整个测试进程带崩（实测 access violation，栈全在 pluggy/pytest 内）。
    # 真退出由独立进程脚本验证，本文件只守「点了退出 → shutdown() 被调用」。
