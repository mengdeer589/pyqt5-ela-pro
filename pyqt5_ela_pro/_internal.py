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
from PyQt5.QtCore import QObject, QPoint, QRect, QSize, Qt, QTimer
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QApplication, QWidget, QWIDGETSIZE_MAX
from PyQt5ElaWidgetTools import ElaThemeType, eTheme

__all__ = [
    "single_shot_on",
    "catch_error",
    "connect_theme_signal",
    "disconnect_theme",
    "disconnect_theme_signal",
    "safe_call",
    "to_logical_pos",
]

F = TypeVar("F", bound=Callable[..., Any])


@runtime_checkable
class _ThemeAwareProtocol(Protocol):
    """_ThemeAwareMixin 所要求的宿主类接口。"""

    _theme_connected: bool
    _theme_mode: int

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None: ...


def single_shot_on(ctx: QObject, msec: int, slot) -> QTimer:
    """在 ``ctx`` 上挂一个**子** :class:`QTimer` 做延时调用。

    **不要用 ``QTimer.singleShot(ms, callable)``**：那个重载建的是没有接收方的
    ``QSingleShotTimer``，它不随任何控件销毁 —— 回调里摸控件就会在控件已释放
    时炸（``RuntimeError`` 穿出 Qt 回调 = 进程 ``0xC0000409`` 零 traceback
    终止）。实测 ``ela_tag_multi_box`` 的
    ``QTimer.singleShot(0, lambda: _pre_init_popup(self))`` 在「构造后立刻
    ``sip.delete``」下确定性崩。

    PyQt5 的 ``singleShot(ms, ctx, callable)`` 重载**也不能单独当保障**
    （实测传了 context 照样崩）—— 真正的保险是「定时器本身是 ``ctx`` 的子对象」，
    ``ctx`` 析构时 Qt 连带销毁它并丢掉待触发的 timeout。

    ``ctx`` 应当选**寿命覆盖整个延时窗口**的那个对象：延时到期前会被重建的
    控件（会被 ``deleteLater``）不能当 context，否则回调永远等不到。

    :param ctx: context 对象（定时器挂在它下面，优先传 QWidget / QObject）
    :param msec: 延迟毫秒
    :param slot: 槽
    :returns: 该定时器（需要取消时自行 ``stop()``）
    """
    timer = QTimer(ctx)
    timer.setSingleShot(True)
    timer.timeout.connect(slot)
    timer.start(int(msec))
    return timer




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

    兜住两处 ``ElaMenu`` 的坑（实测）：

    1. **非主屏上偶发不按 ``sizeHint`` 撑开**，只显示第一项。显式
       ``setMinimumSize(sizeHint())`` 可解，主屏无副作用；
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
    """绘制按钮图标和文字。

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

    PyQt5 不调用「绑定到自身」的 ``destroyed`` 槽（实测：``sip.delete()`` 下绑方法
    触发 0 次，模块级函数 / lambda 各 1 次），详见 AGENTS.md。
    """
    slot = getattr(obj, "_theme_slot", None)
    if slot is not None:
        try:
            obj._theme_connected = False
            obj._theme_slot = None
        except RuntimeError:  # 包装器已不可用
            pass
        disconnect_theme_signal(slot)


def connect_theme_signal(obj, slot: Optional[Callable[[Any], None]] = None) -> None:
    """把 ``eTheme.themeModeChanged`` 接到 ``obj`` 的主题槽并负责断开。

    供**不能继承** :class:`_ThemeAwareMixin` 的控件使用（动态定义的类、多继承基类
    不可控的第三方控件）。两条防线与 mixin 完全一致：

    1. 槽经 :func:`_make_theme_slot` 包一层（存进 ``obj._theme_slot``），并把
       **模块级** :func:`_disconnect_theme_on_destroy` 挂到 ``obj.destroyed``；
    2. 槽自身在 ``sip.isdeleted(obj)`` 时自愈断开，**不依赖 ``destroyed`` 送达**。

    :param slot: 默认为 ``obj._onThemeChanged``。签名必须能接一个模式参数
        （``def _onThemeChanged(self, mode)`` 或 ``(self, _mode=None)``）。
    """
    if slot is None:
        slot = obj._onThemeChanged
    if getattr(obj, "_theme_connected", False):
        return
    obj._theme_connected = True
    obj._theme_slot = _make_theme_slot(obj, slot)
    eTheme.themeModeChanged.connect(obj._theme_slot)
    obj.destroyed.connect(_disconnect_theme_on_destroy)


