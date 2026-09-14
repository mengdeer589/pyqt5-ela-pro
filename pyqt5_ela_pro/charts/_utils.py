"""
charts 包私有共享工具模块。

数值与几何小工具：统一语义为「过滤 NaN/Inf」版：

- ``to_float(v, default=0.0)``：宽松转 float；None / bool / NaN / Inf /
  转换失败一律返回 default（唯一语义，防止 NaN 流入 QPainter 坐标）。
- ``clamp(v, lo, hi)``：区间钳制。
- ``with_alpha(color, a)``：返回设置 alpha（0-255）后的 QColor 副本。
- ``dist_point_segment(p, a, b)``：点 p 到线段 a-b 的距离。
- ``warn_once(key, message)``：异常静默吞噬的可见性出口——同一 key 仅向
  stderr 记录一次（有界去重）。
- ``ON_FILL_WHITE``：绘制在彩色填充上的白字常量。

移植自 InstructionX_UIKit.charts._utils（PySide6 → PyQt5，无逻辑改动；
原库无 LICENSE，保留出处）。
"""

from __future__ import annotations

import math
import sys

from PyQt5.QtGui import QColor

__all__ = [
    "to_float",
    "clamp",
    "with_alpha",
    "dist_point_segment",
    "warn_once",
    "ON_FILL_WHITE",
]

# ---------------------------------------------------------------------------
# 数值 / 几何工具
# ---------------------------------------------------------------------------


def to_float(v, default=0.0):
    """宽松转 float；None / bool / NaN / Inf / 转换失败一律返回 default。"""
    fallback = None if default is None else float(default)
    if isinstance(v, bool) or v is None:
        return fallback
    try:
        f = float(v)
    except (TypeError, ValueError):
        return fallback
    if math.isnan(f) or math.isinf(f):
        return fallback
    return f


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def with_alpha(color, a):
    """返回设置 alpha（0-255，自动钳制）后的 QColor 副本。"""
    c = QColor(color)
    c.setAlpha(int(clamp(a, 0, 255)))
    return c


def dist_point_segment(p, a, b):
    """点 p 到线段 a-b 的距离（退化线段退化为点距）。"""
    ax, ay = a.x(), a.y()
    bx, by = b.x(), b.y()
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq <= 1e-12:
        return math.hypot(p.x() - ax, p.y() - ay)
    t = clamp(((p.x() - ax) * dx + (p.y() - ay) * dy) / length_sq, 0.0, 1.0)
    return math.hypot(p.x() - (ax + t * dx), p.y() - (ay + t * dy))


# ---------------------------------------------------------------------------
# 异常可见性（「失败不影响主图」契约的配套出口）
# ---------------------------------------------------------------------------

_warned_keys = set()
_WARN_LIMIT = 512  # 去重集合上界，防止长期运行无界增长


def warn_once(key: str, message: str) -> None:
    """同一 key 仅向 stderr 记录一次（有界去重）。"""
    if key in _warned_keys:
        return
    if len(_warned_keys) >= _WARN_LIMIT:
        _warned_keys.clear()
    _warned_keys.add(key)
    sys.stderr.write(f"[charts] {message}\n")


# ---------------------------------------------------------------------------
# 硬编码颜色豁免常量
# ---------------------------------------------------------------------------

#: 白字豁免：绘制在彩色填充（系列色块 / 渐变带）之上的标签文字，
#: 与主题无关的「on-fill」前景色，集中于此常量以便审计，不读主题令牌。
ON_FILL_WHITE = "#ffffff"
