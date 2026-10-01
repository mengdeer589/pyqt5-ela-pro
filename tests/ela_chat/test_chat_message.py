"""ElaChatMessage / 角色与状态常量测试。"""

from __future__ import annotations

import pytest

from pyqt5_ela_pro.chat import (
    ElaChatAttachment,
    ElaChatMessage,
    ElaChatReasoningStyle,
    ElaChatRole,
    ElaChatStats,
    ElaChatStatus,
    ElaChatToolCall,
    ElaChatToolStatus,
)


class TestRoleAndStatus:
    def test_role_values(self):
        assert ElaChatRole.User == "user"
        assert ElaChatRole.Assistant == "assistant"
        assert ElaChatRole.System == "system"
        assert set(ElaChatRole.All) == {"user", "assistant", "system"}

    def test_status_values(self):
        assert ElaChatStatus.Streaming == "streaming"
        # queued：流式开始后、首个模型输出前的头部展示态；不进 All（不落数据）
        assert ElaChatStatus.Queued == "queued"
        assert ElaChatStatus.Done == "done"
        assert ElaChatStatus.Stopped == "stopped"
        assert ElaChatStatus.Error == "error"
        assert len(ElaChatStatus.All) == 4

    def test_tool_status_values(self):
        assert ElaChatToolStatus.Pending == "pending"
        assert ElaChatToolStatus.Running == "running"
        assert ElaChatToolStatus.Done == "done"
        assert ElaChatToolStatus.Error == "error"
        # aborted：回合被停止/中断时仍未落定的调用（不会真的失败，故与 error 分开）
        assert ElaChatToolStatus.Aborted == "aborted"
        assert set(ElaChatToolStatus.All) == {
            "pending",
            "running",
            "done",
            "error",
            "aborted",
        }
        # Settled = 不再显示忙碌环
        assert set(ElaChatToolStatus.Settled) == {"done", "error", "aborted"}


class TestConstants:
    def test_reasoning_style(self):

        assert ElaChatReasoningStyle.Collapse == "collapse"
        assert ElaChatReasoningStyle.Inline == "inline"
        assert set(ElaChatReasoningStyle.All) == {"collapse", "inline"}


class TestElaChatMessage:
    def test_defaults(self):
        message = ElaChatMessage(id=1, role=ElaChatRole.User)
        assert message.text == ""
        assert message.status == ElaChatStatus.Done
        assert message.created_at == 0.0

    def test_role_properties(self):
        user = ElaChatMessage(id=1, role=ElaChatRole.User)
        assistant = ElaChatMessage(id=2, role=ElaChatRole.Assistant)
        system = ElaChatMessage(id=3, role=ElaChatRole.System)
        assert user.isUser and not user.isAssistant and not user.isSystem
        assert assistant.isAssistant and not assistant.isUser
        assert system.isSystem and not system.isUser

    def test_is_streaming(self):
        streaming = ElaChatMessage(
            id=1, role=ElaChatRole.Assistant, status=ElaChatStatus.Streaming
        )
        assert streaming.isStreaming
        assert not ElaChatMessage(id=2, role=ElaChatRole.User).isStreaming

    def test_frozen_and_helpers(self):
        original = ElaChatMessage(id=1, role=ElaChatRole.User, text="a")
        with pytest.raises(Exception):
            original.text = "b"  # type: ignore[misc]
        changed = original.withText("b")
        assert changed.text == "b" and original.text == "a"
        stopped = original.withStatus(ElaChatStatus.Stopped)
        assert stopped.status == ElaChatStatus.Stopped
        assert original.status == ElaChatStatus.Done

    def test_rich_defaults(self):
        message = ElaChatMessage(id=1, role=ElaChatRole.Assistant)
        assert message.title == ""
        assert message.timestamp == ""
        assert message.reasoning == ""
        assert message.reasoning_ms == 0.0
        assert message.tool_calls == ()
        assert message.attachments == ()
        assert message.stats is None
        assert message.error == ""

    def test_rich_helpers(self):
        message = ElaChatMessage(id=1, role=ElaChatRole.Assistant)
        tool_call = ElaChatToolCall(id="t1", name="search")
        updated = (
            message.withTitle("模型")
            .withTimestamp("12:00")
            .withReasoning("推理", 900.0)
            .withToolCall(tool_call)
            .withAttachments([ElaChatAttachment(name="a.txt")])
            .withStats(ElaChatStats(total_tokens=5))
            .withDuration(4200.0)
            .withError("err")
        )
        assert updated.title == "模型"
        assert updated.timestamp == "12:00"
        assert updated.reasoning == "推理"
        assert updated.reasoning_ms == 900.0
        assert updated.tool_calls == (tool_call,)
        assert updated.attachments[0].name == "a.txt"
        assert updated.stats.total_tokens == 5
        assert updated.duration_ms == 4200.0
        assert updated.error == "err"
        # 合并同一 id 的工具调用
        merged = updated.withToolCall(
            ElaChatToolCall(id="t1", name="search", result="ok")
        )
        assert len(merged.tool_calls) == 1
        assert merged.tool_calls[0].result == "ok"


class TestElaChatAttachment:
    def test_display_size(self):
        assert ElaChatAttachment(name="a", size=0).displaySize == "0 B"
        assert ElaChatAttachment(name="a", size=1024).displaySize == "1.0 KB"
        attachment = ElaChatAttachment(name="a", path="C:/a", size=2)
        assert attachment.withName("b").name == "b"

    def test_image_detection(self):
        assert ElaChatAttachment(name="a.png").isImage
        assert ElaChatAttachment(name="b.JPG").isImage
        assert ElaChatAttachment(name="c", mime="image/webp").isImage
        assert not ElaChatAttachment(name="d.txt").isImage
        # 宿主可能传 None，不能因此崩溃
        assert not ElaChatAttachment(name="e.txt", mime=None).isImage

    def test_digest_and_mime_fields(self):
        attachment = ElaChatAttachment(name="a.png", digest="abc", mime="image/png")
        assert attachment.digest == "abc"
        assert attachment.mime == "image/png"


class TestElaChatToolCall:
    def test_status_properties(self):
        call = ElaChatToolCall(id="t", name="run")
        assert call.isRunning and not call.isDone and not call.isError
        done = call.withResult("ok")
        assert done.isDone and done.result == "ok"
        failed = call.withResult("boom", ElaChatToolStatus.Error)
        assert failed.isError
        assert call.withArguments("{}").arguments == "{}"


class TestElaChatStats:
    def test_tooltip(self):
        stats = ElaChatStats(
            duration_ms=3200.0, ttft_ms=250.0, tps=12.34, cached_tokens=64
        )
        tooltip = stats.tooltip()
        # 首字在前，耗时紧随其后（便于把端到端耗时并入同一行）
        assert tooltip.startswith("首字 250 ms")
        assert "耗时 3.2s" in tooltip
        assert "12.3 词元/s" in tooltip
        assert "缓存 64 词元" in tooltip
        assert ElaChatStats().tooltip() == ""
        assert "耗时 1m 20s" in ElaChatStats(duration_ms=80000.0).tooltip()
        assert "端到端 3.2s" in ElaChatStats(duration_ms=3200.0).tooltip("端到端")
