"""
流式布局模块。

提供增强的流式布局，支持拖拽重排序和阴影效果。
"""

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import ElaFlowLayout as _ElaFlowLayout


class ElaFlowLayout(_ElaFlowLayout):
    """
    增强的流式布局

    继承自 PyQt5ElaWidgetTools.ElaFlowLayout。
    """

    def __init__(
        self,
        parent: QWidget = None,
        margin: int = -1,
        hSpacing: int = -1,
        vSpacing: int = -1,
    ):
        super().__init__(parent, margin, hSpacing, vSpacing)
        self._h_spacing = hSpacing if hSpacing >= 0 else self.horizontalSpacing()
        self._v_spacing = vSpacing if vSpacing >= 0 else self.verticalSpacing()

    def columnSpacing(self) -> int:
        """获取列间距"""
        return self._h_spacing

    def setColumnSpacing(self, spacing: int):
        """设置列间距"""
        self._h_spacing = spacing

    def lineSpacing(self) -> int:
        """获取行间距"""
        return self._v_spacing

    def setLineSpacing(self, spacing: int):
        """设置行间距"""
        self._v_spacing = spacing
