"""语义令牌层（semantic token layer）。

上游 ``eTheme.getThemeColor(mode, index)`` 给的是**颜色槽位**（``BasicText`` /
``WindowBase`` / ``PrimaryNormal`` …），不是语义。本层做两件事：

1. **命名**：把槽位翻译成「这层表面 / 这级文字 / 这条边」的可读角色；
2. **补齐上游缺的语义**：上游 43 个槽位里没有 charts 调色板，也没有 Success /
   Warning 状态色（只有 ``StatusDanger``）。

**读取层必须 ``QColor(...)`` 拷贝** —— ``getThemeColor`` 返回的是上游持有的
``const QColor&``，直接 ``setAlpha`` 会污染全局调色板且不随主题信号复原。

强调色换色
----------
上游的 ``PrimaryHover`` / ``PrimaryPress`` / ``ToggleSwitchNoToggledCenter`` 是
**独立存储**的槽位（控件直接读），只写 ``PrimaryNormal`` 的症状是「按钮本体换成
红色、悬停又跳回出厂蓝」。:func:`setAccentColor` 因此一并派生写入这三个槽位，
派生表 ``_ACCENT_STEPS`` 是从出厂值反解的（ΔS 两模式一致，ΔL 符号随模式翻转），
用默认强调色走一遍能逐值还原上游出厂值。

**别照抄 Fluent-Qt 的「降 alpha 阶梯」**：本库槽位是纯不透明色，降 alpha 会让换色
后的 hover 与未换色的控件不是一个体系。

**换色后不会自动重绘**：``eTheme.setThemeColor`` 没有 NOTIFY 信号，调用方需自行
触发（遍历顶层窗口 ``update()``）。这是上游限制，绕不过。
"""

from __future__ import annotations

from enum import IntEnum
from typing import List, Optional

from PyQt5.QtGui import QColor

from PyQt5ElaWidgetTools import eTheme, ElaThemeType

__all__ = [
    "StatusRole",
    "accent",
    "blend",
    "border",
    "borderStrong",
    "chartPalette",
    "currentMode",
    "relativeLuminance",
    "resetAccentColor",
    "setAccentColor",
    "statusColor",
    "surface",
    "surfaceDialog",
    "surfacePopup",
    "surfaceRaised",
    "text",
    "textDisabled",
    "textMuted",
    "textOnAccent",
]


_TC = ElaThemeType.ThemeColor
_TM = ElaThemeType.ThemeMode


def currentMode() -> int:  # noqa: N802 (与 Qt 命名一致)
    """当前主题模式（``Light`` / ``Dark``）。

    自绘控件在 ``paintEvent`` 开头调一次即可 —— 比「构造时算好缓存、主题信号里重算」
    简单得多，也不用给每个控件挂一条 ``themeModeChanged`` 连接。需要**缓存**颜色的
    控件（``ColorText`` 之类颜色是快照的）仍应走 ``_apply_theme`` 重算。

    ``eTheme.getThemeColor`` 的 ``mode`` 参数**不接受 ``None``**（传 ``None`` 直接
    ``TypeError``），本层的访问器都包了一层，``mode=None`` 即「当前模式」。
    """
    return eTheme.getThemeMode()


def blend(base: QColor, other: QColor, t: float) -> QColor:
    """按比例混合两种颜色，``t`` 是**第二个参数（前景）**的占比（0-1，**含 alpha**）。

    等价于 CSS 的 ``rgba(前景, t) 叠在 底 上面``::

        blend(白底, 黑, 0.075)  ==  #ececec 上叠 7.5% 黑

    **参数序很容易搞反**：直觉写法 ``blend(黑, 白底, 0.075)`` 会算出近黑
    （``#121212``），差一整个明度档。搬运到共享层时踩过一次，故在此写死约定。

    alpha 一起插值 —— 半透明叠色必须这样算才与两次绘制等价，否则边界出硬环。
    """
    t = max(0.0, min(1.0, float(t)))
    return QColor(
        round(base.red() + (other.red() - base.red()) * t),
        round(base.green() + (other.green() - base.green()) * t),
        round(base.blue() + (other.blue() - base.blue()) * t),
        round(base.alpha() + (other.alpha() - base.alpha()) * t),
    )


def relativeLuminance(color: QColor) -> float:  # noqa: N802 (与数学名一致)
    """**Rec.709** 相对亮度（0-1）。

    **不是** WCAG 公式（那个要先做 sRGB→线性化）。这里的线性加权直接对 0-1 通道值
    算，两者同一数量级，阈值不贴着某个颜色的实际值就不会分歧。记在这里是为了
    **别有人以为是 WCAG 公式然后去改它** —— ``ela_avatar`` 的对比度阈值靠它定。
    """
    return 0.2126 * color.redF() + 0.7152 * color.greenF() + 0.0722 * color.blueF()