def disconnect_theme(obj) -> None:
    """主动断开 :func:`connect_theme_signal` 建立的连接（幂等）。

    **必须断 ``_theme_slot`` 而不是 ``_onThemeChanged``** —— 后者是每次属性访问都
    新建的 bound method，按身份匹配必然 ``TypeError`` 被静默吞掉，连接从未真正断开
    （原实现正是这个 bug：断开失败 + 把 ``_theme_slot`` 置 ``None`` 丢掉引用，
    之后再 ``_init_theme_aware()`` 会**叠上第二条连接**，一次主题切换触发两次）。
    """
    if not getattr(obj, "_theme_connected", False):
        return
    slot = getattr(obj, "_theme_slot", None)
    obj._theme_connected = False
    obj._theme_slot = None
    disconnect_theme_signal(slot)


def _make_theme_slot(obj, slot: Optional[Callable[[Any], None]] = None):
    """造一个「带存活检查 + 自愈断开」的主题槽。

    ``eTheme`` 是进程级单例，``themeModeChanged`` 会一直连着所有创建过的控件；
    控件销毁后包装器可能还活着，信号再发一次就打进已释放的 C++ 对象 =
    0xC0000409 静默终止。所以槽第一件事是 ``sip.isdeleted()``，命中就顺手断开 ——
    **不依赖 ``destroyed`` 一定送达**（那正是本模块的第二条防线）。
    """
    if slot is None:
        slot = obj._onThemeChanged

    def _slot(mode):
        try:
            alive = not sip.isdeleted(obj)
        except (RuntimeError, TypeError):
            alive = False
        if not alive:
            disconnect_theme_signal(_slot)
            return
        slot(mode)

    return _slot


class _ThemeAwareMixin:
    """Mixin that auto-connects theme signals and cleans up on destroy.

    Subclasses must define _onThemeChanged(self, mode) and call
    super().__init__(parent) or self._init_theme_aware().
    """

    # 类级默认值不能只有注解：``_init_theme_aware`` 在 ``__init__`` 链的最上游
    # 就要读 ``_theme_connected``，那时子类还没设过。
    _theme_connected: bool = False
    _theme_slot: object = None
    _theme_mode: ElaThemeType.ThemeMode

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_theme_aware()

    def _init_theme_aware(self) -> None:
        connect_theme_signal(self)

    def _theme_cleanup(self) -> None:
        """主动断开（供不需要等 ``destroyed`` 的场景显式调用）。"""
        disconnect_theme(self)

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

    item_h = combo_box.view().sizeHintForRow(0) if combo_box.count() else 30
    if item_h <= 0:
        item_h = 30
    n = combo_box.maxVisibleItems()
    if combo_box.count() < n:
        n = combo_box.count()
    extra_height = _popup_extra_height(container, "SearchWidget", 40)
    extra_height += _popup_extra_height(container, POPUP_FOOTER_OBJECT_NAME, 36)
    # 与 C++ showPopup 的 count() * 35 + 8 同一套算式，额外加上弹层附件
    final_height = n * item_h + 8 + extra_height

    needed_below = combo_bottom + 3 + final_height

    if needed_below > screen_geo.bottom():
        new_y = combo_top - 3 - final_height
        if new_y >= screen_geo.top():
            container.move(container.x(), new_y)
        else:
            # 上方也不够 → 压缩高度
            max_h = combo_top - 3 - screen_geo.top()
            if max_h > 50:
                container.setFixedHeight(int(max_h))
                container.move(container.x(), screen_geo.top())
