"""
消息对话框组件。

提供一个简化的消息对话框接口，使用 ElaText 组件渲染内容。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import ElaText

from .dialog_base import ElaDialogBase


class ElaMessageDialog(ElaDialogBase):
    """简单的消息对话框。

    提供一个简化的接口来显示文本消息，使用 ElaText 组件渲染内容。

    :param title: 对话框标题
    :param message: 消息文本
    :param middleText: 中间按钮文本，为 None 时隐藏中间按钮
    :param parent: 父级 widget

    Example::

        result = ElaMessageDialog.show(
            parent,
            title="提示",
            message="确定要退出吗？"
        )
    """

    def __init__(
        self,
        title: str = "标题",
        message: str = "",
        middleText: str | None = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(title=title, middleText=middleText, parent=parent)
        self.setMessage(message)

    def setMessage(self, message: str) -> None:
        """设置消息文本。

        :param message: 消息文本
        """
        if self._paramLay.count() > 2:
            item = self._paramLay.takeAt(2)
            if item and item.widget():
                item.widget().deleteLater()

        message_widget = ElaText(message, self._paramWidget)
        message_widget.setTextPixelSize(12)
        message_widget.setWordWrap(True)
        self._paramLay.addWidget(message_widget)

    def show(
        self,
        title: str = "标题",
        message: str = "",
        middleText: str | None = None,
    ) -> int:
        """显示消息对话框（类调用）或普通显示（实例调用）。

        类调用：``ElaMessageDialog.show(parent, title, message, middleText)``
        返回点击的按钮对应的返回值（0=左按钮取消, 1=右按钮确定, 2=中间按钮）。
        实例调用：``dlg.show()`` 与 ``QDialog.show`` 行为一致，返回 ``None``。

        :param title: 对话框标题
        :param message: 消息文本
        :param middleText: 中间按钮文本，为 None 时隐藏中间按钮
        :return: 类调用时返回按钮返回值；实例调用时返回 None
        """
        if isinstance(self, ElaMessageDialog):
            super().show()
            return 0
        parent = self
        dialog = ElaMessageDialog(
            title=title, message=message, middleText=middleText, parent=parent
        )
        dialog.setWindowTitle(title)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        return dialog.exec_()