def _color(mode, token) -> QColor:
    """读一个上游槽位并**拷贝**成新的 QColor。``mode=None`` = 当前模式。"""
    if mode is None:
        mode = currentMode()
    return QColor(eTheme.getThemeColor(mode, token))


# ── 表面 ──────────────────────────────────────────────────────


def surface(mode) -> QColor:
    """最底层表面（窗口 / 画布）。``WindowBase``"""
    return _color(mode, _TC.WindowBase)


def surfaceRaised(mode) -> QColor:
    """抬起一层的表面（卡片 / 输入框）。``BasicBase``"""
    return _color(mode, _TC.BasicBase)


def surfacePopup(mode) -> QColor:
    """弹层表面（菜单 / 气泡 / 下拉）。``PopupBase``"""
    return _color(mode, _TC.PopupBase)


def surfaceDialog(mode) -> QColor:
    """对话框表面。``DialogBase``"""
    return _color(mode, _TC.DialogBase)


# ── 边 ────────────────────────────────────────────────────────


def border(mode) -> QColor:
    """常规描边。``BasicBorder``"""
    return _color(mode, _TC.BasicBorder)


def borderStrong(mode) -> QColor:
    """强调描边（聚焦态外圈等）。``BasicBorderDeep``"""
    return _color(mode, _TC.BasicBorderDeep)


# ── 文字 ──────────────────────────────────────────────────────


def text(mode) -> QColor:
    """正文主色。``BasicText``"""
    return _color(mode, _TC.BasicText)


def textMuted(mode) -> QColor:
    """次要 / 说明文字。``BasicDetailsText``"""
    return _color(mode, _TC.BasicDetailsText)


def textDisabled(mode) -> QColor:
    """禁用文字。``BasicTextDisable``"""
    return _color(mode, _TC.BasicTextDisable)


def accent(mode) -> QColor:
    """强调色（基础档）。``PrimaryNormal``"""
    return _color(mode, _TC.PrimaryNormal)


# ── 语义状态色 ────────────────────────────────────────────────


class StatusRole(IntEnum):
    """校验 / 提示的语义档位。

    刻意**不叫** ``None``：那是 Python 关键字，当不了枚举成员名（``None = 0`` 是
    SyntaxError）。用 ``Neutral`` 表达「无状态」。
    """

    Neutral = 0
    """无状态：不显示图标，文字用次要色。"""

    Error = 1
    Warning = 2
    Success = 3


#: ``Warning`` / ``Success`` 的定值（**刻意不从强调色派生**）。
#:
#: 试过「从 ``PrimaryNormal`` 派生」，结果是强调色为蓝时 Success 派生出一片深蓝
#: （``#113a5e``），语义完全消失。状态色的语义来自**色相**（琥珀=警告 / 绿=成功），
#: 用户换强调色时也不该把「成功绿」染成他选的颜色。色值取自 Fluent 已做过对比度
#: 调校的一组。
_STATUS_COLORS = {
    _TM.Light: {
        StatusRole.Warning: QColor("#9D5D00"),
        StatusRole.Success: QColor("#0F7B0F"),
    },
    _TM.Dark: {
        StatusRole.Warning: QColor("#FCE100"),
        StatusRole.Success: QColor("#6CCB5F"),
    },
}


def _shift(base: QColor, d_s: float, d_l: float) -> QColor:
    """保持色相与 alpha，按 HSL 偏移饱和度 / 亮度。

    ``QColor.getHslF()`` 在 PyQt5 返回 **4 元组**（含 alpha），写成 3 元组会
    ``ValueError``。
    """
    hue, sat, light, alpha = base.getHslF()
    out = QColor()
    out.setHslF(
        hue,
        min(max(sat + d_s, 0.0), 1.0),
        min(max(light + d_l, 0.0), 1.0),
        alpha,
    )
    return out


def statusColor(mode, role: StatusRole) -> QColor:
    """校验 / 提示状态的文字与图标色。

    ``Error`` 用上游原生 ``StatusDanger``；``Warning`` / ``Success`` 取定值（见
    :data:`_STATUS_COLORS`）；``Neutral`` 回落次要文字色。

    :param role: 也接受裸 int；非法值按 ``Neutral`` 处理。
    """
    try:
        role = StatusRole(role)
    except ValueError:
        role = StatusRole.Neutral
    if role == StatusRole.Neutral:
        return textMuted(mode)
    if role == StatusRole.Error:
        return _color(mode, _TC.StatusDanger)
    table = _STATUS_COLORS.get(mode) or _STATUS_COLORS[_TM.Light]
    return QColor(table.get(role, table[StatusRole.Warning]))


# ── 分类调色板（头像兜底色等） ────────────────────────────────


