"""
主题感知基类组件。

提供一个 ``QWidget`` 子类，通过监听 ``eTheme.themeModeChanged`` 信号
自动适应应用程序的当前主题模式（亮色 / 暗色）。
"""

from __future__ import annotations

from typing import Optional, Literal

from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaMessageBar, ElaMessageBarType

from ._internal import disconnect_theme_signal


class ElaThemeWidget(QWidget):
    """自动适应主题变化的 ``QWidget`` 基类。

    在构造时查询当前主题模式，并通过 ``QPalette.Window`` 应用相应的背景色。
    同时连接到全局 ``eTheme.themeModeChanged`` 信号，
    使用户在亮色和暗色模式之间切换时自动更新调色板。

    子类应调用 ``super().__init__(parent)`` 以确保主题连接被建立。

    :param parent: 父级 widget，为 ``None`` 时表示顶级窗口。
    :type parent: QWidget, optional

    Example::

        class MyPanel(ElaThemeWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                # self 已经拥有正确的主题背景色
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("ElaThemeWidget")
        self._themeConnection = self._update_bg_color
        self._update_bg_color(eTheme.getThemeMode())
        eTheme.themeModeChanged.connect(self._themeConnection)

    def _update_bg_color(self, mode: ElaThemeType.ThemeMode) -> None:
        """根据给定的主题模式更新 widget 的背景调色板。

        :param mode: 当前主题模式（亮色或暗色）。
        :type mode: ElaThemeType.ThemeMode
        """
        bg_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicPress)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, bg_color)
        self.setPalette(palette)

    def deleteLater(self) -> None:
        """断开主题信号连接，并调度 widget 进行删除。"""
        if self._themeConnection is not None:
            try:
                eTheme.themeModeChanged.disconnect(self._themeConnection)
            except (TypeError, RuntimeError):
                pass
            self._themeConnection = None
        super().deleteLater()

    def createLayout(
        self,
        layoutType: Literal["h", "v"]='h',
        parent: QWidget | None = None,
    ) -> QHBoxLayout | QVBoxLayout:
        """创建布局。

        :param layoutType: 布局类型，'h' 水平布局，'v' 垂直布局
        :param parent: 父控件，默认为 self
        :return: 创建的布局对象
        """
        if parent is None:
            parent = self
        if layoutType == "h":
            lay = QHBoxLayout(parent)
        else:
            lay = QVBoxLayout(parent)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        return lay

    def alert(
        self,
        message: str,
        level: Literal["error", "warning", "information", "success"] = "information",
        title: str = "提示",
        duration: int = 3000,
        position: Literal[
            "Top",
            "Left",
            "Bottom",
            "Right",
            "TopRight",
            "TopLeft",
            "BottomRight",
            "BottomLeft",
        ] = "TopRight",
        parent: Optional[QWidget] = None,
    ) -> None:
        """显示提示消息条。

        :param message: 消息内容
        :param level: 消息级别，支持 "error" / "warning" / "information" / "success"
        :param title: 消息标题
        :param duration: 显示时长（毫秒）
        :param position: 显示位置
        :param parent: 父控件，用于消息条定位
        """
        func = getattr(ElaMessageBar, level)
        position_policy = getattr(ElaMessageBarType.PositionPolicy, position)
        func(position_policy, title, message, duration, parent)
