"""
Splitter 分割器组件

提供 ELA 主题风格的分割器，支持水平和垂直方向分割。
"""

from __future__ import annotations

from PyQt5.QtWidgets import QSplitter, QWidget, QStyle, QStyleOption, QProxyStyle
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor
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
        pass


def create_ela_splitter(
    widgets: list,
    orientation: Qt.Orientation = Qt.Horizontal,
    handleThickness: int = 4,
    parent: QWidget = None,
) -> QSplitter:
    """将组件列表以 ELA 风格 splitter 分割

    :param widgets: 要分割的组件列表（至少 2 个）
    :param orientation: Qt.Horizontal 或 Qt.Vertical
    :param handleThickness: 手柄粗细（默认 4px）
    :param parent: 父组件
    :returns: 配置好的 QSplitter
    :raises ValueError: 当组件数量少于 2 个时
    """
    if len(widgets) < 2:
        raise ValueError("组件列表至少需要 2 个组件")

    splitter = ElaSplitter(orientation, handleThickness, parent)
    for widget in widgets:
        splitter.addWidget(widget)
    return splitter
