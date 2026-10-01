"""聊天组件性能冒烟测试（宽松阈值，仅防止明显回归）。"""

from __future__ import annotations

import time

from _qthelpers import wait_until as _wait_until

from pyqt5_ela_pro.chat import (
    ElaChatReasoningStyle,
    ElaChatRole,
    ElaChatStats,
    ElaChatStatus,
    ElaChatView,
    ElaChatWidget,
)


class TestChatPerformance:
    def test_many_messages_render_budget(self, qapp):
        view = ElaChatView()
        view.resize(480, 320)
        view.show()
        qapp.processEvents()
        start = time.monotonic()
        for index in range(30):
            view.addMessage(ElaChatRole.User, f"第 {index} 条消息 " + "内容" * 10)
        elapsed = time.monotonic() - start
        assert view.count() == 30
        assert elapsed < 5.0

        # 快照查询不随消息数明显退化
        start = time.monotonic()
        for _ in range(200):
            view.messages()
        assert time.monotonic() - start < 1.0
        view.deleteLater()

    def test_streaming_chunks_budget(self, qapp):
        chat = ElaChatWidget()
        chat.resize(520, 360)
        chat.show()
        qapp.processEvents()
        chat.sendUserMessage("长回答")
        messageId = chat.beginAssistantMessage()
        start = time.monotonic()
        for index in range(300):
            chat.chatView().appendText(messageId, f"分片 {index}，")
        elapsed = time.monotonic() - start
        assert elapsed < 5.0
        chat.endAssistantMessage()
        assert chat.chatView().message(messageId).status == ElaChatStatus.Done
        assert chat.chatView().message(messageId).text.count("分片") == 300

        # 嵌入模式高度贴合内容：不含文末空白，但不裁剪正文
        viewer = chat.chatView().bubble(messageId).markdownViewer()
        document = viewer.document()

        def _hugged_content():
            last = document.lastBlock()
            rect = document.documentLayout().blockBoundingRect(last)
            return (
                rect.height() > 0
                and viewer.height() >= rect.bottom()
                and viewer.height() <= document.size().height()
            )

        assert _wait_until(qapp, _hugged_content)
        chat.deleteLater()

    def test_rich_messages_budget(self, qapp):
        view = ElaChatView()
        view.resize(480, 320)
        view.show()
        qapp.processEvents()
        stats = ElaChatStats(
            prompt_tokens=10, completion_tokens=20, total_tokens=30, tps=40.0
        )
        start = time.monotonic()
        for index in range(12):
            messageId = view.addMessage(
                ElaChatRole.Assistant, f"第 {index} 条回答 " + "内容" * 8
            )
            view.setReasoning(messageId, f"推理 {index}", 500.0)
            callId = view.addToolCall(messageId, "read_file", '{"path": "a.txt"}')
            view.setToolCallResult(messageId, callId, "结果 " + str(index))
            view.setStepStats(messageId, stats)
        elapsed = time.monotonic() - start
        assert view.count() == 12
        assert elapsed < 5.0
        snapshot = view.message(12)
        assert snapshot.reasoning == "推理 11"
        assert len(snapshot.tool_calls) == 1
        assert snapshot.stats is stats
        view.deleteLater()

    def test_long_stream_budget(self, qapp):
        """长正文流：分片缓冲后逐片开销恒定（旧实现为 O(n²) 字符串拼接）。"""
        chat = ElaChatWidget()
        message_id = chat.beginAssistantMessage()
        chunk = "这是一个稍长一些的分片内容用于放大字符串拼接开销"
        chunks = 4000
        start = time.monotonic()
        for _ in range(chunks):
            chat.chatView().appendText(message_id, chunk)
        elapsed = time.monotonic() - start
        assert elapsed < 5.0
        # 实时全文走气泡（纯读取，不物化 part.text）
        bubble = chat.chatView().bubble(message_id)
        assert bubble.text() == chunk * chunks
        # 快照在回合结束前是落定值（空），结束后才是完整正文
        assert chat.chatView().message(message_id).text == ""
        chat.endAssistantMessage(message_id)
        assert chat.chatView().message(message_id).text == chunk * chunks
        chat.deleteLater()

    def test_long_inline_reasoning_budget(self, qapp):
        """长思考流（内联）：标题增量扫描，避免逐片全量正则。"""
        chat = ElaChatWidget()
        message_id = chat.beginAssistantMessage()
        bubble = chat.chatView().bubble(message_id)
        bubble.setReasoningStyle(ElaChatReasoningStyle.Inline)
        chat.chatView().beginReasoning(message_id)
        chunks = 3000
        start = time.monotonic()
        chat.chatView().appendReasoning(message_id, "# 分析步骤\n")
        for _ in range(chunks):
            chat.chatView().appendReasoning(message_id, "推理分片内容")
        elapsed = time.monotonic() - start
        assert elapsed < 5.0
        assert bubble.reasoning() == "# 分析步骤\n" + "推理分片内容" * chunks
        assert chat.chatView().message(message_id).reasoning == ""
        chat.endAssistantMessage(message_id)
        assert (
            chat.chatView().message(message_id).reasoning
            == "# 分析步骤\n" + "推理分片内容" * chunks
        )
        assert bubble.thinkingRow().heading() == "分析步骤"
        chat.deleteLater()

    def test_resize_reflow_deferred_budget(self, qapp):
        """延迟重排：拖动期间冻结宽度，耗时明显低于逐次 reflow。"""
        view = ElaChatView()
        view.resize(480, 320)
        view.show()
        qapp.processEvents()
        md = "## 标题\n\n内容段落。" * 8
        for _ in range(60):
            view.addMessage(ElaChatRole.Assistant, md)
        qapp.processEvents()

        view.setResizeReflowDeferred(False)
        start = time.monotonic()
        for index in range(6):
            view.resize(440 + (index % 2) * 40, 320)
            qapp.processEvents()
        normal = time.monotonic() - start

        view.setResizeReflowDeferred(True, minMessages=2, delayMs=200)
        start = time.monotonic()
        for index in range(6):
            view.resize(460 + (index % 2) * 40, 320)
            qapp.processEvents()
        deferred = time.monotonic() - start
        assert view._resize_frozen_width > 0
        view.setResizeReflowDeferred(True, minMessages=2, delayMs=0)
        assert _wait_until(qapp, lambda: view._resize_frozen_width == 0)
        assert deferred < max(normal * 0.8, 0.1)
        view.deleteLater()

    def test_suspension_bounds_live_viewers(self, qapp):
        """视口外挂起：大消息量下远离视口的查看器被替换为占位。"""
        view = ElaChatView()
        view.resize(360, 200)
        view.show()
        qapp.processEvents()
        view.setViewportSuspension(True, minMessages=2)
        ids = [
            view.addMessage(ElaChatRole.Assistant, "长内容 " * 60) for _ in range(10)
        ]
        bar = view._scroll.verticalScrollBar()
        assert _wait_until(qapp, lambda: bar.maximum() > 0)
        bar.setValue(0)
        assert _wait_until(
            qapp,
            lambda: sum(view.bubble(mid).viewersSuspended() for mid in ids) >= 1,
        )
        assert view.bubble(ids[-1]).viewersSuspended() is True
        assert view.bubble(ids[-1]).markdownViewer() is None
        view.deleteLater()
