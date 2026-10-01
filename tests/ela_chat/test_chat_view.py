"""ElaChatView 消息列表测试：增删改、流式、快照、贴底与空态。"""

from __future__ import annotations

import time

from _qthelpers import wait_until as _wait_until
from PyQt5.QtCore import QPoint, QPointF, Qt
from PyQt5.QtGui import QMouseEvent, QPalette, QWheelEvent
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QTextEdit
from PyQt5ElaWidgetTools import ElaThemeType

from pyqt5_ela_pro.chat import (
    ElaChatReasoningStyle,
    DISCLAIMER_TEXT,
    ElaChatRole,
    ElaChatStats,
    ElaChatStatus,
    ElaChatView,
    ElaChatWidget,
)


def _long_view(qapp, messages: int = 8) -> ElaChatView:
    view = ElaChatView()
    view.resize(420, 220)
    view.show()
    qapp.processEvents()
    for index in range(messages):
        view.addMessage(ElaChatRole.User, f"消息 {index} " + "内容" * 20)
    bar = view._scroll.verticalScrollBar()
    _wait_until(qapp, lambda: bar.maximum() > 0)
    return view


class TestMessages:
    def test_add_and_snapshot(self, qapp):
        view = ElaChatView()
        first = view.addMessage(ElaChatRole.User, "你好")
        second = view.addMessage(ElaChatRole.System, "提示")
        assert (first, second) == (1, 2)
        assert view.count() == 2
        snapshot = view.messages()
        assert [m.text for m in snapshot] == ["你好", "提示"]
        assert [m.role for m in snapshot] == [ElaChatRole.User, ElaChatRole.System]
        assert view.message(second).text == "提示"
        assert view.message(99) is None
        assert view.lastMessage().id == second
        view.deleteLater()

    def test_begin_append_end(self, qapp):
        view = ElaChatView()
        messageId = view.beginMessage(ElaChatRole.Assistant)
        assert view.message(messageId).status == ElaChatStatus.Streaming
        view.appendText(messageId, "部分")
        view.appendText(messageId, "内容")
        # 快照 text 是落定值；实时全文走气泡
        assert view.message(messageId).text == ""
        assert view.bubble(messageId).text() == "部分内容"
        finished = []
        view.messageStreamFinished.connect(
            lambda mid, status: finished.append((mid, status))
        )
        view.endMessage(messageId, ElaChatStatus.Stopped)
        assert finished == [(messageId, ElaChatStatus.Stopped)]
        assert view.message(messageId).status == ElaChatStatus.Stopped
        assert view.message(messageId).text == "部分内容"
        view.deleteLater()

    def test_update_remove_clear(self, qapp):
        view = ElaChatView()
        first = view.addMessage(ElaChatRole.User, "a")
        second = view.addMessage(ElaChatRole.Assistant, "b")
        removed = []
        view.messageRemoved.connect(removed.append)

        view.updateMessage(second, "b2")
        assert view.message(second).text == "b2"

        view.removeMessage(first)
        assert removed == [first]
        assert view.count() == 1
        assert view.bubble(first) is None

        view.clear()
        assert view.messages() == []
        assert view.bubble(second) is None
        view.deleteLater()

    def test_signals_order(self, qapp):
        view = ElaChatView()
        events = []
        view.messageAdded.connect(lambda mid, role: events.append(("added", mid, role)))
        view.messageUpdated.connect(lambda mid: events.append(("updated", mid)))
        view.messageStreamFinished.connect(
            lambda mid, status: events.append(("finished", mid, status))
        )
        messageId = view.beginMessage(ElaChatRole.Assistant)
        view.appendText(messageId, "x")
        view.endMessage(messageId)
        assert events[0] == ("added", messageId, ElaChatRole.Assistant)
        assert ("updated", messageId) in events
        assert events[-1] == ("finished", messageId, ElaChatStatus.Done)
        view.deleteLater()

    def test_append_unknown_id_ignored(self, qapp):
        view = ElaChatView()
        view.appendText(99, "x")
        view.endMessage(99)
        assert view.messages() == []
        view.deleteLater()


