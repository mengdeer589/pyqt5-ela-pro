"""
[ela_ext] 动画演示页面
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import ElaText, ElaPushButton
from ela_ext import fade_in, fade_out, ElaAnimatedMixin, shake_window
from .base_page import ExamplePage


class _AnimatedDemoDialog(ElaAnimatedMixin, QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ElaAnimatedMixin 演示")
        self.resize(300, 200)
        layout = QVBoxLayout(self)
        info = ElaText(
            "通过 ElaAnimatedMixin 继承获得 fade_in() / fade_out()\n对话框自身拥有动画方法",
            self,
        )
        info.setTextPixelSize(14)
        layout.addWidget(info)
        btn_layout = QHBoxLayout()
        close_btn = ElaPushButton("淡出并关闭", self)
        close_btn.setFixedWidth(120)
        close_btn.clicked.connect(lambda: self.fade_out(on_finished=self.close))
        btn_layout.addWidget(close_btn)
        shake_btn = ElaPushButton("抖动", self)
        shake_btn.setFixedWidth(80)
        shake_btn.clicked.connect(self.shake)
        btn_layout.addWidget(shake_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        self.fade_in()

    def shake(self):
        shake_window(self)


class AnimationPage(ExamplePage):
    """动画演示页面"""

    PAGE_TITLE = "[ela_ext] 动画特效"

    def _addDemoContent(self, main_layout):
        self._demoFadeInOut(main_layout)
        self._demoShakeWindow(main_layout)
        self._demoAnimatedMixin(main_layout)

    def _demoFadeInOut(self, parent_layout):
        section = ElaText("01. fade_in / fade_out - 淡入淡出动画", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText(
            "对任意 QWidget 执行淡入淡出动画，支持动画完成回调",
            self,
        )
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        fade_in_btn = ElaPushButton("淡入窗口", self)
        fade_in_btn.setFixedWidth(100)
        fade_in_btn.clicked.connect(self._onFadeIn)
        btn_layout.addWidget(fade_in_btn)

        fade_out_btn = ElaPushButton("淡出窗口", self)
        fade_out_btn.setFixedWidth(100)
        fade_out_btn.clicked.connect(self._onFadeOut)
        btn_layout.addWidget(fade_out_btn)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoShakeWindow(self, parent_layout):
        section = ElaText("02. shake_window - 窗口抖动", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("使窗口产生抖动效果，常用于错误提示", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        shake_btn = ElaPushButton("抖动窗口", self)
        shake_btn.setFixedWidth(100)
        shake_btn.clicked.connect(lambda: shake_window(self))
        btn_layout.addWidget(shake_btn)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoAnimatedMixin(self, parent_layout):
        section = ElaText("03. ElaAnimatedMixin - 对话框动画混入", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText(
            "通过继承 ElaAnimatedMixin，对话框自动获得 fade_in() / fade_out() 方法",
            self,
        )
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        open_btn = ElaPushButton("打开动画对话框", self)
        open_btn.setFixedWidth(120)
        open_btn.clicked.connect(self._openAnimatedDialog)
        btn_layout.addWidget(open_btn)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _onFadeIn(self):
        fade_in(self)

    def _onFadeOut(self):
        fade_out(self)

    def _openAnimatedDialog(self):
        dialog = _AnimatedDemoDialog(self)
        dialog.exec_()
