"""
[ela_ext] 提示组件演示页面
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import ElaText, ElaPushButton
from ela_ext import ElaToolTipPosition, set_tooltip, StateToolTip
from .base_page import ExamplePage


class TooltipComponentsPage(ExamplePage):
    """提示组件演示页面"""

    PAGE_TITLE = "[ela_ext] 提示组件"

    def __init__(self, parent=None):
        self._stateTooltip = None
        self._tooltipState = None
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoToolTip(main_layout)
        self._demoStateToolTip(main_layout)

    def _demoToolTip(self, parent_layout):
        section = ElaText("01. ToolTip - 工具提示", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("鼠标悬停在按钮上查看提示", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        btn1 = ElaPushButton("保存", self)
        btn1.setFixedWidth(100)
        set_tooltip(btn1, "保存当前内容", position=ElaToolTipPosition.BOTTOM)
        btn_layout.addWidget(btn1)

        btn2 = ElaPushButton("删除", self)
        btn2.setFixedWidth(100)
        set_tooltip(
            btn2, "删除选中项目\n（此操作不可撤销）", position=ElaToolTipPosition.RIGHT
        )
        btn_layout.addWidget(btn2)

        btn3 = ElaPushButton("关于", self)
        btn3.setFixedWidth(100)
        set_tooltip(btn3, "关于本软件 v1.0.0", position=ElaToolTipPosition.TOP)
        btn_layout.addWidget(btn3)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoStateToolTip(self, parent_layout):
        section = ElaText("02. StateToolTip - 状态提示", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("显示加载状态、成功/失败状态的提示", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        loading_btn = ElaPushButton("显示加载中", self)
        loading_btn.setFixedWidth(120)
        loading_btn.clicked.connect(self._showLoadingStateTooltip)
        btn_layout.addWidget(loading_btn)

        success_btn = ElaPushButton("显示成功", self)
        success_btn.setFixedWidth(120)
        success_btn.clicked.connect(self._showSuccessStateTooltip)
        btn_layout.addWidget(success_btn)

        close_btn = ElaPushButton("关闭提示", self)
        close_btn.setFixedWidth(120)
        close_btn.clicked.connect(self._closeStateTooltip)
        btn_layout.addWidget(close_btn)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _showLoadingStateTooltip(self):
        if self._stateTooltip is not None:
            try:
                self._stateTooltip.hide()
                self._stateTooltip.deleteLater()
            except Exception:
                pass
        self._stateTooltip = StateToolTip("正在加载", "请稍候...", self)
        self._tooltipState = "loading"
        self._stateTooltip.closedSignal.connect(self._onStateTooltipClosed)
        pos = self._stateTooltip.getSuitablePos()
        self._stateTooltip.move(pos)
        self._stateTooltip.show()

    def _showSuccessStateTooltip(self):
        if self._stateTooltip is not None and self._tooltipState == "loading":
            self._stateTooltip.setTitle("加载完成")
            self._stateTooltip.setContent("数据已成功加载")
            self._stateTooltip.setState(True)
            self._tooltipState = "success"
        else:
            if self._stateTooltip is not None:
                try:
                    self._stateTooltip.hide()
                    self._stateTooltip.deleteLater()
                except Exception:
                    pass
            self._stateTooltip = StateToolTip("加载完成", "数据已成功加载", self)
            self._tooltipState = "success"
            self._stateTooltip.closedSignal.connect(self._onStateTooltipClosed)
            pos = self._stateTooltip.getSuitablePos()
            self._stateTooltip.move(pos)
            self._stateTooltip.show()
            self._stateTooltip.setState(True)

    def _onStateTooltipClosed(self):
        self._stateTooltip = None
        self._tooltipState = None

    def _closeStateTooltip(self):
        try:
            if self._stateTooltip is not None:
                self._stateTooltip.hide()
                self._stateTooltip.deleteLater()
        except Exception:
            pass
        self._stateTooltip = None
        self._tooltipState = None