class TestEmptyState:
    def test_visibility_toggles(self, qapp):
        view = ElaChatView()
        view.show()
        qapp.processEvents()
        assert view._empty.isVisible()
        messageId = view.addMessage(ElaChatRole.User, "hi")
        qapp.processEvents()
        assert not view._empty.isVisible()
        view.removeMessage(messageId)
        qapp.processEvents()
        assert view._empty.isVisible()
        view.deleteLater()

    def test_suggestions_and_titles(self, qapp):
        view = ElaChatView()
        view.setEmptyTitle("标题")
        view.setEmptySubtitle("副标题")
        view.setSuggestions(["A", "B", ""])
        assert view.emptyTitle() == "标题"
        assert view.emptySubtitle() == "副标题"
        assert view.suggestions() == ["A", "B"]
        clicked = []
        view.suggestionClicked.connect(clicked.append)
        buttons = view._empty.findChildren(
            type(view._empty._suggestions_box.itemAt(0).widget())
        )
        assert len(buttons) == 2
        buttons[1].click()
        assert clicked == ["B"]
        view.deleteLater()


class TestStickToBottom:
    def test_follows_bottom_and_jump_button(self, qapp):
        view = _long_view(qapp)
        bar = view._scroll.verticalScrollBar()
        assert bar.maximum() > 0
        assert _wait_until(qapp, lambda: bar.value() >= bar.maximum() - 6)
        assert view.stickToBottom()

        bar.setValue(0)
        assert _wait_until(qapp, lambda: not view.stickToBottom())
        assert view._jump_button.isVisible()

        view._jump_button.click()
        assert _wait_until(qapp, lambda: bar.value() >= bar.maximum() - 6)
        assert view.stickToBottom()
        assert not view._jump_button.isVisible()
        view.deleteLater()

    def test_stick_disabled_does_not_follow(self, qapp):
        view = _long_view(qapp, messages=4)
        bar = view._scroll.verticalScrollBar()
        bar.setValue(0)
        qapp.processEvents()
        view.setStickToBottom(False)
        bar.setValue(0)
        view.addMessage(ElaChatRole.User, "新消息 " + "内容" * 20)
        for _ in range(10):
            qapp.processEvents()
            time.sleep(0.02)
        assert bar.value() < bar.maximum() - 6
        view.deleteLater()


class TestAppearancePropagation:
    def test_content_background_follows_theme(self, qapp):
        view = ElaChatView()
        content = view.contentWidget()
        content._onThemeChanged(ElaThemeType.ThemeMode.Light)
        assert content.palette().color(QPalette.ColorRole.Window).name() == "#f7f7f7"
        content._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert content.palette().color(QPalette.ColorRole.Window).name() == "#3a3a3a"
        view.deleteLater()

    def test_avatar_and_ratio_applied(self, qapp):
        view = ElaChatView()
        view.setAvatarVisible(False)
        view.setUserBubbleMaxWidth(0.5)
        messageId = view.addMessage(ElaChatRole.User, "hi")
        bubble = view.bubble(messageId)
        assert bubble.avatarVisible() is False
        assert bubble.maxWidthRatio() == 0.5

        view.setAvatarVisible(True)
        view.setUserBubbleMaxWidth(0.8)
        assert bubble.avatarVisible() is True
        assert bubble.maxWidthRatio() == 0.8
        view.deleteLater()


