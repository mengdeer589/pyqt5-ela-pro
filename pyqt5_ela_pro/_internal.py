"""
内部工具模块。

包含仅供内部使用的工具函数，不应作为公共API直接调用。
"""

from __future__ import annotations

import sys
import traceback
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QColor, QPainter

F = TypeVar("F", bound=Callable[..., Any])


def catch_error(func: F) -> F:
    """装饰器：捕获函数执行中的异常并打印错误信息。"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            print(
                f"Error in {func.__name__}: {traceback.format_exc()}", file=sys.stderr
            )
            return None

    return wrapper  # type: ignore


def disconnect_theme_signal(slot: Callable[[Any], None]) -> None:
    """安全断开 eTheme.themeModeChanged 信号连接（抑制异常）。"""
    from PyQt5ElaWidgetTools import eTheme

    try:
        eTheme.themeModeChanged.disconnect(slot)
    except (TypeError, RuntimeError):
        pass


def init_painter(widget) -> QPainter:
    """创建 QPainter 并设置常用的渲染提示（抗锯齿等）。

    适用于自定义 paintEvent 中的标准 QPainter 初始化模板。
    使用完毕后仍需调用 paint.end()。
    """
    painter = QPainter(widget)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    return painter


def safe_call(func: Optional[Callable[..., Any]], *args, **kwargs) -> Any:
    """安全调用函数，如果函数为 None 或调用失败返回 None。"""
    if func is None:
        return None
    try:
        return func(*args, **kwargs)
    except Exception:
        print(f"Error calling {func}: {traceback.format_exc()}", file=sys.stderr)
        return None


def _draw_button_content(
    painter: QPainter,
    text: str,
    icon_name,
    icon_size: int,
    shadow_border: int,
    widget_width: int,
    widget_height: int,
    text_color: QColor,
    icon_getter,
) -> QRect:
    """绘制按钮图标和文字布局。

    :return: 文字区域 QRect
    """
    if icon_name is not None:
        icon_sz = QSize(icon_size, icon_size)
        spacing = 8
        content_height = widget_height - 2 * shadow_border

        fm = painter.fontMetrics()
        text_width = fm.horizontalAdvance(text)
        total_content_width = icon_sz.width() + spacing + text_width
        start_x = (
            shadow_border
            + (widget_width - 2 * shadow_border - total_content_width) // 2
        )

        icon_y = shadow_border + (content_height - icon_sz.height()) // 2
        icon_rect = QRect(start_x, icon_y, icon_sz.width(), icon_sz.height())

        text_rect = QRect(
            icon_rect.right() + spacing,
            shadow_border,
            text_width,
            content_height,
        )
        icon = icon_getter(icon_name, text_color)
        painter.drawPixmap(icon_rect, icon.pixmap(icon_sz))
    else:
        rect = QRect(
            shadow_border,
            shadow_border,
            widget_width - 2 * shadow_border,
            widget_height - 2 * shadow_border,
        )
        text_rect = rect

    painter.setPen(text_color)
    painter.setFont(painter.font())
    painter.drawText(
        text_rect,
        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
        text,
    )
    return text_rect
