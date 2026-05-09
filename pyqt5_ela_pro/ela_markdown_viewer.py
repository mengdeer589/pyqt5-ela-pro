"""
Markdown 查看器组件，风格参考 ElaWidgetTools 的 ElaMarkdownViewer。

基于 QTextBrowser 渲染 Markdown，支持主题自适应。

用法::

    viewer = ElaMarkdownViewer(parent=self)
    viewer.setMarkdown("# 标题\\n\\n正文内容")
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtWidgets import QWidget, QTextBrowser, QVBoxLayout, QFrame

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaScrollBar

from ._internal import _ThemeAwareMixin


class ElaMarkdownViewer(_ThemeAwareMixin, QWidget):
    """Markdown 查看器。

    基于 QTextBrowser 渲染 Markdown，支持深浅色主题适配。

    :param parent: 父控件
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._border_radius = 0
        self.setObjectName("ElaMarkdownViewer")

        self._text_browser = QTextBrowser(self)
        self._text_browser.setFrameShape(QFrame.Shape.NoFrame)
        self._text_browser.setReadOnly(True)
        self._text_browser.setOpenExternalLinks(True)

        v_bar = ElaScrollBar(self._text_browser)
        self._text_browser.setVerticalScrollBar(v_bar)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._text_browser)

        self._theme_mode = eTheme.getThemeMode()
        self._applyThemeStyle()

    def setMarkdown(self, text: str) -> None:
        self._text_browser.setMarkdown(text)

    def markdown(self) -> str:
        return self._text_browser.toMarkdown()

    def setBorderRadius(self, r: int) -> None:
        self._border_radius = r
        self.update()

    def borderRadius(self) -> int:
        return self._border_radius

    def _applyThemeStyle(self) -> None:
        mode = self._theme_mode
        text_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicText)
        link_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.PrimaryNormal)
        code_bg = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBaseDeep)
        css = (
            f"QTextBrowser {{ background-color: transparent; color: {text_color.name()}; }}"
            f"a {{ color: {link_color.name()}; }}"
            f"code, pre {{ background-color: {code_bg.name()}; }}"
        )
        self._text_browser.setStyleSheet(css)

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self._applyThemeStyle()
