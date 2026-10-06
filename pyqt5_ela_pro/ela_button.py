"""
统一按钮组件，风格参考 Ant Design Button。

支持 6 种变体 (outlined/dashed/solid/filled/text/link)、
16 种色彩主题以及深色/浅色主题自适应。

用法::

    from pyqt5_ela_pro import ElaButton
    from PyQt5ElaWidgetTools import ElaIconType

    btn = ElaButton("提交", variant="solid", color="primary", parent=self)
    btn = ElaButton("编辑", variant="outlined", icon=ElaIconType.IconName.Pencil, parent=self)
    btn = ElaButton("删除", variant="solid", danger=True, parent=self)
"""

from __future__ import annotations

import warnings
from typing import Literal, Optional

from PyQt5.QtCore import Qt, QRect, QRectF, QSize, QTimer, QVariantAnimation
from PyQt5.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPen,
    QPaintEvent,
    QEnterEvent,
)
from PyQt5.QtWidgets import QPushButton, QWidget

from PyQt5ElaWidgetTools import eApp, eTheme, ElaThemeType, ElaIcon, ElaIconType

from ._internal import _ThemeAwareMixin
from ._colors import get_color_scheme
from ._motion import Duration, start_idle_loop, start_transition
from ._styles import paintOverlayShadow
from ._theme import accent as theme_accent, blend
from .svg_icon import svg_icon_loader, svg_to_pixmap


# ── Type aliases ─────────────────────────────────────────────

ElaButtonVariant = Literal["outlined", "dashed", "solid", "filled", "text", "link"]
ElaButtonColor = Literal[
    "default",
    "primary",
    "danger",
    "blue",
    "purple",
    "cyan",
    "green",
    "magenta",
    "pink",
    "red",
    "orange",
    "yellow",
    "volcano",
    "geekblue",
    "lime",
    "gold",
]
ElaButtonSize = Literal["small", "middle", "large"]


# ── Size presets ─────────────────────────────────────────────

#: 可见按钮面的阴影边距（px）。与上游 ``ElaPushButton`` 的 ``_shadowBorderWidth``
#: 同值：控件高 38 → 可见面 32，两种按钮混排时高度一致。
_SHADOW_MARGIN = 3

#: ``fontDelta`` 是相对 ``eApp.getFontPixelSize()`` 的偏移；middle 与上游
#: ``ElaPushButton``（``eApp + 2``）一致。
#: 高度 30/38/46 → 可见面 24/32/40（对齐 Ant Design 与上游 ElaPushButton）。
_SIZE_MAP: dict[str, dict[str, int]] = {
    "small": {
        "height": 30,
        "fontDelta": 0,
        "paddingH": 12,
        "iconSize": 14,
        "radius": 4,
    },
    "middle": {
        "height": 38,
        "fontDelta": 2,
        "paddingH": 16,
        "iconSize": 16,
        "radius": 6,
    },
    "large": {
        "height": 46,
        "fontDelta": 4,
        "paddingH": 20,
        "iconSize": 18,
        "radius": 8,
    },
}


# ── ElaButton ────────────────────────────────────────────────


