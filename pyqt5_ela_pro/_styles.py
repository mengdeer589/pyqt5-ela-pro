"""
共用样式 / 自绘原语（内部模块，不作为公共 API 暴露）。

``EditBorderlessStyle``：共享 ``QProxyStyle``（去掉 Ela 输入框原生的自绘边框）。

其余部分是**库内禁 QSS** 的替代件：需要「非主题色文字 / 纯色底 / 透明底 / 圆角
卡片」时用这里的控件或 helper，不要再写 ``setStyleSheet``。

为什么 ``ElaText`` 必须换成 :class:`ColorText` 才能上色：``ElaText::paintEvent``
开头就检查 ``palette().color(WindowText) != ElaThemeColor(mode, BasicText)``，不等
就调 ``onThemeChanged(mode)`` **把 palette 改回主题色** —— 所以 palette / QSS 之外
的方式对 ``ElaText`` 无效，历史代码才到处写 ``QSS color:``。:class:`ColorText`
在有显式颜色时直接走 ``QLabel::paintEvent``，不经那次重置。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import QRectF, QSize, Qt
from PyQt5.QtGui import QColor, QIcon, QPainter, QPalette, QPen
from PyQt5.QtWidgets import (
    QFrame,
    QLabel,
    QProxyStyle,
    QPushButton,
    QStyle,
    QToolButton,
    QWidget,
)
from PyQt5ElaWidgetTools import ElaText


class EditBorderlessStyle(QProxyStyle):
    """去掉 ``ElaPlainTextEdit`` 原生自绘边框的代理样式。

    ``ElaPlainTextEditStyle`` 在 ``CE_ShapedFrame`` 里画 1px 边框 + 底色 + 底部
    粗线 + 聚焦展开条；由外层容器接管这些视觉时跳过该元素即可。注意
    ``setFrameShape(NoFrame)`` **单独无效** —— 原生 style 不看 frameShape，
    必须换掉 style。

    典型用法（**必须**走 :func:`editBorderlessStyle`，不要直接实例化）::

        edit = ElaPlainTextEdit(parent)
        edit.setStyle(editBorderlessStyle())
        edit.setFrameShape(QFrame.Shape.NoFrame)   # 冗余但无害
    """

    def drawControl(  # noqa: N802 (Qt 命名)
        self, element, option, painter, widget=None
    ) -> None:
        """跳过框架绘制，其余控件元素透传给原生样式。"""
        if element == QStyle.ControlElement.CE_ShapedFrame:
            return
        super().drawControl(element, option, painter, widget)


#: 共享的无边框样式实例（进程级，见 :func:`editBorderlessStyle` 的说明）
_EDIT_BORDERLESS_STYLE: Optional[EditBorderlessStyle] = None


def editBorderlessStyle() -> EditBorderlessStyle:  # noqa: N802 (Qt 命名)
    """取共享的无边框代理样式（**进程级单例**）。

    **不要给每个控件各建一个** —— ``QWidget.setStyle()`` 不接管所有权，唯一
    的持有者只能是 Python 引用：引用一消失（控件销毁，或干脆没保存），sip 就
    会 delete 掉这个 ``QProxyStyle``，而 Qt 的样式解析链（``QStyleSheetStyle``
    / app style 缓存）**仍持有它的指针**。此后任意控件重绘时就会解引用已释放
    的内存 → 进程 access violation（0xC0000005，无 traceback）。

    实测踩坑路径：销毁一个带此 style 的输入区（``chat/input.py``）后，紧接着
    渲染 200 条聊天消息必崩；把该 style 额外存进一个长生命周期列表就不崩。

    样式本身无状态（只覆写 ``drawControl`` 跳过 ``CE_ShapedFrame``），全局共享
    一个实例没有任何副作用。
    """
    global _EDIT_BORDERLESS_STYLE
    if _EDIT_BORDERLESS_STYLE is None:
        _EDIT_BORDERLESS_STYLE = EditBorderlessStyle()
    return _EDIT_BORDERLESS_STYLE


# ── 禁 QSS 原语：底色 / 边框 ──────────────────────────────────────────────


def setSolidBackground(widget: QWidget, color) -> None:  # noqa: N802 (Qt 命名)
    """给普通控件铺纯色底（palette ``Window`` + 自动填充），替代 QSS ``background-color``。"""
    widget.setAutoFillBackground(True)
    palette = widget.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor(color))
    widget.setPalette(palette)
    widget.update()


def setPlainFrame(widget, background, border) -> None:  # noqa: N802 (Qt 命名)
    """给 ``QFrame`` 套「1px 实线描边 + 纯色底」，替代 QSS ``background + border``。

    ``QFrame`` 的 ``Plain`` 描边用 palette ``WindowText`` 画、底色用 ``Window`` ——
    实测 1px 线正好落在设备像素上（与 QSS ``border: 1px solid`` 观感一致）。
    """
    widget.setFrameShape(QFrame.Shape.Box)
    widget.setFrameShadow(QFrame.Shadow.Plain)
    setSolidBackground(widget, background)
    palette = widget.palette()
    palette.setColor(QPalette.ColorRole.WindowText, QColor(border))
    widget.setPalette(palette)


def setTextColor(widget: QWidget, color) -> None:  # noqa: N802 (Qt 命名)
    """给普通控件（``QLabel`` 等）设文字色（palette ``WindowText``），替代 QSS ``color:``。

    **不适用于 ``ElaText``** —— 它会在 paint 时把 palette 重置回主题色（见模块
    docstring），那类控件要用 :class:`ColorText` / 它的 ``setTextColor()``。
    """
    palette = widget.palette()
    palette.setColor(QPalette.ColorRole.WindowText, QColor(color))
    widget.setPalette(palette)
    widget.update()


def setTransparentTextBase(widget: QWidget) -> None:  # noqa: N802 (Qt 命名)
    """把文本类控件（``QTextBrowser`` / ``QTextEdit``）的底色设为透明。

    等价于 QSS ``QTextBrowser { background-color: transparent; }``：把 palette 的
    ``Base``（``QAbstractScrollArea`` 视口的背景角色）设成透明刷，并关掉视口的
    自动填充 —— 控件本体不加 ``WA_TranslucentBackground``，父级背景照常透出。
    """
    palette = widget.palette()
    palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.transparent)
    widget.setPalette(palette)
    viewport = widget.viewport() if hasattr(widget, "viewport") else None
    if viewport is not None:
        viewport.setAutoFillBackground(False)
    widget.update()


def paintRoundedCard(
    painter: QPainter,
    rect,
    *,
    background: Optional[QColor] = None,
    border: Optional[QColor] = None,
    radius: float = 6.0,
    glow: Optional[QColor] = None,
) -> None:
    """画「圆角卡片」（底 + 可选 1px 描边 + 可选外发光），替代 QSS。

    无描边时底铺满 ``rect``；有描边时整体内缩半像素，保证 1px 线落在设备像素上
    不糊。颜色为 ``None`` / 全透明则跳过对应绘制。

    :param glow: 描边之外再画一圈**向外**的 1px 半透明色（选中态用），画在底与
        描边之后。opencode 的选中卡片就是「底变色 + 描边透明 + 外发光」三件套
        （``--shadow-xs-border-hover``），QSS 表达不了外发光，故自绘。
    """
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    if border is not None and QColor(border).alpha():
        box = QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5)
    else:
        box = QRectF(rect)
    if background is not None and QColor(background).alpha():
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(background))
        painter.drawRoundedRect(box, radius, radius)
    if glow is not None and QColor(glow).alpha():
        pen = QPen(QColor(glow))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        outer = box.adjusted(-1.0, -1.0, 1.0, 1.0)
        painter.drawRoundedRect(outer, radius + 1.0, radius + 1.0)
    if border is not None and QColor(border).alpha():
        pen = QPen(QColor(border))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(box, radius, radius)
    painter.restore()


# ── 禁 QSS 原语：控件 ────────────────────────────────────────────────────


class ColorText(ElaText):
    """``ElaText`` 的「显式文字色」版本（禁 QSS 后的上色正路）。

    ``ElaText`` 没有颜色 API，且 paint 时会把 palette 重置回主题 ``BasicText``
    （见模块 docstring），所以历史上只能靠 ``QSS color:``。本子类在设置了显式
    颜色后改为直接走 ``QLabel::paintEvent``（用我们设的 palette 上色）；图标模式
    / wrap-anywhere 两种特例仍交回 ``ElaText`` 原实现。

    颜色是**快照**：主题切换时各组件照旧在自己的 ``_apply_theme()`` 里重新
    ``setTextColor(...)`` 刷新即可（与原来重设 QSS 的时机一致）。
    """

    def __init__(self, *args) -> None:
        # ElaText 有 ``(parent)`` / ``(text, parent)`` / ``(text, height, parent)``
        # 三个重载，这里原样透传，别自己解释参数。
        super().__init__(*args)
        self._text_color: Optional[QColor] = None

    def setTextColor(self, color) -> None:  # noqa: N802 (Qt 命名)
        """设置文字色；``None`` 还原为 ``ElaText`` 的主题色行为。"""
        self._text_color = None if color is None else QColor(color)
        if self._text_color is not None:
            self._apply_text_color()
        self.update()

    def textColor(self) -> Optional[QColor]:  # noqa: N802 (Qt 命名)
        """当前显式文字色（未设置时为 ``None``）。"""
        return None if self._text_color is None else QColor(self._text_color)

    def setTextWeight(self, weight) -> None:  # noqa: N802 (Qt 命名)
        """设置字重（替代 QSS ``font-weight``）；传 ``QFont.Weight`` 或 0-99 数值。"""
        font = self.font()
        font.setWeight(weight)
        self.setFont(font)

    def _apply_text_color(self) -> None:
        """把显式文字色写进 palette 的**前景色角色**。

        **必须写 ``foregroundRole()`` 而不是写死 ``WindowText``。**
        ``foregroundRole`` 是 per-widget 的属性，而 Ela 的控件树里同一个
        ``ColorText`` 可能拿到各种值（实测 ``_CollapsibleBlock`` 里的标题标签是
        ``8 = ButtonText``）。写死 ``WindowText`` 时 ``textColor()`` 读回来是对的、
        ``palette().color(WindowText)`` 也是对的，唯独绘制走的 ``foregroundRole()``
        仍是主题的 BasicText —— 表现就是**设了颜色却画成黑字**，而且完全没有报错。
        """
        if self._text_color is None:
            return
        palette = self.palette()
        palette.setColor(self.foregroundRole(), self._text_color)
        self.setPalette(palette)

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt 命名)
        if self._text_color is None or self.getElaIcon() or self.getIsWrapAnywhere():
            super().paintEvent(event)
            return
        # ElaText 自己在 C++ 构造里连了 eTheme.themeModeChanged → onThemeChanged，
        # 主题信号一发就把 palette 刷回 BasicText（父容器 _apply_theme 与它的连接
        # 顺序不保证），所以绘制前补一次显式颜色 —— 相等时直接跳过，不会反复触发。
        palette = self.palette()
        if palette.color(self.foregroundRole()) != self._text_color:
            palette.setColor(self.foregroundRole(), self._text_color)
            self.setPalette(palette)
        QLabel.paintEvent(self, event)


class BareButton(QPushButton):
    """只当「可点行容器」用的按钮：什么都不自绘（替代 QSS ``background: transparent; border: none;``）。

    用于头部 / 折叠行这类「按钮当布局容器、内容全是子控件」的场景 ——
    ``setFlat(True)`` 仍会画悬浮 / 按下底色，不符原视觉，故整体跳过绘制。
    """

    def paintEvent(self, _event) -> None:  # noqa: N802 (Qt 命名)
        """不画任何东西（子控件照常绘制）。"""


class FlatIconButton(QToolButton):
    """透明底 + 圆角悬浮 / 按下底色的图标按钮（替代 ``QToolButton`` 的 QSS 写法）。

    QToolButton 默认由 style 画边框与凸起底，以前用
    ``QSS QToolButton { background: transparent; border: none; border-radius: 6px; }``
    压掉、再用 ``:hover`` / ``:pressed`` 给底色。这里改为自己画：平时不画底，
    悬浮 / 按下时画 ``setHoverColor`` / ``setPressColor`` 指定的圆角底，图标沿用
    ``setIcon`` 传入的 ``QIcon``（按 ``iconSize`` 请求，交给 Qt 处理设备像素比）。
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._hover_color = QColor(0, 0, 0, 0)
        self._press_color = QColor(0, 0, 0, 0)
        self._corner_radius = 6.0

    def setHoverColor(self, color) -> None:  # noqa: N802 (Qt 命名)
        """悬浮底色（``QColor`` / hex 串；全透明表示不画底）。"""
        self._hover_color = QColor(color)
        self.update()

    def hoverColor(self) -> QColor:  # noqa: N802 (Qt 命名)
        """悬浮底色。"""
        return QColor(self._hover_color)

    def setPressColor(self, color) -> None:  # noqa: N802 (Qt 命名)
        """按下底色。"""
        self._press_color = QColor(color)
        self.update()

    def pressColor(self) -> QColor:  # noqa: N802 (Qt 命名)
        """按下底色。"""
        return QColor(self._press_color)

    def setCornerRadius(self, radius: float) -> None:  # noqa: N802 (Qt 命名)
        """圆角半径（px）。"""
        self._corner_radius = float(radius)
        self.update()

    def cornerRadius(self) -> float:  # noqa: N802 (Qt 命名)
        """圆角半径（px）。"""
        return self._corner_radius

    def paintEvent(self, _event) -> None:  # noqa: N802 (Qt 命名)
        """只画悬浮 / 按下底色与居中图标。"""
        painter = QPainter(self)
        rect = QRectF(self.rect())
        if self.isDown() and self._press_color.alpha():
            paintRoundedCard(
                painter, rect, background=self._press_color, radius=self._corner_radius
            )
        elif self.underMouse() and self._hover_color.alpha():
            paintRoundedCard(
                painter, rect, background=self._hover_color, radius=self._corner_radius
            )
        icon = self.icon()
        if icon.isNull():
            return
        if not self.isEnabled():
            mode = QIcon.Mode.Disabled
        elif self.isDown() or self.underMouse():
            mode = QIcon.Mode.Active
        else:
            mode = QIcon.Mode.Normal
        # PyQt5 的 QIcon.pixmap 没有 devicePixelRatio 重载（只有 QWindow* 版，且
        # 控件没显示时拿不到 windowHandle），所以按物理尺寸请求位图、再缩到逻辑
        # 尺寸画 —— 高 DPI 下比「请求逻辑尺寸后放大」清晰。
        size = self.iconSize()
        ratio = self.devicePixelRatioF()
        physical = QSize(
            max(1, round(size.width() * ratio)), max(1, round(size.height() * ratio))
        )
        pixmap = icon.pixmap(physical, mode)
        target = QRectF(
            (rect.width() - size.width()) / 2.0,
            (rect.height() - size.height()) / 2.0,
            size.width(),
            size.height(),
        )
        painter.drawPixmap(target, pixmap, QRectF(pixmap.rect()))
