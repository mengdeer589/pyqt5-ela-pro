"""异步聊天后端 worker 基类（``pyqt5_ela_pro.chat``）。

:class:`ElaChatAsyncWorker` 把「QThread + asyncio 事件循环 + 命令队列 +
取消 / 收尾」这套宿主基础设施收进库内；信号契约与
:class:`~pyqt5_ela_pro.chat.mock.ElaChatMockBackend` 完全同构，可直接接到
:class:`~pyqt5_ela_pro.chat.binder.ElaChatStreamBinder`。

子类只需实现与具体后端相关的钩子（在钩子内直接发信号，如
``self.llmStarted.emit()`` / ``self.toolStarted.emit(tool_call)`` /
``self.statsReady.emit(usage, ttft_ms, tps)``）：

- ``_setup()``（async）：初始化后端（创建 agent / HTTP 客户端等），
  完成时发 ``ready``、失败时发 ``failed``；
- ``_stream_turn(prompt)``：返回本回合的异步分片迭代器（可 ``async def``
  生成器或直接返回后端的异步生成器），产出对象由 ``chunkReceived`` 发出；
- ``_rollback_turn(prompt)``（async，可选）：``regenerate()`` 前回滚历史；
- ``_after_turn()``（async，可选）：回合正常结束时收尾（如空正文诊断）；
- ``_reset_backend()``（async，可选）：``reset()`` 命令。

线程安全命令：``ask`` / ``regenerate`` / ``reset`` / ``cancel`` /
``shutdown``（未就绪时 ``ask`` / ``regenerate`` 返回 ``False``）。

用法::

    class MyWorker(ElaChatAsyncWorker):
        async def _setup(self):
            self._client = await create_client()
            self.ready.emit()

        def _stream_turn(self, prompt):
            return self._client.stream(prompt)

    worker = MyWorker(parent)
    worker.ready.connect(on_ready)
    worker.start()                 # QThread.start()
    ...
    worker.ask("你好")

命名规范与库内一致（``camelCase``）。
"""

from __future__ import annotations

import asyncio
import threading
from typing import AsyncIterator, Optional

from PyQt5.QtCore import QThread, pyqtSignal

#: 取消标记轮询间隔（秒）
_CANCEL_POLL_INTERVAL = 0.05
#: shutdown 等待线程退出的最长时间（毫秒）
_SHUTDOWN_WAIT_MS = 4000
#: shutdown 超时后 terminate 兜底的等待时间（毫秒）
_TERMINATE_WAIT_MS = 1000
#: 极端情况下仍未退出、需要保活避免「运行中被销毁」的 worker
_LINGERING_WORKERS: list = []


