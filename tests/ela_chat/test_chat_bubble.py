"""ElaChatBubble 分层气泡组件测试（用户 / 助手 / 系统三种角色）。"""

from __future__ import annotations


from _qthelpers import wait_until as _wait_until
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication
from PyQt5ElaWidgetTools import ElaThemeType

from pyqt5_ela_pro.chat._theme import muted_color

from pyqt5_ela_pro.chat import (
    DISCLAIMER_TEXT,
    ElaChatBubble,
    ElaChatRole,
    ElaChatStats,
    ElaChatStatus,
    ElaChatToolStatus,
    ElaChatWidget,
)


class TestUserBubble:
    def test_plain_text_and_selectable(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.User, "<b>不是 HTML</b>")
        assert bubble.role() == ElaChatRole.User
        assert bubble.text() == "<b>不是 HTML</b>"
        assert bubble._label.textFormat() == Qt.TextFormat.PlainText
        assert (
            bubble._label.textInteractionFlags()
            & Qt.TextInteractionFlag.TextSelectableByMouse
        )
        bubble.deleteLater()

    def test_layers_present(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.User, "hi")
        # 头部层（头像在头部内）+ 正文层 + 底部操作层
        assert bubble.header().role() == ElaChatRole.User
        assert bubble.header().avatar() is not None
        assert bubble._body is not None
        assert bubble.actions().keys() == ["copy", "undo"]
        bubble.deleteLater()

    def test_max_width_ratio(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.User, "一段比较长的文本" * 5)
        bubble.resize(600, 80)
        bubble.show()
        qapp.processEvents()
        bubble.setMaxWidthRatio(0.5)
        assert bubble.maxWidthRatio() == 0.5
        assert bubble._body.maximumWidth() <= int(600 * 0.5) + 1
        bubble.deleteLater()

    def test_set_text_and_append(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.User, "a")
        bubble.setText("b")
        bubble.appendText("c")
        assert bubble.text() == "bc"
        bubble.deleteLater()

    def test_title_timestamp_status(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.User, "hi")
        bubble.setTitle("我")
        bubble.setTimestamp("12:00:01")
        bubble.setStatus(ElaChatStatus.Stopped)
        header = bubble.header()
        assert bubble.title() == "我"
        assert bubble.timestamp() == "12:00:01"
        assert header.title() == "我"
        assert header.timestamp() == "12:00:01"
        assert header.statusText() == "已停止"
        bubble.deleteLater()

    def test_copy_action_copies_clipboard(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.User, "复制我")
        copied = []
        bubble.copyRequested.connect(lambda: copied.append(1))
        bubble.actions().toolButton("copy").click()
        assert copied == [1]
        assert QApplication.clipboard().text() == "复制我"
        bubble.deleteLater()

    def test_undo_action_signal(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.User, "hi")
        undone = []
        bubble.undoRequested.connect(lambda: undone.append(1))
        bubble.actions().toolButton("undo").click()
        assert undone == [1]
        bubble.deleteLater()

    def test_attachments_layer(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.User, "hi")
        assert bubble.attachments() == []
        bubble.addAttachment("a.pdf", "C:/tmp/a.pdf", 2048)
        bubble.setAttachments([{"name": "b.txt", "path": "C:/tmp/b.txt", "size": 10}])
        attachments = bubble.attachments()
        assert len(attachments) == 1
        assert attachments[0].name == "b.txt"
        assert attachments[0].displaySize == "10 B"
        bubble.clearAttachments()
        assert bubble.attachments() == []
        bubble.deleteLater()

    def test_attachment_chips_right_aligned_and_fit(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.User, "hi")
        bubble.resize(700, 220)
        bubble.show()
        qapp.processEvents()
        bubble.addAttachment("算法笔记.pdf", "C:/tmp/notes.pdf", 345678)
        for _ in range(5):
            qapp.processEvents()
        strip = bubble.attachmentStrip()
        assert strip.alignment() == Qt.AlignmentFlag.AlignRight
        chip = strip._cards[0]
        # 文本 + 左右内边距 + 关闭按钮宽度，不能被裁掉
        text_width = chip.fontMetrics().horizontalAdvance(chip.text())
        assert chip.width() >= text_width + 32
        assert chip.geometry().right() <= strip.width()
        bubble.deleteLater()

    def test_bubble_width_follows_text(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.User, "你好")
        bubble.resize(600, 160)
        bubble.show()
        qapp.processEvents()
        narrow = bubble._body.width()
        bubble.setText("很长的内容" * 20)
        qapp.processEvents()
        wide = bubble._body.width()
        assert wide > narrow
        assert wide <= int(600 * 0.72) + 1
        bubble.deleteLater()


