"""批量加载与渐进渲染测试（``beginBatch`` / ``endBatch``）。"""

from __future__ import annotations

import time

from _qthelpers import wait_until as _wait_until

from pyqt5_ela_pro.chat import (
    ElaChatPartKind,
    ElaChatRole,
    ElaChatView,
    ElaChatWidget,
)

MD = "## 标题\n\n这是**回答**，包含 `代码` 与列表：\n\n- 项目一\n- 项目二\n"


class TestBatchRendering:
    def test_defers_markdown_until_end(self, qapp):
        view = ElaChatView()
        view.resize(480, 320)
        view.show()
        qapp.processEvents()

        view.beginBatch()
        assert view.isBatchActive() is True
        first = view.addMessage(ElaChatRole.Assistant, MD)
        second = view.addMessage(ElaChatRole.Assistant, MD)
        bubble = view.bubble(first)
        assert bubble.renderDeferred() is True
        assert bubble.hasPendingRender() is True
        # 延迟期间：快照 text 正确，parts 尚未同步，viewer 未渲染
        assert view.message(first).text == MD
        assert view.message(first).parts == ()
        assert bubble.markdownViewer().markdown() == ""
        view.endBatch()
        assert view.isBatchActive() is False

        assert _wait_until(
            qapp,
            lambda: (
                "标题" in view.bubble(first).markdownViewer().markdown()
                and "标题" in view.bubble(second).markdownViewer().markdown()
            ),
        )
        message = view.message(first)
        assert message.text == MD
        assert [part.kind for part in message.parts] == [ElaChatPartKind.Text]
        assert view.bubble(first).hasPendingRender() is False
        view.deleteLater()

    def test_batch_finished_signal_once(self, qapp):
        view = ElaChatView()
        view.resize(480, 320)
        view.show()
        qapp.processEvents()
        events = []
        view.batchRenderFinished.connect(lambda: events.append(True))

        view.beginBatch()
        view.addMessage(ElaChatRole.Assistant, MD)
        view.endBatch()
        assert _wait_until(qapp, lambda: bool(events))
        assert events == [True]
        view.deleteLater()

    def test_nested_batch_starts_once(self, qapp):
        view = ElaChatView()
        view.resize(480, 320)
        view.show()
        qapp.processEvents()
        events = []
        view.batchRenderFinished.connect(lambda: events.append(True))

        view.beginBatch()
        view.beginBatch()
        messageId = view.addMessage(ElaChatRole.Assistant, MD)
        view.endBatch()
        assert view.isBatchActive() is True
        assert view.bubble(messageId).renderDeferred() is True
        view.endBatch()
        assert view.isBatchActive() is False
        assert _wait_until(qapp, lambda: bool(events))
        assert events == [True]
        view.deleteLater()

    def test_outside_batch_renders_immediately(self, qapp):
        view = ElaChatView()
        view.resize(480, 320)
        view.show()
        qapp.processEvents()
        messageId = view.addMessage(ElaChatRole.Assistant, MD)
        assert view.bubble(messageId).renderDeferred() is False
        assert "标题" in view.bubble(messageId).markdownViewer().markdown()
        view.deleteLater()

    def test_batch_user_message_not_deferred(self, qapp):
        view = ElaChatView()
        view.resize(480, 320)
        view.show()
        qapp.processEvents()
        view.beginBatch()
        messageId = view.addMessage(ElaChatRole.User, "用户消息")
        assert view.bubble(messageId).renderDeferred() is False
        view.endBatch()
        assert view.message(messageId).text == "用户消息"
        view.deleteLater()

    def test_widget_passthrough(self, qapp):
        chat = ElaChatWidget()
        chat.resize(480, 320)
        chat.show()
        qapp.processEvents()
        events = []
        chat.batchRenderFinished.connect(lambda: events.append(True))
        chat.chatView().beginBatch()
        assert chat.chatView().isBatchActive() is True
        messageId = chat.addMessage(ElaChatRole.Assistant, MD)
        chat.chatView().endBatch()
        assert chat.chatView().isBatchActive() is False
        assert _wait_until(qapp, lambda: bool(events))
        assert "标题" in chat.chatView().message(messageId).text
        chat.deleteLater()

    def test_batch_budget(self, qapp):
        """批量建骨架应远快于同步渲染（渐进补齐）。"""
        view = ElaChatView()
        view.resize(480, 320)
        view.show()
        qapp.processEvents()
        count = 200
        start = time.monotonic()
        view.beginBatch()
        ids = [view.addMessage(ElaChatRole.Assistant, MD) for _ in range(count)]
        view.endBatch()
        skeleton = time.monotonic() - start
        assert skeleton < 1.5
        assert view.count() == count
        assert _wait_until(
            qapp,
            lambda: all(not view.bubble(mid).hasPendingRender() for mid in ids),
            timeout_ms=15000,
        )
        assert view.message(ids[-1]).text == MD
        view.deleteLater()
