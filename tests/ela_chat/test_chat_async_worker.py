"""ElaChatAsyncWorker 测试：回合顺序、串行、取消、回滚与关闭（假子类）。"""

from __future__ import annotations

import asyncio

from _qthelpers import wait_until as _wait_until

from pyqt5_ela_pro.chat import ElaChatAsyncWorker
from pyqt5_ela_pro.chat import worker as worker_module


class _FakeWorker(ElaChatAsyncWorker):
    """脚本化假后端：llm / chunk / sleep / tool 事件 + 钩子计数。"""

    def __init__(self, script=None, parent=None) -> None:
        super().__init__(parent)
        self.script = script or [("llm",), ("chunk", "a"), ("chunk", "b")]
        self.setup_count = 0
        self.rollback_args = []
        self.after_count = 0
        self.reset_count = 0
        self.active = 0
        self.max_active = 0

    async def _setup(self) -> None:
        self.setup_count += 1
        self.ready.emit()

    def _stream_turn(self, prompt):
        async def gen():
            self.active += 1
            self.max_active = max(self.max_active, self.active)
            try:
                for item in self.script:
                    if item[0] == "llm":
                        self.llmStarted.emit()
                    elif item[0] == "tool_start":
                        self.toolStarted.emit(item[1])
                    elif item[0] == "tool_end":
                        self.toolEnded.emit(item[1], item[2])
                    elif item[0] == "sleep":
                        await asyncio.sleep(item[1])
                    else:
                        yield item[1]
                    await asyncio.sleep(0)
            finally:
                self.active -= 1

        return gen()

    async def _rollback_turn(self, prompt: str) -> None:
        self.rollback_args.append(prompt)

    async def _after_turn(self) -> None:
        self.after_count += 1

    async def _reset_backend(self) -> None:
        self.reset_count += 1


def _started(qapp, worker):
    worker.start()
    # _queue 就绪才代表 _setup 完成、可以提交命令
    assert _wait_until(qapp, lambda: worker._queue is not None)
    return worker


def _dispose(qapp, worker):
    worker.shutdown()
    worker.deleteLater()
    qapp.processEvents()


class TestLifecycle:
    def test_turn_signal_order(self, qapp):
        worker = _FakeWorker()
        events = []
        worker.ready.connect(lambda: events.append("ready"))
        worker.llmStarted.connect(lambda: events.append("llm"))
        worker.chunkReceived.connect(lambda chunk: events.append(f"chunk:{chunk}"))
        worker.turnFinished.connect(lambda: events.append("finished"))
        _started(qapp, worker)

        assert worker.ask("你好") is True
        assert _wait_until(qapp, lambda: "finished" in events)
        assert events == ["ready", "llm", "chunk:a", "chunk:b", "finished"]
        assert worker.after_count == 1
        _dispose(qapp, worker)

    def test_asks_are_serialized(self, qapp):
        worker = _FakeWorker(script=[("chunk", "x"), ("sleep", 0.05)])
        _started(qapp, worker)
        finished = []
        worker.turnFinished.connect(lambda: finished.append(True))
        assert worker.ask("一") is True
        assert worker.ask("二") is True
        assert _wait_until(qapp, lambda: len(finished) == 2)
        assert worker.max_active == 1
        _dispose(qapp, worker)

    def test_tools_and_stats_pass_through(self, qapp):
        worker = _FakeWorker(
            script=[
                ("llm",),
                ("tool_start", {"id": "t1", "function": {"name": "read"}}),
                ("tool_end", {"id": "t1"}, "内容"),
            ]
        )
        events = []
        worker.toolStarted.connect(lambda tc: events.append(("start", tc["id"])))
        worker.toolEnded.connect(lambda tc, r: events.append(("end", tc["id"], r)))
        _started(qapp, worker)
        assert worker.ask("读文件") is True
        assert _wait_until(qapp, lambda: len(events) == 2)
        assert events == [("start", "t1"), ("end", "t1", "内容")]
        _dispose(qapp, worker)


