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

from ._internal import disconnect_theme_signal


# ── Type aliases ─────────────────────────────────────────────

ElaButtonVariant = Literal[
    "outlined", "dashed", "solid", "filled", "text", "link"
]
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


# ── Color palette ────────────────────────────────────────────

# Each named color defines:
#   accent         — main accent color (text/border/solid-bg)
#   accentHover    — hover variant of accent
#   accentActive   — active/pressed variant of accent
#   accentBg       — semi-transparent bg tint (for filled variant, outlined hover)
#   accentBgHover  — hover variant of bg tint
#   textColor      — contrasting text color on solid bg (usually white)
#
# 'default' color uses the primary accent palette; the "neutral"
# appearance (gray border, dark text for outlined) is handled in paintEvent.

_COLOR_PALETTE: dict[str, dict[str, dict[str, str]]] = {
    "default": {
        "light": {
            "accent": "#1677ff",
            "accentHover": "#4096ff",
            "accentActive": "#0958d9",
            "accentBg": "#e6f4ff",
            "accentBgHover": "#bae0ff",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#1668dc",
            "accentHover": "#3c89e8",
            "accentActive": "#1554ad",
            "accentBg": "#111d2c",
            "accentBgHover": "#15325b",
            "textColor": "#ffffff",
        },
    },
    "primary": {
        "light": {
            "accent": "#1677ff",
            "accentHover": "#4096ff",
            "accentActive": "#0958d9",
            "accentBg": "#e6f4ff",
            "accentBgHover": "#bae0ff",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#1668dc",
            "accentHover": "#3c89e8",
            "accentActive": "#1554ad",
            "accentBg": "#111d2c",
            "accentBgHover": "#15325b",
            "textColor": "#ffffff",
        },
    },
    "danger": {
        "light": {
            "accent": "#ff4d4f",
            "accentHover": "#ff7875",
            "accentActive": "#d9363e",
            "accentBg": "#fff2f0",
            "accentBgHover": "#ffd8d2",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#dc4446",
            "accentHover": "#e86a6b",
            "accentActive": "#ad393a",
            "accentBg": "#2c1415",
            "accentBgHover": "#4a1f20",
            "textColor": "#ffffff",
        },
    },
    "blue": {
        "light": {
            "accent": "#1677ff",
            "accentHover": "#4096ff",
            "accentActive": "#0958d9",
            "accentBg": "#e6f4ff",
            "accentBgHover": "#bae0ff",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#1668dc",
            "accentHover": "#3c89e8",
            "accentActive": "#1554ad",
            "accentBg": "#111d2c",
            "accentBgHover": "#15325b",
            "textColor": "#ffffff",
        },
    },
    "purple": {
        "light": {
            "accent": "#722ed1",
            "accentHover": "#9254de",
            "accentActive": "#531dab",
            "accentBg": "#f9f0ff",
            "accentBgHover": "#efdbff",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#642ab8",
            "accentHover": "#854eca",
            "accentActive": "#51219a",
            "accentBg": "#1e1330",
            "accentBgHover": "#2e1c4a",
            "textColor": "#ffffff",
        },
    },
    "cyan": {
        "light": {
            "accent": "#13c2c2",
            "accentHover": "#36cfc9",
            "accentActive": "#08979c",
            "accentBg": "#e6fffb",
            "accentBgHover": "#b5f5ec",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#10adad",
            "accentHover": "#2fc7c7",
            "accentActive": "#0c8a8a",
            "accentBg": "#112828",
            "accentBgHover": "#1a3d3d",
            "textColor": "#ffffff",
        },
    },
    "green": {
        "light": {
            "accent": "#52c41a",
            "accentHover": "#73d13d",
            "accentActive": "#389e0d",
            "accentBg": "#f6ffed",
            "accentBgHover": "#e8fcd9",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#49aa17",
            "accentHover": "#66c430",
            "accentActive": "#3a8c12",
            "accentBg": "#16280e",
            "accentBgHover": "#243d16",
            "textColor": "#ffffff",
        },
    },
    "magenta": {
        "light": {
            "accent": "#eb2f96",
            "accentHover": "#f06292",
            "accentActive": "#c41d7f",
            "accentBg": "#fff0f6",
            "accentBgHover": "#ffd6e7",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#c92980",
            "accentHover": "#dd5099",
            "accentActive": "#a81e6b",
            "accentBg": "#2c1120",
            "accentBgHover": "#421a31",
            "textColor": "#ffffff",
        },
    },
    "pink": {
        "light": {
            "accent": "#eb2f96",
            "accentHover": "#f06292",
            "accentActive": "#c41d7f",
            "accentBg": "#fff0f6",
            "accentBgHover": "#ffd6e7",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#c92980",
            "accentHover": "#dd5099",
            "accentActive": "#a81e6b",
            "accentBg": "#2c1120",
            "accentBgHover": "#421a31",
            "textColor": "#ffffff",
        },
    },
    "red": {
        "light": {
            "accent": "#f5222d",
            "accentHover": "#ff4d4f",
            "accentActive": "#cf1322",
            "accentBg": "#fff1f0",
            "accentBgHover": "#ffd8d2",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#d91d28",
            "accentHover": "#e8474f",
            "accentActive": "#b0141e",
            "accentBg": "#2c1012",
            "accentBgHover": "#45171b",
            "textColor": "#ffffff",
        },
    },
    "orange": {
        "light": {
            "accent": "#fa8c16",
            "accentHover": "#ffa940",
            "accentActive": "#d46b08",
            "accentBg": "#fff7e6",
            "accentBgHover": "#ffe7ba",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#d97a13",
            "accentHover": "#e8993a",
            "accentActive": "#b0640e",
            "accentBg": "#2c1c0e",
            "accentBgHover": "#452b14",
            "textColor": "#ffffff",
        },
    },
    "yellow": {
        "light": {
            "accent": "#fadb14",
            "accentHover": "#ffec3d",
            "accentActive": "#d4b106",
            "accentBg": "#feffe6",
            "accentBgHover": "#ffffb8",
            "textColor": "#000000",
        },
        "dark": {
            "accent": "#d9bd12",
            "accentHover": "#e8d13a",
            "accentActive": "#b09e0a",
            "accentBg": "#2c280e",
            "accentBgHover": "#453e14",
            "textColor": "#000000",
        },
    },
    "volcano": {
        "light": {
            "accent": "#fa541c",
            "accentHover": "#ff7a45",
            "accentActive": "#d4380d",
            "accentBg": "#fff2e8",
            "accentBgHover": "#ffd8bf",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#d94818",
            "accentHover": "#e86e3a",
            "accentActive": "#b03810",
            "accentBg": "#2c1610",
            "accentBgHover": "#452214",
            "textColor": "#ffffff",
        },
    },
    "geekblue": {
        "light": {
            "accent": "#2f54eb",
            "accentHover": "#597ef7",
            "accentActive": "#1d39c4",
            "accentBg": "#f0f5ff",
            "accentBgHover": "#d6e4ff",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#2a47cc",
            "accentHover": "#4d68e0",
            "accentActive": "#2038a8",
            "accentBg": "#12182c",
            "accentBgHover": "#1c2645",
            "textColor": "#ffffff",
        },
    },
    "lime": {
        "light": {
            "accent": "#a0d911",
            "accentHover": "#bae637",
            "accentActive": "#7cb305",
            "accentBg": "#fcffe6",
            "accentBgHover": "#f4ffb8",
            "textColor": "#000000",
        },
        "dark": {
            "accent": "#8cbd0e",
            "accentHover": "#a3d430",
            "accentActive": "#729b0a",
            "accentBg": "#1c280e",
            "accentBgHover": "#2b3d14",
            "textColor": "#000000",
        },
    },
    "gold": {
        "light": {
            "accent": "#faad14",
            "accentHover": "#ffd666",
            "accentActive": "#d48806",
            "accentBg": "#fffbe6",
            "accentBgHover": "#fff1b8",
            "textColor": "#000000",
        },
        "dark": {
            "accent": "#d99612",
            "accentHover": "#e8b43a",
            "accentActive": "#b07c0a",
            "accentBg": "#2c220e",
            "accentBgHover": "#453414",
            "textColor": "#000000",
        },
    },
}


