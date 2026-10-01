"""聊天组件指南页：源码快照一致性 + 代码围栏 / 语法着色的回归测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from pyqt5_ela_pro.ela_markdown_viewer import ElaMarkdownViewer
from pyqt5_ela_pro.example.chat_guide_page import (
    LLM_TEST_AGENT_DEMO_SOURCE,
    LLM_TEST_MAIN_SOURCE,
    ChatGuidePage,
)

#: 仓库根目录（tests/example/ → 上两级）
_REPO_ROOT = Path(__file__).resolve().parents[2]


def _normalize(text: str) -> str:
    return text.replace("\r\n", "\n").strip("\n")


def test_snapshot_matches_llm_test_sources():
    cases = (
        ("main.py", LLM_TEST_MAIN_SOURCE),
        ("agent_demo.py", LLM_TEST_AGENT_DEMO_SOURCE),
    )
    for name, snapshot in cases:
        path = _REPO_ROOT / "llm_test" / name
        if not path.is_file():
            # llm_test/ 目前不入库（见 .gitignore）；页面侧的快照常量仍在，
            # 缺文件只能跳过这条漂移校验，不能让它把整个 tests/example 拖挂。
            pytest.skip(f"llm_test/{name} 未入库")
        assert _normalize(snapshot) == _normalize(path.read_text(encoding="utf-8")), (
            f"快照与 llm_test/{name} 不一致："
            "请把新源码同步到 example/chat_guide_page.py 的常量"
        )


def test_guide_page_renders_both_sources(qapp):
    page = ChatGuidePage()
    viewers = page.findChildren(ElaMarkdownViewer)
    assert len(viewers) >= 5

    text = "\n".join(viewer.toPlainText() for viewer in viewers)
    assert "组件栈概览" in text
    assert "四步接入" in text and "class DemoWindow" in text
    assert "关键 API 速查" in text
    assert "真实后端" in text and "class AgentWorker" in text
    assert "运行与依赖" in text

    page.deleteLater()
    qapp.processEvents()


def test_guide_page_code_fences_are_closed(qapp):
    """闭合围栏必须独占一行。

    贴到源码末行（快照常量常无尾换行）会被解析成**未闭合围栏**（= 流式中间态）：
    超过 4096 字符时静默丢掉全部 pygments 着色，同一 viewer 里后续内容还会被
    吞进代码块。白盒断言 ``closed`` 标志，不依赖 pygments 是否安装。
    """
    page = ChatGuidePage()
    blocks = [
        fenced
        for viewer in page.findChildren(ElaMarkdownViewer)
        for fenced in viewer._fenced_blocks
    ]
    assert len(blocks) >= 3, blocks
    unclosed = [(lang, code[:40]) for lang, code, closed in blocks if not closed]
    assert not unclosed, f"围栏没闭合（末行与 ``` 粘连）：{unclosed}"

    page.deleteLater()
    qapp.processEvents()


@pytest.mark.parametrize("marker", ["raise SystemExit(main())", "class AgentWorker"])
def test_guide_page_sources_are_highlighted(qapp, marker):
    """两个源码快照块必须真的带 pygments 着色。

    判据：代码行内出现**不止一种**前景色（跳过行号槽）。整块无着色时只有基色一种
    → 必挂。颜色比 ``.name()`` 字符串：``QColor.__eq__`` 对 Qt 内部返回的颜色不靠谱。
    """
    pytest.importorskip("pygments")
    page = ChatGuidePage()
    viewer = next(
        v for v in page.findChildren(ElaMarkdownViewer) if marker in v.toPlainText()
    )
    cursor = viewer.document().find(marker)
    assert not cursor.isNull(), marker

    colors = set()
    it = cursor.block().begin()
    while not it.atEnd():
        fragment = it.fragment()
        if fragment.isValid():
            text = fragment.text().strip()
            if text and not text.isdigit():  # 行号槽是纯数字片段
                colors.add(fragment.charFormat().foreground().color().name())
        it += 1
    assert len(colors) >= 2, f"{marker} 所在代码块没有语法着色：{sorted(colors)}"

    page.deleteLater()
    qapp.processEvents()