def chartPalette(mode=None) -> List[QColor]:
    """一组彼此可区分的分类色，用于「按名字稳定取色」的场景（头像兜底底色等）。

    复用 ``charts._tokens.ECHARTS_PALETTE``（**不另维护一份**，否则两套迟早漂移）。
    调色板主题无关，故 ``mode`` 只为签名对称。**每次返回新 list** —— 调用方常对
    单个元素做 ``setAlpha``，共享实例会让一次绘制污染全局。
    """
    from .charts._tokens import ECHARTS_PALETTE

    return [QColor(c) for c in ECHARTS_PALETTE]


# ── 强调色换色 ────────────────────────────────────────────────


#: 强调色三档的派生偏移，**从上游出厂值反解**：
#: Hover ΔS −22.5% / ΔL +5.9%(Light) −5.5%(Dark)；Press ΔS −39.0% / ΔL
#: +11.6%(Light) −10.8%(Dark)。规律是「饱和度降、亮度向表面靠拢」，用默认强调色走
#: 一遍 :func:`setAccentColor` → :func:`resetAccentColor` 能逐值还原出厂值
#: （回归测试 ``tests/theme/`` 钉住）。
_ACCENT_STEPS = {
    _TM.Light: {"hover": (-0.225, +0.059), "press": (-0.390, +0.116)},
    _TM.Dark: {"hover": (-0.222, -0.055), "press": (-0.385, -0.108)},
}

#: ``ToggleSwitchNoToggledCenter``（开关未激活的圆点）跟随强调色。它在上游是中性灰，
#: 不跟着走就会出现「强调色换了、开关圆点还是灰的」。
_SWITCH_CENTER_DS = -0.55

#: 上游出厂强调色，供 :func:`resetAccentColor` 还原。
_DEFAULT_ACCENT = {
    _TM.Light: QColor("#0067c0"),
    _TM.Dark: QColor("#4cc2ff"),
}

#: 上游出厂的开关圆点色（还原用）。
_DEFAULT_SWITCH_CENTER = {
    _TM.Light: QColor("#6a6a6a"),
    _TM.Dark: QColor("#d0d0d0"),
}


def setAccentColor(color: QColor, modes=None) -> None:
    """换强调色，**并一并派生写入 hover / press / 开关圆点**。

    :param color: 新的基础强调色。
    :param modes: 作用于哪些主题模式，默认两个都改。

    .. note:: 换色后**不会自动重绘**，调用方需自行触发（见模块 docstring）。
    """
    if color is None or not isinstance(color, QColor) or not color.isValid():
        return
    targets = list(modes) if modes else [_TM.Light, _TM.Dark]
    for mode in targets:
        steps = _ACCENT_STEPS.get(mode, _ACCENT_STEPS[_TM.Light])
        eTheme.setThemeColor(mode, _TC.PrimaryNormal, QColor(color))
        for slot, key in (
            (_TC.PrimaryHover, "hover"),
            (_TC.PrimaryPress, "press"),
        ):
            d_s, d_l = steps[key]
            eTheme.setThemeColor(mode, slot, _shift(color, d_s, d_l))
        eTheme.setThemeColor(
            mode, _TC.ToggleSwitchNoToggledCenter, _shift(color, _SWITCH_CENTER_DS, 0.0)
        )


def resetAccentColor(modes=None) -> None:
    """还原成上游出厂强调色（并按出厂值写回开关圆点，不重新派生）。"""
    targets = list(modes) if modes else [_TM.Light, _TM.Dark]
    for mode in targets:
        base = _DEFAULT_ACCENT.get(mode)
        if base is None:
            continue
        eTheme.setThemeColor(mode, _TC.PrimaryNormal, QColor(base))
        eTheme.setThemeColor(
            mode, _TC.ToggleSwitchNoToggledCenter, QColor(_DEFAULT_SWITCH_CENTER[mode])
        )
        # hover / press 一并回到出厂值，换回后视觉与「从未换过色」完全相同
        steps = _ACCENT_STEPS.get(mode, _ACCENT_STEPS[_TM.Light])
        for slot, key in ((_TC.PrimaryHover, "hover"), (_TC.PrimaryPress, "press")):
            d_s, d_l = steps[key]
            eTheme.setThemeColor(mode, slot, _shift(base, d_s, d_l))


def textOnAccent(color: Optional[QColor] = None) -> QColor:
    """强调色上的前景色（按亮度自动黑 / 白）。

    :param color: 底色。阈值取 0.6 —— 与上游按钮选黑/白的分界一致，偏亮才用深色
        前景，避免中间调（图表色常见）配出低对比的文字。
    """
    base = accent(ElaThemeType.ThemeMode.Light) if color is None else color
    if base.lightnessF() > 0.6:
        return QColor(0, 0, 0)
    return QColor(255, 255, 255)
