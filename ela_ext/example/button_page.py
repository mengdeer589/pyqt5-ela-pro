"""
[ela_ext] 按钮组件演示页面
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5ElaWidgetTools import ElaText, ElaPushButton, ElaIconType
from ela_ext import ElaLongPressButton, ElaPrimaryButton, ElaToolButtonExt
from .base_page import ExamplePage


class ButtonComponentsPage(ExamplePage):
    """按钮组件演示页面"""

    PAGE_TITLE = "[ela_ext] 按钮组件"

    def __init__(self, parent=None):
        self._longPressBtn = None
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoPrimaryButton(main_layout)
        self._demoLongPressButton(main_layout)
        self._demoToolButtonExt(main_layout)

    def _demoPrimaryButton(self, parent_layout):
        section = ElaText("01. ElaPrimaryButton - 主要按钮", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText(
            "使用 Primary 主题色的按钮，与 ElaToggleButton ON 状态外观一致",
            self,
        )
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        primary_btn = ElaPrimaryButton(self)
        primary_btn.setText("主要按钮")
        primary_btn.setFixedWidth(120)
        primary_btn.clicked.connect(
            lambda: QMessageBox.information(self, "提示", "ElaPrimaryButton clicked")
        )
        btn_layout.addWidget(primary_btn)

        primary_btn_icon = ElaPrimaryButton(self)
        primary_btn_icon.setText("带图标")
        primary_btn_icon.setFixedWidth(120)
        primary_btn_icon.setElaIcon(ElaIconType.IconName.FloppyDisk, 16)
        primary_btn_icon.clicked.connect(
            lambda: QMessageBox.information(self, "提示", "带图标按钮 clicked")
        )
        btn_layout.addWidget(primary_btn_icon)

        primary_btn_disabled = ElaPrimaryButton(self)
        primary_btn_disabled.setText("禁用状态")
        primary_btn_disabled.setFixedWidth(120)
        primary_btn_disabled.setEnabled(False)
        btn_layout.addWidget(primary_btn_disabled)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoLongPressButton(self, parent_layout):
        section = ElaText("02. ElaLongPressButton - 长按按钮", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText(
            "按住按钮一段时间后才能触发点击事件，适合危险操作防误触",
            self,
        )
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self._longPressBtn = ElaLongPressButton(self, duration=800)
        self._longPressBtn.setText("长按 0.8 秒")
        self._longPressBtn.setFixedWidth(160)
        self._longPressBtn.longPressed.connect(self._onLongPressTriggered)
        btn_layout.addWidget(self._longPressBtn)

        duration_label = ElaText("时长:", self)
        duration_label.setTextPixelSize(14)
        btn_layout.addWidget(duration_label)

        for ms in [300, 500, 800, 1000]:
            btn = ElaPushButton(f"{ms}ms", self)
            btn.setFixedWidth(60)
            btn.clicked.connect(lambda checked, m=ms: self._setLongPressDuration(m))
            btn_layout.addWidget(btn)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _setLongPressDuration(self, ms):
        if self._longPressBtn:
            self._longPressBtn.setDuration(ms)
            self._longPressBtn.setText(f"长按 {ms / 1000:.1f} 秒")

    def _onLongPressTriggered(self):
        QMessageBox.information(self, "提示", "长按触发成功！")

    def _demoToolButtonExt(self, parent_layout):
        section = ElaText("03. ElaToolButtonExt - 图标文字并排按钮", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText(
            "ToolButton 样式设置为文字在图标旁边，适合工具栏使用",
            self,
        )
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        tool_btn = ElaToolButtonExt(self)
        tool_btn.setText("保存")
        tool_btn.setFixedWidth(100)
        tool_btn.setElaIcon(ElaIconType.IconName.FloppyDisk)
        tool_btn.clicked.connect(
            lambda: QMessageBox.information(self, "提示", "保存 clicked")
        )
        btn_layout.addWidget(tool_btn)

        tool_btn_icon = ElaToolButtonExt(self)
        tool_btn_icon.setText("编辑")
        tool_btn_icon.setFixedWidth(100)
        tool_btn_icon.setElaIcon(ElaIconType.IconName.Pencil)
        tool_btn_icon.clicked.connect(
            lambda: QMessageBox.information(self, "提示", "编辑 clicked")
        )
        btn_layout.addWidget(tool_btn_icon)

        tool_btn_disabled = ElaToolButtonExt(self)
        tool_btn_disabled.setText("禁用")
        tool_btn_disabled.setFixedWidth(100)
        tool_btn_disabled.setEnabled(False)
        btn_layout.addWidget(tool_btn_disabled)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)