class ElaButton(_ThemeAwareMixin, QPushButton):
    """统一风格按钮组件。

    支持 6 种变体、16 种色彩主题、3 种尺寸，自动适配深浅色主题。
    尺寸与上游 ``ElaPushButton`` 对齐：可见按钮面内缩 3px 阴影边距
    （控件高 38 → 面 32），middle 字号 = ``eApp.getFontPixelSize() + 2``。

    :param text: 按钮文本
    :param icon: 图标名称 (ElaIconType.IconName)
    :param iconSize: 图标大小，默认 16
    :param variant: 变体样式
    :param color: 色彩主题
    :param danger: 是否使用危险色（覆盖 color 参数）
    :param size: 尺寸规格
    :param parent: 父控件
    """

    def __init__(
        self,
        text: Optional[str] = None,
        icon: Optional[ElaIconType.IconName] = None,
        iconSize: int = 16,
        variant: ElaButtonVariant = "outlined",
        color: ElaButtonColor = "default",
        danger: bool = False,
        size: ElaButtonSize = "middle",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self._variant = variant
        self._color_name = color
        self._danger = danger
        self._border_radius = 6
        self._padding_h = 16
        self._size_height = 38
        self._icon_name: Optional[ElaIconType.IconName] = icon
        self._icon_size = iconSize
        #: SVG 图标源：SVG 源码字符串，或 :class:`ElaSvgIconLoader` 里的图标名
        #: （二选一，见 :meth:`setSvgIcon`）。非 ``None`` 时**压过** ``_icon_name``。
        self._svg_source: Optional[str] = None
        self._svg_is_name: bool = False
        self._hovered = False
        self._focus_ring = False
        self._loading = False
        self._spin_angle = 0
        self._hover_t = 0.0

        if text:
            self.setText(text)

        self._theme_mode = eTheme.getThemeMode()
        self._hover_anim = QVariantAnimation(self)
        self._hover_anim.valueChanged.connect(self._onHoverValue)
        self._spin_timer = QTimer(self)
        self._spin_timer.timeout.connect(self._onSpinTick)
        self._apply_size(size)

    # ── Public API ────────────────────────────────────────

    def setVariant(self, variant: ElaButtonVariant) -> None:
        """设置按钮变体样式。

        :param variant: 变体，可选 ``"outlined"`` / ``"dashed"`` / ``"solid"`` / ``"filled"`` / ``"text"`` / ``"link"``
        """
        self._variant = variant
        self.update()

    def variant(self) -> str:
        """获取当前变体样式。

        :returns: 变体名称
        """
        return self._variant

    def setColor(self, color: ElaButtonColor) -> None:
        """设置色彩主题。

        :param color: 色彩名称（如 ``"primary"`` / ``"danger"`` / ``"blue"`` 等 16 种）
        """
        self._color_name = color
        self.update()

    def color(self) -> str:
        """获取当前色彩主题。

        :returns: 色彩名称
        """
        return self._color_name

    def setDanger(self, danger: bool) -> None:
        """设置是否启用危险模式（覆盖 ``color`` 参数）。

        :param danger: 是否启用危险色
        """
        self._danger = danger
        self.update()

    def isDanger(self) -> bool:
        """当前是否为危险模式。

        :returns: 危险模式状态
        """
        return self._danger

    def setButtonSize(self, size: ElaButtonSize) -> None:
        """设置按钮尺寸。

        :param size: 尺寸，可选 ``"small"`` / ``"middle"`` / ``"large"``
        """
        self._apply_size(size)
        self.update()

    def buttonSize(self) -> str:
        """获取当前按钮尺寸。

        :returns: 尺寸名称
        """
        h = self.height()
        for name, cfg in _SIZE_MAP.items():
            if cfg["height"] == h:
                return name
        return "middle"

    def setElaIcon(self, iconName: ElaIconType.IconName, iconSize: int = 16) -> None:
        """设置按钮图标（ElaAwesome 图标）。

        :param iconName: ElaAwesome 图标名称
        :param iconSize: 图标像素大小，默认 16
        """
        self._icon_name = iconName
        self._icon_size = iconSize
        self._svg_source = None
        self.setIconSize(QSize(iconSize, iconSize))
        self.updateGeometry()
        self.update()

    def setSvgIcon(self, source: str, iconSize: Optional[int] = None) -> bool:
        """设置 **第三方 SVG** 图标，颜色跟随当前主题（文字色 / 禁用色）。

        这是本库唯一能在按钮里放非 ElaAwesome 图标的入口 —— 其余按钮
        （``ElaProgressButton`` / ``ElaChatToolButton`` / 上游 ``ElaPushButton``）
        只认 ``ElaIconType.IconName`` 枚举，而 :meth:`setIcon` 在本控件上是
        **静默无效**的（本控件自绘，只读 ``_icon_name`` / ``_svg_source``）。

        ``source`` 两种形态自动判别：

        * **SVG 源码**（含 ``<svg``）→ 直接渲染；
        * **图标名** → 去 :func:`svg_icon_loader` 里取，宿主需先
          ``svg_icon_loader().loadFromFile(...)`` 加载自己的图标包（本库不
          自带图标集）。

        SVG 里的 ``<<<COLOR_CODE>>>`` 占位符会被替换成当前主题文字色，所以
        多色图标请用占位符标出该跟随主题的部分。

        与 :meth:`setElaIcon` **互斥**：设了 SVG 就清掉 ElaAwesome 图标，反之
        亦然（不这样做会两套图标语义并存、谁生效说不清）。

        :param source: SVG 源码字符串，或图标包里的图标名
        :param iconSize: 图标像素大小，默认沿用当前值（16）
        :returns: 图标名形态且图标包里**找不到**该名字时返回 ``False``
            （此时只画文字，并已 ``warnings.warn`` 一次 —— 静默少一个图标会
            让用户去查图标名，而不是查「图标包没加载」）
        """
        self._svg_source = source or None
        self._svg_is_name = bool(source) and "<svg" not in source
        if iconSize is not None:
            self._icon_size = iconSize
        self._icon_name = None
        found = True
        if self._svg_is_name:
            found = svg_icon_loader().hasIcon(source)
            if not found:
                warnings.warn(
                    f"图标名 {source!r} 在已加载的图标包里不存在"
                    "（svg_icon_loader().loadFromFile(...) 加载过吗？）—— 只画文字。",
                    RuntimeWarning,
                    stacklevel=2,
                )
        self.setIconSize(QSize(self._icon_size, self._icon_size))
        self.updateGeometry()
        self.update()
        return found

    def clearSvgIcon(self) -> None:
        """清掉 SVG 图标（回到无图标状态）。"""
        self._svg_source = None
        self._svg_is_name = False
        self.updateGeometry()
        self.update()

    def svgIcon(self) -> Optional[str]:
        """当前 SVG 图标源（``None`` 表示没设）。"""
        return self._svg_source

    def setIcon(self, icon) -> None:  # noqa: N802 (Qt 命名)
        """**本控件不支持** ``QPushButton.setIcon``，调用只会静默失效。

        ``paintEvent`` 只读 ``_icon_name`` / ``_svg_source``，``QPushButton``
        自己那套 ``icon()`` 根本不参与绘制。这里覆写成警告，避免「设了没反应」
        这种最难查的失败。

        :raises RuntimeError: 恒定抛出，消息里给出正确入口
        """
        del icon
        raise RuntimeError(
            "ElaButton 自绘，不支持 QPushButton.setIcon（会静默不画）。"
            "请用 setElaIcon(ElaIconType.IconName) 放 ElaAwesome 图标，"
            "或 setSvgIcon(svg源码或图标名) 放第三方 SVG。"
        )

    def setBorderRadius(self, radius: int) -> None:
        """设置圆角半径。

        :param radius: 圆角半径（像素）
        """
        self._border_radius = radius
        self.update()

    def borderRadius(self) -> int:
        """获取圆角半径。

        :returns: 圆角半径（像素）
        """
        return self._border_radius

    # ── Internal ──────────────────────────────────────────

    def _apply_size(self, size: ElaButtonSize) -> None:
        cfg = _SIZE_MAP[size]
        self._padding_h = cfg["paddingH"]
        self._size_height = cfg["height"]
        self._border_radius = cfg["radius"]
        self.setFixedHeight(cfg["height"])
        font = self.font()
        # 字号跟随 eApp（与上游 ElaPushButton 的 eApp + 2 同源），不再写死 12/14/16
        font.setPixelSize(eApp.getFontPixelSize() + cfg["fontDelta"])
        self.setFont(font)
        self.updateGeometry()
        self.update()

    def sizeHint(self) -> QSize:
        """按文字 / 图标与内边距计算合适宽度（不再依赖样式默认值）。

        宽度是**控件**宽度：可见按钮面还要内缩 ``_SHADOW_MARGIN``（与上游
        ``ElaPushButton`` 的阴影边距一致），所以面宽 = 控件宽 − 2×margin。
        """
        fm = self.fontMetrics()
        face_width = fm.horizontalAdvance(self.text())
        if self._icon_name is not None or self._svg_source or self._loading:
            face_width += self._icon_size + (8 if self.text() else 0)
        face_width += 2 * self._padding_h
        return QSize(max(64, face_width) + 2 * _SHADOW_MARGIN, self._size_height)

    def minimumSizeHint(self) -> QSize:
        return QSize(
            max(48, 2 * self._padding_h) + 2 * _SHADOW_MARGIN, self._size_height
        )

    def _svg_pixmap_for_paint(self, color: QColor):
        """按当前文字色渲染 SVG 图标；取不到时返回 ``None``（只画文字）。

        绘制路径上**绝不能**让异常穿出去（``paintEvent`` 在 Qt 回调链里，
        未捕获异常 = 0xC0000409 静默终止）。所以三道全兜住：图标名找不到
        （``getSvgData`` 会抛 ``KeyError``）、SVG 语法错、渲染出空图。
        """
        source = self._svg_source
        if not source:
            return None
        size = self._icon_size
        try:
            if self._svg_is_name:
                data = svg_icon_loader().getSvgData(source, color.name())
            else:
                data = source
            pixmap = svg_to_pixmap(data, size, color.name())
        except Exception:  # noqa: BLE001 —— paintEvent 里必须全兜
            return None
        return None if pixmap.isNull() else pixmap

    def _effective_color(self) -> str:
        return "danger" if self._danger else self._color_name

    def _is_dark(self) -> bool:
        return self._theme_mode == ElaThemeType.ThemeMode.Dark

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    # ── Color helpers ─────────────────────────────────────

    def _neutral_text(self) -> QColor:
        """Default text color for 'default' color in neutral situations."""
        return QColor(0xE0, 0xE0, 0xE0) if self._is_dark() else QColor(0x1F, 0x1F, 0x1F)

    def _neutral_border(self) -> QColor:
        """Gray border for 'default' outlined normal state (ElaPushButton 风格)."""
        return eTheme.getThemeColor(self._theme_mode, ElaThemeType.BasicBorder)

    def _disabled_bg(self) -> QColor:
        return eTheme.getThemeColor(
            self._theme_mode, ElaThemeType.ThemeColor.BasicDisable
        )

    def _disabled_text(self) -> QColor:
        return eTheme.getThemeColor(
            self._theme_mode, ElaThemeType.ThemeColor.BasicTextDisable
        )

    def _disabled_border(self) -> QColor:
        return self._neutral_border()

    def _hover_tint(self) -> QColor:
        """状态层：hover ≈ 8%（暗色叠白 / 亮色叠黑）。"""
        return QColor(255, 255, 255, 20) if self._is_dark() else QColor(0, 0, 0, 20)

    def _pressed_tint(self) -> QColor:
        """状态层：press ≈ 12%。"""
        return QColor(255, 255, 255, 31) if self._is_dark() else QColor(0, 0, 0, 31)

    def _scheme(self) -> dict[str, QColor]:
        return get_color_scheme(self._effective_color(), self._theme_mode)

    def _state_colors(
        self, scheme: dict[str, QColor], hovered: bool, pressed: bool
    ) -> tuple:
        """某状态下的 ``(底, 描边, 文字)``；描边为 ``None`` 表示不画。

        彩色变体的文字一律走 ``accentText``（浅底上的可读档，对比度 ≥ 4.5），
        ``accent`` 只用于填充 / 描边。
        """
        variant = self._variant
        is_default = self._effective_color() == "default"
        transparent = QColor(0, 0, 0, 0)
        if variant == "solid":
            bg = (
                scheme["solidActive"]
                if pressed
                else (scheme["solidHover"] if hovered else scheme["solid"])
            )
            return bg, None, scheme["solidText"]
        if variant in ("outlined", "dashed"):
            if is_default:
                bg = self._hover_tint() if (hovered or pressed) else transparent
                return bg, self._neutral_border(), self._neutral_text()
            bg = scheme["accentBgHover"] if (hovered or pressed) else scheme["accentBg"]
            border = QColor(scheme["accent"])
            border.setAlpha(110 if not self._is_dark() else 150)
            return bg, border, scheme["accentText"]
        if variant == "filled":
            bg = scheme["accentBgHover"] if (hovered or pressed) else scheme["accentBg"]
            return bg, None, scheme["accentText"]
        if variant == "text":
            bg = (
                self._pressed_tint()
                if pressed
                else (self._hover_tint() if hovered else transparent)
            )
            return (
                bg,
                None,
                scheme["accentText"] if not is_default else self._neutral_text(),
            )
        if variant == "link":
            return (
                transparent,
                None,
                scheme["accentText"] if not is_default else self._neutral_text(),
            )
        return transparent, None, self._neutral_text()

    # ── Events ────────────────────────────────────────────

    def enterEvent(self, event: QEnterEvent) -> None:
        self._hovered = True
        self._fade_hover(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hovered = False
        self._fade_hover(0.0)
        super().leaveEvent(event)

    def focusInEvent(self, event) -> None:
        """键盘聚焦（Tab / Shift+Tab / 快捷键）才显示 focus ring。"""
        self._focus_ring = event.reason() in (
            Qt.FocusReason.TabFocusReason,
            Qt.FocusReason.BacktabFocusReason,
            Qt.FocusReason.ShortcutFocusReason,
        )
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:
        self._focus_ring = False
        self.update()
        super().focusOutEvent(event)

    def mousePressEvent(self, event) -> None:
        if self._loading:
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._loading:
            event.accept()
            return
        super().mouseReleaseEvent(event)

    # ── Motion / loading ──────────────────────────────────

    def _onHoverValue(self, value) -> None:  # noqa: ANN001
        self._hover_t = float(value)
        self.update()

    def _fade_hover(self, target: float) -> None:
        anim = self._hover_anim
        anim.stop()
        anim.setStartValue(self._hover_t)
        anim.setEndValue(float(target))
        start_transition(anim, Duration.Fast)

    def _onSpinTick(self) -> None:
        self._spin_angle = (self._spin_angle + 30) % 360
        self.update()

    def setLoading(self, loading: bool = True) -> None:  # noqa: N802 (Qt 命名)
        """加载态：左侧显示旋转指示器，期间不响应点击。

        :param loading: 是否进入加载态
        """
        if loading == self._loading:
            return
        self._loading = loading
        if loading:
            start_idle_loop(self._spin_timer, 33)
        else:
            self._spin_timer.stop()
        self.updateGeometry()
        self.update()

    def isLoading(self) -> bool:  # noqa: N802 (Qt 命名)
        """当前是否处于加载态。

        :returns: 加载态
        """
        return self._loading

    # ── Paint ─────────────────────────────────────────────

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

            w = self.width()
            h = self.height()
            # 可见按钮面：与上游 ElaPushButton 一样留出阴影边距（控件高 38 → 面 32）
            fw = w - 2 * _SHADOW_MARGIN
            fh = h - 2 * _SHADOW_MARGIN
            br = self._border_radius

            disabled = not self.isEnabled()
            pressed = self.isDown()
            hovered = self._hovered
            variant = self._variant
            cname = self._effective_color()
            is_default = cname == "default"
            scheme = self._scheme()

            # 阴影与上游同款；text / link 没有面，画阴影会像悬空的框
            if variant not in ("text", "link"):
                paintOverlayShadow(
                    painter, self.rect(), margin=_SHADOW_MARGIN, radius=br
                )

            path = QPainterPath()
            path.addRoundedRect(
                QRectF(
                    _SHADOW_MARGIN + 0.5,
                    _SHADOW_MARGIN + 0.5,
                    fw - 1.0,
                    fh - 1.0,
                ),
                br,
                br,
            )

            # -- Resolve background / border / text color --
            # 彩色文字一律走 accentText（可读档）；hover 用 _hover_t 在两套状态
            # 色之间插值（150ms 淡入淡出，Reduced/Disabled 下同步落终值）。
            if disabled:
                bg = (
                    Qt.GlobalColor.transparent
                    if variant in ("text", "link")
                    else self._disabled_bg()
                )
                text_color = self._disabled_text()
                border_color = (
                    self._disabled_border()
                    if variant in ("outlined", "dashed")
                    else None
                )
            else:
                bg0, border0, text_color = self._state_colors(scheme, False, False)
                if pressed:
                    bg, border_color = self._state_colors(scheme, True, True)[:2]
                else:
                    bg1, border1, _ = self._state_colors(scheme, True, False)
                    t = self._hover_t
                    bg = blend(bg0, bg1, t)
                    if border0 is not None and border1 is not None:
                        border_color = blend(border0, border1, t)
                    else:
                        border_color = border0 if border0 is not None else border1

            border_pen = None
            if border_color is not None:
                border_pen = QPen(border_color, 1)
                if variant == "dashed":
                    border_pen.setStyle(Qt.PenStyle.DashLine)

            painter.setBrush(bg)
            painter.setPen(border_pen if border_pen is not None else Qt.PenStyle.NoPen)
            painter.drawPath(path)

            # -- Focus ring（键盘可见性）--
            if self._focus_ring:
                ring_color = (
                    theme_accent(self._theme_mode)
                    if is_default
                    else QColor(scheme["accent"])
                )
                ring_pen = QPen(ring_color, 2)
                ring_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(ring_pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(
                    QRectF(
                        _SHADOW_MARGIN - 1.0,
                        _SHADOW_MARGIN - 1.0,
                        fw + 2.0,
                        fh + 2.0,
                    ),
                    br + 2.0,
                    br + 2.0,
                )

            # -- Draw icon / spinner + text --
            painter.setPen(text_color)
            icon_name = self._icon_name
            loading = self._loading
            btn_text = self.text()
            svg_pixmap = None if loading else self._svg_pixmap_for_paint(text_color)
            if icon_name is not None or loading or svg_pixmap is not None:
                spacing = 8
                icon_sz = QSize(self._icon_size, self._icon_size)
                fm = painter.fontMetrics()
                tw = fm.horizontalAdvance(btn_text) if btn_text else 0
                if tw:
                    total_w = icon_sz.width() + spacing + tw
                    sx = _SHADOW_MARGIN + (fw - total_w) // 2
                else:
                    # 纯图标按钮：只居中图标本身（含 spacing 会向左偏）
                    sx = _SHADOW_MARGIN + (fw - icon_sz.width()) // 2
                iy = _SHADOW_MARGIN + (fh - icon_sz.height()) // 2
                ir = QRect(sx, iy, icon_sz.width(), icon_sz.height())
                if loading:
                    spin_pen = QPen(text_color, 2)
                    spin_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                    painter.setPen(spin_pen)
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.drawArc(QRectF(ir), self._spin_angle * 16, 270 * 16)
                    painter.setPen(text_color)
                elif svg_pixmap is not None:
                    painter.drawPixmap(ir, svg_pixmap)
                else:
                    icon = ElaIcon.getInstance().getElaIcon(icon_name, text_color)
                    painter.drawPixmap(ir, icon.pixmap(icon_sz))
                if tw:
                    tr = QRect(ir.right() + spacing, _SHADOW_MARGIN, tw, fh)
                    painter.drawText(
                        tr,
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                        btn_text,
                    )
                    if variant == "link" and hovered and not disabled:
                        underline_y = ir.center().y() + fm.ascent() // 2 + 2
                        painter.setPen(QPen(text_color, 1))
                        painter.drawLine(
                            tr.left(), underline_y, tr.left() + tw, underline_y
                        )
            else:
                painter.drawText(
                    QRect(_SHADOW_MARGIN, _SHADOW_MARGIN, fw, fh),
                    Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                    btn_text,
                )
                if variant == "link" and hovered and not disabled:
                    fm = painter.fontMetrics()
                    tw = fm.horizontalAdvance(btn_text)
                    tx = _SHADOW_MARGIN + (fw - tw) // 2
                    ty = _SHADOW_MARGIN + fh // 2 + fm.ascent() // 2 + 2
                    painter.setPen(QPen(text_color, 1))
                    painter.drawLine(tx, ty, tx + tw, ty)
        finally:
            painter.end()
