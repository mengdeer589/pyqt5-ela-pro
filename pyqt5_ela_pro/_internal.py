"""
内部工具模块。

包含仅供内部使用的工具函数，不应作为公共API直接调用。
"""

from __future__ import annotations

import sys
import traceback
from functools import wraps
from typing import Any, Callable, Optional, Protocol, TypeVar, runtime_checkable

from PyQt5 import sip
from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QApplication, QWidget, QWIDGETSIZE_MAX
from PyQt5ElaWidgetTools import ElaThemeType, eTheme

F = TypeVar("F", bound=Callable[..., Any])


@runtime_checkable
class _ThemeAwareProtocol(Protocol):
    """_ThemeAwareMixin 所要求的宿主类接口。"""

    _theme_connected: bool
    _theme_mode: int

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None: ...


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
    try:
        eTheme.themeModeChanged.disconnect(slot)
    except (TypeError, RuntimeError):
        pass


def safe_call(func: Optional[Callable[..., Any]], *args, **kwargs) -> Any:
    """安全调用函数，如果函数为 None 或调用失败返回 None。"""
    if func is None:
        return None
    try:
        return func(*args, **kwargs)
    except BaseException:
        print(f"Error calling {func}: {traceback.format_exc()}", file=sys.stderr)
        return None


def to_logical_pos(x: int, y: int) -> QPoint:
    """物理像素坐标 → Qt 逻辑坐标（按包含该点的屏幕 DPR 换算）。

    Win32 的 ``GetCursorPos`` / ``GetWindowRect`` 等返回物理像素，而
    ``QApplication.widgetAt`` 等 Qt 公开 API 在启用高 DPI 缩放
    （``AA_EnableHighDpiScaling``）后使用逻辑坐标，直接混用会命中错误控件。
    """
    try:
        app = QApplication.instance()
        if app is None:
            return QPoint(int(x), int(y))
        for screen in app.screens():
            dpr = float(screen.devicePixelRatio() or 1.0)
            geo = screen.geometry()
            left = int(geo.x() * dpr)
            top = int(geo.y() * dpr)
            if left <= x < left + int(geo.width() * dpr) and top <= y < top + int(
                geo.height() * dpr
            ):
                return QPoint(int(x / dpr), int(y / dpr))
        dpr = float(app.primaryScreen().devicePixelRatio() or 1.0)
        return QPoint(int(x / dpr), int(y / dpr))
    except Exception:
        return QPoint(int(x), int(y))


def execElaMenu(menu, global_pos) -> None:
    """弹出 ``ElaMenu``（阻塞到关闭）并在关闭后回收。

    两处 ``ElaMenu`` 的坑在这里兜住（实测）：

    1. **非主屏上偶发不按 ``sizeHint`` 撑开** —— 只显示第一项（208x260 的菜单
       弹出成 100x30）。显式 ``setMinimumSize(sizeHint())`` 可解，主屏无副作用；
    2. **``popup()`` 是异步的**，紧跟 ``deleteLater()`` 会在菜单显示前把它删掉 ——
       所以用阻塞的 ``exec_()``，返回后再回收（不留在控件树上累积）。

    :param menu: ``ElaMenu`` 实例
    :param global_pos: 弹出位置（全局坐标）
    """
    try:
        menu.setMinimumSize(menu.sizeHint())
        menu.exec_(global_pos)
    finally:
        menu.deleteLater()


