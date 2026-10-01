"""llm_test 入口：后端选择（mock / agent）的离线冒烟测试。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

#: llm_test 不是安装包，必须先把仓库根目录塞进 sys.path 再导入
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

#: llm_test/ 目前不入库（见 .gitignore：agents/config.py 里有硬编码 key）。
#: 全新 clone 上没有这个目录，模块级 import 会让整个 tests/example 收集失败。
if not (_REPO_ROOT / "llm_test" / "main.py").is_file():
    pytest.skip("llm_test/ 未入库", allow_module_level=True)

import llm_test.agent_demo as agent_demo  # noqa: E402
from llm_test.main import DemoWindow, create_worker  # noqa: E402

from pyqt5_ela_pro.chat import ElaChatMockBackend  # noqa: E402


class TestCreateWorker:
    def test_default_backend_is_mock(self, qapp, monkeypatch):
        monkeypatch.delenv("LLM_TEST_BACKEND", raising=False)

        worker = create_worker()
        assert isinstance(worker, ElaChatMockBackend)
        worker.deleteLater()
        qapp.processEvents()

    def test_agent_backend_uses_agents_copy(self, qapp, monkeypatch):
        pytest.importorskip("openai")
        pytest.importorskip("loguru")
        monkeypatch.setenv("LLM_TEST_BACKEND", "agent")

        worker = create_worker()
        assert isinstance(worker, agent_demo.AgentWorker)
        worker.shutdown()
        worker.deleteLater()
        qapp.processEvents()


class TestClearContextWiring:
    """清空上下文 = 组件清界面 + 宿主 reset 后端（少了后端那半模型还记得上文）。"""

    def test_cleared_resets_worker(self, qapp):

        worker = ElaChatMockBackend()
        window = DemoWindow(worker)
        calls = []
        worker.reset = lambda: calls.append(1)  # 覆盖实例方法做探针

        window.chat.addMessage(1, "你好")
        qapp.processEvents()
        window.chat.clear()
        qapp.processEvents()

        assert calls == [1]
        assert window.chat.chatView().messages() == []
        window.deleteLater()
        worker.deleteLater()
        qapp.processEvents()
