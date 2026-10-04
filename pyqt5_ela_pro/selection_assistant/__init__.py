"""划词助手（``pyqt5_ela_pro.selection_assistant``）。

全局划词监视 + 取词 + 动作条组件，纯 ctypes 实现（无 pywin32 依赖），
只发信号不绑定具体行为；**动作条菜单项完全由宿主定义**：

- :class:`ElaSelectionAssistant`：监视划词手势（拖选 / 双击选词）→ 模拟
  ``Ctrl+C`` 读取选中文本（默认恢复原剪贴板）→ 在落点附近弹出动作条；
  宿主用 ``setActions`` 定义菜单项（不内置任何动作），未定义时只发
  ``selectionCaptured`` 不弹窗；``setCaptureFilter`` 可在注入 ``Ctrl+C`` 前
  过滤非划词拖拽（配合 :func:`foreground_pid` / :func:`window_pid_at`）；
  信号 ``selectionCaptured`` / ``actionTriggered`` / ``popupShown`` /
  ``popupHidden`` / ``enabledChanged`` / ``errorOccurred``；
- :class:`~pyqt5_ela_pro.menu_item.ElaMenuItem`：菜单项定义（id / 名称 / 图标 /
  提示 / 启用），划词动作条与托盘菜单**共用**同一数据模型；
- :class:`ElaSelectionPopup`：动作条浮窗（置顶 / 不抢焦点 / 主题感知），
  可独立复用；助手上外观配置（紧凑模式 / 偏移）走 ``assistant.popup()``，
  取词参数（剪贴板恢复 / 各类延迟）走 ``assistant.capture()`` —— 助手只负责
  手势编排与信号，不做同名转发；
- :class:`ElaSelectionResultDialog`：结果对话框（点「翻译 / 解释」这类要跑
  模型的动作后弹出，实时显示流式 Markdown）。基类是上游 ``ElaWidget``，
  **只发信号不碰网络** —— 宿主推进 ``beginStream`` / ``appendMarkdown`` /
  ``endStream``，取消接 ``stopRequested`` 自己 abort；
- :class:`ElaMouseMonitor` / :class:`ElaClipboardCapture`：监视与取词后端，
  可注入替换（测试用假实现即可脱离真实输入）。

典型用法::

    from PyQt5ElaWidgetTools import ElaIconType
    from pyqt5_ela_pro import ElaMenuItem, ElaSelectionAssistant

    assistant = ElaSelectionAssistant(parent)
    assistant.setActions([
        ElaMenuItem("copy", "复制", ElaIconType.IconName.Copy),
        ElaMenuItem("search", "搜索", ElaIconType.IconName.MagnifyingGlass),
    ])
    assistant.actionTriggered.connect(
        lambda actionId, text, pos: print(actionId, text)
    )
    assistant.setEnabled(True)

注意：取词依赖模拟 Ctrl+C，终端 / 受保护程序可能取不到；剪贴板恢复只还原
文本，图片等非文本格式不保留。
"""

from ..menu_item import ElaMenuItem
from ._native import ElaMouseMonitor, foreground_pid, window_pid_at
from .assistant import ElaSelectionAssistant
from .capture import ElaClipboardCapture
from .popup import ElaSelectionPopup
from .result_dialog import ElaSelectionResultDialog

__all__ = [
    "ElaClipboardCapture",
    "ElaMenuItem",
    "ElaMouseMonitor",
    "ElaSelectionAssistant",
    "ElaSelectionPopup",
    "ElaSelectionResultDialog",
    "foreground_pid",
    "window_pid_at",
]