class TestReasoningLayer:
    def test_reasoning_stream(self, qapp):
        view = ElaChatView()
        messageId = view.beginMessage(ElaChatRole.Assistant)
        view.beginReasoning(messageId)
        assert view.bubble(messageId).reasoningBlock().isOpened()
        view.appendReasoning(messageId, "先想")
        view.appendReasoning(messageId, "再算")
        # 快照 reasoning 是落定值；实时全文走气泡
        assert view.message(messageId).reasoning == ""
        assert view.bubble(messageId).reasoning() == "先想再算"
        view.endReasoning(messageId, 800)
        assert view.message(messageId).reasoning_ms == 800.0
        assert view.message(messageId).reasoning == "先想再算"
        assert not view.bubble(messageId).reasoningBlock().isOpened()
        view.deleteLater()

    def test_set_reasoning_replaces(self, qapp):
        view = ElaChatView()
        messageId = view.addMessage(ElaChatRole.Assistant, "回答")
        view.setReasoning(messageId, "整体推理", 1200.0)
        snapshot = view.message(messageId)
        assert snapshot.reasoning == "整体推理"
        assert snapshot.reasoning_ms == 1200.0
        view.deleteLater()

    def test_unknown_id_ignored(self, qapp):
        view = ElaChatView()
        view.beginReasoning(99)
        view.appendReasoning(99, "x")
        view.endReasoning(99, 1.0)
        assert view.messages() == []
        view.deleteLater()


class TestToolLayer:
    def test_tool_call_flow(self, qapp):
        view = ElaChatView()
        messageId = view.beginMessage(ElaChatRole.Assistant)
        callId = view.addToolCall(messageId, "read_file", '{"path": "a"}')
        assert callId
        calls = view.toolCalls(messageId)
        assert len(calls) == 1
        assert calls[0].name == "read_file"
        assert calls[0].isRunning

        view.setToolCallResult(messageId, callId, "文件内容", ok=True)
        snapshot = view.message(messageId).tool_calls[0]
        assert snapshot.isDone
        assert snapshot.result == "文件内容"

        view.clearToolCalls(messageId)
        assert view.message(messageId).tool_calls == ()
        assert view.toolCalls(messageId) == []
        view.deleteLater()

    def test_unknown_id_ignored(self, qapp):
        view = ElaChatView()
        assert view.addToolCall(99, "tool") is None
        view.setToolCallResult(99, "x", "y")
        assert view.messages() == []
        view.deleteLater()


class TestStatsErrorAttachments:
    def test_stats_and_error(self, qapp):
        view = ElaChatView()
        messageId = view.beginMessage(ElaChatRole.Assistant)
        stats = ElaChatStats(
            prompt_tokens=1, completion_tokens=2, total_tokens=3, tps=9.0
        )
        view.setStepStats(messageId, stats)
        assert view.message(messageId).stats is stats

        view.setMessageError(messageId, "接口超时")
        snapshot = view.message(messageId)
        assert snapshot.error == "接口超时"
        assert snapshot.status == ElaChatStatus.Error
        view.deleteLater()

    def test_message_attachments(self, qapp):
        view = ElaChatView()
        messageId = view.addMessage(ElaChatRole.User, "看这个")
        view.setMessageAttachments(
            messageId, [{"name": "a.png", "path": "C:/tmp/a.png", "size": 1024}]
        )
        assert len(view.message(messageId).attachments) == 1
        view.addMessageAttachment(messageId, "b.txt", "C:/tmp/b.txt", 2)
        assert len(view.message(messageId).attachments) == 2
        view.deleteLater()

    def test_title_and_timestamp(self, qapp):
        view = ElaChatView()
        messageId = view.addMessage(ElaChatRole.Assistant, "hi")
        view.setMessageTitle(messageId, "deepseek")
        view.setMessageTimestamp(messageId, "12:34:56")
        snapshot = view.message(messageId)
        assert snapshot.title == "deepseek"
        assert snapshot.timestamp == "12:34:56"
        assert view.bubble(messageId).title() == "deepseek"
        view.deleteLater()


