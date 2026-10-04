"""ElaClipboardCapture 测试：变化计数取词、超时失败与剪贴板恢复。"""

from __future__ import annotations

import time

from _qthelpers import wait_until as _wait_until

from pyqt5_ela_pro import ElaClipboardCapture
from pyqt5_ela_pro.selection_assistant import capture as capture_module


def _speed_up(capture: ElaClipboardCapture, timeout_ms: int = 120) -> None:
    capture.setCaptureDelayMs(1)
    capture.setPollMs(1)
    capture.setTimeoutMs(timeout_ms)
    capture.setRestoreDelayMs(1)


def _set_clipboard(qapp, text: str) -> str:
    """写入剪贴板并确认生效（Qt/Windows 下连续写入可能被静默丢弃）。"""
    clipboard = qapp.clipboard()
    for _ in range(10):
        clipboard.setText(text)
        qapp.processEvents()
        if clipboard.text() == text:
            return text
        time.sleep(0.01)
    return clipboard.text()


class TestCapture:
    def test_success_and_clipboard_restored(
        self, qapp, monkeypatch, requires_clipboard
    ):
        clipboard = qapp.clipboard()
        before = _set_clipboard(qapp, "旧内容")
        capture = ElaClipboardCapture()
        _speed_up(capture)
        results = []
        capture.captured.connect(results.append)
        monkeypatch.setattr(
            capture_module, "send_copy", lambda: clipboard.setText("选中的文本")
        )

        capture.capture()
        assert capture.isCapturing() is True
        assert _wait_until(qapp, lambda: bool(results))
        assert results == ["选中的文本"]
        assert _wait_until(qapp, lambda: clipboard.text() == before)
        capture.deleteLater()

    def test_timeout_fails_without_touching_clipboard(
        self, qapp, monkeypatch, requires_clipboard
    ):
        clipboard = qapp.clipboard()
        before = _set_clipboard(qapp, "旧内容")
        capture = ElaClipboardCapture()
        _speed_up(capture, timeout_ms=60)
        failures = []
        capture.failed.connect(lambda: failures.append(True))
        monkeypatch.setattr(capture_module, "send_copy", lambda: None)

        capture.capture()
        assert _wait_until(qapp, lambda: bool(failures))
        assert capture.isCapturing() is False
        assert clipboard.text() == before
        capture.deleteLater()

    def test_restore_disabled_keeps_selection(
        self, qapp, monkeypatch, requires_clipboard
    ):
        clipboard = qapp.clipboard()
        _set_clipboard(qapp, "旧内容")
        capture = ElaClipboardCapture()
        _speed_up(capture)
        capture.setRestoreClipboard(False)
        assert capture.restoreClipboard() is False
        results = []
        capture.captured.connect(results.append)
        monkeypatch.setattr(
            capture_module, "send_copy", lambda: clipboard.setText("选中")
        )

        capture.capture()
        assert _wait_until(qapp, lambda: bool(results))
        assert _wait_until(qapp, lambda: clipboard.text() == "选中")
        capture.deleteLater()

    def test_empty_copy_is_failure(self, qapp, monkeypatch, requires_clipboard):
        clipboard = qapp.clipboard()
        _set_clipboard(qapp, "旧内容")
        capture = ElaClipboardCapture()
        _speed_up(capture, timeout_ms=60)
        failures = []
        capture.failed.connect(lambda: failures.append(True))
        monkeypatch.setattr(capture_module, "send_copy", lambda: clipboard.clear())

        capture.capture()
        assert _wait_until(qapp, lambda: bool(failures))
        capture.deleteLater()

    def test_cancel_keeps_clipboard(self, qapp, monkeypatch, requires_clipboard):
        clipboard = qapp.clipboard()
        before = _set_clipboard(qapp, "旧内容")
        capture = ElaClipboardCapture()
        capture.setCaptureDelayMs(1000)
        monkeypatch.setattr(capture_module, "send_copy", lambda: None)

        capture.capture()
        assert capture.isCapturing() is True
        capture.cancel()
        assert capture.isCapturing() is False
        assert clipboard.text() == before
        capture.deleteLater()

    def test_config_roundtrip(self, qapp):
        capture = ElaClipboardCapture()
        capture.setCaptureDelayMs(50)
        capture.setPollMs(20)
        capture.setTimeoutMs(400)
        capture.setRestoreDelayMs(200)
        assert capture.captureDelayMs() == 50
        assert capture.pollMs() == 20
        assert capture.timeoutMs() == 400
        assert capture.restoreDelayMs() == 200
        assert capture.restoreClipboard() is True
        capture.deleteLater()
