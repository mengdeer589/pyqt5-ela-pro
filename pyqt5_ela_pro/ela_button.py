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

from typing import Optional, Literal

from PyQt5.QtCore import Qt, QRect, QRectF, QSize
from PyQt5.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPen,
    QPaintEvent,
    QEnterEvent,
)
from PyQt5.QtWidgets import QPushButton, QWidget

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaIcon, ElaIconType

from ._internal import _ThemeAwareMixin
from ._colors import get_color_scheme


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

_SIZE_MAP: dict[str, dict[str, int]] = {
    "small": {
        "height": 28,
        "fontSize": 12,
        "paddingH": 14,
        "iconSize": 14,
        "radius": 4,
    },
    "middle": {
        "height": 38,
        "fontSize": 14,
        "paddingH": 18,
        "iconSize": 16,
        "radius": 6,
    },
    "large": {
        "height": 46,
        "fontSize": 16,
        "paddingH": 22,
        "iconSize": 18,
        "radius": 8,
    },
}


# ── ElaButton ────────────────────────────────────────────────


class ElaButton(_ThemeAwareMixin, QPushButton):
    """统一风格按钮组件。

    支持 6 种变体、16 种色彩主题、3 种尺寸，自动适配深浅色主题。

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
        self._padding_h = 18
        self._size_height = 38
        self._icon_name: Optional[ElaIconType.IconName] = icon
        self._icon_size = iconSize
        self._hovered = False

        if text:
            self.setText(text)

        self._theme_mode = eTheme.getThemeMode()
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
        """设置按钮图标。

        :param iconName: ElaAwesome 图标名称
        :param iconSize: 图标像素大小，默认 16
        """
        self._icon_name = iconName
        self._icon_size = iconSize
        self.setIconSize(QSize(iconSize, iconSize))
        self.update()

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
        font.setPixelSize(cfg["fontSize"])
        self.setFont(font)
        self.updateGeometry()
        self.update()

    def sizeHint(self) -> QSize:
        """按文字 / 图标与内边距计算合适宽度（不再依赖样式默认值）。"""
        fm = self.fontMetrics()
        width = fm.horizontalAdvance(self.text())
        if self._icon_name is not None:
            width += self._icon_size + (6 if self.text() else 0)
        width += 2 * self._padding_h
        return QSize(max(64, width), self._size_height)

    def minimumSizeHint(self) -> QSize:
        return QSize(max(48, 2 * self._padding_h), self._size_height)

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
        return QColor(0x2A, 0x2A, 0x2A) if self._is_dark() else QColor(0xF5, 0xF5, 0xF5)

    def _disabled_text(self) -> QColor:
        return QColor(0x60, 0x60, 0x60) if self._is_dark() else QColor(0xBF, 0xBF, 0xBF)

    def _disabled_border(self) -> QColor:
        return self._neutral_border()

    def _hover_tint(self) -> QColor:
        """Subtle overlay for 'text' variant hover."""
        return QColor(255, 255, 255, 15) if self._is_dark() else QColor(0, 0, 0, 15)

    def _pressed_tint(self) -> QColor:
        """Darker overlay for 'text' variant pressed."""
        return QColor(255, 255, 255, 30) if self._is_dark() else QColor(0, 0, 0, 38)

    def _scheme(self) -> dict[str, QColor]:
        return get_color_scheme(self._effective_color(), self._theme_mode)

    # ── Events ────────────────────────────────────────────

    def enterEvent(self, event: QEnterEvent) -> None:
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    # ── Paint ─────────────────────────────────────────────

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

            w = self.width()
            h = self.height()
            br = self._border_radius

            disabled = not self.isEnabled()
            pressed = self.isDown()
            hovered = self._hovered
            variant = self._variant
            cname = self._effective_color()
            is_default = cname == "default"
            scheme = self._scheme()

            path = QPainterPath()
            path.addRoundedRect(QRectF(0.5, 0.5, w - 1.0, h - 1.0), br, br)

            # -- Resolve background / border / text color --
            border_pen = None
            if disabled:
                bg = (
                    Qt.GlobalColor.transparent
                    if variant in ("text", "link")
                    else self._disabled_bg()
                )
                text_color = self._disabled_text()
                if variant in ("outlined", "dashed"):
                    border_pen = QPen(self._disabled_border(), 1)
            elif variant == "solid":
                bg = (
                    scheme["solidActive"]
                    if pressed
                    else (scheme["solidHover"] if hovered else scheme["solid"])
                )
                text_color = scheme["solidText"]
            elif variant in ("outlined", "dashed"):
                if is_default:
                    bg = (
                        self._hover_tint()
                        if (hovered or pressed)
                        else Qt.GlobalColor.transparent
                    )
                    text_color = self._neutral_text()
                    border_color = self._neutral_border()
                else:
                    bg = (
                        scheme["accentBgHover"]
                        if (hovered or pressed)
                        else scheme["accentBg"]
                    )
                    text_color = scheme["accent"]
                    border_color = QColor(scheme["accent"])
                    border_color.setAlpha(110 if not self._is_dark() else 150)
                border_pen = QPen(border_color, 1)
            elif variant == "filled":
                bg = (
                    scheme["accentBgHover"]
                    if (hovered or pressed)
                    else scheme["accentBg"]
                )
                text_color = scheme["accent"]
            elif variant == "text":
                bg = (
                    self._pressed_tint()
                    if pressed
                    else (self._hover_tint() if hovered else Qt.GlobalColor.transparent)
                )
                text_color = (
                    scheme["accent"] if not is_default else self._neutral_text()
                )
            elif variant == "link":
                bg = Qt.GlobalColor.transparent
                text_color = (
                    scheme["accent"] if not is_default else self._neutral_text()
                )
            else:
                bg = Qt.GlobalColor.transparent
                text_color = self._neutral_text()

            if variant == "dashed" and border_pen is not None:
                border_pen.setStyle(Qt.PenStyle.DashLine)

            painter.setBrush(bg)
            painter.setPen(border_pen if border_pen is not None else Qt.PenStyle.NoPen)
            painter.drawPath(path)

            # -- Draw icon + text --
            painter.setPen(text_color)
            icon_name = self._icon_name
            btn_text = self.text()
            if icon_name is not None:
                spacing = 6
                icon_sz = QSize(self._icon_size, self._icon_size)
                fm = painter.fontMetrics()
                tw = fm.horizontalAdvance(btn_text) if btn_text else 0
                if tw:
                    total_w = icon_sz.width() + spacing + tw
                    sx = (w - total_w) // 2
                else:
                    # 纯图标按钮：只居中图标本身（含 spacing 会向左偏）
                    sx = (w - icon_sz.width()) // 2
                iy = (h - icon_sz.height()) // 2
                ir = QRect(sx, iy, icon_sz.width(), icon_sz.height())
                icon = ElaIcon.getInstance().getElaIcon(icon_name, text_color)
                painter.drawPixmap(ir, icon.pixmap(icon_sz))
                if tw:
                    tr = QRect(ir.right() + spacing, 0, tw, h)
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
                    QRect(0, 0, w, h),
                    Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                    btn_text,
                )
                if variant == "link" and hovered and not disabled:
                    fm = painter.fontMetrics()
                    tw = fm.horizontalAdvance(btn_text)
                    tx = (w - tw) // 2
                    ty = h // 2 + fm.ascent() // 2 + 2
                    painter.setPen(QPen(text_color, 1))
                    painter.drawLine(tx, ty, tx + tw, ty)
        finally:
            painter.end()
