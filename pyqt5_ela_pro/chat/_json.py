"""
聊天 JSON 编解码（优先 ``orjson``，缺失时回落标准库 ``json``）。
``pyqt5_ela_pro.chat`` 内部的持久化 / journal / 工具参数解析统一走这里：

- 装了 ``orjson``：由它序列化（更快、原生 UTF-8）；``allow_nan=False``
  的严格性用一次快速扫描保持与标准库一致（orjson 默认会把 NaN / Infinity
  写成 ``null``，静默丢数据）；
- 没装：``json.dumps(ensure_ascii=False, separators=(",", ":"))``，
  两套后端产出**同为紧凑 UTF-8 文本**，可逐字节比对。

宿主也可直接用 ``pyqt5_ela_pro.chat.jsonDumps`` / ``jsonLoads`` /
``jsonBackend``（见 ``chat/__init__.py``）。
"""

from __future__ import annotations

import json
import math
from typing import Any

try:  # pragma: no cover - 分支取决于安装环境
    import orjson as _orjson
except ImportError:  # pragma: no cover
    _orjson = None

#: orjson 对非字符串键的兼容开关（旧版本没有该属性时退化为 0，仅字符串键可用）
_ORJSON_OPTIONS = getattr(_orjson, "OPT_NON_STR_KEYS", 0) if _orjson else 0


def backend() -> str:
    """当前 JSON 后端名（``"orjson"`` / ``"json"``）。"""
    return "orjson" if _orjson is not None else "json"


def _has_non_finite(value: Any) -> bool:
    """迭代扫描 NaN / Infinity（不递归，避免深层数据触发递归上限）。"""
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, float):
            if not math.isfinite(item):
                return True
        elif isinstance(item, dict):
            stack.extend(item.values())
        elif isinstance(item, (list, tuple)):
            stack.extend(item)
    return False


def dumps(obj: Any, allow_nan: bool = False) -> str:
    """序列化为紧凑 UTF-8 JSON 文本（``str``）。

    :param allow_nan: ``False``（默认）时 NaN / Infinity 抛
        :class:`ValueError`（与标准库同语义，避免把非 JSON 数值静默写成
        ``null`` / ``NaN``）；``True`` 时交给后端默认行为。
    """
    if _orjson is not None:
        if not allow_nan and _has_non_finite(obj):
            raise ValueError("Out of range float values are not JSON compliant")
        return _orjson.dumps(obj, option=_ORJSON_OPTIONS).decode("utf-8")
    return json.dumps(
        obj,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=allow_nan,
    )


def loads(data: Any) -> Any:
    """解析 JSON 文本 / 字节（``str`` / ``bytes`` / ``bytearray``）。"""
    if _orjson is not None:
        return _orjson.loads(data)
    return json.loads(data)
