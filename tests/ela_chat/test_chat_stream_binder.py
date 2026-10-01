"""ElaChatStreamBinder 映射器测试：步骤边界、思考复用、工具状态与摘要。"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from PyQt5 import sip
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro.chat import (
    ElaChatMockBackend,
    ElaChatPartKind,
    ElaChatStats,
    ElaChatStatus,
    ElaChatStreamBinder,
    ElaChatWidget,
)


class _Clock:
    """可推进的假时钟（秒）。"""

    def __init__(self, now: float = 1000.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, ms: float) -> None:
        self.now += ms / 1000.0


class _FakeWorker(QObject):
    """最小后端（信号契约与 ElaChatMockBackend 同构）。"""

    llmStarted = pyqtSignal()
    chunkReceived = pyqtSignal(object)
    toolStarted = pyqtSignal(dict)
    toolEnded = pyqtSignal(dict, str)
    statsReady = pyqtSignal(object, float, float)
    emptyTurn = pyqtSignal(str)

    def __init__(self, ready: bool = True) -> None:
        super().__init__()
        self.ask_calls: list = []
        self.regenerate_calls: list = []
        self.shutdown_calls: list = []
        self.cancel_calls: list = []
        self.ready = ready

    def ask(self, text: str) -> bool:
        self.ask_calls.append(text)
        return self.ready

    def regenerate(self, text: str) -> bool:
        self.regenerate_calls.append(text)
        return self.ready

    def cancel(self) -> None:
        self.cancel_calls.append(True)

    def shutdown(self) -> None:
        self.shutdown_calls.append(True)


def _begin(chat: ElaChatWidget, binder: ElaChatStreamBinder) -> int:
    chat.sendUserMessage("问")
    messageId = chat.beginAssistantMessage()
    binder.beginTurn()
    return messageId


class TestFullTurn:
    def test_parts_and_summary(self, qapp):
        clock = _Clock()
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, clock)
        _begin(chat, binder)

        clock.advance(100)
        binder.beginRound()
        binder.reasoning("想")
        binder.reasoning("考")
        clock.advance(200)
        binder.answer("正文")
        binder.stats(
            SimpleNamespace(
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15,
                prompt_cache_hit_tokens=3,
            ),
            ttftMs=120,
            tps=42,
        )
        binder.toolStart("t1", "read", {"path": "a.txt"})
        binder.toolEnd("t1", "已读取")
        clock.advance(300)
        binder.beginRound()
        binder.toolStart("t2", "patch", '{"path": "b.md"}')
        binder.toolEnd("t2", "Error: 文件被占用")
        clock.advance(100)
        binder.stats(
            SimpleNamespace(
                prompt_tokens=20,
                completion_tokens=8,
                total_tokens=28,
                prompt_cache_hit_tokens=0,
                prompt_tokens_details=SimpleNamespace(cached_tokens=7),
            )
        )
        binder.answer("后半")
        clock.advance(300)
        summary = binder.finish()

        assert binder.roundIndex() == 2
        assert binder.isOpen() is False
        assert summary.status == ElaChatStatus.Done
        assert summary.hadText is True
        assert summary.isEmptyReply() is False
        assert summary.durationMs == pytest.approx(1000.0)

        message = chat.chatView().messages()[-1]
        assert message.status == ElaChatStatus.Done
        assert message.stepCount == 2
        assert [part.kind for part in message.parts] == [
            ElaChatPartKind.Reasoning,
            ElaChatPartKind.Text,
            ElaChatPartKind.Stats,
            ElaChatPartKind.Tool,
            ElaChatPartKind.Tool,
            ElaChatPartKind.Stats,
            ElaChatPartKind.Text,
        ]
        # 同一轮的推理分片复用同一思考段
        assert len(message.partsOfKind(ElaChatPartKind.Reasoning)) == 1
        assert message.reasoning == "想考"
        assert message.reasoning_ms == pytest.approx(200.0)
        assert message.text == "正文后半"
        assert [(c.name, c.status) for c in message.tool_calls] == [
            ("read", ElaChatStatus.Done),
            ("patch", ElaChatStatus.Error),
        ]
        stats_parts = message.partsOfKind(ElaChatPartKind.Stats)
        assert [
            (s.stats.prompt_tokens, s.stats.cached_tokens) for s in stats_parts
        ] == [
            (10, 3),
            (20, 7),
        ]
        assert stats_parts[0].stats.ttft_ms == 120.0
        assert stats_parts[0].stats.tps == 42.0
        assert stats_parts[0].stats.duration_ms == pytest.approx(200.0)
        assert stats_parts[1].stats.duration_ms == pytest.approx(100.0)

        # 幂等：重复 finish 不重复结束、耗时置零
        again = binder.finish()
        assert again.durationMs == 0.0
        assert chat.isGenerating() is False
        chat.deleteLater()

    def test_stats_accepts_ela_chat_stats(self, qapp):
        clock = _Clock()
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, clock)
        _begin(chat, binder)
        binder.beginRound()
        binder.stats(ElaChatStats(prompt_tokens=3, completion_tokens=4), ttftMs=80)
        stats = (
            chat.chatView().messages()[-1].partsOfKind(ElaChatPartKind.Stats)[0].stats
        )
        assert stats.prompt_tokens == 3
        assert stats.completion_tokens == 4
        assert stats.ttft_ms == pytest.approx(80.0)
        binder.finish()
        chat.deleteLater()

    def test_empty_stats_and_text_ignored(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.beginRound()
        binder.reasoning("")
        binder.answer("")
        binder.stats(None)
        binder.toolEnd("", "ignored")
        message = chat.chatView().messages()[-1]
        assert not message.parts
        binder.finish()
        chat.deleteLater()


class TestToolStatus:
    def test_error_prefix_infers_failure(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.beginRound()
        binder.toolStart("a", "grep")
        binder.toolEnd("a", "Error: 目录不存在")
        binder.toolStart("b", "read")
        binder.toolEnd("b", "内容")
        calls = chat.chatView().messages()[-1].tool_calls
        assert [(c.name, c.status) for c in calls] == [
            ("grep", ElaChatStatus.Error),
            ("read", ElaChatStatus.Done),
        ]
        chat.deleteLater()

    def test_explicit_ok_overrides_prefix(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.beginRound()
        binder.toolStart("a", "shell")
        binder.toolEnd("a", "Error: not really", ok=True)
        calls = chat.chatView().messages()[-1].tool_calls
        assert calls[0].status == ElaChatStatus.Done
        chat.deleteLater()


class TestErrorsAndEmptyTurn:
    def test_error_closes_reasoning_and_marks_message(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.beginRound()
        binder.reasoning("思考中")
        binder.error("worker", "连接中断")
        message = chat.chatView().messages()[-1]
        # 类型单独存字段，不拼进文案（否则错误卡无法判断该不该给「重试」）
        assert message.error == "连接中断"
        assert message.error_type == "worker"
        assert chat.chatView().messageError(message.id) == ("连接中断", "worker")
        assert len(message.partsOfKind(ElaChatPartKind.Reasoning)) == 1
        chat.deleteLater()

    def test_empty_turn_summary(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.beginRound()
        binder.emptyTurn("length")
        summary = binder.finish()
        assert summary.isEmptyReply() is True
        assert summary.hadText is False
        assert summary.finishReason == "length"
        assert chat.chatView().messages()[-1].text == ""
        chat.deleteLater()


class TestConvenienceDispatch:
    """便捷方法：分片对象 / OpenAI 风格 tool_call dict 直接可连信号。"""

    def test_stream_dispatches_reasoning_and_answer(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.beginRound()
        binder.stream(SimpleNamespace(reasoning_content="想", answer_content=""))
        binder.stream(SimpleNamespace(reasoning_content="", answer_content="正文"))
        binder.stream(SimpleNamespace(reasoning_content="再", answer_content="答"))
        # 正文一开始，binder 就结束了推理段 —— 推理是真的结束了，所以已落定；
        # 正文仍在途，快照里是空串，实时全文走气泡。
        bubble = chat.chatView().bubble(chat.streamingMessageId())
        assert bubble.text() == "正文答"
        assert bubble.reasoning() == "想再"
        message = chat.chatView().messages()[-1]
        assert message.reasoning == "想再"
        assert message.text == ""
        # 回合结束后快照才是完整内容
        binder.finish()
        message = chat.chatView().messages()[-1]
        assert message.reasoning == "想再"
        assert message.text == "正文答"
        chat.deleteLater()

    def test_stream_tolerates_missing_fields(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.beginRound()
        binder.stream(object())
        binder.stream(SimpleNamespace(reasoning_content=None, answer_content=None))
        assert chat.chatView().messages()[-1].text == ""
        binder.finish()
        chat.deleteLater()

    def test_tool_call_dict_dispatch(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.beginRound()
        binder.toolCallStarted(
            {
                "id": "t1",
                "function": {"name": "read", "arguments": '{"path": "a"}'},
            }
        )
        binder.toolCallEnded({"id": "t1"}, "内容")
        binder.toolCallStarted({})
        calls = chat.chatView().messages()[-1].tool_calls
        assert calls[0].name == "read"
        assert calls[0].isDone
        assert calls[1].name == "unknown"
        binder.finish()
        chat.deleteLater()

    def test_tool_call_ignores_non_dict(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.beginRound()
        binder.toolCallStarted(None)
        binder.toolCallEnded("not-a-dict", "结果")
        assert chat.chatView().messages()[-1].tool_calls == ()
        binder.finish()
        chat.deleteLater()


class TestWorkerBinding:
    """A/B：构造时绑定 worker 自动接线；startTurn 建消息并驱动后端。"""

    def test_ctor_worker_auto_wires_signals(self, qapp):
        chat = ElaChatWidget()
        worker = _FakeWorker()
        binder = ElaChatStreamBinder(chat, worker=worker)
        assert binder.worker() is worker

        assert binder.startTurn("你好") is True
        assert worker.ask_calls == ["你好"]
        assert chat.isGenerating() is True
        assert binder.isOpen() is True

        worker.llmStarted.emit()
        worker.chunkReceived.emit(
            SimpleNamespace(reasoning_content="想", answer_content="")
        )
        worker.chunkReceived.emit(
            SimpleNamespace(reasoning_content="", answer_content="答")
        )
        worker.toolStarted.emit({"id": "t1", "function": {"name": "read"}})
        worker.toolEnded.emit({"id": "t1"}, "内容")
        worker.statsReady.emit(ElaChatStats(prompt_tokens=1), 12.0, 8.0)

        message = chat.chatView().messages()[-1]
        # 工具 / 用量是结构化数据，回合未结束就已确定
        assert [(c.name, c.status) for c in message.tool_calls] == [
            ("read", ElaChatStatus.Done)
        ]
        assert message.partsOfKind(ElaChatPartKind.Stats)
        # 推理段在正文开始时已结束 -> 落定；正文仍在途 -> 快照为空
        assert message.reasoning == "想"
        assert message.text == ""
        binder.finish()
        message = chat.chatView().messages()[-1]
        assert message.text == "答"
        assert message.reasoning == "想"
        chat.deleteLater()

    def test_connect_worker_after_construction(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat)
        worker = _FakeWorker()
        binder.connectWorker(worker)
        assert binder.worker() is worker
        assert binder.startTurn("问") is True
        chat.deleteLater()

    def test_start_turn_regenerate_uses_regenerate(self, qapp):
        chat = ElaChatWidget()
        worker = _FakeWorker()
        binder = ElaChatStreamBinder(chat, worker=worker)
        assert binder.startTurn("原问题", regenerate=True) is True
        assert worker.regenerate_calls == ["原问题"]
        assert worker.ask_calls == []
        chat.deleteLater()

    def test_start_turn_not_ready_creates_no_message(self, qapp):
        chat = ElaChatWidget()
        worker = _FakeWorker(ready=False)
        binder = ElaChatStreamBinder(chat, worker=worker)
        assert binder.startTurn("你好") is False
        assert chat.chatView().count() == 0
        assert chat.isGenerating() is False
        assert binder.isOpen() is False
        chat.deleteLater()

    def test_start_turn_without_worker_returns_false(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat)
        assert binder.startTurn("你好") is False
        assert chat.chatView().count() == 0
        chat.deleteLater()

    def test_empty_turn_auto_wired_into_summary(self, qapp):
        chat = ElaChatWidget()
        worker = _FakeWorker()
        binder = ElaChatStreamBinder(chat, worker=worker)
        assert binder.startTurn("你好") is True
        worker.emptyTurn.emit("length")
        summary = binder.finish()
        assert summary.finishReason == "length"
        assert summary.isEmptyReply() is True
        chat.deleteLater()

    def test_connect_same_worker_is_idempotent(self, qapp):
        chat = ElaChatWidget()
        worker = _FakeWorker()
        binder = ElaChatStreamBinder(chat, worker=worker)
        binder.connectWorker(worker)  # 重复绑定不得重复连接信号

        assert binder.startTurn("问") is True
        worker.llmStarted.emit()
        assert binder.roundIndex() == 1
        worker.chunkReceived.emit(
            SimpleNamespace(reasoning_content="", answer_content="答")
        )
        assert chat.chatView().messages()[-1].text == ""
        binder.finish()
        assert chat.chatView().messages()[-1].text == "答"
        chat.deleteLater()

    def test_rebind_disconnects_old_worker(self, qapp):
        chat = ElaChatWidget()
        first = _FakeWorker()
        binder = ElaChatStreamBinder(chat, worker=first)
        second = _FakeWorker()
        binder.connectWorker(second)

        assert binder.worker() is second
        assert binder.startTurn("问") is True
        first.llmStarted.emit()
        first.chunkReceived.emit(
            SimpleNamespace(reasoning_content="", answer_content="旧")
        )
        assert binder.roundIndex() == 0
        assert chat.chatView().messages()[-1].text == ""

        second.llmStarted.emit()
        second.chunkReceived.emit(
            SimpleNamespace(reasoning_content="", answer_content="新")
        )
        assert binder.roundIndex() == 1
        assert chat.chatView().messages()[-1].text == ""
        binder.finish()
        # 旧 worker 的分片始终没进消息，只有 "新"
        assert chat.chatView().messages()[-1].text == "新"
        chat.deleteLater()


class TestLateEvents:
    """回合外（beginTurn 前 / finish 后）的迟到事件一律忽略。"""

    def test_events_after_finish_are_ignored(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.beginRound()
        binder.answer("正常")
        binder.finish()

        binder.beginRound()
        binder.reasoning("迟到思考")
        binder.answer("迟到正文")
        binder.toolStart("t1", "read", '{"path": "a"}')
        binder.toolEnd("t1", "结果")
        binder.toolCallStarted({"id": "t2", "function": {"name": "grep"}})
        binder.toolCallEnded({"id": "t2"}, "结果")
        binder.stats(ElaChatStats(total_tokens=99), 10.0, 5.0)
        binder.error("late", "迟到错误")
        binder.emptyTurn("late")

        message = chat.chatView().messages()[-1]
        assert message.text == "正常"
        assert message.reasoning == ""
        assert message.tool_calls == ()
        assert message.stats is None
        assert message.error == ""
        assert binder.roundIndex() == 1
        assert binder.finish().finishReason == ""
        chat.deleteLater()

    def test_new_turn_still_works_after_late_events(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.beginRound()
        binder.answer("第一轮")
        binder.finish()

        binder.answer("旧回合迟到分片")  # 忽略
        message_id = _begin(chat, binder)
        assert binder.isOpen() is True
        binder.beginRound()
        binder.answer("第二轮")
        binder.stats(ElaChatStats(total_tokens=7))
        summary = binder.finish()

        message = chat.chatView().message(message_id)
        assert summary.status == ElaChatStatus.Done
        assert message.text == "第二轮"
        assert message.stats.total_tokens == 7
        chat.deleteLater()


class TestStop:
    def test_finish_after_stop_keeps_status(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.beginRound()
        binder.reasoning("想")
        binder.answer("半句")
        chat.stopGeneration()
        summary = binder.finish(ElaChatStatus.Stopped)
        assert summary.status == ElaChatStatus.Stopped
        message = chat.chatView().messages()[-1]
        assert message.status == ElaChatStatus.Stopped
        assert message.text == "半句"
        assert chat.isGenerating() is False
        chat.deleteLater()

    def test_cancel_closes_reasoning(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.beginRound()
        binder.reasoning("想")
        binder.cancel()
        assert chat.chatView().messages()[-1].reasoning_ms >= 0.0
        binder.finish()
        chat.deleteLater()

    def test_finish_defaults_to_stopped_after_cancel(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.beginRound()
        binder.reasoning("想")
        binder.answer("半句")
        binder.cancel()  # 宿主停止：无需再维护自己的 stopped 标志
        summary = binder.finish()
        assert summary.status == ElaChatStatus.Stopped
        assert chat.chatView().messages()[-1].status == ElaChatStatus.Stopped
        assert chat.isGenerating() is False
        chat.deleteLater()

    def test_begin_turn_resets_cancel_flag(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.cancel()
        assert binder.finish().status == ElaChatStatus.Stopped
        _begin(chat, binder)  # 新回合
        assert binder.finish().status == ElaChatStatus.Done
        chat.deleteLater()

    def test_explicit_status_overrides_cancel(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.cancel()
        assert binder.finish(ElaChatStatus.Done).status == ElaChatStatus.Done
        chat.deleteLater()

    # -- abortTurn（多话题：删除 / 关闭话题时立刻作废回合） ------------------

    def test_abort_turn_closes_turn_and_ignores_late_events(self, qapp):
        chat = ElaChatWidget()
        binder = ElaChatStreamBinder(chat, _Clock())
        _begin(chat, binder)
        binder.answer("写一半")
        messageId = chat.streamingMessageId()

        summary = binder.abortTurn()

        assert summary is not None and summary.status == ElaChatStatus.Stopped
        assert binder.isOpen() is False
        assert chat.isGenerating() is False
        assert chat.chatView().message(messageId).status == ElaChatStatus.Stopped
        before = chat.chatView().message(messageId).text
        # 作废之后迟到的事件一律无落点（多话题下同 id 恢复消息不会被污染）
        binder.stream("迟到的分片")
        binder.toolCallStarted(
            SimpleNamespace(id="late", name="read_file", arguments="{}")
        )
        assert chat.chatView().message(messageId).text == before
        assert chat.chatView().message(messageId).parts[-1].kind != ElaChatPartKind.Tool
        chat.deleteLater()

    def test_abort_turn_outside_turn_is_noop(self, qapp):
        chat = ElaChatWidget()
        worker = _FakeWorker()
        binder = ElaChatStreamBinder(chat, worker=worker)
        assert binder.abortTurn() is None  # 回合外：安全空操作
        assert worker.cancel_calls == []  # 也没有多停一次后端
        assert chat.isGenerating() is False
        assert chat.chatView().messages() == []
        chat.deleteLater()

    def test_abort_turn_cancels_backend_by_default(self, qapp):
        """作废这一轮时默认把后端也停掉 —— 否则白烧 token。"""
        chat = ElaChatWidget()
        worker = _FakeWorker()
        binder = ElaChatStreamBinder(chat, worker=worker)
        assert binder.startTurn("边跑边删") is True

        summary = binder.abortTurn()

        assert summary is not None and summary.status == ElaChatStatus.Stopped
        assert worker.cancel_calls == [True]
        assert binder.isOpen() is False
        chat.deleteLater()

    def test_abort_turn_can_leave_backend_running(self, qapp):
        """``cancelBackend=False``：只闭组件侧回合（后端中止归宿主的场景）。"""
        chat = ElaChatWidget()
        worker = _FakeWorker()
        binder = ElaChatStreamBinder(chat, worker=worker)
        assert binder.startTurn("后端留着") is True

        summary = binder.abortTurn(cancelBackend=False)

        assert summary is not None and summary.status == ElaChatStatus.Stopped
        assert worker.cancel_calls == []
        assert binder.isOpen() is False
        assert chat.isGenerating() is False
        chat.deleteLater()

    def test_abort_turn_does_not_auto_send_queue(self, qapp):
        """作废不顺手起新一轮：排队消息留着，宿主的 autoSendQueue 设置原样还原。"""
        chat = ElaChatWidget()
        worker = _FakeWorker()
        binder = ElaChatStreamBinder(chat, worker=worker)
        assert chat.autoSendQueue() is True
        chat.sendUserMessage("第一轮")
        assert binder.startTurn("第一轮") is True
        chat.enqueueMessage("排队中的第二条")

        binder.abortTurn()

        assert chat.queueCount() == 1  # 没被发出去
        assert chat.autoSendQueue() is True  # 宿主的设置没被改坏
        assert chat.isGenerating() is False
        # 消息照旧留着（作废的是「这一轮」，不是历史）
        assert len(chat.chatView().messages()) == 2
        chat.deleteLater()

    def test_abort_turn_survives_reentrant_finish_from_backend(self, qapp):
        """后端 ``cancel()`` 同步发 ``turnFinished``、宿主接 ``binder.finish``：重入必须幂等。

        先收尾再停后端，重入那次 ``finish()`` 才不会把回合按 ``Done`` 结束
        （也不能因此续发排队消息）。
        """

        chat = ElaChatWidget()
        mock = ElaChatMockBackend(tickMs=0)
        binder = ElaChatStreamBinder(chat, worker=mock)
        mock.turnFinished.connect(binder.finish)  # 与示例 / llm_test 同款接线
        assert binder.startTurn("提问") is True
        chat.enqueueMessage("排队中的第二条")

        summary = binder.abortTurn()

        assert summary is not None and summary.status == ElaChatStatus.Stopped
        assert chat.chatView().messages()[-1].status == ElaChatStatus.Stopped
        assert chat.queueCount() == 1
        assert binder.isOpen() is False
        mock.shutdown()
        chat.deleteLater()


class TestShutdownOnClose:
    """窗口关闭 / 销毁时自动收尾后端（宿主免写 closeEvent）。"""

    def _window_with_binder(self, worker):
        window = QWidget()
        chat = ElaChatWidget(window)
        binder = ElaChatStreamBinder(chat, worker=worker)
        binder.shutdownOnClose(window)
        return window, chat

    def test_close_shuts_down_worker(self, qapp):
        worker = _FakeWorker()
        window, _chat = self._window_with_binder(worker)
        window.close()
        qapp.processEvents()
        assert worker.shutdown_calls == [True]
        window.deleteLater()

    def test_destroy_shuts_down_worker(self, qapp):
        worker = _FakeWorker()
        window, _chat = self._window_with_binder(worker)
        sip.delete(window)
        qapp.processEvents()
        assert worker.shutdown_calls == [True]

    def test_close_without_worker_is_noop(self, qapp):
        window = QWidget()
        chat = ElaChatWidget(window)
        binder = ElaChatStreamBinder(chat)
        binder.shutdownOnClose(window)
        window.close()
        qapp.processEvents()
        window.deleteLater()

    def test_worker_without_shutdown_is_safe(self, qapp):
        window = QWidget()
        chat = ElaChatWidget(window)
        binder = ElaChatStreamBinder(chat)
        binder._worker = object()  # 后端无 shutdown 方法
        binder.shutdownOnClose(window)
        window.close()
        qapp.processEvents()
        window.deleteLater()
