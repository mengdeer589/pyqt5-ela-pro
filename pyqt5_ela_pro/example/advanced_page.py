"""
[ela_ext] Office 文档预览组件演示页面

基于 QAxWidget (ActiveX) 嵌入 MS Office 或 WPS 文档查看器。
仅 Windows 平台有效。
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFileDialog
from PyQt5ElaWidgetTools import ElaText, ElaPushButton
from pyqt5_ela_pro import ElaWordViewer, ElaExcelViewer, ElaPowerPointViewer
from .base_page import ExamplePage


class AdvancedComponentsPage(ExamplePage):
    """Office 文档预览组件演示页面"""

    PAGE_TITLE = "Office 文档预览"

    def __init__(self, parent=None):
        self._word_viewer = None
        self._excel_viewer = None
        self._ppt_viewer = None
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoWordViewer(main_layout)
        self._demoExcelViewer(main_layout)
        self._demoPowerPointViewer(main_layout)

    def _demoWordViewer(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("01. ela_ext - ElaWordViewer Word 文档预览", self._demoWordViewer)
        )
        self._addInfoText(
            "通过 ActiveX 嵌入 Word 文档查看器（需安装 MS Office 或 WPS）",
            parent_layout,
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        open_btn = ElaPushButton("打开 Word 文档", self)
        open_btn.setFixedWidth(130)
        open_btn.clicked.connect(self._onOpenWord)
        btn_layout.addWidget(open_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(10)
        self._word_viewer = ElaWordViewer(self, backend="office")
        self._word_viewer.setFixedHeight(300)
        parent_layout.addWidget(self._word_viewer)
        parent_layout.addSpacing(20)

    def _demoExcelViewer(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("02. ela_ext - ElaExcelViewer Excel 文档预览", self._demoExcelViewer)
        )
        self._addInfoText(
            "通过 ActiveX 嵌入 Excel 文档查看器（需安装 MS Office 或 WPS）",
            parent_layout,
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        open_btn = ElaPushButton("打开 Excel 文档", self)
        open_btn.setFixedWidth(130)
        open_btn.clicked.connect(self._onOpenExcel)
        btn_layout.addWidget(open_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(10)
        self._excel_viewer = ElaExcelViewer(self, backend="office")
        self._excel_viewer.setFixedHeight(300)
        parent_layout.addWidget(self._excel_viewer)
        parent_layout.addSpacing(20)

    def _demoPowerPointViewer(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow("03. ela_ext - ElaPowerPointViewer PPT 文档预览", self._demoPowerPointViewer)
        )
        self._addInfoText(
            "通过 ActiveX 嵌入 PowerPoint 文档查看器（需安装 MS Office 或 WPS）",
            parent_layout,
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        open_btn = ElaPushButton("打开 PPT 文档", self)
        open_btn.setFixedWidth(130)
        open_btn.clicked.connect(self._onOpenPpt)
        btn_layout.addWidget(open_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(10)
        self._ppt_viewer = ElaPowerPointViewer(self, backend="office")
        self._ppt_viewer.setFixedHeight(300)
        parent_layout.addWidget(self._ppt_viewer)
        parent_layout.addSpacing(20)

    def _onOpenWord(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 Word 文档", "", "Word 文档 (*.doc *.docx);;所有文件 (*)"
        )
        if path:
            if not self._word_viewer.loadFile(path):
                self._addInfoText("加载失败，请确认已安装 MS Office 或 WPS", self.layout())

    def _onOpenExcel(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 Excel 文档", "", "Excel 文档 (*.xls *.xlsx);;所有文件 (*)"
        )
        if path:
            if not self._excel_viewer.loadFile(path):
                self._addInfoText("加载失败，请确认已安装 MS Office 或 WPS", self.layout())

    def _onOpenPpt(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 PPT 文档", "", "PPT 文档 (*.ppt *.pptx);;所有文件 (*)"
        )
        if path:
            if not self._ppt_viewer.loadFile(path):
                self._addInfoText("加载失败，请确认已安装 MS Office 或 WPS", self.layout())