class TestAssistantBubble:
    def test_markdown_viewer_embedded(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.Assistant, "**粗体**")
        viewer = bubble.markdownViewer()
        assert viewer is not None
        assert viewer.embeddedMode() is True
        assert viewer.markdown().strip() == "**粗体**"
        bubble.deleteLater()

    def test_text_viewer_trims_trailing_margin(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.Assistant, "一行正文")
        viewer = bubble.markdownViewer()
        assert viewer is not None
        # 聊天正文查看器启用文末空白裁剪（正文 → 后续分段的间距与其它分段一致）
        assert viewer.embeddedTrimBottom() is True

        bubble.resize(520, 200)
        bubble.show()
        qapp.processEvents()
        document = viewer.document()
        last_rect = document.documentLayout().blockBoundingRect(document.lastBlock())
        assert viewer.height() < document.size().height()
        assert viewer.height() >= last_rect.bottom()
        bubble.deleteLater()

    def test_stream_flow(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        finished = []
        bubble.streamFinished.connect(lambda: finished.append(bubble.status()))
        bubble.beginStream()
        assert bubble.isStreaming()
        assert bubble.status() == ElaChatStatus.Streaming
        # 阶段一：等待模型首个输出（TTFT）
        assert bubble.header().statusKind() == ElaChatStatus.Queued
        assert bubble.header().statusText() == "排队中…"
        bubble.appendText("# 标题")
        # 阶段二：收到首个分片即转「生成中」
        assert bubble.header().statusKind() == ElaChatStatus.Streaming
        assert bubble.header().statusText() == "生成中…"
        bubble.appendText("\n\n正文")
        assert _wait_until(qapp, lambda: "正文" in bubble.text())
        bubble.endStream()
        assert not bubble.isStreaming()
        assert bubble.status() == ElaChatStatus.Done
        assert finished == [ElaChatStatus.Done]
        bubble.deleteLater()

    def test_stream_placeholder(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        bubble.beginStream()
        assert bubble.markdownViewer().placeholderText() == "正在生成…"
        bubble.endStream(ElaChatStatus.Stopped)
        assert bubble.status() == ElaChatStatus.Stopped
        bubble.deleteLater()

    def test_non_assistant_begin_stream_noop(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.User, "hi")
        bubble.beginStream()
        assert not bubble.isStreaming()
        bubble.endStream()
        assert bubble.status() == ElaChatStatus.Done
        bubble.deleteLater()

    def test_two_phase_status_reasoning_first(self, qapp):
        """思考先到也算「模型已开始输出」：排队中 → 生成中。"""
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        bubble.beginStream()
        assert bubble.header().statusText() == "排队中…"
        bubble.appendReasoning("先想想")
        assert bubble.header().statusKind() == ElaChatStatus.Streaming
        assert bubble.header().statusText() == "生成中…"
        bubble.endStream()
        bubble.deleteLater()

    def test_two_phase_status_tool_first(self, qapp):
        """工具调用先到同样触发阶段切换。"""
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        bubble.beginStream()
        assert bubble.header().statusKind() == ElaChatStatus.Queued
        bubble.addToolCall("read", "{}")
        assert bubble.header().statusKind() == ElaChatStatus.Streaming
        bubble.endStream()
        bubble.deleteLater()

    def test_two_phase_status_stop_before_first_token(self, qapp):
        """首个输出前停止：直接进终态，不留「排队中」。"""
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        bubble.beginStream()
        bubble.endStream(ElaChatStatus.Stopped)
        assert bubble.header().statusKind() == ElaChatStatus.Stopped
        assert bubble.header().statusText() == "已停止"
        bubble.deleteLater()

    def test_two_phase_status_via_widget(self, qapp):
        """widget 回合路径：beginAssistantMessage → 排队中；首个分片 → 生成中。"""

        chat = ElaChatWidget()
        messageId = chat.beginAssistantMessage()
        view = chat.chatView()
        bubble = view.bubble(messageId)
        assert bubble.header().statusText() == "排队中…"
        view.appendText(messageId, "第一片")
        assert bubble.header().statusText() == "生成中…"
        chat.endAssistantMessage(messageId)
        assert bubble.header().statusText() == ""
        chat.deleteLater()
        qapp.processEvents()

    def test_reasoning_layer(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        bubble.beginReasoning()
        block = bubble.reasoningBlock()
        assert block.isOpened()
        bubble.appendReasoning("先看条件")
        bubble.appendReasoning("再推导")
        assert bubble.reasoning() == "先看条件再推导"
        bubble.endReasoning(1500)
        assert not block.isOpened()
        assert "思考完成 (1.5s)" in block.title()
        bubble.deleteLater()

    def test_tool_call_layer(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        callId = bubble.addToolCall("read_file", '{"path": "a.txt"}')
        assert bubble.toolCallCount() == 1
        running = bubble.toolCall(callId)
        assert running.name == "read_file"
        assert running.status == ElaChatToolStatus.Running
        bubble.setToolCallResult(callId, "文件内容")
        done = bubble.toolCall(callId)
        assert done.isDone and done.result == "文件内容"
        bubble.clearToolCalls()
        assert bubble.toolCallCount() == 0
        bubble.deleteLater()

    def test_stats_layer(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        stats = ElaChatStats(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
            ttft_ms=250.0,
            tps=12.5,
        )
        bubble.setStepStats(stats)
        assert bubble.stats() is stats
        assert bubble.statsBadge().isVisible() is False  # 未 show，父链不可见
        assert "首字 250 ms" in stats.tooltip()
        bubble.deleteLater()

    def test_error_layer(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        bubble.setError("连接超时")
        assert bubble.error() == "连接超时"
        assert bubble.status() == ElaChatStatus.Error
        bubble.clearError()
        assert bubble.error() == ""
        bubble.deleteLater()

    def test_actions_keys(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        assert bubble.actions().keys() == ["copy", "regenerate"]
        bubble.deleteLater()

    def test_header_title_font_stack(self, qapp, make):
        """标题字体走 ``QFont`` 字体栈（拉丁 Segoe UI、中文逐字形回退），不用 QSS。"""
        bubble = make(ElaChatBubble, ElaChatRole.Assistant)
        label = bubble.header()._title_label
        assert list(label.font().families())[:2] == ["Segoe UI", "Microsoft YaHei UI"]
        assert label.font().pixelSize() == 13
        # ElaText 自带一条透明底规则（C++ 构造里设的），这里只断言我们没再写字体 / 颜色 QSS
        assert "font-family" not in label.styleSheet()
        assert "font-size" not in label.styleSheet()

    def test_avatar_icon_offset_aligns_to_device_pixels(self, qapp):
        """头像位图落点要对齐设备像素网格（高 DPI 下发虚 / 偏移的根因）。"""
        from pyqt5_ela_pro.chat.blocks import AVATAR_SIZE, _AvatarBadge

        badge = _AvatarBadge(ElaChatRole.Assistant)
        badge.resize(AVATAR_SIZE, AVATAR_SIZE)
        logical = AVATAR_SIZE * 0.62
        for dpr in (1.0, 1.25, 1.5, 2.0):
            offset = badge._device_aligned_offset(logical, logical, dpr)
            # 落点 × dpr 必须为整数，否则 1:1 位图会被 SmoothPixmapTransform 重采样
            assert (offset.x() * dpr).is_integer(), (dpr, offset)
            assert (offset.y() * dpr).is_integer(), (dpr, offset)
            # 同时仍然居中（误差不超过一个设备像素）
            assert abs(offset.x() - (AVATAR_SIZE - logical) / 2) <= 1 / dpr + 1e-9
        badge.deleteLater()

    def test_disclaimer_label(self, qapp):
        """底部「内容由 AI 生成，仅供参考」：只助手消息有，随整行显隐，可改可关。"""
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        assert bubble.disclaimer() == DISCLAIMER_TEXT
        assert bubble.disclaimerVisible() is True

        bubble.setDisclaimer("本回答由 AI 生成")
        assert bubble.disclaimer() == "本回答由 AI 生成"

        # 流式期间跟着整条底部行一起隐藏（与操作按钮 / 用量同一套规则）
        bubble.beginStream()
        assert bubble.footer().isHidden() is True
        assert bubble.disclaimerVisible() is False
        bubble.endStream()
        assert bubble.disclaimerVisible() is True

        bubble.setDisclaimerVisible(False)
        assert bubble.disclaimerVisible() is False
        bubble.setDisclaimer("")  # 空串 → 自动隐藏
        assert bubble.disclaimer() == ""
        assert bubble.disclaimerVisible() is False
        bubble.deleteLater()

    def test_user_bubble_has_no_disclaimer(self, qapp):
        """「AI 生成」提示只属于助手消息 —— 用户消息没有这个标签。"""
        bubble = ElaChatBubble(ElaChatRole.User, "我发的")
        assert bubble.disclaimer() == DISCLAIMER_TEXT  # 文案仍是全局设置
        assert bubble.disclaimerVisible() is False
        bubble.deleteLater()

    def test_invalid_status_falls_back_to_done(self, qapp):
        """状态是字符串枚举：非法值（如大小写笔误）一律回落 Done，不污染状态机。"""
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        bubble.beginStream()
        assert bubble.status() == ElaChatStatus.Streaming

        bubble.setStatus("Done")  # 笔误：应为 ElaChatStatus.Done
        assert bubble.status() == ElaChatStatus.Done
        assert bubble.footer().isHidden() is False  # 按 Done 收尾，底部行正常回来

        bubble.setStatus("bogus")
        assert bubble.status() == ElaChatStatus.Done
        bubble.setStatus(ElaChatStatus.Stopped)
        assert bubble.status() == ElaChatStatus.Stopped
        bubble.deleteLater()

    def test_footer_hidden_while_streaming(self, qapp):
        """底部行（复制 / 重新生成 / 用量 / 耗时）整行只在回合有结果之后出现。"""
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        assert bubble.footer().isHidden() is False  # 静态消息（Done）→ 正常显示

        bubble.beginStream()
        assert bubble.footer().isHidden() is True
        bubble.appendText("正在写…")
        assert bubble.footer().isHidden() is True  # 流式期间一直不出现
        for key in ("copy", "regenerate"):
            assert bubble.actions().toolButton(key).isVisibleTo(bubble) is False

        bubble.endStream()
        assert bubble.footer().isHidden() is False
        for key in ("copy", "regenerate"):
            assert bubble.actions().toolButton(key).isVisibleTo(bubble) is True
        bubble.deleteLater()

    def test_footer_visible_after_stop_and_error(self, qapp):
        """停止 / 出错之后底部行要回来（这两种结果都需要复制与重新生成）。"""
        for status in (ElaChatStatus.Stopped, ElaChatStatus.Error):
            bubble = ElaChatBubble(ElaChatRole.Assistant)
            bubble.beginStream()
            bubble.endStream(status)
            assert bubble.footer().isHidden() is False
            assert bubble.actions().toolButton("regenerate").isVisibleTo(bubble) is True
            bubble.deleteLater()

    def test_stats_badge_hidden_during_tool_steps(self, qapp):
        """智能体调工具的过程中不显示词元用量：中途数字不是最终值、还会来回跳。"""
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        bubble.beginStream()
        bubble.setStepStats(ElaChatStats(total_tokens=120))
        badge = bubble.statsBadge()
        assert badge is not None
        assert badge.isVisibleTo(bubble) is False  # 第一步用量 → 不显示
        bubble.addToolCall("read_file", '{"path": "a.py"}', "call-1")  # 中间工具步骤
        bubble.beginStep()
        bubble.setStepStats(ElaChatStats(total_tokens=180))
        assert bubble.statsBadge().isVisibleTo(bubble) is False

        bubble.endStream()
        assert bubble.statsBadge().isVisibleTo(bubble) is True  # 回合结束才出现
        assert bubble.stats().total_tokens == 300  # 各步求和
        bubble.deleteLater()

    def test_stats_badge_hidden_in_steps_mode_too(self, qapp):
        """调试用的 ``"steps"`` 模式同样等回合结束 —— 过程里不摆用量。"""
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        bubble.setStatsMode("steps")
        bubble.beginStream()
        bubble.setStepStats(ElaChatStats(total_tokens=10))
        assert bubble.statsBadge().isVisibleTo(bubble) is False
        bubble.endStream()
        assert bubble.statsBadge().isVisibleTo(bubble) is True
        bubble.deleteLater()

    def test_attachment_strip_left_aligned(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        assert bubble.attachmentStrip().alignment() == Qt.AlignmentFlag.AlignLeft
        bubble.deleteLater()


class TestSystemBubble:
    def test_centered_and_header_hidden(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.System, "会话已开始")
        assert bubble.header().isHidden()
        assert bubble._label.alignment() == Qt.AlignmentFlag.AlignCenter
        holder_layout = bubble._label.parentWidget().layout()
        assert holder_layout.itemAt(0).spacerItem() is not None
        assert holder_layout.itemAt(holder_layout.count() - 1).spacerItem() is not None
        # 系统消息文本走 palette 上色（禁 QSS 后不再有 color: 规则）
        assert bubble._label.palette().color(
            QPalette.ColorRole.WindowText
        ) == muted_color(bubble._theme_mode, 0.45)
        assert bubble.actions().isHidden()
        bubble.deleteLater()


class TestAppearance:
    def test_avatar_visibility(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.Assistant, "hi")
        bubble.show()
        qapp.processEvents()
        assert bubble.avatarVisible()
        avatar = bubble.header().avatar()
        assert avatar.isVisible()
        bubble.setAvatarVisible(False)
        assert not bubble.avatarVisible()
        assert not avatar.isVisible()
        bubble.deleteLater()

    def test_theme_switch_recolors_bubble(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.User, "hi")
        before = bubble._body._bg.name()
        bubble._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        after = bubble._body._bg.name()
        assert after != before
        bubble.deleteLater()

    def test_role_fallback(self, qapp):
        bubble = ElaChatBubble("unknown-role", "hi")
        assert bubble.role() == ElaChatRole.Assistant
        bubble.deleteLater()