def _draw_button_content(
    painter: QPainter,
    text: str,
    icon_name,
    icon_size: int,
    shadow_border: int,
    widget_width: int,
    widget_height: int,
    text_color: QColor,
    icon_getter: Callable[[Any, QColor], Any],
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


def _disconnect_theme_on_destroy(obj) -> None:
    """``destroyed`` 的清理槽（**必须是模块级普通函数**）。

    为什么不能直接连 ``self._theme_cleanup``：**PyQt5 不会调用「绑定到自身」的
    ``destroyed`` 槽**（实测：``sip.delete()`` 同步销毁时绑方法触发 0 次、
    lambda / 模块级函数各触发 1 次）。原来的写法
    ``self.destroyed.connect(self._theme_cleanup)`` 等于**清理从来没发生过**。

    但光靠这里也不够 —— 见 :func:`_make_theme_slot` 的自愈分支：即便
    ``destroyed`` 没能送达，槽自己也会在第一次「打到已销毁对象」时断开。
    """
    slot = getattr(obj, "_theme_slot", None)
    if slot is not None:
        try:
            obj._theme_connected = False
            obj._theme_slot = None
        except RuntimeError:  # 包装器已不可用
            pass
        disconnect_theme_signal(slot)


def _make_theme_slot(obj):
    """造一个「带存活检查 + 自愈断开」的主题槽。

    ``eTheme`` 是**进程级单例**，它的 ``themeModeChanged`` 会一直连着所有曾经
    创建过的控件。控件销毁后 Python 包装器可能还活着（lambda 闭包、信号连接
    都持有引用），信号再发一次就直接打进已释放的 C++ 对象 = 0xC0000409 静默
    终止（无 traceback）。所以槽的第一件事是 ``sip.isdeleted()``，命中就顺手
    把自己断开 —— **不依赖 ``destroyed`` 一定送达**。
    """

    def _slot(mode):
        try:
            alive = not sip.isdeleted(obj)
        except (RuntimeError, TypeError):
            alive = False
        if not alive:
            disconnect_theme_signal(_slot)
            return
        obj._onThemeChanged(mode)

    return _slot


class _ThemeAwareMixin:
    """Mixin that auto-connects theme signals and cleans up on destroy.

    Subclasses must define _onThemeChanged(self, mode) and call
    super().__init__(parent) or self._init_theme_aware().

    清理有两条独立防线：``destroyed`` 上的模块级函数（正常路径）+ 槽自身的
    ``sip.isdeleted()`` 自愈（兜底，理由见上面两个函数）。
    """

    # 类级默认值：``_init_theme_aware`` 在 ``__init__`` 链的**最上游**就要读
    # ``_theme_connected``（子类可能还没设过），所以不能只有注解没有值。
    _theme_connected: bool = False
    _theme_slot: object = None
    _theme_mode: ElaThemeType.ThemeMode

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_theme_aware()

    def _init_theme_aware(self) -> None:
        if self._theme_connected:
            return
        self._theme_connected = True
        # 槽**必须存成实例属性**：``disconnect`` 要按身份对得上同一个对象
        self._theme_slot = _make_theme_slot(self)
        eTheme.themeModeChanged.connect(self._theme_slot)
        self.destroyed.connect(_disconnect_theme_on_destroy)  # type: ignore[attr-defined]

    def _theme_cleanup(self) -> None:
        """主动断开（供不需要等 ``destroyed`` 的场景显式调用）。"""
        if self._theme_connected:
            self._theme_connected = False
            self._theme_slot = None
            disconnect_theme_signal(self._onThemeChanged)

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        """子类应重写此方法以响应主题切换。"""

    def deleteLater(self) -> None:
        self._theme_cleanup()
        super().deleteLater()  # type: ignore[misc]


POPUP_FOOTER_OBJECT_NAME = "ElaGhostPopupFooter"


def _popup_extra_height(container: QWidget, object_name: str, fallback: int) -> int:
    """弹层内附加控件（搜索框 / 底部固定区）占用的高度；不存在或已隐藏按 0 计。"""
    widget = container.findChild(QWidget, object_name)
    if widget is None or widget.isHidden():
        return 0
    return widget.height() or widget.sizeHint().height() or fallback


def _adjust_combobox_popup(combo_box) -> None:
    """在 super().showPopup() 之后调用。用最终弹窗高度判断是否需要移到上方。"""
    container = combo_box.findChild(QWidget, "ElaComboBoxContainer")
    if not container or not container.isVisible():
        return

    # 复位上次压缩的固定高度，避免后续弹窗持续偏小
    container.setFixedHeight(QWIDGETSIZE_MAX)

    combo_global = combo_box.mapToGlobal(QPoint(0, 0))
    combo_top = combo_global.y()
    combo_bottom = combo_top + combo_box.height()

    screen = QApplication.screenAt(combo_global)
    if not screen:
        return
    screen_geo = screen.availableGeometry()

    # 计算最终容器高度
    item_h = combo_box.view().sizeHintForRow(0) if combo_box.count() else 30
    if item_h <= 0:
        item_h = 30
    n = combo_box.maxVisibleItems()
    if combo_box.count() < n:
        n = combo_box.count()
    extra_height = _popup_extra_height(container, "SearchWidget", 40)
    extra_height += _popup_extra_height(container, POPUP_FOOTER_OBJECT_NAME, 36)
    final_height = n * item_h + 8 + extra_height

    # 下方所需总空间：组合框底 + 3px 间距 + 弹窗高度
    needed_below = combo_bottom + 3 + final_height

    if needed_below > screen_geo.bottom():
        # 移到上方
        new_y = combo_top - 3 - final_height
        if new_y >= screen_geo.top():
            container.move(container.x(), new_y)
        else:
            # 上方也不够 → 压缩高度
            max_h = combo_top - 3 - screen_geo.top()
            if max_h > 50:
                container.setFixedHeight(int(max_h))
                container.move(container.x(), screen_geo.top())
