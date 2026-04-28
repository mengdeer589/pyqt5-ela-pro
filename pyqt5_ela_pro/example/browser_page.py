"""
浏览器嵌入示例页面。
"""

import os
from pathlib import Path
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QFileDialog
from PyQt5ElaWidgetTools import ElaText, ElaPushButton, ElaPlainTextEdit, ElaLineEdit

from pyqt5_ela_pro import ElaBrowserEmbedder
from .base_page import ExamplePage

BROWSER_PATH = Path(
    os.environ.get(
        "ELA_BROWSER_PATH",
        r"Supermium\chrome.exe",
    )
)
TEST_URLS = [
    "https://www.bilibili.com",
    "https://www.baidu.com",
    "https://www.qq.com",
]


class _BrowserPanel(QWidget):
    """单个浏览器面板"""

    def __init__(self, title: str, url: str, browser_path: Path, debug_port: int, parent=None):
        super().__init__(parent)
        self.setObjectName(f"BrowserPanel_{debug_port}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header = ElaText(title, self)
        header.setTextPixelSize(14)
        layout.addWidget(header)

        row = QHBoxLayout()
        row.setSpacing(6)
        self._url_input = ElaLineEdit()
        self._url_input.setFixedHeight(28)
        self._url_input.setText(url)
        row.addWidget(self._url_input)

        embed_btn = ElaPushButton("嵌入")
        embed_btn.setFixedWidth(50)
        embed_btn.clicked.connect(self._embed)
        row.addWidget(embed_btn)

        load_btn = ElaPushButton("加载")
        load_btn.setFixedWidth(50)
        load_btn.clicked.connect(self._load_url)
        row.addWidget(load_btn)

        file_btn = ElaPushButton("打开文件")
        file_btn.setFixedWidth(70)
        file_btn.clicked.connect(self._open_file)
        row.addWidget(file_btn)

        release_btn = ElaPushButton("释放")
        release_btn.setFixedWidth(50)
        release_btn.clicked.connect(self._release)
        row.addWidget(release_btn)

        layout.addLayout(row)

        self._browser = ElaBrowserEmbedder(
            webview_path=browser_path,
            debug_port=debug_port,
            browser_args=[
                f"--user-data-dir={Path.cwd() / 'runtime' / 'cache' / f'browser_{debug_port}'}"
            ],
            parent=self,
        )
        layout.addWidget(self._browser, 1)

        self._log = ElaPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setFixedHeight(50)
        layout.addWidget(self._log)

        self._browser.windowEmbedded.connect(lambda h: self._append_log(f"已嵌入 0x{h:X}"))
        self._browser.windowReleased.connect(lambda h: self._append_log(f"已释放 0x{h:X}"))
        self._browser.embedError.connect(lambda m: self._append_log(f"错误: {m}"))
        self._browser.embedCompleted.connect(
            lambda ok: self._append_log("CDP 就绪" if ok else "CDP 失败")
        )

    def _append_log(self, msg: str):
        try:
            self._log.appendPlainText(msg)
        except Exception:
            pass

    def _embed(self):
        url = self._url_input.text().strip()
        self._append_log(f"嵌入: {url}")
        try:
            self._browser.embed(url, connect_cdp=True)
        except Exception as e:
            self._append_log(f"错误: {e}")

    def _load_url(self):
        url = self._url_input.text().strip()
        self._append_log(f"加载: {url}")
        try:
            self._browser.load_url(url)
        except Exception as e:
            self._append_log(f"错误: {e}")

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 HTML 文件", "", "HTML 文件 (*.html *.htm);;所有文件 (*)"
        )
        if path:
            self._append_log(f"加载本地文件: {path}")
            try:
                self._browser.load_url(Path(path))
            except Exception as e:
                self._append_log(f"错误: {e}")

    def _release(self):
        try:
            self._browser.release()
            self._append_log("已释放")
        except Exception as e:
            self._append_log(f"错误: {e}")

    def release(self):
        self._browser.release()


class BrowserExamplePage(ExamplePage):
    """浏览器嵌入演示页面"""

    PAGE_TITLE = "浏览器嵌入"

    def __init__(self, parent=None):
        self._panels = []
        super().__init__(parent)

    def _addDemoContent(self, layout):
        if not BROWSER_PATH.exists():
            info = ElaText(
                f"浏览器不存在: {BROWSER_PATH}\n请设置环境变量 ELA_BROWSER_PATH 指向 chrome.exe",
                self,
            )
            info.setTextPixelSize(14)
            layout.addWidget(info)
            return

        rows_layout = QVBoxLayout()
        rows_layout.setSpacing(10)

        for i, url in enumerate(TEST_URLS):
            panel = _BrowserPanel(
                title=f"浏览器 {i + 1}",
                url=url,
                browser_path=BROWSER_PATH,
                debug_port=9223 + i,
                parent=self,
            )
            panel.setMinimumHeight(680)
            rows_layout.addWidget(panel)
            self._panels.append(panel)

        layout.addLayout(rows_layout)

    def deleteLater(self) -> None:
        for panel in self._panels:
            panel.release()
        super().deleteLater()
