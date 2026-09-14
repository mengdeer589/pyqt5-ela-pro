"""Tests for ElaMarkdownViewer quote-reply mapping (block-level approximation)."""

from __future__ import annotations

from PyQt5.QtGui import QTextCursor

from pyqt5_ela_pro.ela_markdown_viewer import ElaMarkdownViewer

SOURCE = """# 一级标题

普通段落 **加粗** 内容。

- 列表项一
- 列表项二

```python
x = 1
y = 2
```
"""


def _select_block(viewer: ElaMarkdownViewer, needle: str) -> None:
    cursor = viewer.document().find(needle)
    assert not cursor.isNull(), needle
    block = cursor.block()
    selection = QTextCursor(block)
    selection.movePosition(QTextCursor.MoveOperation.StartOfBlock)
    selection.movePosition(
        QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor
    )
    viewer.textBrowser().setTextCursor(selection)


def _code_cell_cursor(viewer: ElaMarkdownViewer) -> QTextCursor:
    table = [
        t for t in viewer._iter_tables(viewer.document()) if viewer._is_code_table(t)
    ][0]
    cell = table.cellAt(table.rows() - 1, 0)
    cursor = QTextCursor(cell.firstCursorPosition())
    cursor.movePosition(
        QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor
    )
    return cursor


class TestMarkdownSelection:
    def test_no_selection_returns_empty(self):
        v = ElaMarkdownViewer()
        v.setMarkdown(SOURCE)
        assert v.markdownSelection() == ""
        v.deleteLater()

    def test_heading_source(self):
        v = ElaMarkdownViewer()
        v.setMarkdown(SOURCE)
        _select_block(v, "一级标题")
        assert v.markdownSelection() == "# 一级标题"
        v.deleteLater()

    def test_paragraph_source_with_inline_markup(self):
        v = ElaMarkdownViewer()
        v.setMarkdown(SOURCE)
        _select_block(v, "普通段落")
        assert v.markdownSelection() == "普通段落 **加粗** 内容。"
        v.deleteLater()

    def test_list_item_source(self):
        v = ElaMarkdownViewer()
        v.setMarkdown(SOURCE)
        _select_block(v, "列表项一")
        assert v.markdownSelection() == "- 列表项一"
        v.deleteLater()

    def test_code_selection_returns_whole_fence(self):
        v = ElaMarkdownViewer()
        v.setMarkdown(SOURCE)
        v.textBrowser().setTextCursor(_code_cell_cursor(v))
        quote = v.markdownSelection()
        assert quote == "```python\nx = 1\ny = 2\n```"
        v.deleteLater()

    def test_unmapped_block_falls_back_to_plain_text(self):
        v = ElaMarkdownViewer()
        v.setMarkdown("<think>\n内部推理\n</think>")
        _select_block(v, "思考过程")
        quote = v.markdownSelection()
        assert "思考过程" in quote
        v.deleteLater()


class TestSelectionQuoted:
    def test_copy_emits_signal_and_clipboard(self, qapp):
        v = ElaMarkdownViewer()
        v.setMarkdown(SOURCE)
        _select_block(v, "列表项二")

        received = []
        v.selectionQuoted.connect(received.append)
        v._copy_selection_markdown()
        qapp.processEvents()

        assert received == ["- 列表项二"]
        assert qapp.clipboard().text() == "- 列表项二"
        v.deleteLater()

    def test_menu_action_requires_selection(self):
        v = ElaMarkdownViewer()
        v.setMarkdown(SOURCE)

        menu = v._create_context_menu()
        actions = {action.text(): action for action in menu.actions()}
        assert "复制选中为 Markdown" in actions
        assert not actions["复制选中为 Markdown"].isEnabled()
        menu.deleteLater()

        _select_block(v, "一级标题")
        menu = v._create_context_menu()
        actions = {action.text(): action for action in menu.actions()}
        assert actions["复制选中为 Markdown"].isEnabled()
        menu.deleteLater()
        v.deleteLater()
