"""Tests for ElaMarkdownViewer P4 performance features.

Covers: long-paragraph streaming commit, chunked large-document render,
cache governance.
"""

from __future__ import annotations

from PyQt5.QtTest import QTest

from pyqt5_ela_pro import math_lite
from pyqt5_ela_pro import ela_markdown_viewer as viewer_module
from pyqt5_ela_pro.ela_markdown_viewer import ElaMarkdownViewer


class TestLongParagraphStreaming:
    SENTENCE = "这是一个用于测试超长段落流式提交的句子。"
    CHUNK = 2000

    def test_commits_sentence_boundaries(self):
        paragraph = self.SENTENCE * 1200
        v = ElaMarkdownViewer()
        v.beginStream()
        for start in range(0, len(paragraph), self.CHUNK):
            v.appendMarkdown(paragraph[start : start + self.CHUNK])
            v._stream_timer.stop()
            v._flush_stream()

        assert v._stream_committed > 0
        tail = len(paragraph) - v._stream_committed
        assert tail <= viewer_module._STREAM_SENTENCE_MAX
        v.endStream()
        v.deleteLater()

    def test_final_parity_with_oneshot(self):
        paragraph = self.SENTENCE * 800
        v = ElaMarkdownViewer()
        v.beginStream()
        for start in range(0, len(paragraph), self.CHUNK):
            v.appendMarkdown(paragraph[start : start + self.CHUNK])
            v._stream_timer.stop()
            v._flush_stream()
        v.endStream()

        reference = ElaMarkdownViewer()
        reference._render_into(reference.document(), paragraph)
        assert v.toPlainText() == reference.document().toPlainText()
        v.deleteLater()
        reference.deleteLater()

    def test_blank_line_cut_still_prioritized(self):
        text = "第一段。\n\n第二段内容。"
        assert viewer_module._stable_cut(text, 0, allow_sentence=True) == len(
            "第一段。\n\n"
        )

    def test_short_tail_not_force_cut(self):
        text = "很短的一段。"
        assert viewer_module._stable_cut(text, 0, allow_sentence=True) == 0


class TestLargeRender:
    BIG = (
        "# 标题小节\n\n" + "这是内容段落，包含 `代码` 与 **加粗** 文本。" * 40 + "\n\n"
    ) * 90

    def test_large_source_uses_chunking(self, qapp):
        assert len(self.BIG) > viewer_module._LARGE_RENDER_CHARS
        v = ElaMarkdownViewer()
        progress = []
        finished = []
        v.renderingProgress.connect(progress.append)
        v.renderingFinished.connect(lambda: finished.append(True))

        v.setMarkdown(self.BIG)
        assert v.isRendering()
        for _ in range(600):
            if finished:
                break
            qapp.processEvents()
            QTest.qWait(5)

        assert finished
        assert not v.isRendering()
        assert progress and progress[-1] == 100
        assert v.toPlainText() == self._oneshot_text()
        v.deleteLater()

    def test_small_source_not_chunked(self):
        v = ElaMarkdownViewer()
        v.setMarkdown("# 小文档\n\n内容")
        assert not v.isRendering()
        v.deleteLater()

    def test_reentrant_set_markdown_cancels(self, qapp):
        v = ElaMarkdownViewer()
        v.setMarkdown(self.BIG)
        v.setMarkdown("# 第二个文档\n\n短内容")
        for _ in range(50):
            qapp.processEvents()
            QTest.qWait(5)
        assert not v.isRendering()
        assert "第二个文档" in v.toPlainText()
        v.deleteLater()

    @classmethod
    def _oneshot_text(cls) -> str:
        reference = ElaMarkdownViewer()
        reference._render_into(reference.document(), cls.BIG)
        text = reference.document().toPlainText()
        reference.deleteLater()
        return text


class TestCacheGovernance:
    def test_highlight_cache_cleared(self):
        v = ElaMarkdownViewer()
        v.setMarkdown("```python\nx = 1\n```")
        assert v._highlight_cache
        v.clearCache()
        assert not v._highlight_cache
        v.deleteLater()

    def test_highlight_cache_cap(self):
        import pytest

        pytest.importorskip("pygments")
        v = ElaMarkdownViewer()
        v.setHighlightCacheSize(1)
        v.setMarkdown("```python\na = 1\n```\n\n```python\nb = 2\n```")
        assert len(v._highlight_cache) <= 1
        v.deleteLater()

    def test_math_cache_capacity_and_clear(self):
        old_cap = math_lite._CACHE_CAP
        try:
            math_lite.set_cache_capacity(2)
            assert math_lite._CACHE_CAP == 2
            v = ElaMarkdownViewer()
            v.setMarkdown("$x^2$ 与 $y_1$")
            assert math_lite._CACHE
            v.clearCache()
            assert not math_lite._CACHE
            v.deleteLater()
        finally:
            math_lite.set_cache_capacity(old_cap)

    def test_zero_capacity_disables_highlight_cache(self):
        import pytest

        pytest.importorskip("pygments")
        v = ElaMarkdownViewer()
        v.setHighlightCacheSize(0)
        v.setMarkdown("```python\na = 1\n```")
        assert not v._highlight_cache
        v.deleteLater()
