"""
ElaBrowserEmbedder 使用示例

演示如何嵌入外部浏览器到 PyQt5 窗口中，支持：
- 浏览器嵌入和释放
- 页面导航
- JavaScript 执行
- CDP 连接监控

运行方式:
    uv run python test_browser_embedder.py
"""

import sys
import os

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.fonts.warning=false"

from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QToolButton
from PyQt5ElaWidgetTools import eApp, ElaWindow, ElaText, eTheme, ElaThemeType, ElaToolButton
from pyqt5_ela_pro import ElaBrowserEmbedder

BROWSER_PATH = Path(
    os.environ.get(
        "ELA_BROWSER_PATH",
        r"E:\python_project\elawidgettools\Supermium\chrome.exe",
    )
)
TEST_URL = "https://www.bilibili.com"


class BrowserDemoWindow(ElaWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._browser = None
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("ElaBrowserEmbedder 示例")
        self.resize(1000, 700)
        self.setUserInfoCardTitle("浏览器演示")
        self.setUserInfoCardSubTitle("PyQt5ElaWidgetTools")


        central = QWidget(self)
        self.addPageNode("浏览器示例",central)
        # self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        url_layout = QHBoxLayout()
        self._url_input = QTextEdit()
        self._url_input.setFixedHeight(30)
        self._url_input.setText(TEST_URL)
        url_layout.addWidget(self._url_input)

        embed_btn = QPushButton("嵌入浏览器")
        embed_btn.clicked.connect(self._embed_browser)
        url_layout.addWidget(embed_btn)

        release_btn = QPushButton("释放浏览器")
        release_btn.clicked.connect(self._release_browser)
        url_layout.addWidget(release_btn)

        nav_btn = QPushButton("导航")
        nav_btn.clicked.connect(self._navigate)
        url_layout.addWidget(nav_btn)

        reload_btn = QPushButton("刷新")
        reload_btn.clicked.connect(self._reload)
        url_layout.addWidget(reload_btn)

        js_btn = QPushButton("执行JS")
        js_btn.clicked.connect(self._run_js)
        url_layout.addWidget(js_btn)

        layout.addLayout(url_layout)

        self._browser_widget = ElaBrowserEmbedder(
            webview_path=BROWSER_PATH,
            debug_port=9222,
            browser_args=[f"--user-data-dir={Path.cwd() / 'runtime' / 'cache' / 'browser_demo'}"],
            parent=self,
        )
        layout.addWidget(self._browser_widget, 1)

        self._status_label = ElaText("状态: 就绪")
        self._status_label.setTextPixelSize(14)
        layout.addWidget(self._status_label)

        self._log_output = QTextEdit()
        self._log_output.setReadOnly(True)
        self._log_output.setFixedHeight(80)
        layout.addWidget(self._log_output)

        self._browser_widget.window_embedded.connect(lambda h: self._log(f"窗口已嵌入: 0x{h:X}"))
        self._browser_widget.window_released.connect(lambda h: self._log(f"窗口已释放: 0x{h:X}"))
        self._browser_widget.embed_error.connect(lambda m: self._log(f"嵌入错误: {m}"))
        self._browser_widget.embed_completed.connect(self._on_embed_completed)
        self._browser_widget.load_started.connect(lambda: self._log("页面加载中..."))
        self._browser_widget.load_finished.connect(lambda: self._log("页面加载完成"))
        self._browser_widget.log_message.connect(self._log)

    def _log(self, msg):
        self._log_output.append(msg)
        self._status_label.setText(f"状态: {msg[:20]}...")

    def _on_embed_completed(self, ok: bool):
        if ok:
            self._log("CDP 连接就绪，导航/刷新/JS 已可用")
        else:
            self._log("CDP 连接失败")

    def _embed_browser(self):
        url = self._url_input.toPlainText().strip()
        self._log(f"嵌入: {url}")
        try:
            self._browser_widget.embed(url, window_title="bilibili", connect_cdp=True)
        except Exception as e:
            self._log(f"嵌入错误: {e}")
    def _release_browser(self):
        try:
            self._log("释放浏览器")
            self._browser_widget.release()
        except Exception as e:
            self._log(f"释放错误: {e}")

    def _navigate(self):
        url = self._url_input.toPlainText().strip()
        self._log(f"导航: {url}")
        self._browser_widget.navigate(url)

    def _reload(self):
        self._log("刷新")
        self._browser_widget.reload()

    def _run_js(self):
        self._browser_widget.run_js("console.log('你好')")

    def closeEvent(self, event):
        try:
            self._browser_widget.release()
            super().closeEvent(event)
        except  Exception as e:
            print(e)


def main():
    if not BROWSER_PATH.exists():
        print(f"错误: 浏览器不存在: {BROWSER_PATH}")
        return 1

    app = QApplication(sys.argv)
    eApp.init()

    window = BrowserDemoWindow()
    window.show()

    print("=" * 60)
    print("ElaBrowserEmbedder 使用示例")
    print("=" * 60)
    print(f"浏览器: {BROWSER_PATH}")
    print("功能: 嵌入、导航、刷新、JavaScript执行、主题切换")
    print("=" * 60)

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
