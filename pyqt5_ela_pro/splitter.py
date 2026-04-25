"""
Splitter 分割器组件

提供 ELA 主题风格的分割器，支持水平和垂直方向分割。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtWidgets import QSplitter, QWidget, QStyle, QProxyStyle, QBoxLayout
from PyQt5.QtCore import Qt, QRect
from PyQt5ElaWidgetTools import eTheme, ElaThemeType


class ElaSplitterStyle(QProxyStyle):
    """QSplitter 手柄样式 - ELA 主题风格"""

    def __init__(self, thickness=40):
        super().__init__()
        self._thickness = thickness

    def drawControl(self, element, option, painter, widget=None):
        if element == QStyle.CE_Splitter and widget:
            splitter = widget
            mode = eTheme.getThemeMode()
            color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.PrimaryNormal)
            if splitter.orientation() == Qt.Horizontal:
                x = option.rect.x()
                y = 0
                w = self._thickness
                h = splitter.height()
            else:
                x = 0
                y = option.rect.y()
                w = splitter.width()
                h = self._thickness
            rect = QRect(x, y, w, h)
            painter.fillRect(rect, color)
            return
        super().drawControl(element, option, painter, widget)


class ElaSplitter(QSplitter):
    """ELA 主题风格的分割器

    支持水平和垂直方向，自动响应主题切换，不使用 QSS。

    :param orientation: Qt.Horizontal 或 Qt.Vertical
    :param handleThickness: 手柄粗细（默认 4px）
    :param parent: 父组件
    """

    def __init__(
        self,
        orientation: Qt.Orientation = Qt.Horizontal,
        handleThickness: int = 4,
        parent: QWidget = None,
    ):
        super().__init__(orientation, parent)
        self._handle_thickness = handleThickness
        self._style = ElaSplitterStyle(handleThickness)
        self.setStyle(self._style)
        super().setHandleWidth(handleThickness)
        self.setChildrenCollapsible(False)
        eTheme.themeModeChanged.connect(self._on_theme_changed)

    def _on_theme_changed(self, mode):
        self.update()

    def setHandleWidth(self, width):
        self._handle_thickness = width
        self._style._thickness = width
        super().setHandleWidth(width)


def create_ela_splitter(
    widgets: list,
    orientation: Qt.Orientation = Qt.Horizontal,
    handleThickness: int = 4,
    sizes: Optional[list[int]] = None,
    parent: QWidget = None,
) -> QSplitter:
    """将组件列表以 ELA 风格 splitter 分割

    :param widgets: 要分割的组件列表（至少 2 个）
    :param orientation: Qt.Horizontal 或 Qt.Vertical
    :param handleThickness: 手柄粗细（默认 4px）
    :param sizes: 每个子组件的初始尺寸（像素），长度必须与 widgets 一致，可选
    :param parent: 父组件，为 None 时自动使用 widgets[0] 的父组件
    :returns: 配置好的 QSplitter
    :raises ValueError: 当组件数量少于 2 个时，或 sizes 长度不匹配时
    """
    if len(widgets) < 2:
        raise ValueError("组件列表至少需要 2 个组件")
    if sizes is not None and len(sizes) != len(widgets):
        raise ValueError("sizes 列表长度必须与组件列表长度一致")

    if parent is None and widgets:
        parent = widgets[0].parentWidget()

    splitter = ElaSplitter(orientation, handleThickness, parent)

    if parent is not None and parent.layout() is not None:
        layout = parent.layout()
        if isinstance(layout, QBoxLayout):
            idx = layout.indexOf(widgets[0])
            if idx >= 0:
                layout.insertWidget(idx, splitter)
            else:
                layout.addWidget(splitter)
        else:
            layout.addWidget(splitter)

    for widget in widgets:
        splitter.addWidget(widget)

    if sizes is not None:
        splitter.setSizes(sizes)

    return splitter
