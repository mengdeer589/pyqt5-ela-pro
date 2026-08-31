"""
Markdown 查看器组件，风格参考 ElaWidgetTools 的 ElaMarkdownViewer。

基于 QTextBrowser 渲染 Markdown，支持主题自适应。

用法::

    viewer = ElaMarkdownViewer(parent=self)
    viewer.setMarkdown("# 标题\\n\\n正文内容")
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPainter, QPainterPath, QPaintEvent
from PyQt5.QtWidgets import QWidget, QTextBrowser, QVBoxLayout, QFrame

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaScrollBar

from .widget_base import ElaThemeWidget


class ElaMarkdownViewer(ElaThemeWidget):
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

        self._applyThemeStyle()

    def setMarkdown(self, text: str) -> None:
        """设置 Markdown 内容。

        :param text: Markdown 文本
        """
        self._text_browser.setMarkdown(text)

    def markdown(self) -> str:
        """获取当前 Markdown 内容。

        :returns: Markdown 文本
        """
        return self._text_browser.toMarkdown()

    def setBorderRadius(self, r: int) -> None:
        """设置圆角半径。

        :param r: 圆角半径（像素）
        """
        self._border_radius = max(0, r)
        self.update()

    def borderRadius(self) -> int:
        """获取圆角半径。

        :returns: 圆角半径（像素）
        """
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
        self.update()

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self._applyThemeStyle()

    def paintEvent(self, _event: Optional[QPaintEvent]) -> None:
        """绘制圆角背景（圆角半径为 0 时绘制普通矩形背景）。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg_color = eTheme.getThemeColor(
            self._theme_mode, ElaThemeType.ThemeColor.BasicPress
        )
        if self._border_radius > 0:
            path = QPainterPath()
            path.addRoundedRect(
                QRectF(self.rect()), self._border_radius, self._border_radius
            )
            painter.fillPath(path, bg_color)
        else:
            painter.fillRect(self.rect(), bg_color)