class TestMessageActions:
    def test_action_signals_carry_message_id(self, qapp):
        view = ElaChatView()
        messageId = view.addMessage(ElaChatRole.User, "hi")
        events = []
        copies = []
        view.messageActionTriggered.connect(lambda mid, key: events.append((mid, key)))
        view.copyRequested.connect(copies.append)
        view.bubble(messageId).actions().toolButton("copy").click()
        assert events == [(messageId, "copy")]
        assert copies == [messageId]
        view.deleteLater()

    def test_regenerate_hidden_until_turn_finishes(self, qapp):
        """底部行整行（含「重新生成」）在回合结束前不出现（与气泡层同一判定）。"""
        view = ElaChatView()
        messageId = view.beginMessage(ElaChatRole.Assistant)
        bubble = view.bubble(messageId)
        assert bubble.footer().isHidden() is True
        view.appendText(messageId, "写一半")
        assert bubble.footer().isHidden() is True

        view.endMessage(messageId)
        assert bubble.footer().isHidden() is False
        assert bubble.actions().toolButton("regenerate").isVisibleTo(bubble) is True
        view.deleteLater()

    def test_disclaimer_applies_to_existing_and_new_messages(self, qapp):
        """「AI 生成」提示：view 改一次覆盖已有 + 之后新增的助手消息。"""
        view = ElaChatView()
        first = view.bubble(view.addMessage(ElaChatRole.Assistant, "一"))
        second_id = view.addMessage(ElaChatRole.Assistant, "二")
        assert view.disclaimer() == DISCLAIMER_TEXT
        assert view.disclaimerVisible() is True

        view.setDisclaimer("统一提示：内容由 AI 生成")
        assert first.disclaimer() == "统一提示：内容由 AI 生成"
        assert view.bubble(second_id).disclaimer() == "统一提示：内容由 AI 生成"

        view.setDisclaimerVisible(False)
        assert view.disclaimerVisible() is False
        assert first.disclaimerVisible() is False
        new_id = view.addMessage(ElaChatRole.Assistant, "三")  # 新消息也继承
        assert view.bubble(new_id).disclaimerVisible() is False
        view.deleteLater()
        qapp.processEvents()

    def test_custom_action_passthrough(self, qapp):
        view = ElaChatView()
        messageId = view.addMessage(ElaChatRole.Assistant, "hi")
        events = []
        view.messageActionTriggered.connect(lambda mid, key: events.append((mid, key)))
        bubble = view.bubble(messageId)
        bubble.actions().addCustomAction("favorite", tooltip="收藏")
        bubble.actions().toolButton("favorite").click()
        assert events == [(messageId, "favorite")]
        view.deleteLater()

    def test_attachment_clicked_carries_message_id(self, qapp):
        view = ElaChatView()
        messageId = view.addMessage(ElaChatRole.User, "看附件")
        view.setMessageAttachments(messageId, [{"name": "a.txt", "path": "C:/a.txt"}])
        clicked = []
        view.attachmentClicked.connect(lambda mid, path: clicked.append((mid, path)))
        strip = view.bubble(messageId).attachmentStrip()
        strip.attachmentClicked.emit("C:/a.txt")
        assert clicked == [(messageId, "C:/a.txt")]
        view.deleteLater()


class TestViewPassthroughs:
    def test_duration_title_timestamp_emit_updates(self, qapp):
        view = ElaChatView()
        messageId = view.addMessage(ElaChatRole.Assistant, "hi")
        events = []
        view.messageUpdated.connect(events.append)

        view.setMessageDuration(messageId, 1500)
        view.setMessageTitle(messageId, "模型")
        view.setMessageTimestamp(messageId, "12:00:00")

        assert events == [messageId, messageId, messageId]
        assert view.message(messageId).duration_ms == 1500.0
        view.deleteLater()

    def test_style_and_grouping_applied(self, qapp):
        view = ElaChatView()
        view.setReasoningStyle(ElaChatReasoningStyle.Inline)
        view.setToolGrouping(False)
        assert view.reasoningStyle() == ElaChatReasoningStyle.Inline
        assert view.toolGrouping() is False
        messageId = view.addMessage(ElaChatRole.Assistant, "hi")
        bubble = view.bubble(messageId)
        assert bubble.reasoningStyle() == ElaChatReasoningStyle.Inline
        assert bubble.toolGrouping() is False
        view.deleteLater()

    def test_message_duration(self, qapp):
        view = ElaChatView()
        messageId = view.addMessage(ElaChatRole.Assistant, "hi")
        view.setMessageDuration(messageId, 1500)
        assert view.message(messageId).duration_ms == 1500.0
        assert view.bubble(messageId).duration() == 1500.0
        view.deleteLater()


