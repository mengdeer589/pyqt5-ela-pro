"""
共享颜色面板，供 ElaButton / ElaChip 等组件使用。

每个命名颜色定义：
  accent         — 主色（文字/边框/填充背景）
  accentHover    — 悬浮态
  accentActive   — 按下态
  accentBg       — 半透明背景色（用于 filled 变体、outlined 悬浮）
  accentBgHover  — 背景色悬浮态
  textColor      — 实心背景上的文字颜色（通常为白色）
"""

from __future__ import annotations

from PyQt5.QtGui import QColor
from PyQt5ElaWidgetTools import ElaThemeType

_COLOR_PALETTE: dict[str, dict[str, dict[str, str]]] = {
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
    "default": "blue",
    "primary": "blue",
    "pink": "magenta",
}


def resolve_color(name: str) -> str:
    """将别名映射为实际的调色板键名。"""
    return _COLOR_ALIAS.get(name, name)


def get_color_scheme(
    color_name: str, mode: ElaThemeType.ThemeMode
) -> dict[str, QColor]:
    """获取指定颜色名称在当前主题下的完整色板（QColor 对象）。"""
    resolved = resolve_color(color_name)
    mode_key = "light" if mode == ElaThemeType.ThemeMode.Light else "dark"
    raw = _COLOR_PALETTE[resolved][mode_key]
    return {k: QColor(v) for k, v in raw.items()}


def get_accent_color(color_name: str, mode: ElaThemeType.ThemeMode) -> QColor:
    """仅获取主色 accent。"""
    resolved = resolve_color(color_name)
    mode_key = "light" if mode == ElaThemeType.ThemeMode.Light else "dark"
    return QColor(_COLOR_PALETTE[resolved][mode_key]["accent"])
