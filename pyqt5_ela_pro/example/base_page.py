"""
[pyqt5_ela_pro] 示例页面基类
"""

import os
import inspect
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton, QApplication, QWidget
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QTextCursor, QPalette
from PyQt5ElaWidgetTools import ElaScrollArea, ElaText, ElaPushButton, ElaThemeType, ElaIconType, ElaMessageBar, ElaMessageBarType
from pyqt5_ela_pro import ElaThemeWidget, ElaDialogBase, ElaPrimaryButton

RESOURCE_PATH = os.path.join(os.path.dirname(__file__), "resource", "images")


def _res(filename):
    return os.path.join(RESOURCE_PATH, filename)


class ExamplePage(ElaThemeWidget):
    """示例页面基类，提供通用布局结构"""

    PAGE_TITLE = "[ela_ext] 示例页面"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setupUI()

    def _setupUI(self):
        self._scrollArea = ElaScrollArea(self)
        self._scrollArea.setWidgetResizable(True)
        self._scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        scrollWidget = ElaThemeWidget()
        mainLayout = QVBoxLayout(scrollWidget)
        mainLayout.setContentsMargins(20, 20, 20, 20)
        mainLayout.setSpacing(15)

        self._addDemoContent(mainLayout)

        mainLayout.addStretch()

        self._scrollArea.setWidget(scrollWidget)

        containerLayout = QVBoxLayout(self)
        containerLayout.addWidget(self._scrollArea)

    def _addDemoContent(self, main_layout):
        raise NotImplementedError("子类必须实现 _addDemoContent 方法")

    def _createSectionHeader(self, title):
        section = ElaText(title, self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        return section

    def _addInfoText(self, text, parent_layout):
        info = ElaText(text, self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

    def _createHeaderRow(self, title, method):
        """创建带代码查看按钮的节标题行。

        :param title: 标题文本
        :param method: 要查看源码的 demo 方法
        :returns: QHBoxLayout，包含标题 + 伸缩 + 代码按钮
        """
        row = QHBoxLayout()
        row.setSpacing(8)
        btn = ElaPushButton("</> 代码")
        btn.setFixedWidth(85)
        btn.clicked.connect(lambda: self._show_code(method))
        row.addWidget(btn)
        row.addWidget(self._createSectionHeader(title))
        return row

    def _show_code(self, method):
        try:
            source = inspect.getsource(method)
        except (OSError, TypeError):
            source = "无法获取源码"
        dlg = ElaDialogBase(title="示例代码", parent=self.window())
        dlg.setLeftButtonText("关闭")
        for btn in dlg.findChildren(QPushButton):
            if btn.text() == "确定":
                btn.hide()
                break
        edit = QPlainTextEdit()
        edit.setReadOnly(True)
        edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        edit.setFrameShape(QPlainTextEdit.NoFrame)
        pal = edit.palette()
        pal.setColor(QPalette.Base, QColor("#1E1E1E"))
        pal.setColor(QPalette.Text, QColor("#D4D4D4"))
        edit.setPalette(pal)
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        edit.setFont(font)
        edit.document().setDefaultFont(font)
        _insert_colored_code(edit.document(), source)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(4)
        container_layout.addWidget(edit)
        copy_btn = ElaPrimaryButton(parent=container)
        copy_btn.setText("复制代码")
        copy_btn.setElaIcon(ElaIconType.IconName.Copy, 16)
        copy_btn.clicked.connect(
            lambda: (
                QApplication.clipboard().setText(source),
                ElaMessageBar.success(
                    ElaMessageBarType.PositionPolicy.TopRight,
                    "", "代码已复制到剪贴板", 1000, dlg,
                ),
            )
        )
        container_layout.addWidget(copy_btn)
        dlg._paramLay.setContentsMargins(15, 25, 15, 2)
        dlg.setParamWidget(container)
        dlg.resize(900, 650)
        dlg.exec_()


# ── 彩色代码插入到 QTextDocument ──────────────────────────────

import re as _re

_KEYWORDS = {
    "and", "as", "assert", "async", "await", "break", "class", "continue",
    "def", "del", "elif", "else", "except", "finally", "for", "from",
    "global", "if", "import", "in", "is", "lambda", "nonlocal", "not",
    "or", "pass", "raise", "return", "try", "while", "with", "yield",
    "True", "False", "None",
}
_BUILTINS = {
    "abs", "all", "any", "bin", "bool", "callable", "chr", "classmethod",
    "dict", "dir", "divmod", "enumerate", "eval", "filter", "float", "format",
    "getattr", "globals", "hasattr", "hash", "help", "hex",
    "id", "input", "int", "isinstance", "issubclass", "iter", "len", "list", "locals",
    "map", "max", "min", "next", "object", "oct", "open", "ord",
    "pow", "print", "property", "range", "repr", "reversed", "round",
    "set", "setattr", "slice", "sorted", "staticmethod", "str",
    "sum", "super", "tuple", "type", "vars", "zip",
}

_TOKEN_RE = _re.compile(
    r"""(?P<comment>\#.*)"""
    r"""|(?P<decorator>@\w+)"""
    r"""|(?P<string>(?:f|r)?(?:"[^"\\]*(?:\\.[^"\\]*)*"|'[^'\\]*(?:\\.[^'\\]*)*'))"""
    r"""|(?P<number>\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b)"""
    r"""|(?P<operator>\.\.\.|->|\*\*=?|<<=?|>>=?|//=?|[+\-*/%&|^~<>!=]=?|[:.,;])"""
    r"""|(?P<ident>\b\w+\b)"""
    r"""|(?P<other>.)"""
)

_STYLE = {
    "comment":  ("#6A9955",  False,  True),
    "decorator":("#DCDCAA",  False, False),
    "string":   ("#CE9178",  False, False),
    "number":   ("#B5CEA8",  False, False),
    "kw":       ("#569CD6",  True,  False),
    "builtin":  ("#D8A0DF",  False, False),
    "class":    ("#4EC9B0",  False, False),
    "method":   ("#DCDCAA",  False, False),
    "attr":     ("#9CDCFE",  False, False),
    "operator": ("#D4D4D4",  False, False),
    "defclass": ("#4EC9B0",  False, False),
    "default":  ("#D4D4D4",  False, False),
}


def _make_fmt(color, bold=False, italic=False):
    f = QTextCharFormat()
    f.setForeground(QColor(color))
    if bold:
        f.setFontWeight(QFont.Bold)
    if italic:
        f.setFontItalic(True)
    return f


def _insert_colored_code(doc, source):
    cur = QTextCursor(doc)
    for line in source.split("\n"):
        _insert_colored_line(cur, line)
        cur.insertText("\n")


def _insert_colored_line(cur, raw):
    matches = list(_TOKEN_RE.finditer(raw))
    last = 0
    for i, m in enumerate(matches):
        if m.start() > last:
            cur.insertText(raw[last:m.start()])
        kind = m.lastgroup
        text = m.group()

        if kind == "ident":
            fmt = _make_fmt(*_STYLE[_ident_type(i, matches, raw)])
        elif kind == "other":
            cur.insertText(text)
            last = m.end()
            continue
        elif kind == "operator":
            fmt = _make_fmt(*_STYLE["operator"])
        else:
            fmt = _make_fmt(*_STYLE[kind])

        cur.insertText(text, fmt)
        last = m.end()
    if last < len(raw):
        cur.insertText(raw[last:])


def _ident_type(i, matches, raw):
    """判断 ident 的颜色类别，基于上下文。"""
    text = matches[i].group()

    if text in _KEYWORDS or text == "self":
        return "kw"
    if text in _BUILTINS:
        return "builtin"

    after_dot = False
    for j in range(i - 1, -1, -1):
        tok = matches[j].group()
        if tok.strip() and tok != ".":
            break
        if tok == ".":
            after_dot = True
            break

    followed_by_paren = False
    for j in range(i + 1, len(matches)):
        tok = matches[j].group()
        if tok == "(":
            followed_by_paren = True
            break
        if tok.strip():
            break

    if after_dot:
        return "method" if followed_by_paren else "attr"
    if text and text[0].isupper():
        return "class"
    if followed_by_paren:
        return "method"

    prev = raw[:matches[i].start()].rstrip()
    if prev.endswith("def") or prev.endswith("class"):
        return "defclass"

    return "default"