class TestCancel:
    def test_cancel_stops_stream_and_finishes_once(self, qapp):
        worker = _FakeWorker(script=[("chunk", "a"), ("sleep", 5.0), ("chunk", "b")])
        chunks = []
        finished = []
        worker.chunkReceived.connect(chunks.append)
        worker.turnFinished.connect(lambda: finished.append(True))
        _started(qapp, worker)

        assert worker.ask("长回答") is True
        assert _wait_until(qapp, lambda: chunks == ["a"])
        worker.cancel()
        assert _wait_until(qapp, lambda: bool(finished))
        assert chunks == ["a"]
        assert len(finished) == 1
        qapp.processEvents()
        assert len(finished) == 1
        # 取消后还能继续下一轮
        worker.script = [("chunk", "next")]
        assert worker.ask("再来") is True
        assert _wait_until(qapp, lambda: chunks[-1] == "next")
        _dispose(qapp, worker)


class TestCommands:
    def test_regenerate_rolls_back_first(self, qapp):
        worker = _FakeWorker(script=[("chunk", "x")])
        _started(qapp, worker)
        assert worker.regenerate("原问题") is True
        assert _wait_until(qapp, lambda: worker.rollback_args == ["原问题"])
        assert _wait_until(qapp, lambda: worker.after_count == 1)
        _dispose(qapp, worker)

    def test_reset_calls_backend(self, qapp):
        worker = _FakeWorker()
        _started(qapp, worker)
        worker.reset()
        assert _wait_until(qapp, lambda: worker.reset_count == 1)
        _dispose(qapp, worker)

    def test_ask_before_ready_returns_false(self, qapp):
        worker = _FakeWorker()
        assert worker.ask("你好") is False
        worker.deleteLater()
        qapp.processEvents()

    def test_setup_failure_emits_failed(self, qapp):
        class _BadWorker(_FakeWorker):
            async def _setup(self):
                raise RuntimeError("backend down")

        worker = _BadWorker()
        errors = []
        worker.failed.connect(errors.append)
        worker.start()
        assert _wait_until(qapp, lambda: bool(errors))
        assert "backend down" in errors[0]
        assert worker.ask("你好") is False
        _dispose(qapp, worker)

    def test_sync_stream_error_keeps_worker_alive(self, qapp):
        """_stream_turn 同步抛异常：收尾本回合且线程循环存活。"""

        class _SyncBadWorker(_FakeWorker):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.calls = 0

            def _stream_turn(self, prompt):
                self.calls += 1
                if self.calls == 1:
                    raise RuntimeError("sync boom")
                return super()._stream_turn(prompt)

        worker = _SyncBadWorker()
        errors = []
        finished = []
        worker.errorOccurred.connect(lambda kind, msg: errors.append((kind, msg)))
        worker.turnFinished.connect(lambda: finished.append(True))
        _started(qapp, worker)

        assert worker.ask("你好") is True
        assert _wait_until(qapp, lambda: bool(finished))
        assert errors and "sync boom" in errors[0][1]
        assert worker.isRunning() is True

        chunks = []
        worker.chunkReceived.connect(chunks.append)
        worker.script = [("chunk", "next")]
        assert worker.ask("再来") is True
        assert _wait_until(qapp, lambda: chunks == ["next"])
        _dispose(qapp, worker)


class TestShutdown:
    def test_shutdown_stops_thread(self, qapp):
        worker = _FakeWorker(script=[("sleep", 5.0), ("chunk", "late")])
        _started(qapp, worker)
        assert worker.ask("长任务") is True
        assert _wait_until(qapp, lambda: worker.active == 1)
        worker.shutdown()
        assert worker.isRunning() is False
        worker.deleteLater()
        qapp.processEvents()

    def test_shutdown_terminates_stuck_thread(self, qapp, monkeypatch):
        """线程超时未退出时 terminate 兜底，避免运行中被销毁（Qt fatal）。"""

        worker = _FakeWorker()
        worker._queue = object()
        worker._loop = object()
        calls = []
        monkeypatch.setattr(worker, "wait", lambda ms: False)
        monkeypatch.setattr(worker, "terminate", lambda: calls.append(True))
        worker.shutdown()
        assert calls == [True]
        assert worker in worker_module._LINGERING_WORKERS
        worker_module._LINGERING_WORKERS.remove(worker)
        worker.deleteLater()
        qapp.processEvents()
