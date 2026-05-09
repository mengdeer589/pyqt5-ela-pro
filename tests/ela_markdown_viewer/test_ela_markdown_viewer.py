from __future__ import annotations

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro.ela_markdown_viewer import ElaMarkdownViewer


class TestElaMarkdownViewerInit:
    def test_initialization_with_defaults(self):
        v = ElaMarkdownViewer()
        assert v._border_radius == 0
        assert v._text_browser is not None
        assert v._text_browser.isReadOnly() is True
        assert v._text_browser.openExternalLinks() is True
        v.deleteLater()

    def test_initially_no_markdown(self):
        v = ElaMarkdownViewer()
        assert v.markdown() == ""
        v.deleteLater()


class TestElaMarkdownViewerMarkdown:
    def test_set_markdown(self):
        v = ElaMarkdownViewer()
        v.setMarkdown("# Hello\nWorld")
        assert "# Hello" in v.markdown()
        v.deleteLater()

    def test_set_markdown_empty(self):
        v = ElaMarkdownViewer()
        v.setMarkdown("")
        assert v.markdown() == ""
        v.deleteLater()


class TestElaMarkdownViewerBorderRadius:
    def test_border_radius_default(self):
        v = ElaMarkdownViewer()
        assert v.borderRadius() == 0
        v.deleteLater()

    def test_set_border_radius(self):
        v = ElaMarkdownViewer()
        v.setBorderRadius(8)
        assert v.borderRadius() == 8
        v.deleteLater()


class TestElaMarkdownViewerTheme:
    def test_on_theme_changed_applies_style(self):
        v = ElaMarkdownViewer()
        from PyQt5ElaWidgetTools import ElaThemeType
        v._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert v._theme_mode == ElaThemeType.ThemeMode.Dark
        v.deleteLater()


class TestElaMarkdownViewerDeleteLater:
    def test_delete_later_cleans_up(self):
        v = ElaMarkdownViewer()
        v.deleteLater()