class ElaChatAsyncWorker(QThread):
    """异步后端 worker 基类（QThread + asyncio 事件循环 + 命令队列）。

    :param parent: 父对象
    """

    #: 后端初始化完成，可以提问
    ready = pyqtSignal()
    #: 后端初始化失败（携带人类可读原因）
    failed = pyqtSignal(str)
    #: 错误（类型、消息）
    errorOccurred = pyqtSignal(str, str)
    #: 回合结束但模型未返回正文（参数：finish_reason）
    emptyTurn = pyqtSignal(str)
    #: 新一轮 LLM 调用开始（用于划分步骤）
    llmStarted = pyqtSignal()
    #: 流式分片（对象由子类定义，如含 reasoning / answer 内容）
    chunkReceived = pyqtSignal(object)
    #: 工具调用开始（tool_call dict）
    toolStarted = pyqtSignal(dict)
    #: 工具调用结束（tool_call dict、结果文本）
    toolEnded = pyqtSignal(dict, str)
    #: 单次 LLM 用量（usage、首字耗时 ms、词元/秒）
    statsReady = pyqtSignal(object, float, float)
    #: 本回合结束（无论成功 / 失败 / 停止）
    turnFinished = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._queue: Optional[asyncio.Queue] = None
        self._cancel = threading.Event()
        self._closing = False

    # -- 子类钩子 ----------------------------------------------------------

    async def _setup(self) -> None:
        """初始化后端（子类实现）；默认直接发 ``ready``。"""
        self.ready.emit()

    def _stream_turn(self, prompt: str) -> AsyncIterator:
        """返回本回合的异步分片迭代器（子类实现）。"""
        raise NotImplementedError(f"{type(self).__name__} 未实现 _stream_turn")

    async def _rollback_turn(self, prompt: str) -> None:
        """``regenerate()`` 前回滚上一轮历史（子类可选实现）。"""

    async def _after_turn(self) -> None:
        """回合正常结束时收尾，如空正文诊断（子类可选实现）。"""

    async def _reset_backend(self) -> None:
        """重置后端会话（子类可选实现）。"""

    # -- 线程主体 ----------------------------------------------------------

    def run(self) -> None:  # noqa: D102
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._serve())
        except Exception as exc:
            self.failed.emit(f"worker 线程异常：{exc}")
        finally:
            self._cleanup_loop()

    def _cleanup_loop(self) -> None:
        """退出前收尾：取消残留任务再关异步生成器。"""
        try:
            # 先取消残留任务：否则流式响应仍在运行时
            # ``shutdown_asyncgens`` 会报「already running」。
            pending = asyncio.all_tasks(self._loop)
            for task in pending:
                task.cancel()
            if pending:
                self._loop.run_until_complete(
                    asyncio.gather(*pending, return_exceptions=True)
                )
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
        except Exception:
            pass
        asyncio.set_event_loop(None)
        self._loop.close()
        self._loop = None

    async def _serve(self) -> None:
        try:
            await self._setup()
        except Exception as exc:
            self.failed.emit(f"后端初始化失败：{exc}")
            return
        self._queue = asyncio.Queue()
        while True:
            command = await self._queue.get()
            if command is None:
                break
            kind, payload = command
            if kind == "ask":
                await self._run_turn(payload)
            elif kind == "regenerate":
                try:
                    await self._rollback_turn(payload)
                except Exception as exc:
                    self.errorOccurred.emit("worker", f"{type(exc).__name__}: {exc}")
                await self._run_turn(payload)
            elif kind == "reset":
                try:
                    await self._reset_backend()
                except Exception as exc:
                    self.errorOccurred.emit("worker", f"{type(exc).__name__}: {exc}")

    async def _run_turn(self, prompt: str) -> None:
        self._cancel.clear()
        try:
            stream = self._stream_turn(prompt)
        except Exception as exc:
            # _stream_turn 同步抛异常（创建生成器 / 客户端时就失败）必须
            # 在本回合内收尾：否则异常冲出 _serve 循环，worker 线程直接
            # 退出，后续 ask 永久失败且不发 turnFinished。
            self.errorOccurred.emit("worker", f"{type(exc).__name__}: {exc}")
            self.turnFinished.emit()
            return

        async def pump() -> None:
            async for chunk in stream:
                self.chunkReceived.emit(chunk)

        # 流式迭代独占一个 task：取消时向 task 注入 CancelledError，
        # 让生成器在自己的任务里正常收尾（直接 aclose 会与 SDK 内部的
        # 响应流任务冲突：RuntimeError: aclose(): already running）。
        task = asyncio.ensure_future(pump())
        watcher = asyncio.ensure_future(self._watch_cancel(task))
        try:
            try:
                await task
            except asyncio.CancelledError:
                aclose = getattr(stream, "aclose", None)
                if aclose is not None:
                    try:
                        await aclose()
                    except Exception:
                        pass
                return
            if not (self._cancel.is_set() or self._closing):
                try:
                    await self._after_turn()
                except Exception as exc:
                    self.errorOccurred.emit("worker", f"{type(exc).__name__}: {exc}")
        except Exception as exc:
            self.errorOccurred.emit("worker", f"{type(exc).__name__}: {exc}")
        finally:
            watcher.cancel()
            self.turnFinished.emit()

    async def _watch_cancel(self, task: "asyncio.Future") -> None:
        """轮询取消 / 关闭标记；命中后取消流式 task。"""
        try:
            while not task.done():
                if self._cancel.is_set() or self._closing:
                    task.cancel()
                    return
                await asyncio.sleep(_CANCEL_POLL_INTERVAL)
        except asyncio.CancelledError:
            pass

    # -- 命令接口（线程安全） ----------------------------------------------

    def ask(self, text: str) -> bool:
        """提交提问；worker 未就绪返回 ``False``。"""
        return self._submit(("ask", text))

    def regenerate(self, text: str) -> bool:
        """重新生成：先回滚历史再重跑；未就绪返回 ``False``。"""
        return self._submit(("regenerate", text))

    def reset(self) -> None:
        """重置后端会话。"""
        self._submit(("reset", None))

    def cancel(self) -> None:
        """请求中止当前回合（保留已输出内容）。"""
        self._cancel.set()

    def _submit(self, command) -> bool:
        if self._loop is None or self._queue is None:
            return False
        asyncio.run_coroutine_threadsafe(self._queue.put(command), self._loop)
        return True

    #: shutdown 等待线程退出的最长时间（毫秒），超时后 terminate 兜底
    shutdownWaitMs = _SHUTDOWN_WAIT_MS

    def shutdown(self) -> None:
        """停止 worker：终止当前回合并要求线程退出。

        先等 ``shutdownWaitMs``；仍未退出则 ``terminate()`` 兜底——避免
        窗口销毁时 QThread 仍在运行被析构（Qt fatal，进程 0xC0000409）。
        """
        self._closing = True
        self.cancel()
        if self._loop is not None and self._queue is not None:
            try:
                asyncio.run_coroutine_threadsafe(self._queue.put(None), self._loop)
            except Exception:
                pass
        if self.wait(self.shutdownWaitMs):
            return
        self.terminate()
        if not self.wait(_TERMINATE_WAIT_MS):
            # 极端情况：宁可泄漏对象也不要在运行中被销毁
            _LINGERING_WORKERS.append(self)


__all__ = ["ElaChatAsyncWorker"]
