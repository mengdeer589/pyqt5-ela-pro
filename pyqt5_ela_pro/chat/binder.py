"""流式事件 → 聊天组件映射器（``pyqt5_ela_pro.chat``）。

:class:`ElaChatStreamBinder` 把「分轮流式事件」翻译成 :class:`ElaChatWidget`
的分步 API，宿主只需把后端回调转发进来，无需关心步骤边界、思考段复用、
工具面板归属、统计落位与端到端耗时等细节：

- ``beginTurn()``：宿主提交提问时调用（重置计时与标记）；
- ``beginRound()``：每次 LLM 调用前调用（第 2 轮起自动 ``beginStep``）；
- ``reasoning(text)`` / ``answer(text)`` / ``stream(chunk)``：推理与正文分片
  （同一轮的思考内容复用同一折叠块，正文出现时自动结束思考段；
  ``stream`` 直接从分片对象分派，可直接连 ``chunkReceived`` 信号）；
- ``toolStart(callId, name, arguments)`` / ``toolEnd(callId, result, ok=None)``：
  工具调用开始 / 结束（``ok=None`` 时按 ``result`` 是否以 ``"Error:"``
  开头推断）；``toolCallStarted(toolCall)`` / ``toolCallEnded(toolCall, result)``
  直接接收 OpenAI 风格 ``tool_call`` dict，可直接连 ``toolStarted`` /
  ``toolEnded`` 信号；
- ``stats(usage, ttftMs, tps)``：单轮用量（兼容 OpenAI ``usage`` 对象或
  直接传 :class:`ElaChatStats`，缓存字段兼容两种形态；每步原始数据保存
  在消息 ``parts`` 中，界面默认合并为整轮汇总徽标，见
  ``ElaChatWidget.setStatsMode``）；
- ``error(type, message)`` / ``emptyTurn(reason)``：错误与空正文诊断；
- ``finish(status)``：回合结束（补整轮耗时、结束消息、返回
  :class:`ElaChatTurnSummary`）。

**回合边界**：``beginTurn`` 之前 / ``finish`` 之后到达的分片、工具、
用量与错误事件一律忽略（迟到事件不会写进当前消息，也不会污染下一轮）。

用法::

    binder = ElaChatStreamBinder(chat, worker=worker)   # 自动接机械信号

    worker.ready.connect(on_ready)             # UI 状态归宿主
    worker.failed.connect(on_failed)
    worker.errorOccurred.connect(on_error)
    worker.turnFinished.connect(on_turn_finished)

    ok = binder.startTurn("你好")               # 建消息 + beginTurn + worker.ask
    ...
    summary = binder.finish(ElaChatStatus.Stopped if stopped else ElaChatStatus.Done)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, replace
from typing import Callable, Optional

from PyQt5.QtCore import QEvent, QObject

from . import _json
from .message import ElaChatStats, ElaChatStatus
from .widget import ElaChatWidget


class _WindowCloseFilter(QObject):
    """窗口关闭回调过滤器（内部：不拦截事件，只做收尾）。"""

    def __init__(self, window, callback: Callable[[], None]) -> None:
        super().__init__(window)
        self._callback = callback

    def eventFilter(self, obj, event) -> bool:  # noqa: N802 (Qt 命名)
        if event.type() == QEvent.Type.Close:
            try:
                self._callback()
            except Exception:
                pass
        return False


@dataclass(frozen=True)
class ElaChatTurnSummary:
    """回合结束摘要（由 :meth:`ElaChatStreamBinder.finish` 返回）。

    :param status: 最终状态（见 :class:`ElaChatStatus`）
    :param hadText: 本回合是否输出过正文
    :param finishReason: 模型 ``finish_reason``（``emptyTurn`` 传入）
    :param durationMs: 端到端耗时（毫秒）
    """

    status: str = ElaChatStatus.Done
    hadText: bool = True
    finishReason: str = ""
    durationMs: float = 0.0

    def isEmptyReply(self) -> bool:
        """是否属于「未返回正文」的回合。"""
        return not self.hadText


class ElaChatStreamBinder:
    """把分轮流式事件映射到 :class:`ElaChatWidget`（纯同步、可独立测试）。

    :param chat: 目标聊天组件
    :param clock: 计时函数（默认 ``time.monotonic``，测试可注入）
    :param worker: 可选后端（信号契约与
        :class:`~pyqt5_ela_pro.chat.mock.ElaChatMockBackend` 同构）；
        传入时自动接线（见 :meth:`connectWorker`），并可调用
        :meth:`startTurn`
    """

    def __init__(
        self,
        chat: ElaChatWidget,
        clock: Callable[[], float] = time.monotonic,
        *,
        worker=None,
    ) -> None:
        self._chat = chat
        self._clock = clock
        self._worker = None
        self._close_filter = None
        self._round = 0
        self._turn_start = 0.0
        self._round_start = 0.0
        # 当前回合操作的助手消息 id（view 层所有消息操作都要显式传它）
        self._message_id: Optional[int] = None
        self._reasoning_open = False
        self._reasoning_start = 0.0
        self._had_text = False
        self._finish_reason = ""
        self._cancelled = False
        if worker is not None:
            self.connectWorker(worker)

    # -- 后端接线 ----------------------------------------------------------

    def connectWorker(self, worker) -> None:
        """绑定后端并自动接线机械信号（等价于宿主手写 6 条 connect）。

        自动连接：``llmStarted`` / ``chunkReceived`` / ``toolStarted`` /
        ``toolEnded`` / ``statsReady`` / ``emptyTurn``。
        涉及 UI 决策的 ``ready`` / ``failed`` / ``errorOccurred`` /
        ``turnFinished`` 仍由宿主自行连接（状态文案、完成/停止判定）。

        幂等：重复绑定同一个后端直接返回（避免信号重复连接导致事件
        处理两遍）；换绑其他后端时先解绑旧后端的全部机械信号。
        """
        if worker is self._worker:
            return
        self._disconnectWorker()
        self._worker = worker
        worker.llmStarted.connect(self.beginRound)
        worker.chunkReceived.connect(self.stream)
        worker.toolStarted.connect(self.toolCallStarted)
        worker.toolEnded.connect(self.toolCallEnded)
        worker.statsReady.connect(self.stats)
        worker.emptyTurn.connect(self.emptyTurn)

    def _disconnectWorker(self) -> None:
        """解绑当前后端的机械信号（未连接 / 已销毁时静默忽略）。"""
        worker = self._worker
        if worker is None:
            return
        for name, slot in (
            ("llmStarted", self.beginRound),
            ("chunkReceived", self.stream),
            ("toolStarted", self.toolCallStarted),
            ("toolEnded", self.toolCallEnded),
            ("statsReady", self.stats),
            ("emptyTurn", self.emptyTurn),
        ):
            try:
                getattr(worker, name).disconnect(slot)
            except (AttributeError, TypeError, RuntimeError):
                pass

    def worker(self):
        """已绑定的后端（未绑定返回 ``None``）。"""
        return self._worker

    def shutdownOnClose(self, window) -> None:
        """窗口关闭 / 销毁时自动 ``worker.shutdown()``（宿主免写 closeEvent）。

        :param window: 顶层窗口（通常是 ``chat.window()``）

        显式调用（不做隐式自动）：多窗口 / 跨窗口复用同一后端的宿主不需要
        调用本方法。后端没有 ``shutdown`` 方法时忽略。
        """
        self._close_filter = _WindowCloseFilter(window, self.shutdownWorker)
        window.installEventFilter(self._close_filter)
        window.destroyed.connect(self.shutdownWorker)

    def shutdownWorker(self) -> None:
        """收尾后端（幂等；没有后端 / 后端无 ``shutdown`` 时忽略）。"""
        shutdown = getattr(self._worker, "shutdown", None)
        if callable(shutdown):
            shutdown()

    # -- 回合与轮次 --------------------------------------------------------

    def startTurn(self, prompt: str, regenerate: bool = False) -> bool:
        """开始一个回合：先驱动后端起跑，随后新建助手消息并重置计时。

        与 :meth:`finish` 对称（回合生命周期都在 binder 内闭环）。后端需保证
        ``ask`` / ``regenerate`` 返回后才开始发信号（``ElaChatMockBackend``
        与 :class:`~pyqt5_ela_pro.chat.worker.ElaChatAsyncWorker` 均满足）。

        :param prompt: 提问文本
        :param regenerate: ``True`` 时走 ``worker.regenerate``（历史回滚由
            后端负责）
        :returns: 后端是否已受理；``False`` 时不创建空的助手消息，错误
            文案仍由宿主展示
        """
        if self._worker is None:
            return False
        method = self._worker.regenerate if regenerate else self._worker.ask
        if not method(prompt or ""):
            return False
        # 记住消息 id：删除 widget 的转发层后，消息内容操作全在 view 层，
        # 而 view 的每个方法都要求显式传 messageId（不再有「省略 = 当前流式
        # 消息」这层便利），所以 binder 必须自己攥着这个 id。
        self._message_id = self._chat.beginAssistantMessage()
        self.beginTurn()
        return True

    def _target(self) -> Optional[int]:
        """当前回合操作的消息 id（``None`` 表示回合未开，调用方应忽略）。"""
        return self._message_id

    def beginTurn(self) -> None:
        """开始一个回合（宿主提交提问 / 重新生成时调用）。"""
        self._round = 0
        self._turn_start = self._clock()
        self._round_start = 0.0
        self._reasoning_open = False
        self._reasoning_start = 0.0
        self._had_text = False
        self._finish_reason = ""
        self._cancelled = False
        if self._message_id is None:
            # 宿主可能自己建好消息再调 beginTurn()（不经 startTurn），
            # 这里接上当前流式消息 —— 等价于过去 widget 层「省略即当前流式
            # 消息」的默认行为。view 层不再有这层默认，id 必须由调用链带着。
            self._message_id = self._chat.streamingMessageId()

    def beginRound(self) -> None:
        """开始一轮 LLM 调用（第 2 轮起自动开启新步骤）。

        回合外（``beginTurn`` 前 / ``finish`` 后）的迟到事件一律忽略。

        **这里是 steer（插话）的投递点** —— ``beginStep`` 之前是「上一步的
        工具都跑完了」这个安全边界，正好对应 opencode 的
        ``SessionInbox.nextPromotable`` 位置（``runner/llm.ts:83``）：用户
        在生成中说的话在这一刻送进后端，而不是等整轮跑完。一次只投一条。
        """
        if not self.isOpen():
            return
        self._round_start = self._clock()
        self._round += 1
        if self._round > 1:
            self._endReasoning()
            self._chat.chatView().beginStep(self._target())
            self._drainSteer()

    def _drainSteer(self) -> None:
        """在 step 边界投递一条待送插话（仅开了自动投递时）。

        组件侧只负责「留回执 + 发信号」；把文本送进后端是宿主的事
        （组件不知道后端是什么）。宿主也可关掉自动投递、自己控制时机。
        """
        chat = self._chat
        if not getattr(chat, "steerEnabled", lambda: True)():
            return
        drain = getattr(chat, "drainSteer", None)
        if callable(drain):
            drain()

    def isOpen(self) -> bool:
        """是否处于回合中（``beginTurn`` 之后、``finish`` 之前）**且有目标消息**。

        附带「有目标消息」这个条件，是因为 view 层的每个消息操作都要求显式
        传 ``messageId``（不再有「省略即当前流式」的默认）。没有落点的回合
        视为未开启 —— 所有以 ``isOpen()`` 为闸门的写入点自然全部跳过，
        与「回合外事件一律忽略」是同一条语义。
        """
        return self._turn_start != 0.0 and self._message_id is not None

    def roundIndex(self) -> int:
        """当前回合内的 LLM 轮次序号（从 1 开始）。"""
        return self._round

    # -- 内容分片 ----------------------------------------------------------

    def reasoning(self, text: str) -> None:
        """追加推理分片（同一轮复用同一思考段；回合外忽略）。"""
        if not text or not self.isOpen():
            return
        if not self._reasoning_open:
            self._reasoning_open = True
            self._reasoning_start = self._clock()
            self._chat.chatView().beginReasoning(self._target())
        self._chat.chatView().appendReasoning(self._target(), text)

    def answer(self, text: str) -> None:
        """追加正文分片（自动结束当前推理段；回合外忽略）。"""
        if not text or not self.isOpen():
            return
        self._had_text = True
        self._endReasoning()
        self._chat.chatView().appendText(self._target(), text)

    def stream(self, chunk) -> None:
        """分派流式分片（兼容 ``AgentOutput`` / ``ElaChatMockChunk``）。

        依次读取 ``reasoning_content`` / ``answer_content`` 属性，非空则转给
        :meth:`reasoning` / :meth:`answer`；可直接接到
        ``worker.chunkReceived.connect(binder.stream)``。
        """
        reasoning = getattr(chunk, "reasoning_content", "") or ""
        answer = getattr(chunk, "answer_content", "") or ""
        if reasoning:
            self.reasoning(reasoning)
        if answer:
            self.answer(answer)

    # -- 工具调用 ----------------------------------------------------------

    def toolStart(self, callId: str, name: str, arguments="") -> None:
        """工具调用开始（``arguments`` 支持 dict 或 JSON 字符串；回合外忽略）。"""
        if not self.isOpen():
            return
        if not isinstance(arguments, str):
            arguments = _json.dumps(arguments)
        self._chat.chatView().addToolCall(
            self._target(), name, arguments, callId or None
        )

    def toolEnd(self, callId: str, result: str, ok: Optional[bool] = None) -> None:
        """工具调用结束（``ok`` 为空时按 ``"Error:"`` 前缀推断；回合外忽略）。"""
        if not callId or not self.isOpen():
            return
        text = str(result or "")
        if ok is None:
            ok = not text.startswith("Error:")
        self._chat.chatView().setToolCallResult(
            self._target(), callId, text, ok=bool(ok)
        )

    def toolCallStarted(self, toolCall: dict) -> None:
        """工具调用开始（OpenAI 风格 ``tool_call`` dict，可直接连信号）。

        取 ``id`` 与 ``function.name`` / ``function.arguments`` 转给
        :meth:`toolStart`。
        """
        if not isinstance(toolCall, dict):
            return
        function = toolCall.get("function") or {}
        self.toolStart(
            toolCall.get("id") or "",
            function.get("name") or "unknown",
            function.get("arguments", ""),
        )

    def toolCallEnded(self, toolCall: dict, result: str) -> None:
        """工具调用结束（OpenAI 风格 ``tool_call`` dict，可直接连信号）。"""
        if not isinstance(toolCall, dict):
            return
        self.toolEnd(toolCall.get("id") or "", result)

    # -- 用量与错误 --------------------------------------------------------

    def stats(self, usage, ttftMs: float = 0.0, tps: float = 0.0) -> None:
        """写入当前步骤用量（兼容 OpenAI ``usage`` 或 :class:`ElaChatStats`）。

        回合外（``beginTurn`` 前 / ``finish`` 后）忽略，避免迟到用量
        改写已结束消息的整轮汇总。
        """
        if usage is None or not self.isOpen():
            return
        if isinstance(usage, ElaChatStats):
            stats = usage
            if ttftMs and not stats.ttft_ms:
                stats = replace(stats, ttft_ms=float(ttftMs))
            if tps and not stats.tps:
                stats = replace(stats, tps=float(tps))
        else:
            cached = getattr(usage, "prompt_cache_hit_tokens", 0) or 0
            if not cached:
                details = getattr(usage, "prompt_tokens_details", None)
                cached = getattr(details, "cached_tokens", 0) or 0
            stats = ElaChatStats(
                prompt_tokens=int(getattr(usage, "prompt_tokens", 0) or 0),
                completion_tokens=int(getattr(usage, "completion_tokens", 0) or 0),
                total_tokens=int(getattr(usage, "total_tokens", 0) or 0),
                cached_tokens=int(cached or 0),
                ttft_ms=float(ttftMs or 0.0),
                tps=float(tps or 0.0),
            )
        durationMs = 0.0
        if self._round_start:
            durationMs = (self._clock() - self._round_start) * 1000.0
        if durationMs and not stats.duration_ms:
            stats = replace(stats, duration_ms=durationMs)
        self._chat.chatView().setStepStats(self._target(), stats)

    def error(self, errorType: str, message: str) -> None:
        """写入错误（结束当前推理段并置错误卡片；回合外忽略）。

        ``errorType`` **原样传给 view**（不再格式化成 ``"[Type] msg"`` 拼进
        文案）：错误卡要靠它判断该不该点亮「重试」，宿主也要拿它做结构化
        埋点 / 选择重试策略。类型信息一旦拼进自然语言就再也取不回来了。
        """
        if not self.isOpen():
            return
        self._endReasoning()
        self._chat.chatView().setMessageError(self._target(), message, errorType)

    def emptyTurn(self, finishReason: str = "") -> None:
        """标记「回合结束但未返回正文」（由 ``finish`` 汇总返回；回合外忽略）。"""
        if not self.isOpen():
            return
        self._finish_reason = str(finishReason or "")

    # -- 结束 --------------------------------------------------------------

    def cancel(self) -> None:
        """停止生成：收尾当前思考段，并让 :meth:`finish` 默认按 ``Stopped`` 收尾。

        宿主停止按钮：``binder.cancel()`` + 中止后端（``worker.cancel()``）。
        下一次 :meth:`beginTurn` / :meth:`startTurn` 会清除该标记。
        """
        self._cancelled = True
        self._endReasoning()

    def finish(self, status: Optional[str] = None) -> ElaChatTurnSummary:
        """结束回合：补整轮耗时、结束消息，返回摘要。

        :param status: 最终状态；缺省时按是否调用过 :meth:`cancel` 自动取
            ``Stopped`` / ``Done``（显式传入优先）

        幂等：若消息已被 ``stopGeneration`` 结束（未处于生成中），
        只补耗时不再重复结束。
        """
        if status is None:
            status = ElaChatStatus.Stopped if self._cancelled else ElaChatStatus.Done
        self._endReasoning()
        durationMs = 0.0
        if self._turn_start:
            durationMs = (self._clock() - self._turn_start) * 1000.0
            self._turn_start = 0.0
        if durationMs:
            self._chat.chatView().setMessageDuration(self._target(), durationMs)
        # 不能只在 isGenerating() 时收尾：setMessageError / removeMessage /
        # undoMessage / regenerateFrom / 二次 stop 都已把 _generating 置 False，
        # 那样 finish() 会直接跳过 endAssistantMessage —— generationFinished 不发，
        # autoSendQueue 也永远排不空。
        if self._chat.isGenerating() or self._chat.streamingMessageId() is not None:
            self._chat.endAssistantMessage(status=status)
        # 回合已收尾：清掉目标 id，使 finish() 之后的迟到事件找不到落点
        # （isOpen() 已经为 False，这里是第二道保险 —— 宿主若在 finish() 后
        # 手动再调一次 reasoning()/answer()，不应写进已结束的消息）
        self._message_id = None
        return ElaChatTurnSummary(
            status=status,
            hadText=self._had_text,
            finishReason=self._finish_reason,
            durationMs=durationMs,
        )

    def abortTurn(self, cancelBackend: bool = True) -> Optional[ElaChatTurnSummary]:
        """立刻作废当前回合（不等后端确认），返回摘要；回合外返回 ``None``。

        = ``cancel()`` + ``finish(Stopped)``（+ 默认 ``worker.cancel()``）：用于
        **不打算保留这一轮**的场景 —— 删除 / 关闭话题、销毁页面。收尾后
        ``isOpen()`` 为 False 且目标 id 被清空，之后到达的分片 / 工具结果无处可落
        （多话题下尤其重要：``importSession`` 保留消息 id，旧回合的迟到事件会命中
        新话题里同 id 的消息）。

        两条与 :meth:`cancel` / :meth:`finish` 不同的语义：

        - **默认把后端也停掉**（``cancelBackend=True``）：作废了这一轮，让后端继续
          流下去只会白烧 token。传 ``False`` 只闭组件侧（后端中止归宿主的场景）；
        - **不续发排队消息**：``finish()`` 正常路径会按 ``autoSendQueue`` 自动发出
          队首，但「作废」不该顺手起一轮新的 —— 这里临时关掉再还原宿主的设置。

        后端先收到 :meth:`finish` 之后再停：部分后端（如 ``ElaChatMockBackend``）
        ``cancel()`` 会同步发 ``turnFinished``，宿主常接 ``binder.finish`` —— 先收尾
        能保证那次重入是幂等空操作，而不是把回合按 ``Done`` 结束、还顺手续发队列。

        :param cancelBackend: 是否同时 ``worker.cancel()``（默认 ``True``）
        """
        if not self.isOpen():
            return None
        autoSend = self._chat.autoSendQueue()
        self._chat.setAutoSendQueue(False)
        try:
            self.cancel()
            summary = self.finish(ElaChatStatus.Stopped)
            if cancelBackend and self._worker is not None:
                self._worker.cancel()
            return summary
        finally:
            self._chat.setAutoSendQueue(autoSend)

    # -- 内部 --------------------------------------------------------------

    def _endReasoning(self) -> None:
        if not self._reasoning_open:
            return
        elapsed = (self._clock() - self._reasoning_start) * 1000.0
        self._chat.chatView().endReasoning(self._target(), elapsed)
        self._reasoning_open = False
