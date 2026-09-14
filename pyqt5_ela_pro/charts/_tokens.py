"""
charts 包主题令牌适配层（私有）。

将源引擎（InstructionX_UIKit.charts，PySide6 + 自建令牌）对 ``T("...")``
的读取，映射到本库 ``eTheme`` / ``ElaThemeType`` 语义令牌：颜色一律
实时取 ``eTheme.getThemeColor(mode, ...)``，深浅色主题切换后重绘即生效，
观感与当前 Ela 组件库保持一致。

Ela 主题色中没有的语义色（success / warning / 主色上的浮层文字等）使用
静态双主题色表（light / dark），并集中在本模块以便审计。字体字号 / 圆角
/ 动效时长为固定常量（源令牌值）。

对外仅暴露 ``chart_token(mode, key)`` 与 ``T(key)``（实时模式）及少量常量。
"""

from __future__ import annotations

from PyQt5.QtCore import QEasingCurve
from PyQt5.QtGui import QColor
from PyQt5ElaWidgetTools import eTheme, ElaThemeType

# ---------------------------------------------------------------------------
# 固定令牌（与主题无关）
# ---------------------------------------------------------------------------

#: 图表用字族（首个为 Windows 主推中文字体）
FONT_FAMILIES = [
    "Microsoft YaHei",
    "Segoe UI",
    "PingFang SC",
    "Noto Sans CJK SC",
    "WenQuanYi Micro Hei",
]

#: 字号 / 字重 / 圆角（px）
FONT_XS = 11
FONT_SM = 12
FONT_TITLE_MD = 17
FONT_WEIGHT_SEMIBOLD = 600
RADIUS_MD = 6.0

#: 入场 / 数据过渡动画时长（ms）与缓动（对齐源库 DURATION.slow / EASING.standard）
ANIM_DURATION = 320
ANIM_EASING = QEasingCurve.Type.OutCubic

# ---------------------------------------------------------------------------
# Ela 语义色映射（eTheme 实时取色，主题切换自动跟随）
# ---------------------------------------------------------------------------

#: 源令牌键 -> ElaThemeType.ThemeColor 成员名
_ELA_COLOR_KEYS = {
    "color.bg.base": "BasicBase",  # 画布底色（Ela 窗口基础色）
    "color.bg.elevated": "PopupBase",  # 浮层 / 数据点内芯底色
    "color.bg.muted": "BasicHoverAlpha",  # 次级填充背景
    "color.border": "BasicBorder",  # 网格线
    "color.border.strong": "BasicBorderDeep",  # 轴线 / 引线
    "color.text.primary": "BasicText",  # 主文本
    "color.text.secondary": "BasicDetailsText",  # 次级文本（刻度标签）
    "color.text.tertiary": "BasicTextNoFocus",  # 弱文本（轴名）
    "color.text.disabled": "BasicTextDisable",  # 禁用态文本（图例隐藏项）
    "color.primary": "PrimaryNormal",  # 主题主色
    "color.primary.hover": "PrimaryHover",
    "color.primary.pressed": "PrimaryPress",
    "color.danger": "StatusDanger",  # 危险色
}

#: Ela 主题色中没有的语义色：key -> (light_hex, dark_hex)
_STATIC_COLORS = {
    "color.success": ("#3E7E5F", "#6BA98A"),
    "color.success.hover": ("#34684F", "#55D0A0"),
    "color.warning": ("#C08A3E", "#D2A668"),
    "color.warning.hover": ("#A97A35", "#C08A3E"),
    "color.on.primary": ("#FFFFFF", "#15181E"),
}


def _ela_color(mode, member_name: str) -> QColor:
    return QColor(
        eTheme.getThemeColor(mode, getattr(ElaThemeType.ThemeColor, member_name))
    )


def _subtle_primary(mode) -> QColor:
    """color.primary.subtle：主色与画布底的 12% 混合浅色（主题感知）。"""
    bg = _ela_color(mode, "BasicBase")
    p = _ela_color(mode, "PrimaryNormal")
    return QColor(
        int(bg.red() * 0.88 + p.red() * 0.12),
        int(bg.green() * 0.88 + p.green() * 0.12),
        int(bg.blue() * 0.88 + p.blue() * 0.12),
    )


def chart_token(mode, key):
    """读取单个令牌值：颜色返回 QColor（实时主题），数值返回 int/float。

    :param mode: 主题模式（eTheme.getThemeMode() 返回值）
    :param key: 源库令牌键，如 ``"color.bg.base"`` / ``"font.xs"``
    """
    if key == "color.primary.subtle":
        return _subtle_primary(mode)
    member = _ELA_COLOR_KEYS.get(key)
    if member is not None:
        return _ela_color(mode, member)
    static = _STATIC_COLORS.get(key)
    if static is not None:
        dark = mode == ElaThemeType.ThemeMode.Dark
        return QColor(static[1] if dark else static[0])
    ints = {
        "font.xs": FONT_XS,
        "font.sm": FONT_SM,
        "font.title.md": FONT_TITLE_MD,
        "font.weight.semibold": FONT_WEIGHT_SEMIBOLD,
        "radius.md": RADIUS_MD,
    }
    if key in ints:
        return ints[key]
    raise KeyError(f"未知图表令牌: {key!r}")


def T(key):
    """按当前主题模式读取令牌（对齐源库 T() 调用面）。"""
    return chart_token(eTheme.getThemeMode(), key)


# ---------------------------------------------------------------------------
# 系列默认调色板（数据色：与 Ela 交互色/状态色解耦，两主题各一套保证区分度）
# ---------------------------------------------------------------------------

#: 数据系列取色板（light / dark 各 8 色）
_PALETTE_LIGHT = [
    "#0072BD",
    "#D95319",
    "#EDB120",
    "#77AC30",
    "#7E2F8E",
    "#009688",
    "#A2142F",
    "#6E6E6E",
]

_PALETTE_DARK = [
    "#4DA6D9",
    "#E67A52",
    "#F5C940",
    "#8DB34A",
    "#A855C4",
    "#40B0A8",
    "#D45060",
    "#9E9E9E",
]


def palette_for_mode(mode) -> list:
    """当前主题的数据系列调色板（首色取主题主色，其余按主题固定表）。"""
    dark = mode == ElaThemeType.ThemeMode.Dark
    out = [_ela_color(mode, "PrimaryNormal")]
    out.extend(QColor(c) for c in (_PALETTE_DARK if dark else _PALETTE_LIGHT))
    return out
