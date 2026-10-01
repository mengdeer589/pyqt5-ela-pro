"""
菜单项 / 动作定义（``pyqt5_ela_pro.menu_item``）。

:class:`ElaMenuItem` 是「一条可点击的菜单项」的统一数据模型，被两个消费者共用：

- :class:`~pyqt5_ela_pro.selection_assistant.assistant.ElaSelectionAssistant`
  的划词动作条（``setActions``）；
- :class:`~pyqt5_ela_pro.ela_tray_icon.ElaTrayIcon` 的托盘菜单
  （``example/tray_host.py`` 的 :class:`~example.tray_host.ElaTrayHost`）。

两个消费者都**只发信号、不执行动作**：行为由宿主监听各自的 ``actionTriggered``
自行实现（如「复制」写剪贴板、「搜索」打开浏览器、「退出」调
``QApplication.quit()``）。

命名规范与库内一致（公共 API ``camelCase``，dataclass 字段 ``snake_case``）。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ElaMenuItem:
    """一条菜单项 / 动作的定义（宿主自定义，组件不内置任何动作）。

    :param id: 动作标识（由 ``actionTriggered`` 信号回传）
    :param label: 动作显示名
    :param icon: ``ElaIconType.IconName`` 图标（缺省时按消费者回落为纯文字）
    :param tooltip: 悬停提示（缺省用 ``label``）
    :param enabled: 是否在菜单中**显示**该动作（``False`` 表示整项不出现）
    """

    id: str
    label: str
    icon: Optional[Any] = None
    tooltip: str = ""
    enabled: bool = True


__all__ = ["ElaMenuItem"]
