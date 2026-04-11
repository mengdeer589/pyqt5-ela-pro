"""
可滚动菜单组件。

提供一个以滚动区域作为内容容器的菜单，
支持显示大量自定义组件并提供垂直和水平滚动。
支持主题感知的样式表切换。
"""

from __future__ import annotations

from typing import Any, Optional

from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QShowEvent
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFrame,
)
from PyQt5ElaWidgetTools import (
    ElaMenu,
    ElaScrollArea,
    eTheme,
    ElaThemeType,
)


SCROLLABLE_MENU_LIGHT_BG_COLOR: str = "#ffffff"
SCROLLABLE_MENU_DARK_BG_COLOR: str = "#202020"
SCROLLABLE_MENU_MIN_HEIGHT: int = 50
SCROLLABLE_MENU_LAYOUT_SPACING: int = 2
SCROLLABLE_MENU_LAYOUT_MARGINS: tuple[int, int, int, int] = (5, 5, 5, 5)


class ElaScrollableMenu(ElaMenu):
    """带有可滚动内容区域的下拉菜单组件。

    使用 ``ElaScrollArea`` 替代标准菜单列表，内部包含一个由
    ``QVBoxLayout`` 管理的 ``QWidget``。这允许向菜单中添加任意
    widget（如复选框、行编辑框等）并支持滚动。

    滚动区域的背景色会在亮色主题（``#ffffff``）和暗色主题（``#202020``）
    之间自动切换。

    :param parent: 父级 widget，为 ``None`` 时表示顶级窗口。
    :type parent: QWidget, optional

    Attributes:
        scroll_area: 提供滚动功能的 ``ElaScrollArea`` 实例。
        scroll_widget: 位于滚动区域内部的内容容器 widget。
        scroll_layout: 管理子组件的 ``QVBoxLayout`` 实例。
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)  # type: ignore[arg-type]
        self._themeConnection: Any = None

        self.scroll_area = ElaScrollArea(self)
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("menu_scroll_widget")
        self.scroll_widget.setStyleSheet(
            f"#menu_scroll_widget {{ background-color:{SCROLLABLE_MENU_LIGHT_BG_COLOR}; }}"
        )
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(SCROLLABLE_MENU_LAYOUT_SPACING)
        self.scroll_layout.setContentsMargins(*SCROLLABLE_MENU_LAYOUT_MARGINS)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setMinimumHeight(SCROLLABLE_MENU_MIN_HEIGHT)

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)
        self._themeConnection = eTheme.themeModeChanged.connect(self._change_stylesheet)

    def _disconnectSignals(self) -> None:
        """断开主题切换信号连接，防止悬挂引用。"""
        if self._themeConnection is not None:
            try:
                eTheme.themeModeChanged.disconnect(self._themeConnection)
            except TypeError:
                pass
            self._themeConnection = None

    def _change_stylesheet(self, mode: ElaThemeType.ThemeMode) -> None:
        """根据主题模式切换滚动 widget 的背景色。

        :param mode: 当前主题模式（亮色或暗色）。
        :type mode: ElaThemeType.ThemeMode
        """
        if mode == ElaThemeType.ThemeMode.Light:
            self.scroll_widget.setStyleSheet(
                f"#menu_scroll_widget {{ background-color:{SCROLLABLE_MENU_LIGHT_BG_COLOR}; }}"
            )
        else:
            self.scroll_widget.setStyleSheet(
                f"#menu_scroll_widget {{ background-color:{SCROLLABLE_MENU_DARK_BG_COLOR}; }}"
            )

    def addWidgetAction(self, widget: QWidget) -> None:
        """向滚动区域添加一个自定义 widget。

        :param widget: 要添加的 widget，将由内部
            ``scroll_layout`` 管理。
        :type widget: QWidget
        """
        self.scroll_layout.addWidget(widget)

    def clearMenu(self) -> None:
        """从滚动区域中移除并删除所有子 widget。

        以逆序遍历布局，对每个 widget 及其子组件调用
        ``deleteLater()``，然后移除布局项。
        """
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            if item.widget():
                widget = item.widget()
                for child in widget.findChildren(QObject):
                    try:
                        child.deleteLater()
                    except (RuntimeError, AttributeError):
                        pass
                widget.deleteLater()
            self.scroll_layout.removeItem(item)

    def sizeHint(self) -> Any:
        """返回基于滚动区域的菜单理想尺寸。

        :return: 建议的尺寸。
        :rtype: QSize
        """
        return self.scroll_area.sizeHint()

    def showEvent(self, a0: QShowEvent) -> None:  # ty:ignore[invalid-method-override]
        """显示事件处理，确保菜单宽度与父级 widget 一致。

        将菜单的固定宽度设置为与父级 widget 相同，并激活窗口。

        :param a0: 显示事件。
        :type a0: QShowEvent
        """
        super().showEvent(a0)
        parent = self.parent()
        if parent is not None and isinstance(parent, QWidget):
            self.setFixedWidth(parent.width())
        self.activateWindow()

    def deleteLater(self) -> None:
        """清理信号、子组件，并调度自身删除。"""
        self._disconnectSignals()
        self.clearMenu()
        super().deleteLater()
