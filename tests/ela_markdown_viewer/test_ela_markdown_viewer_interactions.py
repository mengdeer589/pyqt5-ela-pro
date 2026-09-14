"""Tests for ElaMarkdownViewer P2 enhancements.

Covers: images (base URL, scaling, remote blocking), placeholder text,
link signal, zoom, search, export helpers and context menu.
"""

from __future__ import annotations

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QImage, QColor, QTextCursor

from pyqt5_ela_pro.ela_markdown_viewer import ElaMarkdownViewer


def _fragments(viewer: ElaMarkdownViewer) -> list:
    result = []
    block = viewer.document().begin()
    while block.isValid():
        iterator = block.begin()
        while not iterator.atEnd():
            fragment = iterator.fragment()
            if fragment.isValid():
                result.append(fragment)
            iterator += 1
        block = block.next()
    return result


def _image_fragments(viewer: ElaMarkdownViewer) -> list:
    return [f for f in _fragments(viewer) if f.charFormat().isImageFormat()]


def _make_image(tmp_path, name: str, width: int, height: int) -> str:
    image = QImage(width, height, QImage.Format_ARGB32)
    image.fill(QColor("red"))
    path = tmp_path / name
    image.save(str(path))
    return str(path)


class TestPlaceholder:
    def test_set_and_get(self):
        v = ElaMarkdownViewer()
        v.setPlaceholderText("正在生成…")
        assert v.placeholderText() == "正在生成…"

        v.resize(240, 120)
        from PyQt5.QtGui import QPixmap

        pixmap = QPixmap(v.size())
        v.render(pixmap)
        v.deleteLater()

    def test_hidden_when_content_present(self):
        v = ElaMarkdownViewer()
        v.setPlaceholderText("空")
        v.setMarkdown("内容")
        assert v._source
        v.deleteLater()


class TestLinkSignal:
    def test_anchor_clicked_reemits(self):
        v = ElaMarkdownViewer()
        received = []
        v.linkActivated.connect(received.append)
        v.setMarkdown("[内部](#section) 与 [外部](https://example.com)")

        v.textBrowser().anchorClicked.emit(QUrl("#section"))
        assert received and received[-1].endswith("#section")
        v.deleteLater()


class TestZoom:
    def test_zoom_changes_document_font(self):
        v = ElaMarkdownViewer()
        base = v._base_font_point_size
        v.setZoomFactor(1.5)
        assert abs(v.document().defaultFont().pointSizeF() - base * 1.5) < 0.01
        v.zoomOut(0.5)
        assert abs(v.zoomFactor() - 1.0) < 1e-6
        v.deleteLater()

    def test_zoom_clamped(self):
        v = ElaMarkdownViewer()
        v.setZoomFactor(99)
        assert v.zoomFactor() == 4.0
        v.setZoomFactor(0)
        assert v.zoomFactor() == 0.25
        v.deleteLater()


class TestSearch:
    def test_search_highlights_and_counts(self):
        v = ElaMarkdownViewer()
        v.setMarkdown("alpha beta alpha gamma Alpha")

        assert v.searchText("alpha") == 3
        assert len(v.textBrowser().extraSelections()) == 3
        assert v.searchText("alpha", case_sensitive=True) == 2
        v.deleteLater()

    def test_find_next_cycles(self):
        v = ElaMarkdownViewer()
        v.setMarkdown("alpha x alpha y alpha")
        assert v.searchText("alpha") == 3

        first = v.textBrowser().textCursor().selectionStart()
        assert v.findNext()
        second = v.textBrowser().textCursor().selectionStart()
        assert second != first
        assert v.findNext()
        assert v.findNext()
        assert v.textBrowser().textCursor().selectionStart() == first
        v.deleteLater()

    def test_clear_search(self):
        v = ElaMarkdownViewer()
        v.setMarkdown("alpha alpha")
        v.searchText("alpha")
        v.clearSearch()
        assert v.textBrowser().extraSelections() == []
        assert not v.findNext()
        v.deleteLater()