class TestBatchRemoveAndSync:
    def test_remove_messages_from(self, qapp):
        view = ElaChatView()
        first = view.addMessage(ElaChatRole.User, "a")
        second = view.addMessage(ElaChatRole.Assistant, "b")
        third = view.addMessage(ElaChatRole.User, "c")
        removed = []
        view.messageRemoved.connect(removed.append)

        assert view.removeMessagesFrom(second) == [second, third]
        assert removed == [second, third]
        assert [m.id for m in view.messages()] == [first]
        assert view.removeMessagesFrom(999) == []
        view.deleteLater()

    def test_snapshot_stays_synchronous_for_readers(self, qapp):
        """未跑事件循环也能读到一致快照 —— 且与读取时机无关。

        完整反转后快照只含**已落定**内容，所以流式期间是空串；一致性
        （不跑事件循环也能立刻读到、与读几次无关）仍然成立，这正是
        落定语义的前提。
        """
        view = ElaChatView()
        messageId = view.beginMessage(ElaChatRole.Assistant)
        updates = []
        view.messageUpdated.connect(updates.append)

        for chunk in ("a", "b", "c"):
            view.appendText(messageId, chunk)

        # 未跑事件循环也能立刻读到，且读多少次都一样
        assert view.message(messageId).text == ""
        assert view.message(messageId).text == ""
        assert view.message(messageId).text == ""
        assert updates == [messageId, messageId, messageId]

        view.endMessage(messageId)
        assert view.message(messageId).text == "abc"
        view.deleteLater()

    def test_guard_installed_for_streamed_viewer_and_pruned(self, qapp):
        view = ElaChatView()
        messageId = view.beginMessage(ElaChatRole.Assistant)
        view.appendText(messageId, "hello")
        assert view.bubble(messageId).markdownViewer() is not None

        guards = view._guards_by_message.get(messageId, [])
        assert len(guards) == 1
        assert guards[0] in view._scroll_guards

        view.removeMessage(messageId)

        assert messageId not in view._guards_by_message
        assert guards[0] not in view._scroll_guards
        view.deleteLater()


