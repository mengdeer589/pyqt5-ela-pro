"""
对话框基类模块。

提供 ``ElaDialogBase``，基于 ``ElaContentDialog`` 封装，自带取消/确定按钮栏。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QPushButton, QWidget, QVBoxLayout
from PyQt5ElaWidgetTools import ElaContentDialog, ElaText, eTheme, ElaThemeType

eTheme.setThemeColor(
    ElaThemeType.ThemeMode.Light,
    ElaThemeType.ThemeColor.DialogBase,
    QColor("#fafafa"),
)


class ElaDialogBase(ElaContentDialog):
    """基于 ElaContentDialog 的对话框基类。

    默认提供底部按钮栏（取消/确定），可设置标题和主体内容组件。

    :param title: 对话框标题
    :type title: str
    :param middleText: 中间按钮文本，为 ``None`` 时隐藏中间按钮。
    :type middleText: str, optional
    :param parent: 父级 widget（**必填**）。底层 ``ElaContentDialog`` 需要它来创建遮罩控件，
        传 ``None`` 会让进程崩溃，因此这里会抛 :class:`ValueError`。
    :type parent: QWidget
    :raises ValueError: ``parent`` 为 ``None`` 时抛出（否则进程会静默 abort）

    Example::

        dlg = ElaDialogBase(title="退出", middleText="稍后提醒", parent=parent)
        dlg.setTitle("退出")
        dlg.setParamWidget(my_content_widget)
        dlg.exec_()
    """

    def __init__(
        self,
        title: str = "标题",
        middleText: str | None = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        # ElaContentDialog 的 C++ 构造函数无条件解引用 parent（ElaContentDialog.cpp:
        # `d->_maskWidget->setFixedSize(parent->size())`），传 None 会空指针解引用，
        # 在 Qt 之外触发 0xC0000409 静默 abort（无 traceback）。这里提前拦下并给出可读报错。
        if parent is None:
            raise ValueError(
                "ElaDialogBase 需要 parent：底层 ElaContentDialog 用 parent 尺寸创建遮罩控件，"
                "parent=None 会导致进程崩溃。请传入宿主窗口，例如 "
                "ElaDialogBase(parent=self.window())。"
            )
        super().__init__(parent)
        self._titleWidget: Optional[ElaText] = None
        self._paramWidget: Optional[QWidget] = None
        self._paramLay: Optional[QVBoxLayout] = None

        self.setLeftButtonText("取消")
        self.setRightButtonText("确定")

        if middleText is None:
            try:
                btn = self.findChild(QPushButton, "middleButton")
            except Exception:
                btn = None
            if btn is not None:
                btn.setVisible(False)
            else:
                # Fallback: search by default text
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
        self._paramLay.setContentsMargins(25, 20, 25, 10)
        self._paramLay.setSpacing(2)
        self._titleWidget = ElaText(title, self._paramWidget)
        self._titleWidget.setTextPixelSize(15)
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
        while self._paramLay.count() > 2:
            item = self._paramLay.takeAt(2)
            old_widget = item.widget() if item else None
            if old_widget is not None and old_widget is not widget:
                old_widget.deleteLater()
        self._paramLay.addWidget(widget)

    def deleteLater(self) -> None:
        try:
            self.middleButtonClicked.disconnect(self._middleBtnClicked)
        except (TypeError, RuntimeError):
            pass
        super().deleteLater()

    def _middleBtnClicked(self) -> None:
        self.done(2)
