"""
窗口动画和工具函数模块（向后兼容重导出）。

shake_window 已移至 animation 模块，此文件保留为向后兼容的导入路径。
"""
from __future__ import annotations

from .animation import shake_window

__all__ = ["shake_window"]