class TestScrollBehavior:
    def test_jump_threshold(self, qapp):
        view = _long_view(qapp, messages=8)
        bar = view._scroll.verticalScrollBar()
        bar.setValue(0)
        qapp.processEvents()
        view.setJumpThreshold(0)
        assert view._jump_button.isVisible()
        view.setJumpThreshold(10**9)
        assert not view._jump_button.isVisible()
        view.setJumpThreshold(None)
        assert view.jumpThreshold() is None
        view.deleteLater()

    def test_nested_scroll_guard_installed(self, qapp):
        view = ElaChatView()
        messageId = view.addMessage(ElaChatRole.Assistant, "hi")
        viewer = view.bubble(messageId).markdownViewer()
        assert viewer is not None
        assert view.guardNestedScroll(viewer) is not None
        assert len(view._scroll_guards) >= 1
        view.deleteLater()

    def test_follow_timer_does_not_loop(self, qapp):
        view = _long_view(qapp)
        view._scroll_to_bottom_if_sticky()
        for _ in range(5):
            qapp.processEvents()
            time.sleep(0.02)
        assert not view._follow_timer.isActive()
        view.deleteLater()

    def test_tool_toggle_keeps_viewport(self, qapp):
        view = ElaChatView()
        view.resize(480, 260)
        view.show()
        qapp.processEvents()
        for index in range(6):
            view.addMessage(ElaChatRole.User, f"消息 {index} " + "内容" * 30)
        messageId = view.addMessage(ElaChatRole.Assistant, "回答 " + "内容" * 20)
        callId = view.addToolCall(messageId, "read", '{"path": "a.py"}')
        view.setToolCallResult(messageId, callId, "结果 " * 20)
        bar = view._scroll.verticalScrollBar()
        _wait_until(qapp, lambda: bar.maximum() > 0)
        # 等待异步渲染（Markdown）完全稳定后再测展开行为
        time.sleep(0.5)
        for _ in range(10):
            qapp.processEvents()

        # 1) 展开外层面板：内容增长但视口保持不动
        view.scrollToBottom()
        qapp.processEvents()
        before_value = bar.value()
        panel = view.bubble(messageId).toolPanel()
        panel.setOpened(True)
        for _ in range(10):
            qapp.processEvents()
            time.sleep(0.01)
        assert bar.maximum() > before_value
        assert bar.value() == before_value

        # 2) 暂停窗口结束后展开内层卡片，同样不带动视口
        time.sleep(0.4)
        for _ in range(5):
            qapp.processEvents()
        view.scrollToBottom()
        qapp.processEvents()
        before_value = bar.value()
        card = view.bubble(messageId)._tool_cards[callId]
        card.setOpened(True)
        for _ in range(10):
            qapp.processEvents()
            time.sleep(0.01)
        assert bar.maximum() > before_value
        assert bar.value() == before_value
        # 暂停窗口结束后也不会补一次滚动
        time.sleep(0.4)
        for _ in range(5):
            qapp.processEvents()
        assert bar.value() == before_value
        assert view.followHeld() is False
        view.deleteLater()

    def test_nested_scroll_guard_blocks_at_boundary(self, qapp):

        view = ElaChatView()
        inner = QTextEdit()
        inner.setPlainText("\n".join(f"行 {i}" for i in range(200)))
        inner.resize(120, 60)
        inner.show()
        qapp.processEvents()
        guard = view.guardNestedScroll(inner)
        assert guard is not None

        bar = inner.verticalScrollBar()
        assert bar.maximum() > 0
        bar.setValue(bar.maximum())
        event = QWheelEvent(
            QPointF(10, 10),
            QPointF(10, 10),
            QPoint(0, 0),
            QPoint(0, -120),
            0,
            Qt.Orientation.Vertical,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        )
        assert guard.eventFilter(inner.viewport(), event) is True

        bar.setValue(0)
        up_event = QWheelEvent(
            QPointF(10, 10),
            QPointF(10, 10),
            QPoint(0, 0),
            QPoint(0, 120),
            0,
            Qt.Orientation.Vertical,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        )
        assert guard.eventFilter(inner.viewport(), up_event) is True
        inner.deleteLater()
        view.deleteLater()


