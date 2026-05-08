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
    "small": {"height": 28, "fontSize": 12, "paddingH": 8, "iconSize": 14},
    "middle": {"height": 38, "fontSize": 14, "paddingH": 12, "iconSize": 16},
    "large": {"height": 46, "fontSize": 16, "paddingH": 16, "iconSize": 18},
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
        self._border_radius = 4
        self._icon_name: Optional[ElaIconType.IconName] = icon
        self._icon_size = iconSize
        self._hovered = False

        if text:
            self.setText(text)

        self._theme_mode = eTheme.getThemeMode()
        self._apply_size(size)
        eTheme.themeModeChanged.connect(self._onThemeChanged)

    # ── Public API ────────────────────────────────────────

    def setVariant(self, variant: ElaButtonVariant) -> None:
        self._variant = variant
        self.update()

    def variant(self) -> str:
        return self._variant

    def setColor(self, color: ElaButtonColor) -> None:
        self._color_name = color
        self.update()

    def color(self) -> str:
        return self._color_name

    def setDanger(self, danger: bool) -> None:
        self._danger = danger
        self.update()

    def isDanger(self) -> bool:
        return self._danger

    def setButtonSize(self, size: ElaButtonSize) -> None:
        self._apply_size(size)
        self.update()

    def buttonSize(self) -> str:
        h = self.height()
        for name, cfg in _SIZE_MAP.items():
            if cfg["height"] == h:
                return name
        return "middle"

    def setElaIcon(self, iconName: ElaIconType.IconName, iconSize: int = 16) -> None:
        self._icon_name = iconName
        self._icon_size = iconSize
        self.setIconSize(QSize(iconSize, iconSize))
        self.update()

    def setBorderRadius(self, radius: int) -> None:
        self._border_radius = radius
        self.update()

    def borderRadius(self) -> int:
        return self._border_radius

    # ── Internal ──────────────────────────────────────────

    def _apply_size(self, size: ElaButtonSize) -> None:
        cfg = _SIZE_MAP[size]
        self.setFixedHeight(cfg["height"])
        font = self.font()
        font.setPixelSize(cfg["fontSize"])
        self.setFont(font)

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
        """Gray border for 'default' outlined normal state."""
        return QColor(0x42, 0x42, 0x42) if self._is_dark() else QColor(0xD9, 0xD9, 0xD9)

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

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = self.width()
        h = self.height()
        sb = 3
        r = QRect(sb, sb, w - 2 * sb, h - 2 * sb)
        br = self._border_radius

        disabled = not self.isEnabled()
        pressed = self.isDown()
        hovered = self._hovered
        variant = self._variant
        cname = self._effective_color()

        # Neutral state: 'default' color in outlined/dashed when not interacted
        neutral_outlined = (
            cname == "default"
            and variant in ("outlined", "dashed")
            and not hovered
            and not pressed
            and not disabled
        )
        # Neutral state: 'default' color in text variant
        neutral_text = cname == "default" and variant == "text" and not disabled

        scheme = self._scheme()

        # ── Resolve background ────────────────────────────

        if disabled:
            if variant in ("text", "link"):
                bg = Qt.GlobalColor.transparent
            else:
                bg = self._disabled_bg()
        elif variant == "solid":
            bg = (
                scheme["accentActive"]
                if pressed
                else (scheme["accentHover"] if hovered else scheme["accent"])
            )
        elif variant in ("outlined", "dashed"):
            if neutral_outlined:
                bg = Qt.GlobalColor.transparent
            elif pressed:
                bg = scheme["accentBgHover"]
            elif hovered:
                bg = scheme["accentBg"]
            else:
                bg = Qt.GlobalColor.transparent
        elif variant == "filled":
            if pressed:
                bg = scheme["accentBgHover"]
            elif hovered:
                bg = scheme["accentBg"]
            else:
                bg = scheme["accentBg"]
        elif variant == "text":
            if pressed:
                bg = self._pressed_tint()
            elif hovered:
                bg = self._hover_tint()
            else:
                bg = Qt.GlobalColor.transparent
        else:  # link
            bg = Qt.GlobalColor.transparent

        # ── Resolve border pen ────────────────────────────

        if variant == "solid":
            border_pen = Qt.PenStyle.NoPen
        elif variant in ("outlined", "dashed"):
            if disabled:
                bc = self._disabled_border()
            elif neutral_outlined:
                bc = self._neutral_border()
            elif pressed:
                bc = scheme["accentActive"]
            elif hovered:
                bc = scheme["accentHover"]
            else:
                bc = scheme["accent"] if cname != "default" else self._neutral_border()
            border_pen = QPen(bc, 1)
            if variant == "dashed":
                border_pen.setStyle(Qt.PenStyle.DashLine)
        else:
            border_pen = Qt.PenStyle.NoPen

        # ── Resolve text color ────────────────────────────

        if disabled:
            text_color = self._disabled_text()
        elif neutral_outlined or neutral_text:
            text_color = self._neutral_text()
        elif variant == "solid":
            text_color = scheme["textColor"]
        elif variant in ("outlined", "dashed"):
            if pressed:
                text_color = scheme["accentActive"]
            elif hovered:
                text_color = scheme["accentHover"]
            else:
                text_color = (
                    scheme["accent"] if cname != "default" else self._neutral_text()
                )
        elif variant == "filled":
            if pressed:
                text_color = scheme["accentActive"]
            elif hovered:
                text_color = scheme["accentHover"]
            else:
                text_color = scheme["accent"]
        elif variant == "text":
            text_color = (
                scheme["accent"] if cname != "default" else self._neutral_text()
            )
        else:  # link
            if pressed:
                text_color = scheme["accentActive"]
            elif hovered:
                text_color = scheme["accentHover"]
            else:
                text_color = scheme["accent"]

        # ── Draw background ───────────────────────────────

        path = QPainterPath()
        path.addRoundedRect(QRectF(r), br, br)
        painter.setBrush(bg)
        painter.setPen(border_pen)
        painter.drawPath(path)

        # ── Draw icon + text ──────────────────────────────

        painter.setPen(text_color)
        icon_name = self._icon_name
        icon_sz = self._icon_size
        btn_text = self.text()

        if icon_name is not None:
            sz = QSize(icon_sz, icon_sz)
            spacing = 6
            ch = h - 2 * sb
            fm = painter.fontMetrics()
            tw = fm.horizontalAdvance(btn_text)
            total_w = sz.width() + spacing + tw
            sx = sb + (w - 2 * sb - total_w) // 2
            iy = sb + (ch - sz.height()) // 2
            ir = QRect(sx, iy, sz.width(), sz.height())
            icon = ElaIcon.getInstance().getElaIcon(icon_name, text_color)
            painter.drawPixmap(ir, icon.pixmap(sz))
            tr = QRect(ir.right() + spacing, sb, tw, ch)
            painter.drawText(
                tr, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, btn_text
            )
            # Link underline
            if variant == "link" and hovered and not disabled:
                painter.drawLine(
                    tr.left(), ir.bottom() + 1, tr.right(), ir.bottom() + 1
                )
        else:
            tr = QRect(sb, sb, w - 2 * sb, h - 2 * sb)
            painter.drawText(
                tr,
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                btn_text,
            )
            # Link underline
            if variant == "link" and hovered and not disabled:
                fm = painter.fontMetrics()
                tw = fm.horizontalAdvance(btn_text)
                tx = sb + (w - 2 * sb - tw) // 2
                ty = sb + (h - 2 * sb) // 2 + fm.ascent() // 2 + 2
                painter.drawLine(tx, ty, tx + tw, ty)
