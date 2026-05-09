from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path
from PyQt5.QtCore import QUrl

from pyqt5_ela_pro.browser_embedder import _BrowserController, ElaBrowserEmbedder


class TestBrowserControllerInit:
    def test_initialization(self):
        ctrl = _BrowserController("ws://127.0.0.1:9222", timeout=5.0)
        assert ctrl._debugger_url == "ws://127.0.0.1:9222"
        assert ctrl._timeout == 5.0
        assert ctrl._running is False
        assert ctrl._message_id == 0
        assert ctrl._callbacks == {}
        ctrl.close()

    def test_has_signals(self):
        ctrl = _BrowserController("ws://127.0.0.1:9222")
        assert hasattr(ctrl, "cdpReady")
        assert hasattr(ctrl, "errorOccurred")
        assert hasattr(ctrl, "consoleMessage")
        ctrl.close()


class TestBrowserControllerConnection:
    def test_connect_creates_websocket(self):
        with patch("pyqt5_ela_pro.browser_embedder.QWebSocket") as mock_ws:
            ctrl = _BrowserController("ws://127.0.0.1:9222")
            ctrl.connect()
            mock_ws_instance = mock_ws.return_value
            mock_ws_instance.open.assert_called_with(QUrl("ws://127.0.0.1:9222"))
            ctrl.close()

    def test_close_cleans_up(self):
        ctrl = _BrowserController("ws://127.0.0.1:9222")
        ctrl._ws = MagicMock()
        ctrl.close()
        assert ctrl._running is False
        assert ctrl._ws is None

    def test_send_command_returns_id(self):
        ctrl = _BrowserController("ws://127.0.0.1:9222")
        ctrl._ws = MagicMock()
        mid = ctrl.sendCommand("Page.enable")
        assert mid == 0
        ctrl.close()

    def test_runJS_calls_send_command(self):
        ctrl = _BrowserController("ws://127.0.0.1:9222")
        ctrl._ws = MagicMock()
        mid = ctrl.runJS("1+1")
        assert mid >= 0
        ctrl.close()

    def test_navigate_calls_send_command(self):
        ctrl = _BrowserController("ws://127.0.0.1:9222")
        ctrl._ws = MagicMock()
        mid = ctrl.navigate("http://example.com")
        assert mid >= 0
        ctrl.close()

    def test_reload_calls_send_command(self):
        ctrl = _BrowserController("ws://127.0.0.1:9222")
        ctrl._ws = MagicMock()
        mid = ctrl.reload()
        assert mid >= 0
        ctrl.close()


class TestBrowserControllerCallbacks:
    def test_set_load_started_callback(self):
        ctrl = _BrowserController("ws://127.0.0.1:9222")
        cb = MagicMock()
        ctrl.set_loadStarted_callback(cb)
        assert ctrl._loadStarted_callback is cb
        ctrl.close()

    def test_set_load_finished_callback(self):
        ctrl = _BrowserController("ws://127.0.0.1:9222")
        cb = MagicMock()
        ctrl.set_loadFinished_callback(cb)
        assert ctrl._loadFinished_callback is cb
        ctrl.close()

    def test_handle_event_frame_started_loading(self):
        ctrl = _BrowserController("ws://127.0.0.1:9222")
        cb = MagicMock()
        ctrl.set_loadStarted_callback(cb)
        ctrl._handle_event("Page.frameStartedLoading", {})
        cb.assert_called_once()
        ctrl.close()

    def test_handle_event_load_event_fired(self):
        ctrl = _BrowserController("ws://127.0.0.1:9222")
        cb = MagicMock()
        ctrl.set_loadFinished_callback(cb)
        ctrl._handle_event("Page.loadEventFired", {})
        cb.assert_called_once()
        ctrl.close()


class TestElaBrowserEmbedderInit:
    def test_check_dependencies_raises_without_win32(self):
        with patch("pyqt5_ela_pro.browser_embedder.win32gui", None):
            with patch("pyqt5_ela_pro.browser_embedder.win32con", None):
                import pyqt5_ela_pro.browser_embedder as be
                with pytest.raises(ImportError, match="pywin32"):
                    be.ElaBrowserEmbedder._checkDependencies()

    def test_has_signals(self):
        with patch.multiple(
            "pyqt5_ela_pro.browser_embedder",
            win32gui=MagicMock(),
            win32con=MagicMock(),
            win32process=MagicMock(),
        ):
            embedder = ElaBrowserEmbedder(webview_path=Path("chrome.exe"))
            assert hasattr(embedder, "loadStarted")
            assert hasattr(embedder, "loadFinished")
            assert hasattr(embedder, "logMessage")
            assert hasattr(embedder, "embedCompleted")
            assert hasattr(embedder, "consoleMessage")
            embedder.deleteLater()


class TestElaBrowserEmbedderStatic:
    def test_alloc_debug_port_increments(self):
        port1 = ElaBrowserEmbedder._alloc_debug_port()
        port2 = ElaBrowserEmbedder._alloc_debug_port()
        assert port2 > port1

    def test_get_all_instances_returns_list(self):
        instances = ElaBrowserEmbedder.getAllInstances()
        assert isinstance(instances, list)


class TestElaBrowserEmbedderNavigateRunJS:
    def test_navigate_returns_none_when_no_controller(self):
        with patch.multiple(
            "pyqt5_ela_pro.browser_embedder",
            win32gui=MagicMock(),
            win32con=MagicMock(),
            win32process=MagicMock(),
        ):
            embedder = ElaBrowserEmbedder(webview_path=Path("chrome.exe"))
            result = embedder.navigate("http://example.com")
            assert result is None
            embedder.deleteLater()

    def test_runJS_returns_none_when_no_controller(self):
        with patch.multiple(
            "pyqt5_ela_pro.browser_embedder",
            win32gui=MagicMock(),
            win32con=MagicMock(),
            win32process=MagicMock(),
        ):
            embedder = ElaBrowserEmbedder(webview_path=Path("chrome.exe"))
            result = embedder.runJS("1+1")
            assert result is None
            embedder.deleteLater()

    def test_load_url_path_conversion(self):
        with patch.multiple(
            "pyqt5_ela_pro.browser_embedder",
            win32gui=MagicMock(),
            win32con=MagicMock(),
            win32process=MagicMock(),
        ):
            embedder = ElaBrowserEmbedder(webview_path=Path("chrome.exe"))
            result = embedder.load_url(Path("C:\\page.html"))
            assert result is None
            embedder.deleteLater()

    def test_load_url_string(self):
        with patch.multiple(
            "pyqt5_ela_pro.browser_embedder",
            win32gui=MagicMock(),
            win32con=MagicMock(),
            win32process=MagicMock(),
        ):
            embedder = ElaBrowserEmbedder(webview_path=Path("chrome.exe"))
            result = embedder.load_url("http://example.com")
            assert result is None
            embedder.deleteLater()
