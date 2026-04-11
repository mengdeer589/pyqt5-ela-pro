"""
[ela_ext] 对话框组件演示页面
"""

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFrame,
    QLabel,
    QApplication,
)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt
from PyQt5ElaWidgetTools import (
    ElaText,
    ElaPushButton,
    ElaColorDialog,
    ElaContentDialog,
    ElaMessageBar,
    ElaMessageBarType,
)
from .base_page import ExamplePage


class DialogComponentsPage(ExamplePage):
    """ela 对话框组件演示页面"""

    PAGE_TITLE = "ela 对话框组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoColorDialog(main_layout)
        self._demoContentDialog(main_layout)

    def _demoColorDialog(self, parent_layout):
        section = ElaText("01. ElaColorDialog - 颜色对话框", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("点击按钮打开颜色选择对话框", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        color_btn = ElaPushButton("选择颜色", self)
        color_btn.setFixedWidth(120)
        color_btn.clicked.connect(self._onOpenColorDialog)
        btn_layout.addWidget(color_btn)

        self._colorFrame = QFrame(self)
        self._colorFrame.setFixedSize(60, 30)
        self._colorFrame.setFrameShape(QFrame.StyledPanel)
        self._colorFrame.setAutoFillBackground(True)
        self._colorFrame.setCursor(Qt.PointingHandCursor)
        self._colorFrame.mousePressEvent = self._onColorPreviewClick
        btn_layout.addWidget(self._colorFrame)

        self._colorLabel = ElaText("#808080", self)
        self._colorLabel.setTextPixelSize(14)
        btn_layout.addWidget(self._colorLabel)

        self._updatePreviewColor(QColor(128, 128, 128))

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoContentDialog(self, parent_layout):
        section = ElaText("02. ElaContentDialog - 内容对话框", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("点击按钮打开内容对话框", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        open_btn = ElaPushButton("打开对话框", self)
        open_btn.setFixedWidth(120)
        open_btn.clicked.connect(self._onOpenContentDialog)
        btn_layout.addWidget(open_btn)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _onOpenColorDialog(self):
        dialog = ElaColorDialog(self)
        dialog.colorSelected.connect(self._updatePreviewColor)
        dialog.exec_()

    def _updatePreviewColor(self, color: QColor):
        self._currentColor = color
        palette = self._colorFrame.palette()
        palette.setColor(QPalette.Window, color)
        self._colorFrame.setPalette(palette)
        self._colorLabel.setText(color.name().upper())

    def _onColorPreviewClick(self, event):
        if hasattr(self, "_currentColor"):
            clipboard = QApplication.clipboard()
            clipboard.setText(self._currentColor.name().upper())
            ElaMessageBar.success(
                ElaMessageBarType.PositionPolicy.Top,
                "已复制",
                f"颜色 {self._currentColor.name().upper()} 已复制到剪贴板",
                2000,
            )

    def _onOpenContentDialog(self):
        dialog = ElaContentDialog(self)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_text = ElaText(
            "这是内容对话框的描述文本。\n可以在这里放置各种组件。", content_widget
        )
        content_text.setTextPixelSize(14)
        content_layout.addWidget(content_text)

        dialog.setCentralWidget(content_widget)
        dialog.setLeftButtonText("确定")
        dialog.setMiddleButtonText("取消")
        dialog.setRightButtonText("应用")

        dialog.leftButtonClicked.connect(lambda: print("点击了确定"))
        dialog.middleButtonClicked.connect(lambda: print("点击了取消"))
        dialog.rightButtonClicked.connect(lambda: print("点击了应用"))
        dialog.exec_()
