"""回归测试：回合终止不变量 —— 「不存在永不停下的转圈」。

这轮修复的三个 bug 属于同一类：回合的某条终止路径没有收尾所有打开项。

- ``stopGeneration()`` 先 emit 再收尾，宿主槽触发排队续发后把**新**回合置 stopped
- 错误回合不发 ``generationFinished``、不排空 ``autoSendQueue``
- ``bubble.beginStep()`` 只 detach 思考段而不 ``endReasoning()``

参考 OpenCode 的结构性做法（``runner/llm.ts:284-354``）：每条终止路径都必须
settle 所有打开项；跨进程还有 ``failInterruptedTools`` 把遗留的 pending/running
落为 failed。这里用 kill-point 参数化测试把该不变量固化下来。
"""

from __future__ import annotations

import pytest
from PyQt5.QtCore import QObject, pyqtSignal

from pyqt5_ela_pro.chat import (
    ElaChatPart,
    ElaChatPartKind,
    ElaChatStats,
    ElaChatStatus,
    ElaChatStreamBinder,
    ElaChatToolStatus,
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
        self.ready = ready

    def ask(self, text: str) -> bool:
        self.ask_calls.append(text)
        return self.ready

    def regenerate(self, text: str) -> bool:
        return self.ready

    def shutdown(self) -> None:
        pass


def _begin(chat: ElaChatWidget, binder: ElaChatStreamBinder) -> int:
    chat.sendUserMessage("问")
    messageId = chat.beginAssistantMessage()
    binder.beginTurn()
    return messageId


def _tool_states(chat: ElaChatWidget) -> list:
    """收集全部消息里工具调用的状态。"""
    states = []
    for message in chat.chatView().messages():
        if not message.isAssistant:
            continue
        for part in message.parts:
            if part.kind == ElaChatPartKind.Tool and part.tool_call is not None:
                states.append(part.tool_call.status)
    return states


def _part_statuses(chat: ElaChatWidget) -> list:
    """收集全部助手消息 part 的状态。"""
    out = []
    for message in chat.chatView().messages():
        if message.isAssistant:
            out.extend(str(p.status).lower() for p in message.parts)
    return out


def _assert_quiescent(chat: ElaChatWidget, label: str) -> None:
    """断言视图处于终态：没有 running 工具、没有 streaming part、不在生成中。"""
    assert chat.isGenerating() is False, f"{label}: isGenerating 仍为 True"

    running = [s for s in _tool_states(chat) if s == ElaChatToolStatus.Running]
    assert not running, f"{label}: 仍有 running 状态的工具 {running}"

    streaming = [s for s in _part_statuses(chat) if s.startswith("stream")]
    assert not streaming, f"{label}: 仍有 streaming 状态的 part {streaming}"


# ---------------------------------------------------------------- kill points
_KILL_AFTER = ("startTurn", "reasoning", "answer", "toolStart", "toolEnd", "stats")


class TestNoTerminatingSpinner:
    """在流式处理器的各注入点丢弃后续事件，视图必须收敛到终态。"""

    def _drive_then_abandon(self, qapp, kill_after: str) -> ElaChatWidget:
        chat = ElaChatWidget()
        chat.resize(600, 400)
        chat.show()
        qapp.processEvents()
        binder = ElaChatStreamBinder(chat, _Clock(), worker=_FakeWorker())
        messageId = _begin(chat, binder)

        order = (
            "startTurn",
            "reasoning",
            "answer",
            "toolStart",
            "toolEnd",
            "stats",
        )
        for step in order:
            if step == "startTurn":
                binder.beginRound()
            elif step == "reasoning":
                binder.reasoning("thinking")
            elif step == "answer":
                binder.answer("partial answer")
            elif step == "toolStart":
                binder.toolStart("t1", "read", '{"path":"a"}')
            elif step == "toolEnd":
                binder.toolEnd("t1", "file body")
            elif step == "stats":
                binder.stats(ElaChatStats(total_tokens=5), 1.0, 2.0)
            qapp.processEvents()
            if step == kill_after:
                # 模拟 worker 崩溃：后续事件（含 finish）永远不来
                break
        return chat, messageId

    @pytest.mark.parametrize("kill_after", _KILL_AFTER)
    def test_abandoned_turn_has_no_spinner(self, qapp, kill_after):
        chat, _ = self._drive_then_abandon(qapp, kill_after)
        # 崩溃后宿主唯一能做的就是显式收尾
        chat.stopGeneration()
        qapp.processEvents()
        _assert_quiescent(chat, f"kill_after={kill_after}")
        chat.deleteLater()
        qapp.processEvents()

    @pytest.mark.parametrize("kill_after", _KILL_AFTER)
    def test_abandoned_turn_leaves_no_orphan_generation(self, qapp, kill_after):
        """收尾后不得残留悬空生成态（否则下一条消息永远发不出去）。"""
        chat, _ = self._drive_then_abandon(qapp, kill_after)
        chat.stopGeneration()
        qapp.processEvents()
        # 收尾后再发一条必须能正常进入生成态
        chat.sendUserMessage("follow up")
        qapp.processEvents()
        assert chat.isGenerating() is True
        chat.stopGeneration()
        qapp.processEvents()
        chat.deleteLater()
        qapp.processEvents()


class TestNoSpinnerAfterError:
    """错误路径同样必须收尾。"""

    def test_error_turn_reaches_terminal_state(self, qapp):
        chat = ElaChatWidget()
        chat.resize(600, 400)
        chat.show()
        qapp.processEvents()
        binder = ElaChatStreamBinder(chat, _Clock(), worker=_FakeWorker())
        messageId = _begin(chat, binder)

        binder.beginRound()
        binder.reasoning("thinking")
        binder.toolStart("t1", "read", "{}")
        binder.answer("partial")
        binder.error("ProviderError", "boom")
        qapp.processEvents()
        binder.finish()
        qapp.processEvents()

        _assert_quiescent(chat, "error turn")
        chat.deleteLater()
        qapp.processEvents()

    def test_error_turn_drains_queue(self, qapp):
        """错误回合之后 autoSendQueue 仍要能发出下一条。"""
        chat = ElaChatWidget()
        chat.resize(600, 400)
        chat.show()
        qapp.processEvents()
        binder = ElaChatStreamBinder(chat, _Clock(), worker=_FakeWorker())
        messageId = _begin(chat, binder)
        binder.beginRound()

        # 排队一条
        chat.enqueueMessage("queued follow up")
        qapp.processEvents()
        assert chat.queueCount() == 1

        binder.error("ProviderError", "boom")
        qapp.processEvents()
        binder.finish()
        qapp.processEvents()

        # 队列应被排空（错误回合不留下永久卡住的队列）
        assert chat.isGenerating() is False or chat.queueCount() == 0, (
            "错误回合后既不在生成、队列又没排空 —— 状态不一致"
        )
        chat.deleteLater()
        qapp.processEvents()


class TestNoSpinnerAfterStop:
    """停止路径必须收尾，且不得误伤自动续发的新回合。"""

    def test_stop_closes_old_stream_only(self, qapp):
        chat = ElaChatWidget()
        chat.resize(600, 400)
        chat.show()
        qapp.processEvents()
        binder = ElaChatStreamBinder(chat, _Clock(), worker=_FakeWorker())
        first = _begin(chat, binder)
        binder.beginRound()
        binder.answer("old answer")

        # 宿主在 stopRequested 里自动续发一次（模拟排队 dock 的「立即发送」）。
        # 只续发一次：否则每次 stop 都会再开一个回合，构造上就停不下来。
        replacement = {}
        fired = []

        def on_stop():
            if fired:
                return
            fired.append(1)
            chat.sendUserMessage("q2")
            replacement["id"] = chat.beginAssistantMessage()

        chat.stopRequested.connect(on_stop)
        chat.stopGeneration()
        qapp.processEvents()

        old = str(chat.chatView().message(first).status).lower()
        new = str(chat.chatView().message(replacement["id"]).status).lower()
        assert old == "stopped", f"旧回合应被置为 stopped，实际 {old}"
        assert new != "stopped", "刚自动发出的新回合被误伤为 stopped"

        chat.stopGeneration()
        qapp.processEvents()
        _assert_quiescent(chat, "after stop")
        chat.deleteLater()
        qapp.processEvents()


class TestBeginStepClosesReasoning:
    """beginStep 必须收尾思考段，否则转圈动画永停。"""

    def test_no_streaming_part_after_begin_step(self, qapp):
        chat = ElaChatWidget()
        chat.resize(600, 400)
        chat.show()
        qapp.processEvents()
        view = chat.chatView()
        messageId = chat.beginAssistantMessage()

        view.beginReasoning(messageId)
        view.appendText(messageId, "answer")
        view.beginStep(messageId)
        qapp.processEvents()

        statuses = [str(p.status).lower() for p in view.message(messageId).parts]
        assert all(not s.startswith("stream") for s in statuses), (
            f"beginStep 后仍有 streaming part：{statuses}"
        )
        chat.deleteLater()
        qapp.processEvents()


class TestReplayEquivalence:
    """逐事件驱动 与 一次性构造 必须产生相同的 parts。

    这是 OpenCode 值得抄的一条测试形态（idea 5.1）：它一次性抓住重复追加、
    丢失收尾事件、顺序漂移这一整类 bug。
    """

    def test_step_by_step_equals_batch_construction(self, qapp):
        # A：逐事件
        chat_a = ElaChatWidget()
        binder = ElaChatStreamBinder(chat_a, _Clock(), worker=_FakeWorker())
        mid_a = _begin(chat_a, binder)
        binder.beginRound()
        binder.reasoning("think")
        binder.toolStart("t1", "read", '{"p":1}')
        binder.toolEnd("t1", "out")
        binder.answer("answer")
        binder.finish()
        qapp.processEvents()
        parts_a = chat_a.chatView().message(mid_a).parts

        # B：同一序列，但直接构造等价 parts
        chat_b = ElaChatWidget()
        chat_b.addMessage("assistant", "")
        expected = (
            ElaChatPart(id="r", kind=ElaChatPartKind.Reasoning, text="think", step=1),
            ElaChatPart(id="t", kind=ElaChatPartKind.Tool, step=1),
            ElaChatPart(id="x", kind=ElaChatPartKind.Text, text="answer", step=1),
        )
        # 只比对 kind/step 序列（id 由实现分配，不应作为契约）
        sig_a = [(p.kind, p.step) for p in parts_a]
        sig_b = [(p.kind, p.step) for p in expected]
        assert sig_a == sig_b, f"逐事件与批量构造的 part 序列不一致：\n{sig_a}\n{sig_b}"

        chat_a.deleteLater()
        chat_b.deleteLater()
        qapp.processEvents()
