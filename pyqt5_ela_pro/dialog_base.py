"""
对话框基类模块。

提供 ``ElaDialogBase``，基于 ``ElaContentDialog`` 封装，自带取消/确定按钮栏。
"""

from __future__ import annotations

from typing import Optional, Literal

from PyQt5.QtWidgets import QPushButton, QWidget, QLayout, QHBoxLayout, QVBoxLayout
from PyQt5ElaWidgetTools import ElaContentDialog, ElaText, ElaTextType


class ElaDialogBase(ElaContentDialog):
    """基于 ElaContentDialog 的对话框基类。

    默认提供底部按钮栏（取消/确定），可设置标题和主体内容组件。

    :param parent: 父级 widget（必须提供）。
    :type parent: QWidget
    :param middleText: 中间按钮文本，为 ``None`` 时隐藏中间按钮。
    :type middleText: str, optional

    Example::

        dlg = ElaDialogBase(parent, middleText="稍后提醒")
        dlg.setTitle("退出")
        dlg.setParamWidget(my_content_widget)
        dlg.exec_()
    """

    def __init__(
        self,
        title: str = "标题",
        parent: Optional[QWidget] = None,
        middleText: str | None = None,
    ) -> None:
        super().__init__(parent)  # type: ignore[arg-type]
        self._titleWidget: Optional[ElaText] = None
        self._paramWidget: Optional[QWidget] = None
        self._paramLay: Optional[QVBoxLayout] = None

        self.setLeftButtonText("取消")
        self.setRightButtonText("确定")

        if middleText is None:
            for btn in self.findChildren(QPushButton):
                if btn.text() == "minimum":
                    btn.setVisible(False)
                    break
        else:
            self.setMiddleButtonText(middleText)
            self.middleButtonClicked.connect(self._middleBtnClicked)

        self._initParamArea(title)

    def _initParamArea(self, title: str = "标题") -> None:
        """初始化主体内容区域。"""
        self._paramWidget = QWidget(self)
        self._paramLay = QVBoxLayout(self._paramWidget)
        self._paramLay.setContentsMargins(15, 25, 15, 10)
        self._paramLay.setSpacing(2)
        self._titleWidget = ElaText(title, self._paramWidget)
        self._titleWidget.setTextStyle(ElaTextType.TextStyle.Title)
        self._paramLay.addWidget(self._titleWidget)
        self._paramLay.addSpacing(5)
        super().setCentralWidget(self._paramWidget)

    def setTitle(self, title: str) -> None:
        """设置对话框标题。

        :param title: 标题文本。
        :type title: str
        """
        self._titleWidget.setText(title)

    def setParamWidget(self, widget: QWidget) -> None:
        """设置对话框主体内容组件。

        :param widget: 内容 widget。
        :type widget: QWidget
        """
        if self._paramLay.count() > 2:
            self._paramLay.takeAt(2).widget().deleteLater()
        self._paramLay.addWidget(widget)

    def _middleBtnClicked(self) -> None:
        self.done(2)
