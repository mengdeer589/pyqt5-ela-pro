"""ElaMarkdownViewer 嵌入模式测试（聊天消息等外层滚动容器场景）。"""

from __future__ import annotations


from _qthelpers import wait_until as _wait_until
from PyQt5.QtCore import QPoint, QPointF, Qt
from PyQt5.QtGui import QColor, QImage, QWheelEvent
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5ElaWidgetTools import ElaThemeType

from pyqt5_ela_pro.ela_markdown_viewer import ElaMarkdownViewer

SHORT = "一行文本"
LONG = "\n\n".join(f"第 {i} 段正文，用于把文档高度撑起来。" for i in range(20))
CODE = "```python\nprint('hi')\nprint('there')\n```"


def _render_image(
    viewer: ElaMarkdownViewer, width: int = 320, height: int = 240
) -> QImage:
    image = QImage(width, height, QImage.Format_ARGB32)
    image.fill(QColor(0, 0, 0, 0))
    viewer.resize(width, height)
    viewer.render(image, flags=QWidget.RenderFlag.DrawChildren)
    return image


class TestEmbeddedMode:
    def test_background_transparent_when_embedded(self, qapp):
        viewer = ElaMarkdownViewer()
        viewer.setMarkdown(SHORT)
        viewer.show()
        qapp.processEvents()

        opaque = _render_image(viewer).pixelColor(4, 4)
        assert opaque.alpha() == 255

        viewer.setEmbeddedMode(True)
        qapp.processEvents()
        transparent = _render_image(viewer).pixelColor(4, 4)
        assert transparent.alpha() == 0

        viewer.setEmbeddedMode(False)
        qapp.processEvents()
        restored = _render_image(viewer).pixelColor(4, 4)
        assert restored.alpha() == 255
        viewer.deleteLater()

    def test_scrollbars_and_wheel(self, qapp):
        viewer = ElaMarkdownViewer()
        viewer.setMarkdown(LONG)
        browser = viewer.textBrowser()

        viewer.setEmbeddedMode(True)
        assert (
            browser.verticalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        assert (
            browser.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        assert browser.forward_wheel is True

        event = QWheelEvent(
            QPointF(10, 10),
            QPointF(10, 10),
            QPoint(0, 0),
            QPoint(0, -120),
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.NoScrollPhase,
            False,
        )
        QApplication.sendEvent(browser, event)
        assert not event.isAccepted()

        viewer.setEmbeddedMode(False)
        assert browser.verticalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded
        assert browser.forward_wheel is False
        viewer.deleteLater()

    def test_height_follows_document(self, qapp):
        viewer = ElaMarkdownViewer()
        viewer.setEmbeddedMode(True)
        viewer.show()
        viewer.setMarkdown(SHORT)
        qapp.processEvents()
        short_height = viewer.height()

        viewer.setMarkdown(LONG)
        qapp.processEvents()
        long_height = viewer.height()
        assert long_height > short_height

        document_height = viewer.document().size().height()
        assert abs(long_height - document_height) <= 4
        assert viewer.minimumHeight() == viewer.maximumHeight() == long_height
        viewer.deleteLater()

    def test_height_updates_while_streaming(self, qapp):
        viewer = ElaMarkdownViewer()
        viewer.setEmbeddedMode(True)
        viewer.show()
        viewer.beginStream()
        viewer.appendMarkdown("第一段")
        assert _wait_until(qapp, lambda: viewer.height() > 10)
        first = viewer.height()
        viewer.appendMarkdown("\n\n" + "\n\n".join(f"更多内容 {i}" for i in range(15)))
        assert _wait_until(qapp, lambda: viewer.height() > first)
        viewer.endStream()
        assert _wait_until(
            qapp,
            lambda: abs(viewer.height() - viewer.document().size().height()) <= 4,
        )
        viewer.deleteLater()

    def test_theme_switch_keeps_transparent(self, qapp):
        viewer = ElaMarkdownViewer()
        viewer.setMarkdown(SHORT)
        viewer.setEmbeddedMode(True)
        viewer.show()
        qapp.processEvents()

        viewer._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        qapp.processEvents()
        pixel = _render_image(viewer).pixelColor(4, 4)
        assert pixel.alpha() == 0
        assert viewer.embeddedMode() is True
        viewer.deleteLater()

    def test_code_copy_buttons_still_available(self, qapp):
        viewer = ElaMarkdownViewer()
        viewer.setEmbeddedMode(True)
        viewer.setMarkdown(CODE)
        viewer.show()
        qapp.processEvents()
        assert viewer._code_buttons
        viewer.deleteLater()

    def test_extra_padding_applied(self, qapp):
        viewer = ElaMarkdownViewer()
        viewer.setEmbeddedMode(True)
        viewer.setMarkdown(SHORT)
        qapp.processEvents()
        base = viewer.height()
        viewer.setEmbeddedExtra(20)
        qapp.processEvents()
        assert viewer.height() == base + 18  # 20 - 默认 2
        assert viewer.embeddedExtra() == 20
        viewer.deleteLater()

    def test_trim_bottom_hugs_content(self, qapp):
        viewer = ElaMarkdownViewer()
        viewer.setEmbeddedMode(True)
        assert viewer.embeddedTrimBottom() is False

        viewer.setEmbeddedTrimBottom(True)
        assert viewer.embeddedTrimBottom() is True
        viewer.show()
        viewer.setMarkdown(SHORT)
        qapp.processEvents()

        document = viewer.document()
        last_rect = document.documentLayout().blockBoundingRect(document.lastBlock())
        # 文末段落下边距（12px）不再计入高度
        assert viewer.height() < document.size().height()
        # 正文没有被裁剪：最后一行底边仍在控件内
        assert viewer.height() >= last_rect.bottom()
        viewer.deleteLater()

    def test_trim_bottom_keeps_table_bottom(self, qapp):
        viewer = ElaMarkdownViewer()
        viewer.setEmbeddedMode(True)
        viewer.setEmbeddedTrimBottom(True)
        viewer.show()
        viewer.setMarkdown("| a | b |\n|---|---|\n| 1 | 2 |")
        qapp.processEvents()

        document = viewer.document()
        last_rect = document.documentLayout().blockBoundingRect(document.lastBlock())
        # 表格 / 非段落结尾走 min 守卫：内容边界不会被裁掉
        assert last_rect.height() > 0
        assert viewer.height() >= last_rect.bottom()
        viewer.deleteLater()