def _get_scheme(color_name: str, mode: ElaThemeType.ThemeMode) -> dict[str, QColor]:
    mode_key = "light" if mode == ElaThemeType.ThemeMode.Light else "dark"
    raw = _COLOR_PALETTE[color_name][mode_key]
    return {k: QColor(v) for k, v in raw.items()}


# ── Size presets ─────────────────────────────────────────────

_SIZE_MAP: dict[str, dict[str, int]] = {
    "small": {"height": 28, "fontSize": 12, "paddingH": 8, "iconSize": 14},
    "middle": {"height": 38, "fontSize": 14, "paddingH": 12, "iconSize": 16},
    "large": {"height": 46, "fontSize": 16, "paddingH": 16, "iconSize": 18},
}


# ── ElaButton ────────────────────────────────────────────────

class ElaButton(QPushButton):
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

        self._apply_size(size)
        self._onThemeChanged(eTheme.getThemeMode())
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

    def setElaIcon(
        self, iconName: ElaIconType.IconName, iconSize: int = 16
    ) -> None:
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
        return eTheme.getThemeMode() == ElaThemeType.ThemeMode.Dark

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
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
        return _get_scheme(self._effective_color(), eTheme.getThemeMode())

    # ── Events ────────────────────────────────────────────

    def enterEvent(self, event: QEnterEvent) -> None:
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def deleteLater(self) -> None:
        disconnect_theme_signal(self._onThemeChanged)
        super().deleteLater()

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
            and not hovered and not pressed and not disabled
        )
        # Neutral state: 'default' color in text variant
        neutral_text = (
            cname == "default"
            and variant == "text"
            and not disabled
        )

        scheme = self._scheme()

        # ── Resolve background ────────────────────────────

        if disabled:
            if variant in ("text", "link"):
                bg = Qt.GlobalColor.transparent
            else:
                bg = self._disabled_bg()
        elif variant == "solid":
            bg = scheme["accentActive"] if pressed else (scheme["accentHover"] if hovered else scheme["accent"])
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
                text_color = scheme["accent"] if cname != "default" else self._neutral_text()
        elif variant == "filled":
            if pressed:
                text_color = scheme["accentActive"]
            elif hovered:
                text_color = scheme["accentHover"]
            else:
                text_color = scheme["accent"]
        elif variant == "text":
            text_color = scheme["accent"] if cname != "default" else self._neutral_text()
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
            painter.drawText(tr, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, btn_text)
            # Link underline
            if variant == "link" and hovered and not disabled:
                painter.drawLine(tr.left(), ir.bottom() + 1, tr.right(), ir.bottom() + 1)
        else:
            tr = QRect(sb, sb, w - 2 * sb, h - 2 * sb)
            painter.drawText(tr, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter, btn_text)
            # Link underline
            if variant == "link" and hovered and not disabled:
                fm = painter.fontMetrics()
                tw = fm.horizontalAdvance(btn_text)
                tx = sb + (w - 2 * sb - tw) // 2
                ty = sb + (h - 2 * sb) // 2 + fm.ascent() // 2 + 2
                painter.drawLine(tx, ty, tx + tw, ty)
