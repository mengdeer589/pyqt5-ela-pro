"""扫全库的 PyQt5 遗留写法 —— 这些形态在 PySide6 下**必然失败**，不是风格问题。

迁移期实测：示例页里 ``btn.clicked.connect(self._onModeClicked, mode)``（PyQt5 的
「连接时附带实参」重载）在 PySide6 抛 ``TypeError``；它落在示例页的构造路径里，表现为
「按钮点了没反应」而不是崩溃，靠真跑示例才发现（``tests/example/`` 的页面守卫不构造页面）。

只收「一定失败」的形态；``Qt.AlignCenter`` / ``QFont.Monospace`` 这类 PySide6 仍保留的
别名不算（那是风格，交给 lint）。规则：

- ``x.connect(a, b)``：PySide6 的两位置参重载是 ``connect(上下文 QObject, 槽)``，
  写成 ``connect(槽, 额外实参)``（PyQt5 语义）必 ``TypeError``。判据：第一个位置参
  是绑定方法（``obj.method``）/ lambda 时，第二个位置参即「额外实参」。
- ``pyqtSignal`` / ``pyqtSlot`` / ``pyqtProperty`` → ``Signal`` / ``Slot`` / ``Property``。
- ``PyQt5`` / ``PyQt6`` / ``sip`` 的 import、``QVariant`` → PySide6 下不存在。
- ``.exec_()`` → ``.exec()``。
- 上游绑定的枚举参数只收枚举成员：写成 ``setDisplayMode(0)`` 会抛误导性的
  ``NameError: name 'ElaWidgetTools' is not defined``（实测，窗口构造期即炸）。
"""

from __future__ import annotations

import ast
import pathlib

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_SCANNED = [p for p in (_ROOT / "pyside6_ela_pro", _ROOT / "llm_test") if p.is_dir()]

#: PySide6 里不存在的名字 / 模块（命中即运行期 NameError / ModuleNotFoundError）。
_BANNED_NAMES = {"pyqtSignal", "pyqtSlot", "pyqtProperty", "QVariant"}
_BANNED_MODULES = {"PyQt5", "PyQt6", "sip"}

#: 上游绑定里**实测**只收枚举成员的方法 → 哪些位置参必须是枚举成员（按 .h 的签名）。
_ENUM_ONLY_ARG_POSITIONS = {
    "setDisplayMode": (0,),
    "setWindowButtonFlags": (0,),
    "setTextStyle": (0,),
    "setThemeMode": (0,),
    "getThemeColor": (0, 1),
    "setThemeColor": (0, 1),
}
_ENUM_ONLY_ARG_NAMES = {
    "displayMode",
    "buttonFlags",
    "textStyle",
    "themeMode",
    "themeColor",
}


def _is_int_constant(node: ast.expr) -> bool:
    """裸 int 字面量（``True`` / ``False`` 不算 —— bool 是合法实参）。"""
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, int)
        and not isinstance(node.value, bool)
    )


def _iter_py_files():
    for base in _SCANNED:
        for path in sorted(base.rglob("*.py")):
            if "__pycache__" in str(path):
                continue
            yield path


def _looks_like_slot(node: ast.expr) -> bool:
    """第一个位置参是否「槽的写法」（不是上下文 QObject 的写法）。"""
    if isinstance(node, (ast.Lambda, ast.Attribute)):
        return True
    return isinstance(node, ast.Call) and "partial" in ast.unparse(node.func)


def _scan_tree(tree: ast.Module, label: str) -> list[str]:
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in _BANNED_NAMES:
            found.append(f"{label}:{node.lineno}: {node.id}")
        elif isinstance(node, ast.Attribute) and node.attr == "exec_":
            found.append(f"{label}:{node.lineno}: .exec_() 应为 .exec()")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in _BANNED_MODULES:
                found.append(f"{label}:{node.lineno}: from {node.module} import ...")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in _BANNED_MODULES:
                    found.append(f"{label}:{node.lineno}: import {alias.name}")
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "connect"
            and len(node.args) >= 2
            and _looks_like_slot(node.args[0])
        ):
            found.append(f"{label}:{node.lineno}: {ast.unparse(node)}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            positions = _ENUM_ONLY_ARG_POSITIONS.get(node.func.attr, ())
            bad_args = [
                i
                for i in positions
                if i < len(node.args) and _is_int_constant(node.args[i])
            ]
            bad_kwargs = [
                kw.arg
                for kw in node.keywords
                if kw.arg in _ENUM_ONLY_ARG_NAMES and _is_int_constant(kw.value)
            ]
            if bad_args or bad_kwargs:
                found.append(
                    f"{label}:{node.lineno}: {ast.unparse(node)} —— 枚举参数收到 int 字面量"
                )
    return found


def _sites() -> list[str]:
    found: list[str] = []
    for path in _iter_py_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:  # pragma: no cover - 由 ruff 拦
            found.append(f"{path}:{exc.lineno}: SyntaxError {exc.msg}")
            continue
        found.extend(_scan_tree(tree, str(path.relative_to(_ROOT))))
    return found


def _count_sites(source: str) -> int:
    return len(_scan_tree(ast.parse(source), "<snippet>"))


class TestNoPyQt5OnlyCallForms:
    def test_no_pyqt5_only_call_forms(self):
        offenders = _sites()
        assert offenders == [], (
            "这些写法在 PySide6 下必然失败（PyQt5 遗留）：\n"
            + "\n".join("  " + o for o in offenders)
            + "\n\n带额外实参的连接用 lambda 固定实参："
            " ``btn.clicked.connect(lambda _checked=False, m=mode: self._onMode(m))``。"
        )

    def test_scanner_finds_planted_sites(self):
        """守卫本身要有效：坏形状必须被抓到、安全形状必须放过。"""
        bad = (
            "from PyQt5.QtCore import QPoint\n"
            "from sip import isdeleted\n"
            "class A:\n"
            "    sig = pyqtSignal()\n"
            "    def f(self, btn, mode):\n"
            "        btn.clicked.connect(self._onMode, mode)\n"
            "        self.menu.exec_()\n"
            "        nav.setDisplayMode(0)\n"
            "        eTheme.getThemeColor(mode, 0)\n"
        )
        good = (
            "from PySide6.QtCore import Signal\n"
            "class A:\n"
            "    changed = Signal(object)\n"
            "    def f(self, btn, mode, other):\n"
            "        btn.clicked.connect(lambda _checked=False, m=mode: self._onMode(m))\n"
            "        self.changed.connect(other, other._onChanged)\n"
            "        btn.clicked.connect(self._onMode)\n"
            "        nav.setDisplayMode(ElaNavigationType.NavigationDisplayMode.Maximal, False)\n"
            "        eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBase)\n"
        )
        assert _count_sites(bad) == 7, "坏形状没被抓全"
        assert _count_sites(good) == 0, "安全形状被误报"
