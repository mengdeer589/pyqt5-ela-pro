"""
共享颜色面板，供 ElaButton / ElaChip 等组件使用。

每个命名颜色定义：
  accent         — 主色（文字/边框/填充背景）
  accentHover    — 悬浮态
  accentActive   — 按下态
  accentBg       — 半透明背景色（用于 filled 变体、outlined 悬浮）
  accentBgHover  — 背景色悬浮态
  textColor      — 实心背景上的文字颜色（通常为白色）

``get_color_scheme`` 额外派生实心按钮专用色（保证文字对比度 ≥ 4.5:1）：
  solid / solidHover / solidActive / solidText
"""

from __future__ import annotations

from PyQt5.QtGui import QColor
from PyQt5ElaWidgetTools import ElaThemeType

_COLOR_PALETTE: dict[str, dict[str, dict[str, str]]] = {
    "default": {
        "light": {
            "accent": "#4f5459",
            "accentHover": "#6a7075",
            "accentActive": "#3a3f44",
            "accentBg": "#f2f3f4",
            "accentBgHover": "#e4e6e8",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#5a5f63",
            "accentHover": "#6e747a",
            "accentActive": "#45494d",
            "accentBg": "#2c2e30",
            "accentBgHover": "#3a3d40",
            "textColor": "#ffffff",
        },
    },
    "blue": {
        "light": {
            "accent": "#0067c0",
            "accentHover": "#2680ce",
            "accentActive": "#004fa0",
            "accentBg": "#e5eff9",
            "accentBgHover": "#c8dcf0",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#4cc2ff",
            "accentHover": "#70cfff",
            "accentActive": "#38ade8",
            "accentBg": "#142a38",
            "accentBgHover": "#1e4059",
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
            "accent": "#f759ab",
            "accentHover": "#ff85c0",
            "accentActive": "#c41d7f",
            "accentBg": "#fff0f6",
            "accentBgHover": "#ffd6e7",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#c95a91",
            "accentHover": "#d97cab",
            "accentActive": "#a14473",
            "accentBg": "#2c1120",
            "accentBgHover": "#421a31",
            "textColor": "#ffffff",
        },
    },
    "red": {
        "light": {
            "accent": "#e81123",
            "accentHover": "#eb424f",
            "accentActive": "#c40d1c",
            "accentBg": "#fde6e8",
            "accentBgHover": "#facacd",
            "textColor": "#ffffff",
        },
        "dark": {
            "accent": "#e81123",
            "accentHover": "#eb424f",
            "accentActive": "#c40d1c",
            "accentBg": "#2c1114",
            "accentBgHover": "#451a1e",
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

_COLOR_ALIAS: dict[str, str] = {
    "primary": "blue",
}


def _resolve_color(name: str) -> str:
    return _COLOR_ALIAS.get(name, name)


def _relative_luminance(color: QColor) -> float:
    """WCAG 相对亮度。"""

    def channel(value: int) -> float:
        v = value / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    return (
        0.2126 * channel(color.red())
        + 0.7152 * channel(color.green())
        + 0.0722 * channel(color.blue())
    )


def _contrast_ratio(a: QColor, b: QColor) -> float:
    """WCAG 对比度（1~21）。"""
    la, lb = _relative_luminance(a), _relative_luminance(b)
    high, low = max(la, lb), min(la, lb)
    return (high + 0.05) / (low + 0.05)


def _mix(a: QColor, b: QColor, t: float) -> QColor:
    return QColor(
        int(a.red() * (1 - t) + b.red() * t),
        int(a.green() * (1 - t) + b.green() * t),
        int(a.blue() * (1 - t) + b.blue() * t),
    )


#: 实心背景使用黑字的色系（亮黄色系，白字天然不达标）
_BLACK_TEXT_COLORS = {"yellow", "lime", "gold"}


def _solid_palette(accent: QColor, color_name: str) -> dict[str, QColor]:
    """派生实心按钮配色：保证 ``solidText`` 与 ``solid`` 对比度 ≥ 4.5:1。

    亮黄色系（黄 / 柠檬 / 金）固定黑字且不压暗；其余颜色统一白字，
    并按需逐步加深底色直到达标，避免霓虹色块配白字的低对比问题。
    """
    white, black = QColor("#ffffff"), QColor("#000000")
    if color_name in _BLACK_TEXT_COLORS:
        text, solid = black, QColor(accent)
    else:
        text, solid = white, QColor(accent)
        for _ in range(32):
            if _contrast_ratio(solid, text) >= 4.5:
                break
            solid = _mix(solid, black, 0.06)
    hover = _mix(solid, white, 0.08)
    if _contrast_ratio(hover, text) < 4.0:
        hover = _mix(solid, black, 0.08)
    active = _mix(solid, black, 0.12)
    return {
        "solid": solid,
        "solidHover": hover,
        "solidActive": active,
        "solidText": text,
    }


def get_color_scheme(
    color_name: str, mode: ElaThemeType.ThemeMode
) -> dict[str, QColor]:
    """获取指定颜色名称在当前主题下的完整色板（QColor 对象）。

    在原始 6 个键之外，额外包含对比度达标的实心按钮色：
    ``solid`` / ``solidHover`` / ``solidActive`` / ``solidText``。
    """
    resolved = _resolve_color(color_name)
    if resolved not in _COLOR_PALETTE:
        resolved = "blue"
    mode_key = "light" if mode == ElaThemeType.ThemeMode.Light else "dark"
    raw = _COLOR_PALETTE[resolved][mode_key]
    scheme = {k: QColor(v) for k, v in raw.items()}
    scheme.update(_solid_palette(scheme["accent"], resolved))
    return scheme


def get_accent_color(color_name: str, mode: ElaThemeType.ThemeMode) -> QColor:
    """仅获取主色 accent。"""
    resolved = _resolve_color(color_name)
    if resolved not in _COLOR_PALETTE:
        resolved = "blue"
    mode_key = "light" if mode == ElaThemeType.ThemeMode.Light else "dark"
    return QColor(_COLOR_PALETTE[resolved][mode_key]["accent"])
