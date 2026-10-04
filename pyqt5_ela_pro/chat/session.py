"""
会话（话题）快照数据模型（``pyqt5_ela_pro.chat``）。

**多话题由宿主管理**：组件是「单话题视图」，多话题按「一话题一 widget」
放大（``ElaTabBar`` + ``QStackedWidget``，见 ``example/chat_session_page.py``）——
话题的新建 / 归档 / 切换 / 列表 UI 全是宿主的事，组件侧只用
``ElaChatWidget.setCurrentSessionId()` 记一个纯标记。

本模块只提供两样东西：

- :class:`ElaChatSessionInfo`：话题元数据快照（``id`` / 标题 / 创建时间 /
  消息条数 / 工作目录），成对 ``toDict()`` / ``fromDict()`` 可直接落库；
- 整会话（元数据 + 消息 + 视图外观）的导出 / 导入见
  ``ElaChatView.exportSession()`` / ``importSession()`` —— 归档 / 恢复话题
  就是「导出 bundle → 销毁页面；重建页面 → 导入 bundle」。
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .message import _as_float, _as_int, _as_str

#: 会话 bundle 格式版本（与消息的 ``SCHEMA_VERSION`` 独立演进）
SESSION_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ElaChatSessionInfo:
    """会话（话题）快照。"""

    #: 会话唯一标识
    id: str
    #: 会话标题
    title: str = "新话题"
    #: 创建时间（``time.time()`` 秒）
    created_at: float = 0.0
    #: 消息条数
    message_count: int = 0
    #: 关联工作目录（宿主自定义用途）
    work_dir: str = ""

    def withTitle(self, title: str) -> "ElaChatSessionInfo":
        """返回替换标题后的新快照。"""
        return replace(self, title=title or "新话题")

    def withMessageCount(self, count: int) -> "ElaChatSessionInfo":
        """返回替换消息条数后的新快照。"""
        return replace(self, message_count=_as_int(count))

    # -- 持久化 ------------------------------------------------------------

    def toDict(self) -> dict:
        """转为纯 JSON 字典，可直接 ``json.dumps`` 落库。"""
        return {
            "id": self.id,
            "title": self.title,
            "created_at": _as_float(self.created_at),
            "message_count": _as_int(self.message_count),
            "work_dir": self.work_dir,
        }

    @classmethod
    def fromDict(cls, data) -> "ElaChatSessionInfo":
        """从字典还原（容错：缺字段取默认、多余字段忽略、类型不对就强转）。"""
        if not isinstance(data, dict):
            return cls(id="")
        return cls(
            id=_as_str(data.get("id")),
            title=_as_str(data.get("title"), "新话题"),
            created_at=_as_float(data.get("created_at")),
            message_count=_as_int(data.get("message_count")),
            work_dir=_as_str(data.get("work_dir")),
        )