class TestScrollBar:
    """垂直滚动条必须**看得见、拖得动**。

    回归背景：``ElaScrollArea`` 构造时装了 ``ElaScrollBar`` 之后又强制
    ``ScrollBarAlwaysOff``（ElaScrollArea.cpp:16-19），滚动条永远不显示 ——
    滚轮能滚但没有把手。这几个用例守住 ``__init__`` 里那次
    ``setVerticalScrollBarPolicy(AsNeeded)`` 不被回退。
    """

    def test_default_policy_is_as_needed(self, qapp):

        view = ElaChatView()
        assert view.scrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded
        assert view.scrollBar() is view._scroll.verticalScrollBar()
        view.deleteLater()

    def test_visible_when_overflowing_hidden_when_fits(self, qapp):
        view = _long_view(qapp, messages=8)
        bar = view.scrollBar()
        assert bar.maximum() > 0
        assert bar.isVisible()
        # 内容不足一屏时 AsNeeded 语义：自动隐藏
        for messageId in [m.id for m in view.messages()]:
            view.removeMessage(messageId)
        assert _wait_until(qapp, lambda: bar.maximum() == 0)
        assert not bar.isVisible()
        view.deleteLater()

    def test_set_policy_toggles_visibility(self, qapp):

        view = _long_view(qapp, messages=8)
        bar = view.scrollBar()
        view.setScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        qapp.processEvents()
        assert view.scrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        assert not bar.isVisible()
        view.setScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        assert _wait_until(qapp, bar.isVisible)
        assert view.scrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded
        view.deleteLater()

    def test_reflow_release_resyncs_width_after_viewport_shrink(self, qapp):
        """冻结期间滚动条出现会窄化视口，解冻后必须把内容拉回视口宽度。

        否则内容比视口宽、水平方向又 AlwaysOff → 右侧被裁掉一个滚动条的宽度。
        """

        view = ElaChatView()
        view.resize(420, 260)
        view.show()
        qapp.processEvents()
        view.addMessage(ElaChatRole.Assistant, "短")
        qapp.processEvents()
        view.setResizeReflowDeferred(True, minMessages=0, delayMs=20)
        view.resize(460, 260)  # 冻结内容宽度
        # 冻结期间灌满内容 → 滚动条出现，视口窄 10px
        for index in range(6):
            view.addMessage(ElaChatRole.Assistant, f"消息 {index} " + "内容" * 20)
        assert _wait_until(qapp, lambda: view.scrollBar().maximum() > 0)
        assert view.scrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded
        assert _wait_until(qapp, lambda: view._resize_frozen_width == 0)
        assert view._content.width() == view._scroll.viewport().width()
        view.deleteLater()

    def test_drag_handle_scrolls_and_stops_following(self, qapp):

        view = _long_view(qapp, messages=8)
        bar = view.scrollBar()
        bar.setValue(0)
        qapp.processEvents()
        assert view.stickToBottom() is False

        # QTest.mouseMove 不带 buttons 位，拖动段要直发带 LeftButton 的事件
        QTest.mousePress(
            bar,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            QPoint(5, 10),
        )
        for y in (40, 80, 120):
            bar.setValue(0)
            qapp.sendEvent(
                bar,
                QMouseEvent(
                    QMouseEvent.Type.MouseMove,
                    QPointF(5, y),
                    Qt.MouseButton.NoButton,
                    Qt.MouseButton.LeftButton,
                    Qt.KeyboardModifier.NoModifier,
                ),
            )
            qapp.processEvents()
            assert bar.value() > 0
        QTest.mouseRelease(
            bar,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            QPoint(5, 120),
        )
        # 停在中间：既滚动了，又没回到底部
        assert 0 < bar.value() < bar.maximum()
        assert view._content.y() == -bar.value()
        # 手动拖动后不再贴底跟随
        assert view.stickToBottom() is False
        view.deleteLater()


class TestContentMaxWidth:
    """阅读宽度默认不限；宿主显式收紧时只作用于助手内容列。"""

    def test_default_unlimited(self, qapp):
        view = ElaChatView()
        assert view.contentMaxWidth() == 0
        messageId = view.addMessage(ElaChatRole.Assistant, "hi")
        assert view.bubble(messageId).contentMaxWidth() == 0
        assert view.bubble(messageId)._column.maximumWidth() == 16777215
        view.deleteLater()

    def test_user_message_unaffected(self, qapp):
        view = ElaChatView()
        messageId = view.addMessage(ElaChatRole.User, "hi")
        assert view.bubble(messageId).contentMaxWidth() == 0
        assert view.bubble(messageId)._column.maximumWidth() == 16777215
        view.deleteLater()

    def test_setter_applies_to_existing_and_disable(self, qapp):
        view = ElaChatView()
        messageId = view.addMessage(ElaChatRole.Assistant, "hi")
        view.setContentMaxWidth(500)
        # 限的是整列（正文 + 附件条 + 底部行），不是只限正文 ——
        # 否则宽窗口下 footer 比正文列宽，往右伸出去
        bubble = view.bubble(messageId)
        assert bubble._column.maximumWidth() == 500
        view.setContentMaxWidth(0)
        assert bubble._column.maximumWidth() == 16777215
        assert view.contentMaxWidth() == 0
        view.deleteLater()

    def test_column_wraps_content_and_footer(self, qapp):
        """内容列必须同时装下正文、附件条与底部行（否则限宽时 footer 伸出列外）。"""
        view = ElaChatView()
        messageId = view.addMessage(ElaChatRole.Assistant, "hi")
        bubble = view.bubble(messageId)
        assert bubble._content.parentWidget() is bubble._column
        assert bubble._footer.parentWidget() is bubble._column
        assert bubble._attachments_host.parentWidget() is bubble._column
        view.deleteLater()

    def test_widget_passthrough(self, qapp):

        chat = ElaChatWidget()
        assert chat.chatView().contentMaxWidth() == 0
        chat.chatView().setContentMaxWidth(640)
        assert chat.chatView().contentMaxWidth() == 640
        chat.deleteLater()