class TestImages:
    def test_local_image_scaled_to_viewport(self, tmp_path):
        path = _make_image(tmp_path, "wide.png", 1200, 600)
        v = ElaMarkdownViewer()
        v.resize(320, 240)
        v.setBaseUrl(str(tmp_path))
        v.setMarkdown(f"![宽图]({path.replace(chr(92), '/')})")

        images = _image_fragments(v)
        assert len(images) == 1
        fmt = images[0].charFormat().toImageFormat()
        assert 0 < fmt.width() <= max(v.textBrowser().viewport().width() - 24, 120)
        # 纵横比保持
        assert abs(fmt.width() / fmt.height() - 2.0) < 0.05
        v.deleteLater()

    def test_local_image_relative_path(self, tmp_path):
        _make_image(tmp_path, "pic.png", 40, 20)
        v = ElaMarkdownViewer()
        v.setBaseUrl(str(tmp_path))
        v.setMarkdown("![图](pic.png)")

        images = _image_fragments(v)
        assert len(images) == 1
        assert "pic.png" in images[0].charFormat().toImageFormat().name()
        v.deleteLater()

    def test_missing_image_becomes_placeholder(self, tmp_path):
        v = ElaMarkdownViewer()
        v.setBaseUrl(str(tmp_path))
        v.setMarkdown("![缺失](nope.png)")

        assert "[图片]" in v.document().toPlainText()
        assert _image_fragments(v) == []
        v.deleteLater()

    def test_remote_images_blocked_by_default(self):
        v = ElaMarkdownViewer()
        v.setMarkdown("![远程](https://example.com/a.png)")

        assert "[图片]" in v.document().toPlainText()
        assert _image_fragments(v) == []
        assert v.remoteImagesEnabled() is False
        v.deleteLater()

    def test_remote_images_kept_when_enabled(self):
        v = ElaMarkdownViewer()
        v.setRemoteImagesEnabled(True)
        v.setMarkdown("![远程](https://example.com/a.png)")

        images = _image_fragments(v)
        assert len(images) == 1
        assert images[0].charFormat().toImageFormat().name().startswith("https://")
        v.deleteLater()


class TestExportAndMenu:
    def test_export_helpers(self):
        v = ElaMarkdownViewer()
        v.setMarkdown("# 标题\n\n正文 **加粗**")

        assert "标题" in v.toPlainText()
        assert "标题" in v.toHtml()
        v.deleteLater()

    def test_context_menu_actions(self):
        v = ElaMarkdownViewer()
        v.setMarkdown("```python\nprint(1)\n```")
        menu = v._create_context_menu()
        labels = [action.text() for action in menu.actions()]
        assert "复制代码块" in labels and "复制全文" in labels
        menu.deleteLater()
        v.deleteLater()

    def test_copy_code_at_cursor_emits_signal(self, qapp):
        v = ElaMarkdownViewer()
        v.setMarkdown("```python\nprint(1)\n```")
        from PyQt5.QtGui import QTextTable

        table = None
        stack = [v.document().rootFrame()]
        while stack:
            frame = stack.pop()
            for child in frame.childFrames():
                if isinstance(child, QTextTable):
                    table = child
                stack.append(child)
        assert table is not None

        cursor = QTextCursor(v.document())
        cursor.setPosition(table.cellAt(0, 0).firstCursorPosition().position())
        v.textBrowser().setTextCursor(cursor)

        received = []
        v.codeCopied.connect(received.append)
        v._copy_code_at_cursor()
        qapp.processEvents()
        assert received and received[0].strip() == "print(1)"
        assert qapp.clipboard().text().strip() == "print(1)"
        v.deleteLater()

    def test_copy_full_text(self, qapp):
        v = ElaMarkdownViewer()
        v.setMarkdown("hello world")
        v._copy_all()
        qapp.processEvents()
        assert "hello world" in qapp.clipboard().text()
        v.deleteLater()