class TestResizeReflowDeferred:
    """交互 resize 延迟重排：拖动期间冻结内容宽度，停手统一 reflow。"""

    def _view_with_messages(self, qapp, count: int = 4) -> ElaChatView:
        view = ElaChatView()
        view.resize(420, 260)
        view.show()
        qapp.processEvents()
        for index in range(count):
            view.addMessage(ElaChatRole.Assistant, f"消息 {index} " + "内容" * 10)
        qapp.processEvents()
        return view

    def test_freeze_then_release(self, qapp):
        view = self._view_with_messages(qapp)
        view.setResizeReflowDeferred(True, minMessages=2, delayMs=30)
        view.resize(460, 260)
        frozen = view._content.width()
        assert view._content.minimumWidth() == frozen
        assert view._content.maximumWidth() == frozen

        assert _wait_until(qapp, lambda: view._resize_frozen_width == 0)
        assert view._content.maximumWidth() == 16777215
        assert view._content.width() == view._scroll.viewport().width()
        view.deleteLater()

    def test_continuous_resize_freezes_once(self, qapp):
        view = self._view_with_messages(qapp)
        view.setResizeReflowDeferred(True, minMessages=2, delayMs=40)
        view.resize(460, 260)
        frozen = view._content.minimumWidth()
        for width in (470, 480, 490):
            view.resize(width, 260)
            qapp.processEvents()
            assert view._content.minimumWidth() == frozen  # 拖动期间保持首帧宽度
        assert view._resize_frozen_width > 0
        assert _wait_until(qapp, lambda: view._resize_frozen_width == 0)
        view.deleteLater()

    def test_below_threshold_not_frozen(self, qapp):
        view = self._view_with_messages(qapp)
        view.setResizeReflowDeferred(True, minMessages=50, delayMs=30)
        view.resize(460, 260)
        assert view._resize_frozen_width == 0
        assert view._content.maximumWidth() == 16777215
        view.deleteLater()

    def test_disabled_not_frozen(self, qapp):
        view = self._view_with_messages(qapp)
        view.setResizeReflowDeferred(False, minMessages=2)
        assert view.resizeReflowDeferred() is False
        view.resize(460, 260)
        assert view._resize_frozen_width == 0
        view.deleteLater()

    def test_release_returns_to_bottom(self, qapp):
        view = ElaChatView()
        view.resize(420, 200)
        view.show()
        qapp.processEvents()
        for index in range(6):
            view.addMessage(ElaChatRole.Assistant, f"消息 {index} " + "内容" * 20)
        view.setResizeReflowDeferred(True, minMessages=2, delayMs=20)
        view.scrollToBottom()
        qapp.processEvents()
        view.resize(380, 200)
        assert _wait_until(qapp, lambda: view._resize_frozen_width == 0)
        assert _wait_until(qapp, lambda: view._atBottom())
        view.deleteLater()
