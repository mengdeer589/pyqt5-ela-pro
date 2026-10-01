"""
Markdown 查看器组件，风格参考 ElaWidgetTools 的 ElaMarkdownViewer。

基于 QTextBrowser 渲染 Markdown，支持主题自适应、流式追加（AI 对话场景）、
代码语法高亮（可选 Pygments）与轻量数学公式渲染。

由于 Qt 5.15 的 Markdown 导入器存在以下限制，本组件在原生渲染前做了
轻量预处理与渲染后处理：

- 围栏代码块不会渲染为等宽字体，也没有背景色；
- 行内代码 ``code`` 完全丢失代码语义；
- 链接颜色硬编码为蓝色，无法通过样式表或调色板覆盖，暗色主题下可读性差；
- 表格为左右贴边的全网格线且无内边距，观感陈旧；
- 任务列表 ``- [x]`` 不渲染勾选框；数学公式与锚点均不支持；
- 脚注、``==高亮==`` / ``~x~`` / ``^x^`` / emoji 短代码、GitHub Alert
  提示块、``[toc]`` 目录等扩展语法均不支持。

处理方式：围栏代码块在预处理时替换为占位符，解析后按占位符精确插入
代码内容并套用代码格式（可带语言标签行与悬浮复制按钮）；行内代码在解析后
按文本顺序定位并套用代码样式；正文与链接统一补上主题色；表格与代码块使用
与背景预混合的轻量色块，并预留上下间距；任务列表在预处理时替换为 ☑/☐；
数学公式由 :mod:`pyqt5_ela_pro.math_lite` 渲染为图片后按占位标记嵌入；
标题自动生成 slug 锚点并可由 ``[toc]`` 生成目录；脚注定义抽取到文末并
支持上标跳转；提示块按语义色加淡底。

流式增量渲染（``appendMarkdown``）与公式占位标记方案参考
InstructionX_UIKit（原库无 LICENSE，思路移植并适配 PyQt5）：
稳定段（围栏/公式块之外的空行边界）只渲染一次并追加进文档，未稳定尾部
在每次节流刷新时整体重渲染替换（超长段落退化为句末标点提交以限制重排
规模）；最终 ``endStream`` 全量重渲染，保证与一次性 ``setMarkdown`` 的
内容完全一致。超过 :data:`_LARGE_RENDER_CHARS` 的超长文档走分块渲染路径，
按时间片让出事件循环并发出 ``renderingProgress`` / ``renderingFinished``。

用法::

    viewer = ElaMarkdownViewer(parent=self)
    viewer.setMarkdown("# 标题\\n\\n正文内容")

    # 流式追加（AI 逐 token 输出）
    viewer.beginStream()
    viewer.appendMarkdown("# 标题\\n")
    viewer.appendMarkdown("正文 ")
    viewer.endStream()
"""

from __future__ import annotations

import base64
import hashlib
import math
import mimetypes
import os
import re
from typing import Optional

from PyQt5.QtCore import (
    QBuffer,
    QElapsedTimer,
    QEvent,
    QFileInfo,
    QIODevice,
    QMarginsF,
    QPoint,
    QPointF,
    QRectF,
    QSize,
    Qt,
    QTimer,
    QUrl,
    pyqtSignal,
)
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QCursor,
    QDesktopServices,
    QFont,
    QFontDatabase,
    QImage,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPalette,
    QPen,
    QTextBlockFormat,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    QTextDocumentFragment,
    QTextFormat,
    QTextImageFormat,
    QTextLength,
    QTextOption,
    QTextTable,
    QTextTableCellFormat,
    QTextTableFormat,
    QPageLayout,
    QPageSize,
    QPdfWriter,
)
from PyQt5 import sip
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QFrame,
    QTextBrowser,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from PyQt5ElaWidgetTools import (
    eTheme,
    ElaIcon,
    ElaIconType,
    ElaMenu,
    ElaScrollBar,
    ElaThemeType,
)

from ._internal import execElaMenu
from ._styles import FlatIconButton, setTransparentTextBase
from .math_lite import (
    MATH_ENVS,
    clear_cache as clear_math_cache,
    extract_math,
    render_formula,
)
from . import mermaid_support
from .mermaid_support import ElaMermaidRenderer
from .widget_base import ElaThemeWidget

#: 行内代码：`` `code` `` / ``` ``code`` ```（不允许跨行、不允许空内容）
_INLINE_CODE_RE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")

_FENCE_MARKERS = ("```", "~~~")

#: 围栏代码块占位符（私有区字符，正常文本不会出现）：
#: 预处理时替换为占位符，Markdown 解析后再用真实代码内容替换
_CODE_TOKEN_PREFIX = "\ue000elacode"
_CODE_TOKEN_SUFFIX = "\ue001"

#: Mermaid 围栏占位符与图片资源前缀
_MERMAID_TOKEN_PREFIX = "\ue000elamermaid"
_MERMAID_IMAGE_PREFIX = "elamermaid://"
_MERMAID_TIP_PREFIX = "Mermaid: "
#: Mermaid 待渲染任务视口优先级刷新间隔（毫秒）
_MERMAID_PRIORITY_INTERVAL_MS = 80
#: Mermaid 占位/降级图锚点前缀（异步结果按此定位）
_MERMAID_PENDING_PREFIX = "mermaid-pending-"
#: Mermaid 图片左右留白（与视口宽度相减）
_MERMAID_IMAGE_MARGIN = 24

#: 可折叠块（推理块 / details）：起始与结束占位符
_FOLD_TOKEN_PREFIX = "\ue000elafold"
_FOLD_END_TOKEN_PREFIX = "\ue000elafoldend"
#: 右键菜单行高（ElaMenu，与 terminal_view.py 一致）
_CONTEXT_MENU_ITEM_HEIGHT = 28

#: 内部控件锚点前缀（不显示 href tooltip）
_CONTROL_ANCHOR_PREFIXES = (
    "#elafold-",
    "#elacode-expand-",
    "#elatask-",
    "#fn-",
    "#fnref-",
)

#: 推理块标签（默认 `` ... ``，可经 ``setReasoningTag`` 修改/关闭）
_DEFAULT_REASONING_TAG = "think"
_DEFAULT_REASONING_LABEL = "思考过程"

#: front matter（YAML 头部）剥离：``---`` 开头且成对闭合
_FRONT_MATTER_RE = re.compile(r"\A---[ \t]*\r?\n.*?\r?\n---[ \t]*\r?\n?", re.DOTALL)

#: details 折叠块：``<details>`` + 可选 ``<summary>``
_DETAILS_OPEN_RE = re.compile(r"^<details>\s*$", re.IGNORECASE)
_DETAILS_CLOSE_RE = re.compile(r"^</details>\s*$", re.IGNORECASE)
_SUMMARY_RE = re.compile(r"^<summary>(.*)</summary>\s*$", re.IGNORECASE)

#: 任务列表：``- [x]`` / ``- [ ]`` → ☑ / ☐（保留列表标记与缩进）
_TASK_LIST_RE = re.compile(r"^([ \t]*(?:[-+*]|\d+[.)])[ \t]+)\[([ xX])\][ \t]?")

#: 行内下标 ``H~2~O`` / 上标 ``x^2^``（内容不含空白/方括号；不匹配 ``~~删除线~~``）
_SUB_RE = re.compile(r"(?<!~)~([^~\s\[\]]+)~(?!~)")
_SUP_RE = re.compile(r"(?<!\^)\^([^\^\s\[\]]+)\^(?!\^)")

#: 行内高亮 ``==text==``（内容含 Markdown 特殊符时不做处理，交给原生解析）
_MARK_RE = re.compile(r"==([^=\s](?:[^=]*[^=\s])?)==")
_MARK_SPECIAL_CHARS = ("*", "_", "[", "]", "`", "~", "<", ">")

#: emoji 短代码 ``:smile:`` → Unicode（仅覆盖常用集合，未知短代码原样保留）
_EMOJI_RE = re.compile(r":([a-z0-9_+-]+):")
_EMOJI_MAP = {
    "smile": "😄",
    "grin": "😁",
    "joy": "😂",
    "rofl": "🤣",
    "wink": "😉",
    "blush": "😊",
    "heart": "❤️",
    "broken_heart": "💔",
    "thumbsup": "👍",
    "+1": "👍",
    "thumbsdown": "👎",
    "-1": "👎",
    "ok_hand": "👌",
    "clap": "👏",
    "pray": "🙏",
    "muscle": "💪",
    "wave": "👋",
    "point_right": "👉",
    "point_left": "👈",
    "eyes": "👀",
    "thinking": "🤔",
    "sweat_smile": "😅",
    "cry": "😢",
    "sob": "😭",
    "angry": "😠",
    "rage": "😡",
    "scream": "😱",
    "sunglasses": "😎",
    "star": "⭐",
    "star2": "🌟",
    "sparkles": "✨",
    "fire": "🔥",
    "rocket": "🚀",
    "tada": "🎉",
    "balloon": "🎈",
    "gift": "🎁",
    "trophy": "🏆",
    "medal": "🏅",
    "warning": "⚠️",
    "check": "✅",
    "heavy_check_mark": "✔️",
    "x": "❌",
    "cross_mark": "❌",
    "question": "❓",
    "no_entry": "⛔",
    "bulb": "💡",
    "book": "📖",
    "books": "📚",
    "pencil": "📝",
    "gear": "⚙️",
    "wrench": "🔧",
    "hammer": "🔨",
    "bug": "🐛",
    "zap": "⚡",
    "boom": "💥",
    "100": "💯",
    "clock": "🕐",
    "hourglass": "⏳",
    "calendar": "📅",
    "pushpin": "📌",
    "paperclip": "📎",
    "link": "🔗",
    "lock": "🔒",
    "key": "🔑",
    "mag": "🔍",
    "chart": "📈",
    "package": "📦",
    "computer": "💻",
    "phone": "📱",
    "email": "📧",
    "speech_balloon": "💬",
    "arrow_right": "➡️",
    "arrow_left": "⬅️",
    "arrow_up": "⬆️",
    "arrow_down": "⬇️",
    "information_source": "ℹ️",
    "heavy_plus_sign": "➕",
    "heavy_minus_sign": "➖",
}

#: Callout 提示块：``> [!NOTE]`` 等（GitHub 风格）
_CALLOUT_RE = re.compile(
    r"^>[ \t]*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\][ \t]*$", re.IGNORECASE
)
_CALLOUT_LABELS = {
    "note": "提示",
    "tip": "技巧",
    "important": "重要",
    "warning": "警告",
    "caution": "注意",
}
_CALLOUT_COLORS = {
    "note": {"light": "#0969da", "dark": "#4493f8"},
    "tip": {"light": "#1a7f37", "dark": "#3fb950"},
    "important": {"light": "#8250df", "dark": "#ab7df8"},
    "warning": {"light": "#9a6700", "dark": "#d29922"},
    "caution": {"light": "#cf222e", "dark": "#f85149"},
}

#: 脚注定义 ``[^id]: text``（id 不允许空白）与引用 ``[^id]``
_FOOTNOTE_DEF_RE = re.compile(r"^\[\^([^\]\s]+)\]:[ \t]*(.*)$")
_FOOTNOTE_REF_RE = re.compile(r"\[\^([^\]\s]+)\]")

#: 独立目录行 ``[toc]``
_TOC_LINE_RE = re.compile(r"^\[toc\]$", re.IGNORECASE)

#: 引用块左缩进判定阈值（Qt Markdown 导入器为引用块设置 ~40px 左缩进）
_QUOTE_LEFT_MARGIN = 20.0

#: Typora（github.css）标题排版：级别 → (字号倍率, 上边距, 下边距, 行高%)
_HEADING_TYPOGRAPHY = {
    1: (2.25, 16.0, 16.0, 120.0),
    2: (1.75, 16.0, 16.0, 122.0),
    3: (1.5, 16.0, 16.0, 143.0),
    4: (1.25, 16.0, 16.0, 150.0),
    5: (1.0, 16.0, 16.0, 150.0),
    6: (1.0, 16.0, 16.0, 150.0),
}
#: 正文行高（百分比，Typora 风格松弛行距）
_BODY_LINE_HEIGHT = 160.0
#: 列表项 / 引用块的行间距（比段落紧凑）
_LIST_ITEM_MARGIN = 4.0
_QUOTE_BLOCK_MARGIN = 8.0
#: 普通段落的下边距（Typora 0.8em ≈ 12px）
_PARAGRAPH_MARGIN = 12.0
#: 表格与前后块的间距（Typora 0.8em ≈ 12px）
_TABLE_BLOCK_MARGIN = 12.0
#: h1 / h2 底部分隔线厚度（像素）
_HEADING_RULE_WIDTH = 1.0
#: 引用块左侧竖线（宽度 / 内缩，像素）
_QUOTE_RAIL_WIDTH = 4.0
_QUOTE_RAIL_INSET = 4.0
#: 分割线（hr）厚度（像素，opencode TUI 为 1px 正文色线）
_HR_LINE_WIDTH = 1.0
#: 代码卡圆角半径（像素，软卡片：无描边）
_CODE_CARD_RADIUS = 6.0
#: 行内代码水平内边距 / 圆角（像素）
_INLINE_CODE_PADDING = 3.0
_INLINE_CODE_RADIUS = 3.0

#: 脚注 / Callout / 高亮 / 目录占位符前缀（末尾拼索引或 id + ``_CODE_TOKEN_SUFFIX``）
_FOOTNOTE_REF_PREFIX = "\ue000elafnref"
_FOOTNOTE_DEF_PREFIX = "\ue000elafndef"
_MARK_TOKEN_PREFIX = "\ue000elamark"
_CALLOUT_TOKEN_PREFIX = "\ue000elacallout"
_TOC_TOKEN = "\ue000elatoc\ue001"

#: 代码块包裹表标记（存于 QTextTableFormat，fragment 复制后仍保留）
_CODE_MARKER = QTextFormat.UserProperty + 101
#: 代码块原始文本（存于 QTextTableFormat，供复制按钮精确取值）
_CODE_TEXT_PROPERTY = QTextFormat.UserProperty + 102
#: 代码块源行范围 "start,end"（存于 QTextTableFormat，供引用回复还原）
_CODE_SOURCE_PROPERTY = QTextFormat.UserProperty + 103
#: 代码块语言（存于 QTextTableFormat，供复制按钮 tooltip）
_CODE_LANG_PROPERTY = QTextFormat.UserProperty + 104
#: 分割线（hr）标记（存于块格式，Qt 自带横线颜色不可控，改为自绘 2px 线）
_HR_MARK = QTextFormat.UserProperty + 105
#: Callout 竖线颜色（存于块格式，值为 #rrggbb 字符串）
_CALLOUT_RAIL_PROPERTY = QTextFormat.UserProperty + 106
#: 行内代码标记（存于字符格式，供自绘圆角底与边框）
_INLINE_CODE_MARK = QTextFormat.UserProperty + 107
_CODE_MARKER_VALUE = "elacode"
#: 代码复制按钮尺寸（像素）
_CODE_BUTTON_SIZE = 24

#: 优先使用的代码字体（Windows 常见等宽字体），均不可用时回退系统等宽字体
_PREFERRED_CODE_FONTS = ("Consolas", "Cascadia Mono", "Courier New")

#: 超过该长度的代码块不做语法高亮（避免流式重排时词法分析开销）
_HIGHLIGHT_MAX_CHARS = 20000
#: 流式渲染中未闭合围栏超过该长度时暂不高亮（闭合后自动恢复）
_STREAM_HIGHLIGHT_MAX_CHARS = 4096
#: 高亮结果缓存条数
_HIGHLIGHT_CACHE_CAP = 32

#: 内部锚点返回栈上限
_ANCHOR_HISTORY_CAP = 50

#: 滚动跟随判定余量（像素）
_SCROLL_MARGIN = 4

#: 流式刷新间隔（毫秒）：按未稳定尾部大小自适应。
#:
#: 40ms 实测只有约 10.7 次视觉更新/秒 —— 不刷屏，但明显"跳"，读起来是分段
#: 出现而非逐字浮现（人眼平滑阈值约 20-40 次/秒，对齐 opencode 的 24ms 节奏）。
#: 改为 24ms 后实测 16.9-17.5 次/秒，**墙钟时间不变**（12 万字流式仍 7 次渲染、
#: 0.69s），即平滑度提升不花吞吐代价。150/400ms 两档保持不变 —— 它们负责
#: 在超长尾部时保护渲染吞吐，不该为观感让路。
_STREAM_INTERVAL = 24
_STREAM_INTERVAL_MID = 150
_STREAM_INTERVAL_LONG = 400
_STREAM_MID_CHARS = 16000
_STREAM_LONG_CHARS = 64000

#: 超长段落流式补充提交：未稳定尾部超过该长度后在句末标点处提交
_STREAM_SENTENCE_MIN = 4096
#: 超过该长度仍无句末标点时，退化为最近空白处软切（限制尾部重排规模）
_STREAM_SENTENCE_MAX = 16384
_SENTENCE_RE = re.compile(r"[。！？!?;；]")

#: 大文档分块渲染：超过该长度走分块路径（按空行边界切块，逐块提交）
_LARGE_RENDER_CHARS = 65536
_LARGE_RENDER_CHUNK = 8192
_LARGE_RENDER_BUDGET_MS = 16

#: Pygments 惰性导入状态（{"loaded": bool, "module": (get_lexer_by_name, Token) | None}）
_PYGMENTS_STATE = {"loaded": False, "module": None}

#: markdown 内置主题注册表：名称 → {"light": {...}, "dark": {...}}。
#: 每套主题含 ``semantic``（标题 / 加粗 / 斜体 / 行内代码 / 链接 / 引用 /
#: 列表 / 高亮底色）与 ``syntax``（13 个语法高亮 token 键）；结构色
#: （背景 / 正文 / 边框）仍由 eTheme 令牌提供。用 :func:`registerMarkdownTheme`
#: 可注册自定义主题，:func:`setDefaultMarkdownTheme` 改默认，查看器实例上
#: ``setMarkdownTheme(name)`` 切换。
_MD_THEME_SEMANTIC_KEYS = (
    "heading",
    "strong",
    "emphasis",
    "code",
    "link",
    "quote",
    "list",
    "mark",
)
_MD_THEME_SYNTAX_KEYS = (
    "keyword",
    "constant",
    "type",
    "function",
    "class",
    "decorator",
    "builtin",
    "attribute",
    "tag",
    "string",
    "number",
    "comment",
    "operator",
)

_MD_THEMES = {
    # opencode 终端版（默认）：标题紫/橙、加粗橙、斜体黄、行内码绿、链接青
    "opencode": {
        "light": {
            "semantic": {
                "heading": "#d68c27",
                "strong": "#d68c27",
                "emphasis": "#b0851f",
                "code": "#3d9a57",
                "link": "#318795",
                "quote": "#b0851f",
                "list": "#d68c27",
                "mark": "#f2cc0c",
            },
            "syntax": {
                "keyword": "#d68c27",
                "constant": "#d68c27",
                "type": "#b0851f",
                "function": "#3b7dd8",
                "class": "#b0851f",
                "decorator": "#3b7dd8",
                "builtin": "#3b7dd8",
                "attribute": "#d1383d",
                "tag": "#d1383d",
                "string": "#3d9a57",
                "number": "#d68c27",
                "comment": "#8a8a8a",
                "operator": "#318795",
            },
        },
        "dark": {
            "semantic": {
                "heading": "#9d7cd8",
                "strong": "#f5a742",
                "emphasis": "#e5c07b",
                "code": "#7fd88f",
                "link": "#56b6c2",
                "quote": "#e5c07b",
                "list": "#9d7cd8",
                "mark": "#f2cc0c",
            },
            "syntax": {
                "keyword": "#9d7cd8",
                "constant": "#f5a742",
                "type": "#e5c07b",
                "function": "#fab283",
                "class": "#e5c07b",
                "decorator": "#fab283",
                "builtin": "#fab283",
                "attribute": "#e06c75",
                "tag": "#e06c75",
                "string": "#7fd88f",
                "number": "#f5a742",
                "comment": "#808080",
                "operator": "#56b6c2",
            },
        },
    },
    # GitHub 风格：标题 / 强调沿用正文色（靠字重 / 斜体区分），链接蓝
    "github": {
        "light": {
            "semantic": {
                "heading": "#1f2328",
                "strong": "#1f2328",
                "emphasis": "#1f2328",
                "code": "#1f2328",
                "link": "#0969da",
                "quote": "#59636e",
                "list": "#1f2328",
                "mark": "#ffd33d",
            },
            "syntax": {
                "keyword": "#cf222e",
                "constant": "#0550ae",
                "type": "#953800",
                "function": "#8250df",
                "class": "#953800",
                "decorator": "#8250df",
                "builtin": "#0550ae",
                "attribute": "#0550ae",
                "tag": "#116329",
                "string": "#0a3069",
                "number": "#0550ae",
                "comment": "#59636e",
                "operator": "#59636e",
            },
        },
        "dark": {
            "semantic": {
                "heading": "#f0f6fc",
                "strong": "#f0f6fc",
                "emphasis": "#f0f6fc",
                "code": "#f0f6fc",
                "link": "#4493f8",
                "quote": "#9198a1",
                "list": "#f0f6fc",
                "mark": "#d29922",
            },
            "syntax": {
                "keyword": "#ff7b72",
                "constant": "#79c0ff",
                "type": "#ffa657",
                "function": "#d2a8ff",
                "class": "#ffa657",
                "decorator": "#d2a8ff",
                "builtin": "#79c0ff",
                "attribute": "#79c0ff",
                "tag": "#7ee787",
                "string": "#a5d6ff",
                "number": "#79c0ff",
                "comment": "#8b949e",
                "operator": "#c9d1d9",
            },
        },
    },
    # Solarized：黄 / 橙 / 紫 / 绿 / 蓝 五色语义
    "solarized": {
        "light": {
            "semantic": {
                "heading": "#b58900",
                "strong": "#cb4b16",
                "emphasis": "#6c71c4",
                "code": "#859900",
                "link": "#268bd2",
                "quote": "#657b83",
                "list": "#268bd2",
                "mark": "#b58900",
            },
            "syntax": {
                "keyword": "#859900",
                "constant": "#d33682",
                "type": "#b58900",
                "function": "#268bd2",
                "class": "#b58900",
                "decorator": "#6c71c4",
                "builtin": "#268bd2",
                "attribute": "#dc322f",
                "tag": "#dc322f",
                "string": "#2aa198",
                "number": "#d33682",
                "comment": "#93a1a1",
                "operator": "#657b83",
            },
        },
        "dark": {
            "semantic": {
                "heading": "#b58900",
                "strong": "#cb4b16",
                "emphasis": "#6c71c4",
                "code": "#859900",
                "link": "#268bd2",
                "quote": "#93a1a1",
                "list": "#268bd2",
                "mark": "#b58900",
            },
            "syntax": {
                "keyword": "#859900",
                "constant": "#d33682",
                "type": "#b58900",
                "function": "#268bd2",
                "class": "#b58900",
                "decorator": "#6c71c4",
                "builtin": "#268bd2",
                "attribute": "#dc322f",
                "tag": "#dc322f",
                "string": "#2aa198",
                "number": "#d33682",
                "comment": "#586e75",
                "operator": "#93a1a1",
            },
        },
    },
    # Dracula（深色）/ Alucard（浅色）
    "dracula": {
        "light": {
            "semantic": {
                "heading": "#644ac9",
                "strong": "#a34d14",
                "emphasis": "#846e15",
                "code": "#14710a",
                "link": "#036a96",
                "quote": "#6c664b",
                "list": "#a3144d",
                "mark": "#f1fa8c",
            },
            "syntax": {
                "keyword": "#a3144d",
                "constant": "#a3144d",
                "type": "#644ac9",
                "function": "#14710a",
                "class": "#644ac9",
                "decorator": "#14710a",
                "builtin": "#036a96",
                "attribute": "#a34d14",
                "tag": "#a34d14",
                "string": "#846e15",
                "number": "#644ac9",
                "comment": "#6c664b",
                "operator": "#a3144d",
            },
        },
        "dark": {
            "semantic": {
                "heading": "#bd93f9",
                "strong": "#ffb86c",
                "emphasis": "#f1fa8c",
                "code": "#50fa7b",
                "link": "#8be9fd",
                "quote": "#f1fa8c",
                "list": "#ff79c6",
                "mark": "#f1fa8c",
            },
            "syntax": {
                "keyword": "#ff79c6",
                "constant": "#bd93f9",
                "type": "#8be9fd",
                "function": "#50fa7b",
                "class": "#8be9fd",
                "decorator": "#50fa7b",
                "builtin": "#8be9fd",
                "attribute": "#ffb86c",
                "tag": "#ff79c6",
                "string": "#f1fa8c",
                "number": "#bd93f9",
                "comment": "#6272a4",
                "operator": "#ff79c6",
            },
        },
    },
}
#: 默认 markdown 主题（可用 setDefaultMarkdownTheme 调整，影响之后新建的查看器）
_DEFAULT_MD_THEME = "opencode"


def _md_theme_spec(name: str) -> dict:
    """取主题定义（未知名称回落默认主题）。"""
    return _MD_THEMES.get(name) or _MD_THEMES[_DEFAULT_MD_THEME]


def markdownThemes() -> list:
    """全部内置 / 已注册的 markdown 主题名（按注册顺序）。"""
    return list(_MD_THEMES)


def defaultMarkdownTheme() -> str:
    """获取新建查看器使用的默认 markdown 主题名。"""
    return _DEFAULT_MD_THEME


def setDefaultMarkdownTheme(name: str) -> bool:
    """设置默认 markdown 主题（只影响之后新建的查看器，不重渲染已存在实例）。

    :returns: 主题存在并设置成功返回 ``True``，未知名称返回 ``False``
    """
    global _DEFAULT_MD_THEME
    if name not in _MD_THEMES:
        return False
    _DEFAULT_MD_THEME = name
    return True


def registerMarkdownTheme(
    name: str, light: Optional[dict] = None, dark: Optional[dict] = None
) -> None:
    """注册 / 覆盖一套 markdown 主题。

    :param name: 主题名（覆盖同名主题；``"opencode"`` 亦可覆盖）
    :param light/dark: ``{"semantic": {...}, "syntax": {...}}``，可省略或只给
        部分键（其余键合并自 opencode 默认主题）。``semantic`` 的 8 个键为
        ``heading`` / ``strong`` / ``emphasis`` / ``code`` / ``link`` /
        ``quote`` / ``list``（列表项，含项目符号）/ ``mark``（``==高亮==``
        底色的基色，与背景混合后使用）。
    """
    if not isinstance(name, str) or not name:
        raise ValueError("registerMarkdownTheme: 主题名不能为空")
    base = _MD_THEMES.get("opencode") or {}
    _MD_THEMES[name] = {
        variant: _merge_md_variant(base.get(variant, {}), patch)
        for variant, patch in (("light", light), ("dark", dark))
    }


def unregisterMarkdownTheme(name: str) -> bool:
    """移除已注册主题（``"opencode"`` 不可移除）；返回是否移除成功。"""
    if name == "opencode" or name not in _MD_THEMES:
        return False
    _MD_THEMES.pop(name, None)
    return True


def _merge_md_variant(base: dict, patch: Optional[dict]) -> dict:
    """把主题补丁合并到基准变体上（只接受已存在的键与字符串值）。"""
    merged = {
        "semantic": dict(base.get("semantic") or {}),
        "syntax": dict(base.get("syntax") or {}),
    }
    if isinstance(patch, dict):
        for section in ("semantic", "syntax"):
            values = patch.get(section)
            if isinstance(values, dict):
                for key, value in values.items():
                    if key in merged[section] and isinstance(value, str):
                        merged[section][key] = value
    return merged


def _default_code_font_family() -> str:
    """选择默认代码字体族。"""
    families = set(QFontDatabase().families())
    for name in _PREFERRED_CODE_FONTS:
        if name in families:
            return name
    fixed_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
    return fixed_font.family() or _PREFERRED_CODE_FONTS[0]


#: 引用回复：源行 → 归一化文本（去 Markdown 标记，用于块级近似匹配）
_SOURCE_DECOR_RE = re.compile(
    r"^\s*(?:>+\s*|[-+*]\s+|\d+[.)]\s+|\[[ xX]\]\s+|#{1,6}\s+)+"
)
_INLINE_LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
_INLINE_SYMBOL_RE = re.compile(
    r"(\*\*|\*|__|_|~~|==|`+|<sub>|</sub>|<sup>|</sup>|~|\^)"
)


def _normalize_text(text: str) -> str:
    """块/行文本归一化：去装饰符、链接语法与全部空白（含任务标记）。"""
    text = text.replace("☑", "").replace("☐", "")
    text = _INLINE_LINK_RE.sub(lambda m: m.group(1), text)
    text = _SOURCE_DECOR_RE.sub("", text)
    text = _INLINE_SYMBOL_RE.sub("", text)
    return "".join(text.split())


def _source_line_text(line: str) -> str:
    """源行 → 归一化文本；不可匹配的行（代码围栏/占位符/标签/脚注定义）返回空。"""
    stripped = line.strip()
    if not stripped:
        return ""
    if stripped.startswith(_FENCE_MARKERS):
        return ""
    if any(
        token in stripped
        for token in (
            _FOLD_TOKEN_PREFIX,
            _FOLD_END_TOKEN_PREFIX,
            _CODE_TOKEN_PREFIX,
            _MERMAID_TOKEN_PREFIX,
            _FOOTNOTE_DEF_PREFIX,
            _TOC_TOKEN,
            _CALLOUT_TOKEN_PREFIX,
        )
    ):
        return ""
    if stripped.startswith(("<", "[")) and (
        _DETAILS_OPEN_RE.match(stripped)
        or _DETAILS_CLOSE_RE.match(stripped)
        or _SUMMARY_RE.match(stripped)
        or _FOOTNOTE_DEF_RE.match(line)
    ):
        return ""
    return _normalize_text(line)


def _match_source_lines(lines: list[str], start: int, block_text: str):
    """从 ``start`` 起搜索与块文本匹配的源行（支持跨行段落/合并引用）。

    在窗口内逐行作为起点尝试消费；累计文本必须是目标的前缀才继续，
    否则换下一行起点（避免把无关行误吞进匹配）。

    :returns: ``(匹配起始行号, 结束行号)``；无法匹配返回 ``None``
    """
    target = _normalize_text(block_text)
    if not target:
        return None
    total = len(lines)
    index = start
    while index < total and index < start + 80:
        if not _source_line_text(lines[index]):
            index += 1
            continue
        accumulated = ""
        cursor = index
        while cursor < total and cursor < index + 40:
            part = _source_line_text(lines[cursor])
            cursor += 1
            if not part:
                continue
            accumulated += part
            if accumulated == target:
                return (index, cursor)
            if not target.startswith(accumulated):
                break
        index += 1
    return None


def _front_matter_end(lines: list[str]) -> int:
    """front matter（``---`` 头部）结束后的行号；不存在返回 0。"""
    if not lines or lines[0].strip() != "---":
        return 0
    for index in range(1, min(len(lines), 200)):
        if lines[index].strip() == "---":
            return index + 1
    return 0


def _stable_cut(text: str, committed: int = 0, allow_sentence: bool = False) -> int:
    """返回围栏 / 块级公式之外的稳定提交边界偏移（无则 0）。

    稳定段只包含边界之前的内容；未闭合的围栏与公式块整体留在尾部，
    由流式刷新按当前结构渲染。``allow_sentence`` 用于超长段落：当没有
    空行边界且未稳定尾部过长时，退而在句末标点（或最近空白）处提交，
    避免每次刷新都重排整段超长文本。
    """
    lines = text.split("\n")
    offsets = [0]
    for line in lines[:-1]:
        offsets.append(offsets[-1] + len(line) + 1)
    n = len(lines)
    cut = 0
    sentence_cut = 0
    i = 0
    while i < n:
        stripped = lines[i].strip()
        if stripped.startswith(("```", "~~~")):
            mark = stripped[:3]
            i += 1
            while i < n and not lines[i].strip().startswith(mark):
                i += 1
            i += 1
            continue
        closer = None
        env_m = re.match(r"\\begin\{(\w+\*?)\}\s*$", stripped)
        if stripped in ("$$", "\\["):
            closer = stripped if stripped == "$$" else "\\]"
        elif env_m and env_m.group(1).rstrip("*") in MATH_ENVS:
            closer = "\\end{" + env_m.group(1) + "}"
        if closer is not None:
            i += 1
            while i < n and lines[i].strip() != closer:
                i += 1
            i += 1
            continue
        if lines[i] == "" and 0 < i < n - 1:
            cut = offsets[i + 1]
        elif allow_sentence and not lines[i].startswith(("    ", "\t")):
            for match in _SENTENCE_RE.finditer(lines[i]):
                sentence_cut = offsets[i] + match.end()
        i += 1

    if cut > committed:
        return cut
    if not allow_sentence:
        return cut
    if sentence_cut > committed and sentence_cut - committed >= _STREAM_SENTENCE_MIN:
        return sentence_cut
    if len(text) - committed >= _STREAM_SENTENCE_MAX:
        limit = min(committed + _STREAM_SENTENCE_MAX, len(text))
        pos = max(
            text.rfind(" ", committed, limit),
            text.rfind("\n", committed, limit),
        )
        if pos > committed:
            return pos + 1
    return cut


def _load_pygments():
    """惰性导入 Pygments（缺失时返回 None，组件自动降级为纯代码块样式）。

    :returns: ``(get_lexer_by_name, Token)`` 或 ``None``
    """
    if _PYGMENTS_STATE["loaded"]:
        return _PYGMENTS_STATE["module"]
    _PYGMENTS_STATE["loaded"] = True
    try:
        from pygments.lexers import get_lexer_by_name
        from pygments.token import Token

        _PYGMENTS_STATE["module"] = (get_lexer_by_name, Token)
    except ImportError:
        _PYGMENTS_STATE["module"] = None
    return _PYGMENTS_STATE["module"]


def _token_style(token_type, token, palette):
    """Pygments token → ``(颜色, 斜体)``；未覆盖的 token 返回 ``None``。"""
    if token_type in token.Comment:
        return palette["comment"], True
    if token_type in token.Keyword.Type:
        return palette["type"], False
    if token_type in token.Keyword.Constant:
        return palette["constant"], False
    if token_type in token.Keyword:
        return palette["keyword"], True
    if token_type in token.Name.Function:
        return palette["function"], False
    if token_type in token.Name.Class:
        return palette["class"], False
    if token_type in token.Name.Decorator:
        return palette["decorator"], False
    if token_type in token.Name.Builtin:
        return palette["builtin"], False
    if token_type in token.Name.Attribute:
        return palette["attribute"], False
    if token_type in token.Name.Tag:
        return palette["tag"], False
    if token_type in token.String:
        return palette["string"], False
    if token_type in token.Number:
        return palette["number"], False
    if token_type in token.Operator:
        return palette["operator"], False
    return None


class _ElaTextBrowser(QTextBrowser):
    """内部 QTextBrowser：按开关拦截远程图片资源（默认关闭）。"""

    #: 左键单击图片时发射（参数为文档位置）
    imageClicked = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.remote_images_enabled = False
        #: 嵌入模式：滚轮事件不消费，交给外层滚动容器
        self.forward_wheel = False
        self._press_pos = None

    def wheelEvent(self, event) -> None:  # noqa: N802 (Qt 命名)
        if self.forward_wheel:
            event.ignore()
            return
        super().wheelEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt 命名)
        """先画行内代码底、再走文档绘制、最后画装饰线（Typora 风格）。"""
        viewer = self.parent()
        under = getattr(viewer, "_paint_inline_code_backgrounds", None)
        if callable(under):
            painter = QPainter(self.viewport())
            try:
                under(self, painter)
            finally:
                painter.end()
        super().paintEvent(event)
        over = getattr(viewer, "_paint_document_decorations", None)
        if callable(over):
            painter = QPainter(self.viewport())
            try:
                over(self, painter)
            finally:
                painter.end()

    def loadResource(self, resource_type, url):  # noqa: N802 (Qt 命名)
        if (
            resource_type == QTextDocument.ResourceType.ImageResource
            and not self.remote_images_enabled
            and url.scheme() in ("http", "https")
        ):
            return None
        return super().loadResource(resource_type, url)

    def mousePressEvent(self, event) -> None:  # noqa: N802 (Qt 命名)
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_pos = event.pos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 (Qt 命名)
        super().mouseReleaseEvent(event)
        if event.button() != Qt.MouseButton.LeftButton:
            return
        press_pos = self._press_pos
        self._press_pos = None
        if press_pos is None or (event.pos() - press_pos).manhattanLength() > 4:
            return
        if self.textCursor().hasSelection():
            return
        cursor = self.cursorForPosition(event.pos())
        if cursor.charFormat().isImageFormat():
            self.imageClicked.emit(cursor.position())


class ElaMarkdownViewer(ElaThemeWidget):
    """Markdown 查看器。

    基于 QTextBrowser 渲染 Markdown，支持深浅色主题适配。

    - 围栏代码块渲染为带语言标签的卡片，可选语法高亮（Pygments），
      鼠标悬停右上角可一键复制，支持行号显示与超长折叠；
    - 行内代码以等宽字体 + 主题背景色渲染；
    - 任务列表 ``- [x]`` / ``- [ ]`` 渲染为可点击勾选的 ☑ / ☐；
    - 数学公式（``$...$`` / ``$$...$$``）由内置轻量渲染器绘制为图片，
      悬浮显示 LaTeX 源码，右键可复制；
    - Mermaid 围栏（`` ```mermaid ``）在安装可选依赖 ``mermaidx`` 时异步渲染为
      图片（缺失/失败时回退代码卡片），支持右键复制源码；
    - 表格去除全网格线，改为表头底色 + 行分隔线的轻量样式；
    - GitHub Alert 提示块（``> [!NOTE]`` 等）、脚注、``[toc]`` 目录、
      ``==高亮==`` / ``~x~`` / ``^x^`` / emoji 短代码；
    - 标题自动生成锚点，内部 ``#anchor`` 链接可跳转；
    - 图片支持基准路径（``setBaseUrl``）、超宽缩放与远程默认拦截，
      单击图片发出 ``imageClicked``；
    - 链接颜色跟随主题（``PrimaryNormal``），``linkActivated`` 转发点击；
    - 缩放（``setZoomFactor``）、搜索高亮（``searchText`` / ``findNext``）、
      导出（``toHtml`` / ``toPlainText`` / ``exportPdf``）；
    - ``appendMarkdown`` 支持流式追加（AI 逐 token 输出），贴底时自动跟随，
      末尾绘制闪烁打字光标；超长文档自动分块渲染并发出
      ``renderingProgress`` / ``renderingFinished``；
    - 主题切换时自动重新渲染已设置的内容。

    :param parent: 父控件
    """

    #: 流式追加收尾（``endStream``）时发射
    streamFinished = pyqtSignal()
    #: 链接被点击时发射（参数为 URL 字符串，含内部 ``#anchor``）
    linkActivated = pyqtSignal(str)
    #: 代码块内容被复制时发射（参数为代码文本）
    codeCopied = pyqtSignal(str)
    #: 公式 LaTeX 源码被复制时发射
    formulaCopied = pyqtSignal(str)
    #: Mermaid 源码被复制时发射
    mermaidCopied = pyqtSignal(str)
    #: 选中内容复制为 Markdown 时发射（参数为 Markdown 源）
    selectionQuoted = pyqtSignal(str)
    #: 图片被点击时发射（参数为解析后的 URL）
    imageClicked = pyqtSignal(str)
    #: 任务列表项被点击切换时发射（参数为序号与勾选状态）
    taskToggled = pyqtSignal(int, bool)
    #: 大文档分块渲染进度（0-100）
    renderingProgress = pyqtSignal(int)
    #: 大文档分块渲染完成
    renderingFinished = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._border_radius = 0
        #: 嵌入模式（透明背景 + 隐藏滚动条 + 高度随文档自适应）
        self._embedded = False
        #: 嵌入模式高度附加余量（避免取整误差触发内部滚动）
        self._embedded_extra = 2
        #: 嵌入模式是否裁剪文末空白（最后一段落的下边距不计入高度）
        self._embedded_trim_bottom = False
        #: 原始 Markdown 文本（``markdown()`` 原样返回，避免 toMarkdown 往返丢失）
        self._source = ""
        #: 行内代码文本（解析后按顺序定位并套用代码样式）
        self._inline_codes: list[str] = []
        #: 围栏代码块内容（预处理时转为占位符，解析后替换）：[(lang, code, closed)]
        self._fenced_blocks: list[tuple[str, str, bool]] = []
        #: Mermaid 代码块源码（与 ``_MERMAID_TOKEN_PREFIX`` 占位符索引对应）
        self._mermaid_blocks: list[str] = []
        #: Mermaid 渲染配置（``None`` 时自动探测 mermaidx）
        self._mermaid_override = None
        self._mermaid_disabled = False
        self._mermaid_renderer: Optional[ElaMermaidRenderer] = None
        #: Mermaid 待渲染任务队列（按视口距离优先，逐个提交给渲染器）
        self._mermaid_jobs: list[dict] = []
        self._mermaid_job_keys: set = set()
        #: 在途 Mermaid 请求数（引擎串行，>0 时不再提交下一个）
        self._mermaid_active = 0
        #: 引擎预热开关（默认关闭；开启后首次渲染不必等待引擎冷启动）
        self._mermaid_prewarm = False
        #: 视口优先级刷新计时器（滚动时节流重算）
        self._mermaid_priority_timer = QTimer(self)
        self._mermaid_priority_timer.setSingleShot(True)
        self._mermaid_priority_timer.setInterval(_MERMAID_PRIORITY_INTERVAL_MS)
        self._mermaid_priority_timer.timeout.connect(self._refresh_mermaid_priorities)
        #: 任务提交计时器（延后一拍，先让文档滚动/贴底逻辑生效再选下一个任务）
        self._mermaid_pump_timer = QTimer(self)
        self._mermaid_pump_timer.setSingleShot(True)
        self._mermaid_pump_timer.setInterval(0)
        self._mermaid_pump_timer.timeout.connect(self._pump_mermaid)
        #: 行内高亮文本（``==text==``，解析后按顺序套用背景色）
        self._mark_texts: list[str] = []
        #: 脚注定义（预处理时抽取到文末）：[(id, text)]
        self._footnote_defs: list[tuple[str, str]] = []
        #: Callout 类型序列（与占位符索引对应）
        self._callout_types: list[str] = []
        #: 任务列表项（预处理时记录）：[(源行号, 是否勾选)]
        self._task_items: list[tuple[int, bool]] = []
        #: 本文档标题列表（解析后收集）：[(level, text, slug)]
        self._headings: list[tuple[int, str, str]] = []
        #: 代码字体族
        self._code_font_family = _default_code_font_family()
        #: 超长代码折叠行数（0 表示关闭）
        self._code_collapse_lines = 0
        #: 已展开的代码块索引集合
        self._expanded_code_blocks: set[int] = set()
        #: 推理块标签（``None`` 关闭；默认 `` ... ``）
        self._reasoning_tag: Optional[str] = _DEFAULT_REASONING_TAG
        self._reasoning_label = _DEFAULT_REASONING_LABEL
        #: 可折叠块（推理 / ``<details>``）元数据与展开状态
        self._fold_blocks: list[dict] = []
        self._expanded_folds: set[int] = set()
        #: 围栏代码块的源行范围（与 ``_fenced_blocks`` 对应）：[(start, end)]
        self._fenced_source_lines: list[tuple[int, int]] = []
        #: 文档块号 → 源行范围（引用回复用；``None`` 表示未映射）
        self._block_source_map: dict[int, Optional[tuple[int, int]]] = {}
        #: 全量渲染时是否允许剥离 front matter（片段渲染不剥离）
        self._allow_front_matter = False
        #: 渲染降级记录：[(类型, 详情)]，全量渲染时重置
        self._render_issues: list[tuple[str, str]] = []
        #: 行号显示开关
        self._line_numbers_enabled = False
        #: 表格斑马纹开关与列宽（百分比列表；``None`` 表示自动）
        self._table_zebra = False
        self._table_column_widths: Optional[list] = None
        #: markdown 主题名（``setMarkdownTheme`` 切换，按浅 / 深自动取对应变体）
        self._md_theme = defaultMarkdownTheme()
        #: token 颜色覆盖（setCodeTokenColors；对所有主题生效）
        self._token_overrides: dict = {}
        #: 当前生效的 token 调色板（_applyThemeStyle 填充：主题 + 覆盖）
        self._token_palette: dict = {}
        #: 公式占位标记模板（实例唯一，跨实例零碰撞；结尾 q 是终止符）
        self._math_mark = f"elamath{id(self):x}z{{}}q"
        #: 高亮结果缓存 {(lang, code, theme_key): [(text, QColor, bold, italic)]}
        self._highlight_cache: dict = {}
        self._highlight_cache_cap = _HIGHLIGHT_CACHE_CAP
        # 主题色缓存（_applyThemeStyle 填充）
        self._text_color = QColor()
        self._link_color = QColor()
        self._code_bg = QColor()
        self._code_border = QColor()
        self._code_text = QColor()
        self._is_dark_theme = False
        self._table_header_bg = QColor()
        self._table_border = QColor()
        self._table_stripe_bg = QColor()
        self._base_bg = QColor()
        self._mark_bg = QColor()
        self._muted_color = QColor()
        self._placeholder_color = QColor()
        self._quote_rail_color = QColor()
        self._heading_rule_color = QColor()
        self._hr_color = QColor()
        self._search_bg = QColor()
        self._inline_code_bg = QColor()
        self._inline_code_border = QColor()
        self._code_button_hover_bg = QColor()
        self._code_button_press_bg = QColor()
        self._diff_add_bg = QColor()
        self._diff_del_bg = QColor()
        self._diff_hunk_bg = QColor()
        self.setObjectName("ElaMarkdownViewer")

        # 图片 / 占位 / 缩放 / 搜索状态
        self._base_url = QUrl()
        self._remote_images_enabled = False
        self._placeholder = ""
        self._zoom_factor = 1.0
        self._search_selections: list = []
        self._last_search = ""
        #: 内部锚点跳转前的滚动位置栈（供 backToPreviousAnchor 返回）
        self._anchor_back_stack: list[int] = []

        # 代码块悬浮复制按钮
        self._code_buttons: list[QToolButton] = []
        self._code_buttons_tables: list = []
        self._code_button_rects: list = []

        # 流式状态
        self._stream_active = False
        self._stream_source = ""
        self._stream_committed = 0
        self._stream_tail_pos = 0
        self._stream_first_flush = True
        self._stream_capture_at_bottom = True
        self._stick_to_bottom = True
        self._stream_timer = QTimer(self)
        self._stream_timer.setSingleShot(True)
        self._stream_timer.timeout.connect(self._stream_flush)

        # 流式末尾打字光标
        self._caret_visible = False
        self._caret_timer = QTimer(self)
        self._caret_timer.setInterval(500)
        self._caret_timer.timeout.connect(self._toggle_stream_caret)

        # 大文档分块渲染状态
        self._large_render_chunks: list[str] = []
        self._large_render_index = 0
        self._large_render_timer = QTimer(self)
        self._large_render_timer.setSingleShot(True)
        self._large_render_timer.timeout.connect(self._render_large_step)

        self._text_browser = _ElaTextBrowser(self)
        self._text_browser.setFrameShape(QFrame.Shape.NoFrame)
        self._text_browser.setReadOnly(True)
        # 必须为 False：Qt 的 QTextBrowserPrivate::_q_anchorClicked 在
        # openExternalLinks 为真时会先调 QDesktopServices::openUrl() 并**直接
        # return**，不再发出 anchorClicked —— 那样任务列表复选框（#elatask-）、
        # 代码/思考折叠（#elafold- / #elacode-expand-）与内部锚点跳转全部失效。
        # 外部链接改由 _on_anchor_clicked 自行打开（见 _open_external_links）。
        self._open_external_links = True
        self._text_browser.setOpenExternalLinks(False)
        self._text_browser.setWordWrapMode(
            QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere
        )
        self._text_browser.document().setUndoRedoEnabled(False)
        # 不按键也接收 MouseMove，代码块悬停复制按钮依赖此设置
        self._text_browser.viewport().setMouseTracking(True)
        self._text_browser.setVerticalScrollBar(ElaScrollBar(self._text_browser))
        self._text_browser.setHorizontalScrollBar(
            ElaScrollBar(Qt.Orientation.Horizontal, self._text_browser)
        )
        self._text_browser.anchorClicked.connect(self._on_anchor_clicked)
        self._text_browser.imageClicked.connect(self._on_image_clicked)
        self._text_browser.installEventFilter(self)
        self._text_browser.viewport().installEventFilter(self)
        self._text_browser.verticalScrollBar().valueChanged.connect(
            self._on_view_scrolled
        )
        self._text_browser.document().documentLayout().documentSizeChanged.connect(
            self._on_document_size_changed
        )

        base_font = self._text_browser.document().defaultFont()
        self._base_font_point_size = base_font.pointSizeF()
        if self._base_font_point_size <= 0:
            pixel = base_font.pixelSize()
            self._base_font_point_size = pixel * 0.75 if pixel > 0 else 10.0

        # 布局刷新（滚动/尺寸变化后重排代码复制按钮与图片宽度）
        self._layout_timer = QTimer(self)
        self._layout_timer.setSingleShot(True)
        self._layout_timer.timeout.connect(self._on_layout_refresh)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._text_browser)

        self._applyThemeStyle()

    # -- 内容 --------------------------------------------------------------

    def setMarkdown(self, text: str) -> None:
        """设置 Markdown 内容（重置流式状态；超长文本自动分块渲染）。

        :param text: Markdown 文本
        """
        self._stop_stream()
        self._cancel_large_render()
        self._expanded_code_blocks.clear()
        self._expanded_folds.clear()
        self._source = text or ""
        if len(self._source) > _LARGE_RENDER_CHARS:
            self._begin_large_render()
        else:
            self._render()

    def markdown(self) -> str:
        """获取当前 Markdown 内容（与传入的文本一致）。

        :returns: Markdown 文本
        """
        return self._source

    def clear(self) -> None:
        """清空内容。"""
        self.setMarkdown("")

    def document(self) -> QTextDocument:
        """返回底层 ``QTextDocument``，便于设置默认字体等高级选项。"""
        return self._text_browser.document()

    def textBrowser(self) -> QTextBrowser:
        """返回底层 ``QTextBrowser``（可访问 ``anchorClicked`` 等信号）。"""
        return self._text_browser

    def setOpenExternalLinks(self, on: bool) -> None:
        """设置链接是否用系统浏览器打开。

        内部锚点（``#elatask-`` / ``#elafold-`` / ``#elacode-expand-`` / ``#sec``）
        始终由组件自己处理；本开关只影响**带 scheme 的外部链接**是否交给系统浏览器。

        :param on: ``True`` 时外部链接用系统浏览器打开
        """
        self._open_external_links = bool(on)

    def openExternalLinks(self) -> bool:
        """外部链接是否使用系统浏览器打开。"""
        return self._open_external_links

    def scrollToAnchor(self, name: str) -> None:
        """滚动到指定锚点。

        :param name: 锚点名称
        """
        self._text_browser.scrollToAnchor(name)

    def backToPreviousAnchor(self) -> bool:
        """返回上一个内部锚点跳转前的位置。

        :returns: 是否成功返回（历史为空时 ``False``）
        """
        if not self._anchor_back_stack:
            return False
        value = self._anchor_back_stack.pop()
        bar = self._text_browser.verticalScrollBar()
        bar.setValue(min(value, bar.maximum()))
        return True

    def clearAnchorHistory(self) -> None:
        """清空内部锚点访问历史。"""
        self._anchor_back_stack.clear()

    def _on_anchor_clicked(self, url: QUrl) -> None:
        """链接点击：内部锚点跳转 / 折叠与任务勾选控制 + 外部链接 + 转发 ``linkActivated``。"""
        target = url.toString()
        if target.startswith("#elacode-expand-"):
            self._toggle_code_block_expanded(target[len("#elacode-expand-") :])
            return
        if target.startswith("#elafold-"):
            self._toggle_fold_expanded(target[len("#elafold-") :])
            return
        if target.startswith("#elatask-"):
            self._toggle_task_by_ordinal(target[len("#elatask-") :])
            return
        if not url.scheme() and url.fragment():
            self._anchor_back_stack.append(
                self._text_browser.verticalScrollBar().value()
            )
            if len(self._anchor_back_stack) > _ANCHOR_HISTORY_CAP:
                self._anchor_back_stack.pop(0)
            self._text_browser.scrollToAnchor(url.fragment())
            self.linkActivated.emit(target)
            return
        # 带 scheme / 绝对地址：外部链接。Qt 侧的 openExternalLinks 恒为 False
        # （否则 anchorClicked 不会发出），所以这里自己交给系统浏览器。
        if self._open_external_links:
            QDesktopServices.openUrl(url)
        self.linkActivated.emit(target)

    def _toggle_code_block_expanded(self, raw_index: str) -> None:
        """折叠链接点击：切换代码块展开状态并重渲染。"""
        try:
            index = int(raw_index)
        except (TypeError, ValueError):
            return
        if index in self._expanded_code_blocks:
            self._expanded_code_blocks.discard(index)
        else:
            self._expanded_code_blocks.add(index)
        self._render()

    def _toggle_fold_expanded(self, raw_index: str) -> None:
        """推理块 / details 折叠标签点击：切换展开状态并重渲染。"""
        try:
            index = int(raw_index)
        except (TypeError, ValueError):
            return
        if index in self._expanded_folds:
            self._expanded_folds.discard(index)
        else:
            self._expanded_folds.add(index)
        self._render()

    def _toggle_task_by_ordinal(self, raw: str) -> None:
        """任务复选框点击：翻转源文本并重渲染（流式期间忽略）。"""
        if self._stream_active:
            return
        try:
            ordinal = int(raw)
        except (TypeError, ValueError):
            return
        if not 0 <= ordinal < len(self._task_items):
            return
        line_index, checked = self._task_items[ordinal]
        lines = self._source.split("\n")
        if not 0 <= line_index < len(lines):
            return
        new_checked = not checked

        def flip(match):
            prefix = match.group(1)
            rest = match.group(0)[len(prefix) :]
            body = rest[3:]
            return prefix + ("[x]" if new_checked else "[ ]") + body

        replaced, count = _TASK_LIST_RE.subn(flip, lines[line_index], count=1)
        if count == 0:
            return
        lines[line_index] = replaced
        self._source = "\n".join(lines)
        self._render()
        self.taskToggled.emit(ordinal, new_checked)

    def _on_image_clicked(self, position: int) -> None:
        """图片单击：公式/Mermaid 复制源码，普通图片发射 ``imageClicked``。"""
        cursor = QTextCursor(self.document())
        cursor.setPosition(max(0, min(position, self.document().characterCount() - 1)))
        candidates = [cursor.charFormat()]
        probe = QTextCursor(cursor)
        if probe.movePosition(
            QTextCursor.MoveOperation.PreviousCharacter, QTextCursor.MoveMode.KeepAnchor
        ):
            candidates.append(probe.charFormat())
        for fmt in candidates:
            if not fmt.isImageFormat():
                continue
            image_format = fmt.toImageFormat()
            name = image_format.name()
            tooltip = image_format.toolTip()
            if name.startswith("elamath://"):
                if tooltip.startswith("LaTeX: "):
                    latex = tooltip[len("LaTeX: ") :]
                    QApplication.clipboard().setText(latex)
                    self.formulaCopied.emit(latex)
                return
            if name.startswith(_MERMAID_IMAGE_PREFIX):
                if tooltip.startswith(_MERMAID_TIP_PREFIX):
                    code = tooltip[len(_MERMAID_TIP_PREFIX) :]
                    QApplication.clipboard().setText(code)
                    self.mermaidCopied.emit(code)
                return
            url = self._resolve_image_url(name, self.document().baseUrl())
            self.imageClicked.emit(url.toString())
            return

    # -- 占位 / 缩放 / 搜索 / 图片 / 导出 ----------------------------------

    def setPlaceholderText(self, text: str) -> None:
        """设置内容为空时的居中占位文本（如"正在生成…"）。

        :param text: 占位文本，空字符串关闭
        """
        self._placeholder = text or ""
        self.update()

    def placeholderText(self) -> str:
        """获取占位文本。"""
        return self._placeholder

    def setZoomFactor(self, factor: float) -> None:
        """设置缩放系数（相对于默认字号，同时影响公式尺寸）。

        :param factor: 缩放系数（限制在 0.25-4.0）
        """
        factor = max(0.25, min(4.0, float(factor)))
        if abs(factor - self._zoom_factor) < 1e-6:
            return
        self._zoom_factor = factor
        font = self.document().defaultFont()
        font.setPointSizeF(self._base_font_point_size * factor)
        self.document().setDefaultFont(font)
        if self._source:
            self._render()

    def zoomFactor(self) -> float:
        """获取缩放系数。"""
        return self._zoom_factor

    def zoomIn(self, step: float = 0.1) -> None:
        """放大一级。"""
        self.setZoomFactor(self._zoom_factor + step)

    def zoomOut(self, step: float = 0.1) -> None:
        """缩小一级。"""
        self.setZoomFactor(self._zoom_factor - step)

    def searchText(self, text: str, caseSensitive: bool = False) -> int:
        """高亮全部匹配并选中第一处。

        :param text: 搜索文本
        :param caseSensitive: 是否区分大小写
        :returns: 匹配数量
        """
        self.clearSearch()
        if not text:
            return 0
        flags = QTextDocument.FindFlag(0)
        if caseSensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        cursor = QTextCursor(self.document())
        while True:
            found = self.document().find(text, cursor, flags)
            if found.isNull():
                break
            selection = QTextEdit.ExtraSelection()
            selection.cursor = found
            fmt = QTextCharFormat()
            fmt.setBackground(self._search_bg)
            selection.format = fmt
            self._search_selections.append(selection)
            cursor = found
        if self._search_selections:
            self._text_browser.setExtraSelections(self._search_selections)
            self._text_browser.setTextCursor(self._search_selections[0].cursor)
            self._last_search = text
        return len(self._search_selections)

    def findNext(self, backward: bool = False) -> bool:
        """在 ``searchText`` 的匹配间跳转（循环）。

        :param backward: 是否向前查找
        :returns: 是否成功跳转
        """
        if not self._search_selections:
            return False
        current = self._text_browser.textCursor().selectionStart()
        positions = [s.cursor.selectionStart() for s in self._search_selections]
        if backward:
            candidates = [p for p in positions if p < current]
            target = max(candidates) if candidates else positions[-1]
        else:
            candidates = [p for p in positions if p > current]
            target = min(candidates) if candidates else positions[0]
        self._text_browser.setTextCursor(
            self._search_selections[positions.index(target)].cursor
        )
        return True

    def clearSearch(self) -> None:
        """清除搜索高亮。"""
        self._search_selections = []
        self._last_search = ""
        self._text_browser.setExtraSelections([])

    def setBaseUrl(self, url) -> None:
        """设置图片等资源的基准路径（本地目录或 URL）。

        :param url: 本地目录路径字符串 / URL 字符串 / ``QUrl``
        """
        if isinstance(url, QUrl):
            qurl = QUrl(url)
        elif isinstance(url, str):
            if url.startswith(("http://", "https://", "file:")):
                qurl = QUrl(url)
            else:
                qurl = QUrl.fromLocalFile(url)
        else:
            raise TypeError(f"url 应为 str 或 QUrl，收到 {type(url).__name__}")
        if qurl.isLocalFile() and not qurl.path().endswith("/"):
            qurl.setPath(qurl.path() + "/")
        self._base_url = qurl
        self._text_browser.document().setBaseUrl(qurl)

    def baseUrl(self) -> QUrl:
        """获取资源基准路径。"""
        return self._base_url

    def setRemoteImagesEnabled(self, on: bool) -> None:
        """设置是否允许加载远程（http/https）图片，默认关闭。

        :param on: ``True`` 允许，``False`` 拦截并显示占位文本
        """
        self._remote_images_enabled = bool(on)
        self._text_browser.remote_images_enabled = bool(on)
        if self._source:
            self._render()

    def remoteImagesEnabled(self) -> bool:
        """是否允许加载远程图片。"""
        return self._remote_images_enabled

    def toHtml(self, embedImages: bool = False) -> str:
        """导出当前渲染结果为 HTML。

        :param embedImages: ``True`` 时把公式 / Mermaid / 本地图片内嵌为
            data URI（单文件分享用；远程图片保持原样），默认关闭
        """
        html = self.document().toHtml()
        if not embedImages:
            return html

        def replace(match: re.Match) -> str:
            embedded = self._embed_image_data_uri(match.group(2))
            if not embedded:
                return match.group(0)
            return match.group(1) + embedded + match.group(3)

        return re.sub(r'(<img\b[^>]*?\ssrc=")([^"]*)(")', replace, html)

    def _embed_image_data_uri(self, name: str) -> str:
        """图片名 → data URI（生成图片 / 本地文件；远程或缺失返回空串）。"""
        url = self._resolve_image_url(name, self.document().baseUrl())
        if url.scheme() in ("elamath", "elamermaid"):
            resource = self.document().resource(
                QTextDocument.ResourceType.ImageResource, url
            )
            if resource is None:
                return ""
            image = resource if isinstance(resource, QImage) else resource.toImage()
            if image.isNull():
                return ""
            buffer = QBuffer()
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            image.save(buffer, "PNG")
            data = bytes(buffer.data())
            return "data:image/png;base64," + base64.b64encode(data).decode("ascii")
        if not url.isLocalFile():
            return ""
        path = url.toLocalFile()
        if not os.path.isfile(path):
            return ""
        mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
        with open(path, "rb") as handle:
            data = handle.read()
        return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")

    def toPlainText(self) -> str:
        """导出当前渲染结果为纯文本。"""
        return self.document().toPlainText()

    def renderIssues(self) -> list:
        """获取本次渲染的降级记录。

        :returns: ``[(类型, 详情)]``，类型为 ``"math"`` / ``"mermaid"`` / ``"image"``；
            全量渲染时重置，流式期间追加
        """
        return list(self._render_issues)

    def markdownSelection(self) -> str:
        """把当前选中内容还原为 Markdown 源（块级近似）。

        - 代码块按源围栏精确还原（含围栏行）；
        - 普通块按归一化文本匹配源行，多块合并为连续切片；
        - 任一块无法映射时退回选中纯文本（无选中内容时返回空串）。
        """
        cursor = self._text_browser.textCursor()
        raw_selection = cursor.selection().toPlainText()
        if not cursor.hasSelection():
            return ""
        document = self.document()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        first = document.findBlock(start)
        last = document.findBlock(max(end - 1, start))
        if not first.isValid() or not last.isValid():
            return raw_selection
        ranges: list[tuple[int, int]] = []
        block = first
        while block.isValid():
            mapped = self._block_source_map.get(block.blockNumber())
            if block.text().strip() or mapped is not None:
                if mapped is None:
                    return raw_selection
                ranges.append(mapped)
            if block.blockNumber() >= last.blockNumber():
                break
            block = block.next()
        if not ranges:
            return raw_selection
        lines = self._source.split("\n")
        quote_start = min(item[0] for item in ranges)
        quote_end = max(item[1] for item in ranges)
        quote = "\n".join(lines[quote_start:quote_end]).strip("\n")
        return quote or raw_selection

    def _build_block_source_map(self) -> dict:
        """构建 文档块号 → 源行范围 的近似映射（引用回复用）。

        代码块使用表格式上记录的源围栏范围；普通块用归一化文本双指针匹配。
        """
        lines = self._source.split("\n")
        code_ranges: dict = {}
        for table in self._iter_tables(self.document()):
            stored = table.format().property(_CODE_SOURCE_PROPERTY)
            if not isinstance(stored, str):
                continue
            start_text, _, end_text = stored.partition(",")
            try:
                code_range = (int(start_text), int(end_text))
            except ValueError:
                continue
            for row in range(table.rows()):
                cell = table.cellAt(row, 0)
                first = cell.firstCursorPosition().blockNumber()
                last = cell.lastCursorPosition().blockNumber()
                for number in range(first, last + 1):
                    code_ranges[number] = code_range
        mapping: dict = {}
        source_index = 0
        block = self.document().begin()
        while block.isValid():
            number = block.blockNumber()
            code_range = code_ranges.get(number)
            if code_range is not None:
                mapping[number] = code_range
                source_index = max(source_index, code_range[1])
            else:
                text = block.text().strip()
                if not text:
                    mapping[number] = None
                else:
                    matched = _match_source_lines(lines, source_index, text)
                    if matched is not None:
                        mapping[number] = matched
                        source_index = matched[1]
                    else:
                        mapping[number] = None
            block = block.next()
        return mapping

    def exportPdf(
        self,
        path: str,
        *,
        pageSize="A4",
        marginsMm=15.0,
    ) -> bool:
        """把当前渲染结果导出为 PDF 文件。

        :param path: 目标文件路径
        :param pageSize: 纸张，``"A4"`` / ``"Letter"`` 等
            :class:`QPageSize.PageSizeId` 名称，或直接传 :class:`QPageSize`
        :param marginsMm: 页边距（毫米）：单值表示四边一致，
            二元组 ``(水平, 垂直)`` 或四元组 ``(左, 上, 右, 下)``
        :returns: 是否导出成功
        """
        if not path:
            return False
        if isinstance(pageSize, QPageSize):
            size = pageSize
        else:
            size_id = getattr(
                QPageSize.PageSizeId, str(pageSize).upper(), QPageSize.PageSizeId.A4
            )
            size = QPageSize(size_id)
        if isinstance(marginsMm, (int, float)):
            margins = QMarginsF(*([float(marginsMm)] * 4))
        else:
            values = [float(value) for value in marginsMm]
            if len(values) == 2:
                margins = QMarginsF(values[0], values[1], values[0], values[1])
            elif len(values) == 4:
                margins = QMarginsF(*values)
            else:
                margins = QMarginsF(15.0, 15.0, 15.0, 15.0)
        try:
            writer = QPdfWriter(str(path))
            writer.setResolution(96)
            writer.setPageSize(size)
            writer.setPageMargins(margins, QPageLayout.Unit.Millimeter)
            self.document().print_(writer)
        except Exception:
            return False
        return os.path.exists(path)

    def printDocument(self, printer=None) -> bool:
        """打印当前渲染内容。

        :param printer: 已配置的 :class:`QPrinter`；为 ``None`` 时弹出
            系统打印对话框（取消返回 ``False``）
        :returns: 是否完成打印
        """
        try:
            if printer is None:
                from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

                printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                dialog = QPrintDialog(printer, self)
                if dialog.exec_() != QDialog.DialogCode.Accepted:
                    return False
            self.document().print_(printer)
        except Exception:
            return False
        return True

    def isRendering(self) -> bool:
        """是否正在分块渲染大文档。"""
        return bool(self._large_render_chunks)

    def clearCache(self) -> None:
        """清空代码高亮、公式与 Mermaid 渲染缓存。"""
        self._highlight_cache.clear()
        clear_math_cache()
        if self._mermaid_renderer is not None:
            self._mermaid_renderer.clearCache()

    def setHighlightCacheSize(self, size: int) -> None:
        """设置代码高亮缓存条数上限。

        :param size: 缓存条数上限（<=0 时清空并停止缓存）
        """
        self._highlight_cache_cap = max(0, int(size))
        while (
            self._highlight_cache
            and len(self._highlight_cache) > self._highlight_cache_cap
        ):
            self._highlight_cache.pop(next(iter(self._highlight_cache)))

    def highlightCacheSize(self) -> int:
        """获取代码高亮缓存条数上限（0 表示不缓存）。"""
        return self._highlight_cache_cap

    # -- 流式追加 ----------------------------------------------------------

    def beginStream(self) -> None:
        """开始流式模式：清空内容，等待 ``appendMarkdown`` 追加。"""
        self._stop_stream()
        self._cancel_large_render()
        self._expanded_code_blocks.clear()
        self._expanded_folds.clear()
        self._block_source_map = {}
        self._stream_active = True
        self._stream_source = ""
        self._stream_committed = 0
        self._stream_tail_pos = 0
        self._stream_first_flush = True
        self._stream_capture_at_bottom = True
        self._source = ""
        # 清空文档会销毁旧代码表对象；按钮 / 表格引用必须同步失效，
        # 否则重绘或布局刷新会访问已删除的 C++ 对象（PyQt 静默 abort）
        self._rebuild_code_buttons([])
        self._text_browser.document().clear()
        self._caret_visible = True
        self._caret_timer.start()

    def appendMarkdown(self, chunk: str) -> None:
        """流式追加 Markdown 片段（AI 逐 token 输出场景）。

        稳定段只增量提交一次；未稳定的尾部按节流整体重渲染替换。
        贴底时自动跟随滚动，用户上翻后保持阅读位置。最终内容以
        ``endStream`` 的全量渲染为准。

        :param chunk: Markdown 片段
        """
        if not isinstance(chunk, str):
            raise TypeError(f"chunk 应为 str，收到 {type(chunk).__name__}")
        if not self._stream_active:
            self._cancel_large_render()
            bar = self._text_browser.verticalScrollBar()
            captured_at_bottom = bar.value() >= bar.maximum() - _SCROLL_MARGIN
            prefix = self._source
            self.beginStream()
            self._stream_capture_at_bottom = captured_at_bottom
            self._stream_source = prefix
        self._stream_source += chunk
        self._source = self._stream_source

        if self._stream_timer.isActive():
            return
        tail_len = len(self._stream_source) - self._stream_committed
        if tail_len > _STREAM_LONG_CHARS:
            interval = _STREAM_INTERVAL_LONG
        elif tail_len > _STREAM_MID_CHARS:
            interval = _STREAM_INTERVAL_MID
        else:
            interval = _STREAM_INTERVAL
        self._stream_timer.start(interval)

    def endStream(self) -> None:
        """结束流式模式：全量重渲染，保证与一次性设置内容一致。"""
        if not self._stream_active:
            return
        self._stop_stream()
        self._source = self._stream_source
        self._render()
        self.streamFinished.emit()

    def isStreaming(self) -> bool:
        """当前是否处于流式模式。"""
        return self._stream_active

    def setStickToBottom(self, on: bool) -> None:
        """设置贴底时是否自动跟随滚动。

        :param on: ``True`` 时内容在底部则追加后自动滚到底
        """
        self._stick_to_bottom = bool(on)

    def stickToBottom(self) -> bool:
        """是否贴底自动跟随。"""
        return self._stick_to_bottom

    def _stop_stream(self) -> None:
        if not sip.isdeleted(self._stream_timer):
            self._stream_timer.stop()
        if not sip.isdeleted(self._caret_timer):
            self._caret_timer.stop()
        if self._caret_visible:
            self._caret_visible = False
            if not sip.isdeleted(self):
                self.update()
        self._stream_active = False

    def _toggle_stream_caret(self) -> None:
        """流式末尾打字光标闪烁。"""
        if sip.isdeleted(self):
            return
        self._caret_visible = not self._caret_visible
        self.update()

    # -- 大文档分块渲染 ----------------------------------------------------

    @staticmethod
    def _split_large_chunks(text: str) -> list:
        """按空行 / 换行 / 空白边界把超长文本切成渲染块。"""
        chunks: list[str] = []
        start = 0
        length = len(text)
        while start < length:
            end = min(start + _LARGE_RENDER_CHUNK, length)
            if end < length:
                floor = start + _LARGE_RENDER_CHUNK // 2
                cut = text.rfind("\n\n", floor, end)
                if cut == -1:
                    cut = text.rfind("\n", floor, end)
                if cut == -1:
                    cut = text.rfind(" ", floor, end)
                if cut != -1:
                    end = cut + 1
            chunks.append(text[start:end])
            start = end
        return chunks

    def _begin_large_render(self) -> None:
        """启动分块渲染：清空文档后按时间片逐块提交。"""
        self._large_render_chunks = self._split_large_chunks(self._source)
        self._large_render_index = 0
        self._render_issues = []
        # 同 beginStream：清空文档前先让旧代码表引用失效（分块渲染期间
        # 事件循环仍会重绘，访问已删除表格会 PyQt abort）
        self._rebuild_code_buttons([])
        self._text_browser.document().clear()
        self._large_render_timer.start(0)

    def _render_large_step(self) -> None:
        """渲染一个时间片内的若干块，随后让出事件循环。"""
        if sip.isdeleted(self) or sip.isdeleted(self._text_browser):
            return
        if not self._large_render_chunks:
            return
        timer = QElapsedTimer()
        timer.start()
        document = self._text_browser.document()
        total = len(self._large_render_chunks)
        while (
            self._large_render_index < total
            and timer.elapsed() < _LARGE_RENDER_BUDGET_MS
        ):
            chunk = self._large_render_chunks[self._large_render_index]
            cursor = QTextCursor(document)
            cursor.movePosition(QTextCursor.MoveOperation.End)
            if document.characterCount() > 1:
                cursor.insertBlock(QTextBlockFormat(), QTextCharFormat())
            first_chunk = self._large_render_index == 0
            if first_chunk:
                self._allow_front_matter = True
            try:
                cursor.insertFragment(self._render_fragment(chunk, document))
            finally:
                if first_chunk:
                    self._allow_front_matter = False
            self._large_render_index += 1
        self.renderingProgress.emit(int(self._large_render_index * 100 / total))
        if self._large_render_index >= total:
            self._finish_large_render()
        else:
            self._large_render_timer.start(0)

    def _finish_large_render(self) -> None:
        self._large_render_chunks = []
        self._large_render_index = 0
        self.renderingProgress.emit(100)
        self._sync_code_buttons()
        self._schedule_layout_refresh()
        self.renderingFinished.emit()

    def _cancel_large_render(self) -> None:
        self._large_render_timer.stop()
        self._large_render_chunks = []
        self._large_render_index = 0

    def _stream_flush(self) -> None:
        """流式刷新：提交新稳定段并替换未稳定尾部。

        迟到的定时器回调可能落在控件已销毁之后（窗口关闭 / 消息重建），
        此时直接忽略，避免访问已删除的 C++ 对象（PyQt 会 abort）。
        """
        if sip.isdeleted(self) or sip.isdeleted(self._text_browser):
            return
        try:
            self._flush_stream()
        except Exception:
            if sip.isdeleted(self) or sip.isdeleted(self._text_browser):
                return
            # 增量状态异常：退回全量渲染，保证内容正确
            self._stop_stream()
            self._render()

    def _flush_stream(self) -> None:
        browser = self._text_browser
        document = browser.document()
        bar = browser.verticalScrollBar()
        old_value, old_max = bar.value(), bar.maximum()
        at_bottom = old_value >= old_max - _SCROLL_MARGIN
        if self._stream_first_flush:
            # 从静态模式续写时 beginStream 会清空文档，首个 flush 的
            # max==0 不能作为贴底依据；使用清空前捕获的滚动状态
            at_bottom = self._stream_capture_at_bottom
            self._stream_first_flush = False

        browser.setUpdatesEnabled(False)
        try:
            cut = max(
                _stable_cut(
                    self._stream_source,
                    self._stream_committed,
                    allow_sentence=True,
                ),
                self._stream_committed,
            )

            # 删除旧尾部
            if document.characterCount() > 1:
                # 必须先丢弃 _code_buttons_tables：removeSelectedText 会连带销毁
                # 尾段里的代码卡 QTextTable，而 _schedule_layout_refresh 是 80ms 后
                # 才补 _sync_code_buttons —— 期间任何一次重绘都会让
                # _paint_code_card_chrome 访问已析构的表对象（0xC0000409 静默 abort）。
                self._rebuild_code_buttons([])
                cursor = QTextCursor(document)
                position = min(self._stream_tail_pos, document.characterCount() - 1)
                cursor.setPosition(position)
                cursor.movePosition(
                    QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor
                )
                cursor.removeSelectedText()
            else:
                self._stream_tail_pos = 0

            # 提交新稳定段（只渲染一次）
            if cut > self._stream_committed:
                segment = self._stream_source[self._stream_committed : cut]
                cursor = QTextCursor(document)
                cursor.movePosition(QTextCursor.MoveOperation.End)
                if document.characterCount() > 1:
                    cursor.insertBlock(QTextBlockFormat(), QTextCharFormat())
                cursor.insertFragment(self._render_fragment(segment, document))
                self._stream_committed = cut

            self._stream_tail_pos = document.characterCount() - 1

            # 渲染未稳定尾部
            tail = self._stream_source[self._stream_committed :]
            if tail:
                cursor = QTextCursor(document)
                cursor.movePosition(QTextCursor.MoveOperation.End)
                if document.characterCount() > 1:
                    cursor.insertBlock(QTextBlockFormat(), QTextCharFormat())
                cursor.insertFragment(self._render_fragment(tail, document))
        finally:
            browser.setUpdatesEnabled(True)

        if self._stick_to_bottom and at_bottom:
            bar.setValue(bar.maximum())
        else:
            bar.setValue(min(old_value, bar.maximum()))
        browser.viewport().update()
        self._sync_embedded_height()
        # 立刻重建代码按钮（不要等 80ms 后的 _schedule_layout_refresh）
        self._sync_code_buttons()
        self._schedule_layout_refresh()

    def _render_fragment(self, text: str, resource_doc: QTextDocument):
        """把一段 Markdown 渲染为可插入主文档的片段。

        使用临时文档走与全量渲染完全相同的管线（代码/表格/公式/主题色），
        因此片段插入后与一次性渲染结果一致；公式图片资源注册在主文档上，
        片段插入后仍可解析。
        """
        scratch = QTextDocument()
        scratch.setDefaultStyleSheet(self._document_css())
        scratch.setDefaultFont(self.document().defaultFont())
        scratch.setBaseUrl(self._text_browser.document().baseUrl())
        self._render_into(scratch, text, resource_doc=resource_doc)
        cursor = QTextCursor(scratch)
        cursor.select(QTextCursor.SelectionType.Document)
        return QTextDocumentFragment(cursor)

    # -- 外观 --------------------------------------------------------------

    def setCodeFontFamily(self, family: str) -> None:
        """设置代码字体族。

        :param family: 字体族名称，空字符串恢复系统等宽字体
        """
        if family:
            self._code_font_family = family
        else:
            self._code_font_family = _default_code_font_family()
        self._highlight_cache.clear()
        self._applyThemeStyle()

    def codeFontFamily(self) -> str:
        """获取代码字体族。"""
        return self._code_font_family

    def setCodeBlockCollapseLines(self, lines: int) -> None:
        """设置超长代码块折叠行数（0 表示关闭折叠）。

        :param lines: 折叠后显示的行数
        """
        self._code_collapse_lines = max(0, int(lines))
        if self._source:
            self._render()

    def codeBlockCollapseLines(self) -> int:
        """获取代码块折叠行数。"""
        return self._code_collapse_lines

    def setLineNumbersEnabled(self, on: bool) -> None:
        """设置代码块行号显示（默认关闭；复制内容不含行号）。

        :param on: 是否显示行号
        """
        on = bool(on)
        if on == self._line_numbers_enabled:
            return
        self._line_numbers_enabled = on
        if self._source:
            self._render()

    def lineNumbersEnabled(self) -> bool:
        """是否显示代码块行号。"""
        return self._line_numbers_enabled

    def setCodeTokenColors(self, colors: Optional[dict] = None) -> None:
        """覆盖代码高亮 token 颜色（``None`` 清除覆盖、回到主题自带配色）。

        可用键：``keyword/constant/type/function/class/decorator/builtin/
        attribute/tag/string/number/comment/operator``（未提供的键保留主题默认；
        覆盖对浅 / 深两套同时生效）。

        :param colors: ``{token 类型: 颜色字符串}``
        """
        overrides = {}
        if colors:
            for key, value in colors.items():
                if key in _MD_THEME_SYNTAX_KEYS and isinstance(value, str):
                    overrides[key] = value
        self._token_overrides = overrides
        self._applyThemeStyle()

    def codeTokenColors(self) -> dict:
        """获取当前主题 / 模式下的 token 调色板（含覆盖；颜色为 hex 字符串）。"""
        return dict(self._token_palette)

    def setMarkdownTheme(self, name: str) -> bool:
        """切换 markdown 主题（内置 / 已注册），立即重渲染已有内容。

        :param name: :func:`markdownThemes` 里的主题名
        :returns: 切换成功（或本来就是该主题）返回 ``True``；未知名称返回
            ``False`` 且不改动当前主题
        """
        if name not in _MD_THEMES:
            return False
        if name == self._md_theme:
            return True
        self._md_theme = name
        self._applyThemeStyle()
        return True

    def markdownTheme(self) -> str:
        """当前 markdown 主题名（默认取 :func:`defaultMarkdownTheme`）。"""
        return self._md_theme

    def setTableZebra(self, on: bool) -> None:
        """设置表格斑马纹（数据行奇偶淡底）。

        :param on: 是否启用
        """
        on = bool(on)
        if on == self._table_zebra:
            return
        self._table_zebra = on
        if self._source:
            self._render()

    def tableZebra(self) -> bool:
        """是否启用表格斑马纹。"""
        return self._table_zebra

    def setTableColumnWidths(self, widths: Optional[list] = None) -> None:
        """按百分比设置 Markdown 表格列宽（``None`` 恢复自动）。

        :param widths: 每列百分比（如 ``[60, 40]``）；
            数量与表格列数不一致时该表忽略设置
        """
        if widths is None:
            self._table_column_widths = None
        else:
            try:
                values = [float(width) for width in widths]
            except (TypeError, ValueError):
                return
            if not values or any(width <= 0 for width in values):
                self._table_column_widths = None
            else:
                self._table_column_widths = values
        if self._source:
            self._render()

    def tableColumnWidths(self) -> Optional[list]:
        """获取当前表格列宽设置（``None`` 表示自动）。"""
        if self._table_column_widths is None:
            return None
        return list(self._table_column_widths)

    def setBorderRadius(self, r: int) -> None:
        """设置圆角半径。

        :param r: 圆角半径（像素）
        """
        self._border_radius = max(0, r)
        self.update()

    def borderRadius(self) -> int:
        """获取圆角半径。

        :returns: 圆角半径（像素）
        """
        return self._border_radius

    # -- 嵌入模式 ----------------------------------------------------------

    def setEmbeddedMode(self, on: bool) -> None:
        """嵌入模式：透明背景、隐藏内部滚动条、高度随文档自适应。

        适合把查看器嵌进聊天消息等外层滚动容器：

        - 不再自绘背景（由父容器提供底色）；
        - 两个滚动条始终隐藏，滚轮事件交给外层容器；
        - 文档高度变化（含流式追加）时自动调整控件高度。

        :param on: 是否启用（默认关闭，关闭后恢复原有行为）
        """
        on = bool(on)
        if on == self._embedded:
            return
        self._embedded = on
        policy = (
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            if on
            else Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._text_browser.setVerticalScrollBarPolicy(policy)
        self._text_browser.setHorizontalScrollBarPolicy(policy)
        self._text_browser.forward_wheel = on
        if on:
            self._sync_embedded_height()
        else:
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)
            self.updateGeometry()
        self.update()

    def embeddedMode(self) -> bool:
        """是否处于嵌入模式。"""
        return self._embedded

    def setEmbeddedExtra(self, extra: int) -> None:
        """设置嵌入模式高度余量（像素，默认 2）。

        :param extra: 追加到文档高度上的余量，避免取整误差触发内部滚动
        """
        self._embedded_extra = max(0, int(extra))
        self._sync_embedded_height()

    def embeddedExtra(self) -> int:
        """获取嵌入模式高度余量（像素）。"""
        return self._embedded_extra

    def setEmbeddedTrimBottom(self, on: bool) -> None:
        """设置嵌入模式是否裁剪文末空白（默认关闭）。

        开启后，控件高度不再包含文末段落的下边距（Qt Markdown 导入器会给
        每个段落加下边距，最后一个段落的下边距是纯空白），控件底边贴合
        正文内容 —— 聊天消息中「正文 → 工具面板 / 下一步思考」的视觉间距
        因此与其它分段间距一致。表格 / 代码块等非段落结尾按块边界取更小
        值（``min``），不会裁剪内容。
        """
        on = bool(on)
        if on == self._embedded_trim_bottom:
            return
        self._embedded_trim_bottom = on
        self._sync_embedded_height()

    def embeddedTrimBottom(self) -> bool:
        """是否裁剪嵌入模式下的文末空白。"""
        return self._embedded_trim_bottom

    def _sync_embedded_height(self) -> None:
        """嵌入模式下按文档高度更新控件高度（幂等，仅变化时应用）。"""
        if not self._embedded:
            return
        document = self._text_browser.document()
        margins = self._text_browser.contentsMargins()
        content = document.size().height()
        if self._embedded_trim_bottom:
            content = min(content, self._embedded_content_bottom(document))
        height = (
            int(math.ceil(content + margins.top() + margins.bottom()))
            + self._embedded_extra
        )
        height = max(1, height)
        if self._embedded_trim_bottom:
            # 裁剪后控件高度小于文档高度，内部出现可滚动范围：必须把滚动位置
            # 归零（否则 QTextBrowser 会贴底显示文末边距、并裁掉首行上边距）。
            bar = self._text_browser.verticalScrollBar()
            if bar.value() != 0:
                bar.setValue(0)
        if self.minimumHeight() == height and self.maximumHeight() == height:
            return
        self.setFixedHeight(height)

    @staticmethod
    def _embedded_content_bottom(document: QTextDocument) -> float:
        """文末内容底边（不含最后一段落的下边距与文末文档边距）。

        布局未就绪（流式首帧 / 宽度为 0）时返回文档高度，保持原行为。
        """
        total = document.size().height()
        last = document.lastBlock()
        if not last.isValid():
            return total
        rect = document.documentLayout().blockBoundingRect(last)
        if rect.height() <= 0 or rect.bottom() <= 0:
            return total
        return rect.bottom()

    # -- 渲染 --------------------------------------------------------------

    def _render(self) -> None:
        """按当前主题全量渲染 ``_source``。"""
        browser = self._text_browser
        document = browser.document()
        bar = browser.verticalScrollBar()
        old_value, old_max = bar.value(), bar.maximum()
        at_bottom = old_value >= old_max - _SCROLL_MARGIN

        browser.setUpdatesEnabled(False)
        try:
            self._render_issues = []
            self._allow_front_matter = True
            self._render_into(document, self._source)
        finally:
            self._allow_front_matter = False
            browser.setUpdatesEnabled(True)
        self._block_source_map = self._build_block_source_map()
        if self._stream_active:
            # 全量渲染后增量状态失效，从头重新提交
            self._stream_committed = 0
            self._stream_tail_pos = 0
        if at_bottom:
            bar.setValue(bar.maximum())
        else:
            bar.setValue(min(old_value, bar.maximum()))
        browser.viewport().update()
        self._sync_code_buttons()
        self._sync_embedded_height()
        self._schedule_layout_refresh()

    def _render_into(
        self,
        document: QTextDocument,
        source: str,
        resource_doc: Optional[QTextDocument] = None,
    ) -> None:
        """完整渲染管线（主文档与流式片段临时文档共用）。

        :param document: 目标文档
        :param source: Markdown 源文
        :param resource_doc: 公式图片资源注册文档（缺省为目标文档）
        """
        processed, maths = extract_math(source, self._math_mark)
        processed = self._preprocess(processed)
        document.setMarkdown(processed)
        self._insert_fenced_code(document)
        self._apply_inline_code_formats(document)
        self._replace_mark_tokens(document)
        self._replace_footnote_refs(document)
        self._apply_footnote_defs(document)
        self._apply_heading_anchors(document)
        self._replace_toc_token(document)
        self._apply_folds(document)
        self._style_callouts(document)
        self._style_typography(document)
        self._style_tables(document)
        self._apply_fragment_colors(document)
        self._style_task_markers(document)
        if maths:
            self._embed_math(document, maths, resource_doc or document)
        self._apply_images(document, resource_doc)
        self._embed_mermaid(
            document, resource_doc, reset=document is self._text_browser.document()
        )

    @staticmethod
    def _collect_footnote_defs(lines: list[str]) -> tuple[list, set]:
        """收集围栏之外的脚注定义行。

        :returns: ``(defs, indices)``：``[(id, text)]`` 与定义行号集合
        """
        defs: list[tuple[str, str]] = []
        indices: set[int] = set()
        seen: set[str] = set()
        fence: Optional[str] = None
        for index, line in enumerate(lines):
            stripped = line.strip()
            if fence is not None:
                if stripped.startswith(fence):
                    fence = None
                continue
            if not line.startswith((" ", "\t")) and stripped.startswith(_FENCE_MARKERS):
                fence = stripped[:3]
                continue
            match = _FOOTNOTE_DEF_RE.match(line)
            if match and match.group(1) not in seen:
                seen.add(match.group(1))
                indices.add(index)
                defs.append((match.group(1), match.group(2).strip()))
        return defs, indices

    def _extract_folds(self, lines: list[str]) -> tuple[list[str], list[dict]]:
        """扫描可折叠块（推理标签 / ``<details>``）并替换为占位符行。

        - 围栏代码块内的标签不处理；
        - 未闭合的块标记 ``pending``（流式期间标签显示"思考中…"）；
        - 内容行原样保留（渲染后按展开状态隐藏或展示）。

        :returns: ``(改写后的行, [(kind, label, pending)])``
        """
        result: list[str] = []
        folds: list[dict] = []
        tag = (self._reasoning_tag or "").strip()
        open_re = (
            re.compile(rf"^<{re.escape(tag)}>\s*$", re.IGNORECASE) if tag else None
        )
        close_re = (
            re.compile(rf"^</{re.escape(tag)}>\s*$", re.IGNORECASE) if tag else None
        )
        fence: Optional[str] = None
        index = 0
        i = 0
        total = len(lines)
        index_map: list[int] = []

        def append(text: str, raw_index: int) -> None:
            result.append(text)
            index_map.append(raw_index)

        def append_fold(
            start: int, end: int, meta: dict, closed: bool, anchor: int
        ) -> None:
            nonlocal index
            if result and result[-1].strip():
                append("", anchor)
            append(f"{_FOLD_TOKEN_PREFIX}{index}{_CODE_TOKEN_SUFFIX}", anchor)
            append("", anchor)
            for raw in range(start, end):
                append(lines[raw], raw)
            if closed:
                append("", anchor)
                append(f"{_FOLD_END_TOKEN_PREFIX}{index}{_CODE_TOKEN_SUFFIX}", anchor)
                append("", anchor)
            folds.append(meta)
            index += 1

        while i < total:
            stripped = lines[i].strip()
            if fence is not None:
                if stripped.startswith(fence):
                    fence = None
                append(lines[i], i)
                i += 1
                continue
            if not lines[i].startswith((" ", "\t")) and stripped.startswith(
                _FENCE_MARKERS
            ):
                fence = stripped[:3]
                append(lines[i], i)
                i += 1
                continue
            if open_re is not None and open_re.match(stripped):
                j = i + 1
                while j < total and not close_re.match(lines[j].strip()):
                    j += 1
                closed = j < total
                append_fold(
                    i + 1,
                    j,
                    {
                        "kind": "reasoning",
                        "label": self._reasoning_label if closed else "思考中…",
                        "pending": not closed,
                    },
                    closed,
                    i,
                )
                i = j + 1 if closed else total
                continue
            if _DETAILS_OPEN_RE.match(stripped):
                depth = 1
                label = "详情"
                content_start = i + 1
                if content_start < total:
                    summary = _SUMMARY_RE.match(lines[content_start].strip())
                    if summary:
                        label = summary.group(1).strip() or label
                        content_start += 1
                k = content_start
                while k < total and depth > 0:
                    inner = lines[k].strip()
                    if _DETAILS_OPEN_RE.match(inner):
                        depth += 1
                    elif _DETAILS_CLOSE_RE.match(inner):
                        depth -= 1
                        if depth == 0:
                            break
                    k += 1
                closed = depth == 0
                append_fold(
                    content_start,
                    k if closed else total,
                    {"kind": "details", "label": label, "pending": not closed},
                    closed,
                    i,
                )
                i = k + 1 if closed else total
                continue
            append(lines[i], i)
            i += 1
        return result, folds, index_map

    def _preprocess(self, text: str) -> str:
        """预处理 Markdown 源文。

        - 围栏代码块（含未闭合）替换为唯一占位符，解析后精确插入；
        - 任务列表 ``- [x]`` / ``- [ ]`` 替换为 ☑ / ☐；
        - 行内代码记录文本，解析后按顺序定位上色；
        - 行内下标 ``~x~``/上标 ``^x^`` 改写为 ``<sub>/<sup>``，
          ``==高亮==`` 记录后着色，``:emoji:`` 替换为 Unicode；
        - 脚注定义抽取到文末，引用替换为占位符；
        - Callout 标记行替换为占位符，解析后套用提示块样式；
        - 独立 ``[toc]`` 行替换为占位符，解析后生成目录；
        - 推理标签 / ``<details>`` 折叠块替换为占位符，解析后按状态折叠。
        """
        raw_lines = text.split("\n")
        if self._allow_front_matter:
            front_end = _front_matter_end(raw_lines)
            if front_end:
                for number in range(front_end):
                    raw_lines[number] = ""
        lines, folds, index_map = self._extract_folds(raw_lines)
        fn_defs, fn_def_lines = self._collect_footnote_defs(raw_lines)
        defined = {fid for fid, _ in fn_defs}

        out: list[str] = []
        inline_codes: list[str] = []
        fenced_blocks: list[tuple[str, str]] = []
        fenced_source_lines: list[tuple[int, int]] = []
        mermaid_blocks: list[str] = []
        marks: list[str] = []
        callouts: list[str] = []
        tasks: list[tuple[int, bool]] = []
        fence: Optional[str] = None
        fence_lang = ""
        fence_start = 0
        buffer: list[str] = []

        def emit_closed_fence(
            lang: str, code: str, start_line: int, end_line: int
        ) -> None:
            """闭合围栏：mermaid 且启用渲染时产出 Mermaid 占位符，否则代码卡片。"""
            if lang == "mermaid" and code.strip() and self._mermaid_enabled():
                mermaid_blocks.append(code)
                out.append(
                    f"{_MERMAID_TOKEN_PREFIX}{len(mermaid_blocks) - 1}"
                    f"{_CODE_TOKEN_SUFFIX}"
                )
                return
            token = f"{_CODE_TOKEN_PREFIX}{len(fenced_blocks)}{_CODE_TOKEN_SUFFIX}"
            fenced_blocks.append((lang, code, True))
            fenced_source_lines.append((start_line, end_line))
            out.append(token)

        def transform(segment: str) -> str:
            if not segment:
                return segment

            def replace_ref(match):
                fid = match.group(1)
                if fid not in defined:
                    return match.group(0)
                return f"{_FOOTNOTE_REF_PREFIX}{fid}{_CODE_TOKEN_SUFFIX}"

            # 脚注引用先替换为占位符，避免 ``^`` 被上标规则误配
            segment = _FOOTNOTE_REF_RE.sub(replace_ref, segment)
            segment = _SUB_RE.sub(lambda m: f"<sub>{m.group(1)}</sub>", segment)
            segment = _SUP_RE.sub(lambda m: f"<sup>{m.group(1)}</sup>", segment)

            def replace_mark(match):
                content = match.group(1)
                if any(ch in content for ch in _MARK_SPECIAL_CHARS):
                    return match.group(0)
                marks.append(content)
                return f"{_MARK_TOKEN_PREFIX}{len(marks) - 1}{_CODE_TOKEN_SUFFIX}"

            segment = _MARK_RE.sub(replace_mark, segment)
            return _EMOJI_RE.sub(
                lambda m: _EMOJI_MAP.get(m.group(1).lower(), m.group(0)), segment
            )

        def transform_line(line: str) -> str:
            """行内语法转换（行内代码区间原样保留并记录）。"""
            pieces: list[str] = []
            last = 0
            for match in _INLINE_CODE_RE.finditer(line):
                pieces.append(transform(line[last : match.start()]))
                pieces.append(match.group(0))
                inline_codes.append(match.group(2))
                last = match.end()
            pieces.append(transform(line[last:]))
            return "".join(pieces)

        for line_no, line in enumerate(lines):
            raw_index = index_map[line_no]
            stripped = line.strip()
            if fence is not None:
                if stripped.startswith(fence):
                    emit_closed_fence(
                        fence_lang, "\n".join(buffer), fence_start, raw_index + 1
                    )
                    fence = None
                    fence_lang = ""
                    buffer = []
                else:
                    buffer.append(line)
                continue

            if raw_index in fn_def_lines:
                # 定义行抽取到文末；正文以空行占位避免段落粘连
                out.append("")
                continue

            if not line.startswith((" ", "\t")) and stripped.startswith(_FENCE_MARKERS):
                fence = stripped[:3]
                fence_lang = stripped[3:].strip().split(" ", 1)[0].lower()
                fence_start = raw_index
                continue

            callout = _CALLOUT_RE.match(stripped)
            if callout is not None:
                callouts.append(callout.group(1).lower())
                out.append(
                    f"> {_CALLOUT_TOKEN_PREFIX}{len(callouts) - 1}{_CODE_TOKEN_SUFFIX}"
                )
                continue

            if _TOC_LINE_RE.match(stripped):
                out.append(_TOC_TOKEN)
                continue

            def replace_task(match, line_index=raw_index):
                checked = match.group(2).lower() == "x"
                tasks.append((line_index, checked))
                marker = "☑" if checked else "☐"
                return f"{match.group(1)}[{marker}](#elatask-{len(tasks) - 1})"

            line = _TASK_LIST_RE.sub(replace_task, line)
            out.append(transform_line(line))

        if fence is not None:
            # 未闭合围栏：同样按代码块渲染（GitHub 语义），流式期间体验更好
            token = f"{_CODE_TOKEN_PREFIX}{len(fenced_blocks)}{_CODE_TOKEN_SUFFIX}"
            fenced_blocks.append((fence_lang, "\n".join(buffer), False))
            fenced_source_lines.append((fence_start, len(lines)))
            out.append(token)

        if fn_defs:
            out.append("")
            out.append("---")
            out.append("")
            for index, (fid, body) in enumerate(fn_defs, start=1):
                out.append(
                    f"{_FOOTNOTE_DEF_PREFIX}{index}{_CODE_TOKEN_SUFFIX} [{index}] {body}"
                )
                out.append("")

        self._inline_codes = inline_codes
        self._fenced_blocks = fenced_blocks
        self._fenced_source_lines = fenced_source_lines
        self._mark_texts = marks
        self._footnote_defs = fn_defs
        self._callout_types = callouts
        self._task_items = tasks
        self._mermaid_blocks = mermaid_blocks
        self._fold_blocks = folds
        return "\n".join(out)

    # -- 代码块 ------------------------------------------------------------

    def _code_format(self) -> QTextCharFormat:
        """行内代码格式（等宽 + 标记属性；底色/圆角由自绘提供）。"""
        fmt = QTextCharFormat()
        fmt.setFontFamilies(
            [self._code_font_family, "Microsoft YaHei UI", "Microsoft YaHei"]
        )
        fmt.setFontFixedPitch(True)
        point_size = self._math_point_size()
        if point_size > 0:
            fmt.setFontPointSize(point_size * 0.92)
        fmt.setProperty(_INLINE_CODE_MARK, True)
        fmt.setForeground(self._md_code_color)
        return fmt

    def _code_text_format(self) -> QTextCharFormat:
        """围栏代码文本格式（0.9em 等宽，Typora 风格；底色由单元格提供）。"""
        fmt = QTextCharFormat()
        fmt.setFontFamilies(
            [self._code_font_family, "Microsoft YaHei UI", "Microsoft YaHei"]
        )
        fmt.setFontFixedPitch(True)
        fmt.setForeground(self._code_text)
        base_font = self.document().defaultFont()
        point_size = base_font.pointSizeF()
        if point_size > 0:
            fmt.setFontPointSize(point_size * 0.9)
        return fmt

    def _code_table_format(
        self,
        lang: str,
        code: str,
        source_lines: Optional[tuple] = None,
    ) -> QTextTableFormat:
        """代码块包裹表格式：整行宽度、无边框（Typora 风格纯底色卡片）。"""
        fmt = QTextTableFormat()
        fmt.setBorder(0)
        fmt.setBorderCollapse(True)
        fmt.setCellPadding(0)
        fmt.setCellSpacing(0)
        fmt.setWidth(QTextLength(QTextLength.Type.PercentageLength, 100))
        fmt.setTopMargin(8)
        fmt.setBottomMargin(8)
        fmt.setAlignment(Qt.AlignmentFlag.AlignLeft)
        fmt.setProperty(_CODE_MARKER, _CODE_MARKER_VALUE)
        fmt.setProperty(_CODE_TEXT_PROPERTY, code)
        fmt.setProperty(_CODE_LANG_PROPERTY, lang)
        if source_lines is not None:
            fmt.setProperty(
                _CODE_SOURCE_PROPERTY, f"{source_lines[0]},{source_lines[1]}"
            )
        return fmt

    def _code_cell_format(self) -> QTextTableCellFormat:
        """代码单元格格式：底色 + 内边距（Qt 富文本无块级 padding）。"""
        fmt = QTextTableCellFormat()
        fmt.setBackground(QBrush(self._code_bg))
        fmt.setBorder(0)
        fmt.setTopPadding(9)
        fmt.setBottomPadding(9)
        fmt.setLeftPadding(14)
        fmt.setRightPadding(14)
        return fmt

    def _insert_fenced_code(self, document: QTextDocument) -> None:
        """用真实代码内容替换占位符：表格包裹（可选语言标签行）+ 语法高亮。

        逐行字符底色会覆盖块 margin，导致多段围栏灰色连片、无内边距；
        改为表格：底色与 padding 由单元格提供，块间距由表格外边距提供。
        有语言时首行渲染语言标签；支持超长代码折叠与行号显示。
        """
        if not self._fenced_blocks:
            return
        # 多张代码卡合并成一次编辑块：每张卡内部的 endEditBlock 都会触发重排，
        # 一页几十个代码块时能省下可观的布局时间（嵌套编辑块 Qt 会一并合并）
        outer = QTextCursor(document)
        outer.beginEditBlock()
        try:
            for index, (lang, code_text, closed) in enumerate(self._fenced_blocks):
                token = f"{_CODE_TOKEN_PREFIX}{index}{_CODE_TOKEN_SUFFIX}"
                found = document.find(token)
                if found.isNull():
                    continue
                source_lines = (
                    self._fenced_source_lines[index]
                    if index < len(self._fenced_source_lines)
                    else None
                )
                self._insert_code_card(
                    found,
                    lang,
                    code_text,
                    closed=closed,
                    fold_index=index,
                    source_lines=source_lines,
                )
        finally:
            outer.endEditBlock()

    def _insert_code_card(
        self,
        cursor: QTextCursor,
        lang: str,
        code_text: str,
        closed: bool = True,
        fold_index: Optional[int] = None,
        source_lines: Optional[tuple] = None,
    ) -> None:
        """把当前选中的占位符替换为代码卡片（Typora 风格：无头栏、单行）。

        语言标签不再占一行，改为存入表格式供复制按钮 tooltip 展示。
        """
        document = cursor.document()
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        table = cursor.insertTable(
            1, 1, self._code_table_format(lang, code_text, source_lines)
        )
        code_cell = table.cellAt(0, 0)
        code_cell.setFormat(self._code_cell_format())
        cell_cursor = code_cell.firstCursorPosition()

        lines = code_text.split("\n")
        collapsed = (
            fold_index is not None
            and self._code_collapse_lines > 0
            and not self._stream_active
            and len(lines) > self._code_collapse_lines + 1
            and fold_index not in self._expanded_code_blocks
        )
        visible_code = (
            "\n".join(lines[: self._code_collapse_lines]) if collapsed else code_text
        )
        highlight_lang = lang
        if not closed and len(visible_code) > _STREAM_HIGHLIGHT_MAX_CHARS:
            # 未闭合围栏的中间态跳过高亮：内容每次刷新都在增长，
            # 全量词法分析且缓存中间态会显著拖慢流式渲染
            highlight_lang = ""
        self._insert_code_text(cell_cursor, visible_code, highlight_lang)
        if fold_index is not None:
            self._insert_code_fold_link(cell_cursor, fold_index, lines, collapsed)
        self._style_code_cell_blocks(document, code_cell)
        cursor.endEditBlock()

    def _insert_code_text(
        self, cell_cursor: QTextCursor, code_text: str, lang: str
    ) -> None:
        """把代码写入单元格（可选行号；``diff`` 行级底色；逐行拆分保留高亮）。"""
        styles = self._highlight_code(code_text, lang)
        is_diff = lang.lower() == "diff"
        if not self._line_numbers_enabled and not is_diff:
            for text, fmt in styles:
                if text:
                    cell_cursor.insertText(text, fmt)
            return
        lines = self._split_styled_lines(styles)
        width = len(str(len(lines)))
        number_format = self._line_number_format()
        for position, parts in enumerate(lines):
            if position:
                cell_cursor.insertBlock(QTextBlockFormat(), QTextCharFormat())
            line_bg = self._diff_line_background(parts) if is_diff else None
            if self._line_numbers_enabled:
                number_fmt = number_format
                if line_bg is not None:
                    number_fmt = QTextCharFormat(number_format)
                    number_fmt.setBackground(line_bg)
                cell_cursor.insertText(f"{position + 1:>{width}}  ", number_fmt)
            for text, fmt in parts:
                if not text:
                    continue
                if line_bg is not None:
                    fmt = QTextCharFormat(fmt)
                    fmt.setBackground(line_bg)
                cell_cursor.insertText(text, fmt)

    def _diff_line_background(self, parts: list) -> Optional[QBrush]:
        """``diff`` 代码行底色：``+`` 绿、``-`` 红、``@@`` 蓝（其余无）。"""
        text = "".join(part[0] for part in parts).lstrip()
        if text.startswith("@@"):
            return QBrush(self._diff_hunk_bg)
        if text.startswith("+") and not text.startswith("+++"):
            return QBrush(self._diff_add_bg)
        if text.startswith("-") and not text.startswith("---"):
            return QBrush(self._diff_del_bg)
        return None

    def _insert_code_fold_link(
        self, cell_cursor: QTextCursor, index: int, lines: list, collapsed: bool
    ) -> None:
        """折叠/展开链接行（仅在启用折叠且代码足够长时插入）。"""
        if self._code_collapse_lines <= 0 or self._stream_active:
            return
        if len(lines) <= self._code_collapse_lines + 1:
            return
        cell_cursor.insertBlock(QTextBlockFormat(), QTextCharFormat())
        fmt = QTextCharFormat(self._code_text_format())
        fmt.setAnchor(True)
        fmt.setAnchorHref(f"#elacode-expand-{index}")
        fmt.setForeground(self._link_color)
        if collapsed:
            remaining = len(lines) - self._code_collapse_lines
            cell_cursor.insertText(f"▸ 展开其余 {remaining} 行", fmt)
        else:
            cell_cursor.insertText("▾ 收起", fmt)

    @staticmethod
    def _split_styled_lines(styles: list) -> list:
        """高亮 token 序列按换行拆分为每行的 [(文本, 格式)]。"""
        lines: list[list] = [[]]
        for text, fmt in styles:
            parts = text.split("\n")
            for position, part in enumerate(parts):
                if position:
                    lines.append([])
                if part:
                    lines[-1].append((part, fmt))
        return lines

    def _line_number_format(self) -> QTextCharFormat:
        """行号字符格式：等宽、次级文字色。"""
        fmt = QTextCharFormat(self._code_text_format())
        fmt.setForeground(self._muted_color)
        return fmt

    @staticmethod
    def _style_code_cell_blocks(document: QTextDocument, cell) -> None:
        """代码单元格内块：行高 130%、上下 margin 0（间距由单元格 padding 提供）。"""
        first = cell.firstCursorPosition().blockNumber()
        last = cell.lastCursorPosition().blockNumber()
        block = document.findBlockByNumber(first)
        while block.isValid() and block.blockNumber() <= last:
            block_format = block.blockFormat()
            block_format.setLineHeight(
                130.0, QTextBlockFormat.LineHeightTypes.ProportionalHeight
            )
            block_format.setTopMargin(0)
            block_format.setBottomMargin(0)
            cursor = QTextCursor(document)
            cursor.setPosition(block.position())
            cursor.setBlockFormat(block_format)
            block = block.next()

    def _highlight_code(self, code: str, lang: str) -> list:
        """代码 → [(文本, 字符格式)]；未安装 Pygments / 无语言时整段底色。"""
        base = self._code_text_format()
        module = _load_pygments()
        if module is None or not lang or len(code) > _HIGHLIGHT_MAX_CHARS:
            return [(code, base)]
        get_lexer_by_name, token_module = module
        theme_key = "dark" if self._is_dark_theme else "light"
        cache_key = (lang, code, theme_key)
        cached = self._highlight_cache.get(cache_key)
        if cached is not None:
            return cached
        try:
            lexer = get_lexer_by_name(lang, stripnl=False, ensurenl=False)
        except Exception:
            return [(code, base)]
        palette = self._token_palette
        result = []
        try:
            for token_type, value in lexer.get_tokens(code):
                if not value:
                    continue
                fmt = QTextCharFormat(base)
                style = _token_style(token_type, token_module, palette)
                if style is not None:
                    color, italic = style
                    fmt.setForeground(QColor(color))
                    if italic:
                        fmt.setFontItalic(True)
                result.append((value, fmt))
        except Exception:
            return [(code, base)]
        if not result:
            return [(code, base)]
        if self._highlight_cache_cap > 0:
            while len(self._highlight_cache) >= self._highlight_cache_cap:
                self._highlight_cache.pop(next(iter(self._highlight_cache)))
            self._highlight_cache[cache_key] = result
        return result

    def _in_code_table(self, cursor: QTextCursor) -> bool:
        """游标是否位于代码块包裹表内。"""
        frame = cursor.currentFrame()
        while frame is not None:
            if isinstance(frame, QTextTable) and self._is_code_table(frame):
                return True
            frame = frame.parentFrame()
        return False

    # -- 行内增强 / 脚注 / 锚点 / Callout -----------------------------------

    def _replace_mark_tokens(self, document: QTextDocument) -> None:
        """把 ``==高亮==`` 占位符替换为带主题背景色的文本。"""
        if not self._mark_texts:
            return
        for index, content in enumerate(self._mark_texts):
            token = f"{_MARK_TOKEN_PREFIX}{index}{_CODE_TOKEN_SUFFIX}"
            found = document.find(token)
            if found.isNull():
                continue
            found.beginEditBlock()
            found.removeSelectedText()
            fmt = QTextCharFormat()
            fmt.setBackground(QBrush(self._mark_bg))
            found.insertText(content, fmt)
            found.endEditBlock()

    def _replace_footnote_refs(self, document: QTextDocument) -> None:
        """把脚注引用占位符替换为上标编号链接（``[n](#fn-id)``）。

        每个脚注的首次引用处同时附加 ``fnref-id`` 锚点，供定义区编号回跳。
        """
        if not self._footnote_defs:
            return
        anchored: set[str] = set()
        for index, (fid, _body) in enumerate(self._footnote_defs, start=1):
            token = f"{_FOOTNOTE_REF_PREFIX}{fid}{_CODE_TOKEN_SUFFIX}"
            while True:
                found = document.find(token)
                if found.isNull():
                    break
                fmt = QTextCharFormat()
                fmt.setAnchor(True)
                fmt.setAnchorHref(f"#fn-{fid}")
                if fid not in anchored:
                    fmt.setAnchorNames([f"fnref-{fid}"])
                    anchored.add(fid)
                fmt.setVerticalAlignment(
                    QTextCharFormat.VerticalAlignment.AlignSuperScript
                )
                fmt.setForeground(self._link_color)
                found.beginEditBlock()
                found.removeSelectedText()
                found.insertText(f"[{index}]", fmt)
                found.endEditBlock()

    def _apply_footnote_defs(self, document: QTextDocument) -> None:
        """给文末脚注定义块设置锚点（``fn-id``）并着色编号。"""
        if not self._footnote_defs:
            return
        for index, (fid, _body) in enumerate(self._footnote_defs, start=1):
            token = f"{_FOOTNOTE_DEF_PREFIX}{index}{_CODE_TOKEN_SUFFIX}"
            found = document.find(token)
            if found.isNull():
                continue
            found.beginEditBlock()
            found.removeSelectedText()
            if found.block().text().startswith(" "):
                found.deleteChar()
            block = found.block()
            block_format = block.blockFormat()
            block_format.setTopMargin(2)
            block_format.setBottomMargin(2)
            found.setBlockFormat(block_format)

            number = document.find(f"[{index}]", block.position())
            if (
                not number.isNull()
                and number.block() == block
                and number.selectionEnd() <= block.position() + block.length()
            ):
                number_fmt = QTextCharFormat()
                number_fmt.setAnchor(True)
                number_fmt.setAnchorHref(f"#fnref-{fid}")
                number_fmt.setForeground(self._link_color)
                number.mergeCharFormat(number_fmt)

            anchor_fmt = QTextCharFormat()
            anchor_fmt.setAnchor(True)
            anchor_fmt.setAnchorNames([f"fn-{fid}"])
            cursor = QTextCursor(document)
            cursor.setPosition(block.position())
            cursor.setPosition(
                block.position() + max(block.length() - 1, 0),
                QTextCursor.MoveMode.KeepAnchor,
            )
            cursor.mergeCharFormat(anchor_fmt)
            found.endEditBlock()

    @staticmethod
    def _slugify(text: str, used: dict) -> str:
        """标题文本 → GitHub 风格锚点（保留 CJK，去标点，重名追加序号）。"""
        slug = re.sub(r"elamath[0-9a-f]+z\d+q", "", text).strip().lower()
        slug = re.sub(r"[^\w\u4e00-\u9fff -]+", "", slug)
        slug = re.sub(r"[\s-]+", "-", slug).strip("-")
        if not slug:
            slug = "section"
        base = slug
        index = 1
        while slug in used:
            slug = f"{base}-{index}"
            index += 1
        used[slug] = True
        return slug

    def _apply_heading_anchors(self, document: QTextDocument) -> None:
        """给标题块附加锚点名称，并记录标题列表（供目录生成）。"""
        self._headings = []
        used: dict = {}
        block = document.begin()
        while block.isValid():
            level = block.blockFormat().headingLevel()
            if level > 0:
                text = re.sub(r"elamath[0-9a-f]+z\d+q", "", block.text()).strip()
                slug = self._slugify(text, used)
                fmt = QTextCharFormat()
                fmt.setAnchor(True)
                fmt.setAnchorNames([slug])
                cursor = QTextCursor(document)
                cursor.setPosition(block.position())
                cursor.setPosition(
                    block.position() + max(block.length() - 1, 0),
                    QTextCursor.MoveMode.KeepAnchor,
                )
                cursor.mergeCharFormat(fmt)
                self._headings.append((level, text, slug))
            block = block.next()

    def _replace_toc_token(self, document: QTextDocument) -> None:
        """把 ``[toc]`` 占位符替换为标题链接列表。"""
        found = document.find(_TOC_TOKEN)
        if found.isNull():
            return
        if not self._headings:
            found.removeSelectedText()
            return
        cursor = QTextCursor(found)
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        for index, (level, text, slug) in enumerate(self._headings):
            if index > 0:
                cursor.insertBlock(QTextBlockFormat(), QTextCharFormat())
            indent = "  " * max(level - 1, 0)
            if indent:
                cursor.insertText(indent)
            cursor.insertText("• ")
            link_fmt = QTextCharFormat()
            link_fmt.setAnchor(True)
            link_fmt.setAnchorHref(f"#{slug}")
            link_fmt.setForeground(self._link_color)
            cursor.insertText(text or slug, link_fmt)
        cursor.endEditBlock()

    def _apply_folds(self, document: QTextDocument) -> None:
        """把折叠占位符替换为可点击标签，并按展开状态隐藏/展示内容。"""
        if not self._fold_blocks:
            return
        for index, fold in enumerate(self._fold_blocks):
            start_token = f"{_FOLD_TOKEN_PREFIX}{index}{_CODE_TOKEN_SUFFIX}"
            end_token = f"{_FOLD_END_TOKEN_PREFIX}{index}{_CODE_TOKEN_SUFFIX}"
            found = document.find(start_token)
            if found.isNull():
                continue
            expanded = index in self._expanded_folds
            label = fold.get("label") or ""
            marker = "▾" if expanded else "▸"
            fmt = QTextCharFormat()
            fmt.setForeground(self._muted_color)
            fmt.setFontItalic(True)
            fmt.setAnchor(True)
            fmt.setAnchorHref(f"#elafold-{index}")
            found.beginEditBlock()
            found.removeSelectedText()
            found.insertText(f"{marker} {label}", fmt)
            found.endEditBlock()
            label_block = document.findBlock(max(found.position() - 1, 0))
            if not label_block.isValid():
                continue
            end_found = document.find(end_token)
            end_number = (
                end_found.block().blockNumber()
                if not end_found.isNull()
                else document.blockCount() - 1
            )
            if expanded:
                block = label_block.next()
                while block.isValid() and block.blockNumber() < end_number:
                    self._style_fold_block(document, block)
                    block = block.next()
                if not end_found.isNull():
                    self._delete_blocks(document, end_number, end_number)
            else:
                self._delete_blocks(document, label_block.blockNumber() + 1, end_number)

    @staticmethod
    def _delete_blocks(document: QTextDocument, first: int, last: int) -> None:
        """按块号区间删除块（从后往前，避免块号失效）。"""
        for number in range(last, first - 1, -1):
            block = document.findBlockByNumber(number)
            if not block.isValid():
                continue
            cursor = QTextCursor(document)
            cursor.setPosition(block.position())
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
            cursor.removeSelectedText()

    def _style_fold_block(self, document: QTextDocument, block) -> None:
        """展开的折叠内容：左缩进 + 次级文字色。"""
        block_format = block.blockFormat()
        block_format.setLeftMargin(block_format.leftMargin() + 12)
        cursor = QTextCursor(document)
        cursor.setPosition(block.position())
        cursor.setBlockFormat(block_format)
        iterator = block.begin()
        while not iterator.atEnd():
            fragment = iterator.fragment()
            if fragment.isValid() and (
                fragment.charFormat().foreground().style() == Qt.BrushStyle.NoBrush
            ):
                edit = QTextCursor(document)
                edit.setPosition(fragment.position())
                edit.setPosition(
                    fragment.position() + fragment.length(),
                    QTextCursor.MoveMode.KeepAnchor,
                )
                fmt = QTextCharFormat()
                fmt.setForeground(self._muted_color)
                edit.mergeCharFormat(fmt)
            iterator += 1

    def _style_callouts(self, document: QTextDocument) -> None:
        """Callout：标记行替换为彩色标签，整段引用块加语义色淡底。"""
        if not self._callout_types:
            return
        tint = 0.14 if self._is_dark_theme else 0.08
        for index, kind in enumerate(self._callout_types):
            token = f"{_CALLOUT_TOKEN_PREFIX}{index}{_CODE_TOKEN_SUFFIX}"
            found = document.find(token)
            if found.isNull():
                continue
            label = _CALLOUT_LABELS.get(kind, kind)
            color = QColor(
                _CALLOUT_COLORS.get(kind, _CALLOUT_COLORS["note"])[
                    "dark" if self._is_dark_theme else "light"
                ]
            )
            background = QBrush(self._blend(self._base_bg, color, tint))
            label_fmt = QTextCharFormat()
            label_fmt.setFontWeight(QFont.Weight.DemiBold)
            label_fmt.setForeground(color)

            found.beginEditBlock()
            found.removeSelectedText()
            first_number = found.blockNumber()
            on_empty_line = found.atBlockEnd()
            found.insertText(label, label_fmt)
            if not on_empty_line:
                found.insertBlock(QTextBlockFormat(), QTextCharFormat())
            found.endEditBlock()

            block = document.findBlockByNumber(first_number)
            while block.isValid():
                block_format = block.blockFormat()
                if block_format.leftMargin() < _QUOTE_LEFT_MARGIN:
                    break
                block_format.setBackground(background)
                # 语义色左竖线（GitHub / Typora 风格），由自绘统一绘制
                block_format.setProperty(_CALLOUT_RAIL_PROPERTY, color.name())
                cursor = QTextCursor(document)
                cursor.setPosition(block.position())
                cursor.setBlockFormat(block_format)
                block = block.next()

    def _apply_inline_code_formats(self, document: QTextDocument) -> None:
        """定位行内代码文本并套用等宽字体与标记属性（底色由自绘提供）。"""
        if not self._inline_codes:
            return
        fmt = self._code_format()
        cursor = QTextCursor(document)
        for code_text in self._inline_codes:
            search_pos = cursor.position()
            while True:
                found = document.find(code_text, search_pos)
                if found.isNull():
                    break
                # 已标记 / 位于围栏代码表格内的匹配无需重复处理
                if found.charFormat().property(
                    _INLINE_CODE_MARK
                ) or self._in_code_table(found):
                    search_pos = found.selectionEnd()
                    continue
                found.mergeCharFormat(fmt)
                cursor.setPosition(found.selectionEnd())
                break

    # -- 表格 / 排版 -------------------------------------------------------

    def _style_typography(self, document: QTextDocument) -> None:
        """Typora 风格排版：正文行高、标题层级字号与间距、引用块与列表间距。

        在 ``_style_callouts`` 之后调用：Callout 已带底色，引用块样式不再覆盖；
        表格单元格仅统一行高（代码卡片保持自身行高）。
        """
        base = document.defaultFont().pointSizeF()
        if base <= 0:
            pixel = document.defaultFont().pixelSize()
            base = pixel * 0.75 if pixel > 0 else 10.0
        cursor = QTextCursor(document)
        probe = QTextCursor(document)
        # 整个排版阶段合并成一次编辑块：逐块 setBlockFormat 会各自触发一次重排，
        # 几百个块的文档会明显卡顿（实测 760 块 ≈ 108ms）；合并后只在末尾重排一次
        cursor.beginEditBlock()
        try:
            block = document.begin()
            while block.isValid():
                probe.setPosition(block.position())
                table = probe.currentTable()
                if table is not None:
                    if self._in_code_table(probe):
                        block = block.next()
                        continue
                    table_format = block.blockFormat()
                    table_format.setLineHeight(
                        150.0, QTextBlockFormat.LineHeightTypes.ProportionalHeight
                    )
                    # 单元格内统一无块边距（间距由单元格 padding 提供），
                    # 避免导入器给首格加的默认段落边距造成表头基线不齐
                    table_format.setTopMargin(0)
                    table_format.setBottomMargin(0)
                    self._apply_block_format(document, block, table_format, cursor)
                    block = block.next()
                    continue
                block_format = block.blockFormat()
                level = block_format.headingLevel()
                if level:
                    scale, top, bottom, line_height = _HEADING_TYPOGRAPHY.get(
                        level, (1.0, 16.0, 16.0, 150.0)
                    )
                    block_format.setTopMargin(top)
                    block_format.setBottomMargin(bottom)
                    block_format.setLineHeight(
                        line_height, QTextBlockFormat.LineHeightTypes.ProportionalHeight
                    )
                    self._apply_block_format(document, block, block_format, cursor)
                    self._style_heading_fragments(
                        document, block, base * scale, level, cursor
                    )
                elif block_format.hasProperty(
                    QTextFormat.BlockTrailingHorizontalRulerWidth
                ):
                    # hr：Qt 自带横线仅 1px 且颜色不可控（实测属性/调色板均无效），
                    # 清除属性后由 _paint_document_decorations 自绘 2px 主题线
                    block_format.clearProperty(
                        QTextFormat.BlockTrailingHorizontalRulerWidth
                    )
                    block_format.setProperty(_HR_MARK, True)
                    block_format.setTopMargin(16.0)
                    block_format.setBottomMargin(16.0)
                    self._apply_block_format(document, block, block_format, cursor)
                else:
                    block_format.setLineHeight(
                        _BODY_LINE_HEIGHT,
                        QTextBlockFormat.LineHeightTypes.ProportionalHeight,
                    )
                    if block.textList() is not None:
                        block_format.setTopMargin(_LIST_ITEM_MARGIN)
                        block_format.setBottomMargin(_LIST_ITEM_MARGIN)
                    elif block_format.leftMargin() >= _QUOTE_LEFT_MARGIN:
                        block_format.setLeftMargin(_QUOTE_LEFT_MARGIN)
                        block_format.setTopMargin(_QUOTE_BLOCK_MARGIN)
                        block_format.setBottomMargin(_QUOTE_BLOCK_MARGIN)
                        self._mute_quote_fragments(document, block, cursor)
                    elif block.text().strip():
                        block_format.setBottomMargin(_PARAGRAPH_MARGIN)
                    self._apply_block_format(document, block, block_format, cursor)
                block = block.next()
        finally:
            cursor.endEditBlock()

    @staticmethod
    def _apply_block_format(
        document: QTextDocument,
        block,
        block_format: QTextBlockFormat,
        cursor: Optional[QTextCursor] = None,
    ) -> None:
        """把块格式写回指定块（``cursor`` 可复用以避免逐块创建）。"""
        cursor = cursor if cursor is not None else QTextCursor(document)
        cursor.setPosition(block.position())
        cursor.setBlockFormat(block_format)

    def _style_heading_fragments(
        self,
        document: QTextDocument,
        block,
        point_size: float,
        level: int,
        cursor: Optional[QTextCursor] = None,
    ) -> None:
        """标题片段：按层级放大字号、加粗，并强制为正文色（h6 次级色）。

        Qt Markdown 导入器可能给标题带上默认前景色（如深蓝），样式表无法
        覆盖；这里显式着色，保证深浅主题下标题颜色可控（Typora 风格）。
        """
        weight = QFont.Weight.Bold
        color = self._muted_color if level >= 6 else self._md_heading_color
        edit = cursor if cursor is not None else QTextCursor(document)
        iterator = block.begin()
        while not iterator.atEnd():
            fragment = iterator.fragment()
            if fragment.isValid() and fragment.text():
                edit.setPosition(fragment.position())
                edit.setPosition(
                    fragment.position() + fragment.length(),
                    QTextCursor.MoveMode.KeepAnchor,
                )
                fmt = QTextCharFormat()
                fmt.setFontPointSize(point_size)
                fmt.setFontWeight(weight)
                fmt.setForeground(color)
                edit.mergeCharFormat(fmt)
            iterator += 1

    def _mute_quote_fragments(
        self, document: QTextDocument, block, cursor: Optional[QTextCursor] = None
    ) -> None:
        """引用块正文：opencode TUI 风格（斜体 + 引用色；链接 / 行内代码保持自身颜色）。"""
        edit = cursor if cursor is not None else QTextCursor(document)
        iterator = block.begin()
        while not iterator.atEnd():
            fragment = iterator.fragment()
            if fragment.isValid() and (
                fragment.charFormat().foreground().style() == Qt.BrushStyle.NoBrush
            ):
                edit.setPosition(fragment.position())
                edit.setPosition(
                    fragment.position() + fragment.length(),
                    QTextCursor.MoveMode.KeepAnchor,
                )
                fmt = QTextCharFormat()
                fmt.setForeground(self._md_quote_color)
                fmt.setFontItalic(True)
                edit.mergeCharFormat(fmt)
            iterator += 1

    def _style_task_markers(self, document: QTextDocument) -> None:
        """任务复选框跟随主题 list 色（仍可点击，避免显示成整段链接色）。

        任务项整行是 anchor（点击切换勾选），文字会拿到链接色；勾选框单独
        取 list 色，既跟主题走，又与链接色区分得开。
        """
        if not self._task_items:
            return
        for marker in ("☑", "☐"):
            cursor = QTextCursor(document)
            while True:
                found = document.find(marker, cursor)
                if found.isNull():
                    break
                fmt = found.charFormat()
                if fmt.isAnchor() and fmt.anchorHref().startswith("#elatask-"):
                    plain = QTextCharFormat()
                    plain.setForeground(self._md_list_color)
                    found.mergeCharFormat(plain)
                cursor = found

    def _style_tables(self, document: QTextDocument) -> None:
        """美化 Markdown 表格。

        Qt 默认表格为左右贴边的全网格线且无内边距，这里改为：
        表头行主题底色 + 半粗体、单元格内边距、仅保留行分隔线。
        """
        header_brush = QBrush(self._table_header_bg)
        border_brush = QBrush(self._table_border)

        # 同段落排版：整轮表格样式合并成一次编辑块，避免每个单元格重排一次
        cursor = QTextCursor(document)
        cursor.beginEditBlock()
        try:
            stack = [document.rootFrame()]
            while stack:
                frame = stack.pop()
                for child in frame.childFrames():
                    stack.append(child)
                    if isinstance(child, QTextTable):
                        if self._is_code_table(child):
                            continue
                        self._trim_table_cell_blocks(document, child)
                        self._style_table(child, header_brush, border_brush)
                        self._set_table_margins(document, child)
        finally:
            cursor.endEditBlock()

    def _trim_table_cell_blocks(
        self, document: QTextDocument, table: QTextTable
    ) -> None:
        """移除单元格首尾的纯空块。

        Qt Markdown 导入器在引用块 / 代码块之后的表格首格会多插一个空块
        （渲染时把表头首格文字挤到第二行），这里用段落合并清理
        （单元格内 ``removeSelectedText`` 删除块无效，改用 ``deletePreviousChar``）。
        """
        for row in range(table.rows()):
            for column in range(table.columns()):
                cell = table.cellAt(row, column)
                while True:
                    first = cell.firstCursorPosition().blockNumber()
                    last = cell.lastCursorPosition().blockNumber()
                    if last <= first:
                        break
                    block = document.findBlockByNumber(first)
                    if not block.isValid() or block.text().strip():
                        break
                    following = document.findBlockByNumber(first + 1)
                    if not following.isValid():
                        break
                    cursor = QTextCursor(document)
                    cursor.setPosition(following.position())
                    cursor.deletePreviousChar()
                while True:
                    first = cell.firstCursorPosition().blockNumber()
                    last = cell.lastCursorPosition().blockNumber()
                    if last <= first:
                        break
                    block = document.findBlockByNumber(last)
                    if not block.isValid() or block.text().strip():
                        break
                    cursor = QTextCursor(document)
                    cursor.setPosition(block.position())
                    cursor.deletePreviousChar()

    def _set_table_margins(self, document: QTextDocument, table: QTextTable) -> None:
        """给表格前后的块留出上下间距。

        注意 ``table.firstCursorPosition()`` 指向首个单元格内部，
        直接改它的块边距会把表头首格文字顶下来；应改表格外的相邻块。
        """
        before_pos = table.firstPosition() - 1
        if before_pos >= 0:
            before = document.findBlock(before_pos)
            if before.isValid() and before.position() < table.firstPosition():
                self._set_block_margins(document, before, bottom=_TABLE_BLOCK_MARGIN)
        after_pos = table.lastPosition() + 1
        if after_pos < document.characterCount():
            after = document.findBlock(after_pos)
            if after.isValid() and after.position() > table.lastPosition():
                self._set_block_margins(document, after, top=_TABLE_BLOCK_MARGIN)

    def _is_code_table(self, table: QTextTable) -> bool:
        """是否为代码块包裹表（表格式标记优先，单列同色兜底）。

        兜底仅限单列、最多两行的表：浅色主题下表格表头底色与代码底色
        恰好相同，多列普通表格不能按颜色判定。
        """
        if table.rows() < 1 or table.columns() < 1:
            return False
        if table.format().property(_CODE_MARKER) == _CODE_MARKER_VALUE:
            return True
        if table.columns() != 1 or table.rows() > 2:
            return False
        cell = table.cellAt(0, 0)
        if cell is None:
            # cellAt() 对被合并覆盖的单元格返回 None
            return False
        background = cell.format().background()
        return (
            background.style() != Qt.BrushStyle.NoBrush
            and background.color() == self._code_bg
        )

    @staticmethod
    def _set_block_margins(
        document: QTextDocument,
        block,
        top: Optional[float] = None,
        bottom: Optional[float] = None,
    ) -> None:
        """设置指定块的上下外边距（None 表示保持不变）。"""
        block_format = block.blockFormat()
        if top is not None:
            block_format.setTopMargin(top)
        if bottom is not None:
            block_format.setBottomMargin(bottom)
        cursor = QTextCursor(document)
        cursor.setPosition(block.position())
        cursor.setBlockFormat(block_format)

    @staticmethod
    def _blend(base: QColor, over: QColor, alpha: float) -> QColor:
        """将 over 按 alpha 比例混合到 base 上，返回不透明颜色。"""
        return QColor(
            int(base.red() * (1 - alpha) + over.red() * alpha),
            int(base.green() * (1 - alpha) + over.green() * alpha),
            int(base.blue() * (1 - alpha) + over.blue() * alpha),
        )

    def _style_table(
        self, table: QTextTable, header_brush: QBrush, border_brush: QBrush
    ) -> None:
        table_format = QTextTableFormat(table.format())
        table_format.setBorder(0)
        table_format.setBorderCollapse(True)
        table_format.setCellPadding(0)
        table_format.setCellSpacing(0)
        if (
            self._table_column_widths
            and len(self._table_column_widths) == table.columns()
        ):
            table_format.setColumnWidthConstraints(
                [
                    QTextLength(QTextLength.Type.PercentageLength, width)
                    for width in self._table_column_widths
                ]
            )
        table.setFormat(table_format)

        stripe_brush = QBrush(self._table_stripe_bg)
        for row in range(table.rows()):
            for column in range(table.columns()):
                cell = table.cellAt(row, column)
                cell_format = cell.format().toTableCellFormat()
                # Typora（github.css）：单元格 6px 13px 内边距 + 全网格 1px
                cell_format.setTopPadding(6)
                cell_format.setBottomPadding(6)
                cell_format.setLeftPadding(13)
                cell_format.setRightPadding(13)
                cell_format.setBorderBrush(border_brush)
                cell_format.setBorder(1.0)
                if row == 0:
                    cell_format.setBackground(header_brush)
                    cell_format.setFontWeight(QFont.Weight.Bold)
                    cell_format.setForeground(QBrush(self._md_heading_color))
                elif self._table_zebra and row % 2 == 0:
                    cell_format.setBackground(stripe_brush)
                cell.setFormat(cell_format)
                if row == 0:
                    self._color_table_header_text(cell)

    def _color_table_header_text(self, cell) -> None:
        """表头文字显式着标题色（片段级，避免被后置的正文着色覆盖）。"""
        start = cell.firstCursorPosition()
        end = cell.lastCursorPosition()
        if end.position() <= start.position():
            return
        start.setPosition(end.position(), QTextCursor.MoveMode.KeepAnchor)
        fmt = QTextCharFormat()
        fmt.setForeground(self._md_heading_color)
        start.mergeCharFormat(fmt)

    # -- 公式 --------------------------------------------------------------

    def _math_point_size(self) -> float:
        """公式字号（pt）：跟随文档默认字体。"""
        font = self.document().defaultFont()
        size = font.pointSizeF()
        if size > 0:
            return size
        pixel = font.pixelSize()
        return pixel * 0.75 if pixel > 0 else 10.0

    def _embed_math(self, document: QTextDocument, maths: list, resource_doc) -> None:
        """把公式占位标记替换为渲染图片（结构错误时保留源码文本）。

        行内公式按正文字号的 1.2 倍渲染并垂直居中（``AlignMiddle``），
        避免 Qt 内联图片"底部贴基线"造成的整体上浮；块级按 1.35 倍并居中。
        容错渲染（未知命令字面显示）的公式也会记入 ``renderIssues()``。
        """
        base_point_size = self._math_point_size()
        plain_format = QTextCharFormat()
        plain_format.setForeground(self._text_color)
        for index, (latex, display) in enumerate(maths):
            marker = self._math_mark.format(index)
            found = document.find(marker)
            if found.isNull():
                continue
            point_size = base_point_size * (1.55 if display else 1.3)
            report: dict = {}
            image = render_formula(
                latex, self._text_color, point_size, display, report=report
            )
            if image is None:
                self._record_issue("math", latex)
                text = latex if display else f"${latex}$"
                found.insertText(text, plain_format)
                if display:
                    block_format = found.blockFormat()
                    block_format.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    found.setBlockFormat(block_format)
                continue
            if report.get("degraded") and not report.get("repaired"):
                self._record_issue("math", latex)
            digest = hashlib.md5(
                f"{latex}|{self._text_color.name()}|{point_size:.2f}|{display}".encode(
                    "utf-8"
                )
            ).hexdigest()
            url = f"elamath://{digest}"
            resource_doc.addResource(QTextDocument.ImageResource, QUrl(url), image)
            image_format = QTextImageFormat()
            image_format.setName(url)
            image_format.setWidth(image.width() / 2.0)
            image_format.setHeight(image.height() / 2.0)
            image_format.setToolTip(f"LaTeX: {latex}")
            image_format.setVerticalAlignment(
                QTextCharFormat.VerticalAlignment.AlignMiddle
            )
            found.insertImage(image_format)
            if display:
                block_format = found.blockFormat()
                block_format.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                block_format.setTopMargin(10)
                block_format.setBottomMargin(10)
                found.setBlockFormat(block_format)

    # -- Mermaid -----------------------------------------------------------

    def setMermaidRenderer(self, renderer=None) -> None:
        """设置 Mermaid 渲染器（``None`` 关闭，回退为代码卡片）。

        :param renderer: ``callable(code, theme) -> QImage | None``、
            :class:`~pyqt5_ela_pro.mermaid_support.ElaMermaidRenderer`
            或 ``None``（关闭）
        """
        if isinstance(renderer, ElaMermaidRenderer):
            if self._mermaid_renderer is not renderer:
                self._disconnect_mermaid_renderer()
                self._mermaid_renderer = renderer
                renderer.rendered.connect(self._on_mermaid_rendered)
            self._mermaid_override = None
            self._mermaid_disabled = False
        elif renderer is None:
            self._disconnect_mermaid_renderer()
            self._mermaid_override = None
            self._mermaid_disabled = True
        else:
            self._disconnect_mermaid_renderer()
            self._mermaid_override = renderer
            self._mermaid_disabled = False
        if self._source:
            self._render()

    def setMermaidEnabled(self, on: bool) -> None:
        """启用/禁用 Mermaid 渲染（启用时自动探测 mermaidx）。"""
        on = bool(on)
        if on == (not self._mermaid_disabled):
            return
        self._disconnect_mermaid_renderer()
        self._mermaid_disabled = not on
        if on:
            self._mermaid_override = None
        if self._source:
            self._render()

    def mermaidAvailable(self) -> bool:
        """当前是否有可用的 Mermaid 渲染后端。"""
        return self._mermaid_enabled()

    def mermaidEnabled(self) -> bool:
        """是否启用 Mermaid 渲染（``setMermaidEnabled`` 的开关状态）。"""
        return not self._mermaid_disabled

    def setMermaidPrewarm(self, on: bool) -> None:
        """设置是否后台预热 Mermaid 引擎（默认关闭）。

        开启后立即创建渲染器并在后台启动 mermaid.js 引擎（约 0.4s），
        首次出图不再叠加冷启动耗时；仅在未设置自定义渲染函数时生效。
        """
        self._mermaid_prewarm = bool(on)
        if not self._mermaid_prewarm:
            return
        had_renderer = self._mermaid_renderer is not None
        renderer = self._ensure_mermaid_renderer()
        # 新建渲染器时 _ensure_mermaid_renderer 已触发预热，这里只补已有渲染器
        if renderer is not None and had_renderer:
            renderer.prewarm()

    def mermaidPrewarm(self) -> bool:
        """获取 Mermaid 引擎预热开关状态。"""
        return self._mermaid_prewarm

    def mermaidRenderer(self) -> Optional[ElaMermaidRenderer]:
        """获取（惰性创建的）Mermaid 渲染器。"""
        return self._ensure_mermaid_renderer()

    # -- 推理块折叠 --------------------------------------------------------

    def setReasoningTag(self, tag: Optional[str]) -> None:
        """设置推理块标签名（``None`` 关闭折叠，标签内容按原文渲染）。

        :param tag: 标签名（默认 ``"think"``，即 `` ... `` 语法）
        """
        self._reasoning_tag = tag
        if self._source:
            self._render()

    def reasoningTag(self) -> Optional[str]:
        """获取当前推理块标签名。"""
        return self._reasoning_tag

    def setReasoningLabel(self, label: str) -> None:
        """设置推理块折叠标签文案（默认"思考过程"）。"""
        self._reasoning_label = label or _DEFAULT_REASONING_LABEL
        if self._source:
            self._render()

    def reasoningLabel(self) -> str:
        """获取推理块折叠标签文案。"""
        return self._reasoning_label

    def _disconnect_mermaid_renderer(self) -> None:
        if self._mermaid_renderer is not None:
            try:
                self._mermaid_renderer.rendered.disconnect(self._on_mermaid_rendered)
            except TypeError:
                pass
            self._mermaid_renderer = None
        # 旧渲染器的在途结果不再回调（信号已断开），计数一并复位
        self._mermaid_active = 0
        self._mermaid_jobs.clear()
        self._mermaid_job_keys.clear()

    def _mermaid_enabled(self) -> bool:
        if self._mermaid_disabled:
            return False
        if self._mermaid_override is not None:
            return True
        return mermaid_support.mermaidx_available()

    def _ensure_mermaid_renderer(self) -> Optional[ElaMermaidRenderer]:
        if self._mermaid_disabled:
            return None
        if self._mermaid_renderer is None:
            renderer = ElaMermaidRenderer(parent=self)
            if self._mermaid_override is not None:
                renderer.setRenderer(self._mermaid_override)
            if not renderer.available():
                return None
            renderer.rendered.connect(self._on_mermaid_rendered)
            self._mermaid_renderer = renderer
            if self._mermaid_prewarm:
                renderer.prewarm()
        return self._mermaid_renderer

    def _theme_key(self) -> str:
        return "dark" if self._is_dark_theme else "light"

    def _embed_mermaid(
        self, document: QTextDocument, resource_doc, reset: bool = False
    ) -> None:
        """把 Mermaid 占位符替换为渲染图片（异步；失败/未装回退代码卡片）。

        未命中缓存的图进入待渲染队列（:attr:`_mermaid_jobs`），由
        :meth:`_pump_mermaid` 按**距视口距离**逐个提交（引擎串行，逐个提交
        不损失吞吐，但能保证当前可见的图最先出图）。

        :param reset: 全量渲染（主文档）时重置任务队列；流式片段渲染
            （临时文档）只追加，避免丢弃前面片段尚未完成的占位任务
        """
        if reset:
            self._mermaid_jobs.clear()
            self._mermaid_job_keys.clear()
        if not self._mermaid_blocks:
            return
        theme = self._theme_key()
        renderer = self._ensure_mermaid_renderer()
        resource_document = resource_doc or document
        for index, code in enumerate(self._mermaid_blocks):
            token = f"{_MERMAID_TOKEN_PREFIX}{index}{_CODE_TOKEN_SUFFIX}"
            found = document.find(token)
            if found.isNull():
                continue
            if renderer is None:
                self._insert_code_card(found, "mermaid", code)
                continue
            known, image = renderer.lookup(code, theme)
            if known:
                if image is None:
                    self._insert_code_card(found, "mermaid", code)
                else:
                    self._insert_mermaid_image(
                        found, code, image, resource_document, theme
                    )
                continue
            # 其它主题已有同源码图片时先顶上（避免主题切换时长期空白），
            # 挂上 pending 锚点，当前主题渲染完成后再替换。
            anchor = f"{_MERMAID_PENDING_PREFIX}{self._mermaid_digest(code)}-{index}"
            known_other, other_theme, other_image = renderer.lookupAnyTheme(code, theme)
            if known_other and other_image is not None:
                self._insert_mermaid_image(
                    found,
                    code,
                    other_image,
                    resource_document,
                    other_theme,
                    pending_anchor=anchor,
                )
            else:
                self._insert_mermaid_placeholder(found, index, code, anchor)
            key = (self._mermaid_digest(code), theme)
            if key in self._mermaid_job_keys:
                continue
            self._mermaid_job_keys.add(key)
            self._mermaid_jobs.append(
                {
                    "index": index,
                    "code": code,
                    "digest": key[0],
                    "anchor": anchor,
                    "theme": theme,
                    "distance": float("inf"),
                }
            )
        self._refresh_mermaid_priorities()
        self._schedule_mermaid_pump()

    def _mermaid_view_max_width(self) -> float:
        """当前视口可用的图片最大宽度（像素）。"""
        return max(self._text_browser.viewport().width() - _MERMAID_IMAGE_MARGIN, 120)

    def _mermaid_anchor_positions(self) -> dict:
        """一次遍历收集 ``mermaid-pending-`` 锚点的视口 y 坐标。"""
        positions: dict = {}
        if not self._mermaid_jobs:
            return positions
        browser = self._text_browser
        document = self.document()
        block = document.begin()
        while block.isValid():
            iterator = block.begin()
            while not iterator.atEnd():
                fragment = iterator.fragment()
                if fragment.isValid():
                    for name in fragment.charFormat().anchorNames():
                        if name.startswith(_MERMAID_PENDING_PREFIX):
                            cursor = QTextCursor(document)
                            cursor.setPosition(fragment.position())
                            positions[name] = browser.cursorRect(cursor).center().y()
                iterator += 1
            block = block.next()
        return positions

    def _refresh_mermaid_priorities(self) -> None:
        """重算待渲染任务与视口中心的距离（滚动/文档变化后调用）。"""
        if sip.isdeleted(self) or not self._mermaid_jobs:
            return
        center = max(1, self._text_browser.viewport().height()) / 2.0
        positions = self._mermaid_anchor_positions()
        for job in self._mermaid_jobs:
            y = positions.get(job.get("anchor"))
            job["distance"] = float("inf") if y is None else abs(y - center)

    def _schedule_mermaid_pump(self, delay: int = 0) -> None:
        """延后提交下一个任务（让贴底/滚动逻辑先更新视口位置）。"""
        if not self._mermaid_pump_timer.isActive():
            self._mermaid_pump_timer.start(delay)

    def _pump_mermaid(self) -> None:
        """提交下一个待渲染任务（引擎串行，同一时刻只保留一个在途请求）。"""
        if sip.isdeleted(self):
            return
        if self._mermaid_disabled or not self._mermaid_jobs or self._mermaid_active:
            return
        renderer = self._ensure_mermaid_renderer()
        if renderer is None:
            return
        theme = self._theme_key()
        self._refresh_mermaid_priorities()
        renderer.setMaxImageWidth(self._mermaid_view_max_width())
        while self._mermaid_jobs:
            job = min(self._mermaid_jobs, key=lambda item: item["distance"])
            self._mermaid_jobs.remove(job)
            job_theme = job.get("theme", theme)
            if job_theme != theme:
                continue  # 旧主题任务：主题已切换，丢弃
            known, image = renderer.lookup(job["code"], theme)
            if known:
                self._replace_mermaid_pending(job["code"], theme, image)
                continue
            self._mermaid_active += 1
            renderer.request(job["code"], theme)
            return

    def _replace_mermaid_pending(self, code: str, theme: str, image) -> None:
        """把文档中该源码的 pending 锚点（占位文本/旧主题图）替换为最终结果。"""
        prefix = f"mermaid-pending-{self._mermaid_digest(code)}-"
        ranges = self._find_anchor_ranges(self.document(), prefix)
        if not ranges:
            return
        document = self.document()
        for start, end in reversed(ranges):
            cursor = QTextCursor(document)
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            if image is None:
                self._record_issue("mermaid", code)
                self._insert_code_card(cursor, "mermaid", code)
            else:
                self._insert_mermaid_image(cursor, code, image, document, theme)

    @staticmethod
    def _mermaid_digest(code: str) -> str:
        return hashlib.md5(code.encode("utf-8")).hexdigest()[:12]

    def _insert_mermaid_placeholder(
        self, cursor: QTextCursor, index: int, code: str, anchor: Optional[str] = None
    ) -> None:
        """渲染进行中占位（带唯一锚点名，供异步结果定位替换）。"""
        name = anchor or f"mermaid-pending-{self._mermaid_digest(code)}-{index}"
        fmt = QTextCharFormat()
        fmt.setForeground(self._muted_color)
        fmt.setFontItalic(True)
        fmt.setAnchorNames([name])
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText("Mermaid 渲染中…", fmt)
        cursor.endEditBlock()

    def _insert_mermaid_image(
        self,
        cursor: QTextCursor,
        code: str,
        image: QImage,
        resource_doc: QTextDocument,
        theme: str,
        pending_anchor: Optional[str] = None,
    ) -> None:
        """把占位符替换为 Mermaid 渲染图片（居中、限宽、tooltip 存源码）。

        :param pending_anchor: 非空时给图片挂上 pending 锚点（旧主题降级图），
            当前主题渲染完成后可再次定位替换
        """
        digest = hashlib.md5(f"{code}|{theme}".encode("utf-8")).hexdigest()
        url = f"{_MERMAID_IMAGE_PREFIX}{digest}"
        resource_doc.addResource(
            QTextDocument.ResourceType.ImageResource, QUrl(url), image
        )
        width = image.width() / 2.0
        height = image.height() / 2.0
        max_width = self._mermaid_view_max_width()
        if width > max_width > 0:
            height = height * max_width / width
            width = max_width
        image_format = QTextImageFormat()
        image_format.setName(url)
        image_format.setWidth(width)
        image_format.setHeight(height)
        image_format.setToolTip(f"{_MERMAID_TIP_PREFIX}{code}")
        image_format.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignMiddle)
        if pending_anchor:
            image_format.setAnchorNames([pending_anchor])
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertImage(image_format)
        block_format = cursor.blockFormat()
        block_format.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        block_format.setTopMargin(6)
        block_format.setBottomMargin(6)
        cursor.setBlockFormat(block_format)
        cursor.endEditBlock()

    def _find_anchor_ranges(self, document: QTextDocument, prefix: str) -> list:
        """扫描文档中锚点名以 ``prefix`` 开头的片段范围 ``[(start, end)]``。"""
        ranges: list = []
        block = document.begin()
        while block.isValid():
            iterator = block.begin()
            while not iterator.atEnd():
                fragment = iterator.fragment()
                if fragment.isValid():
                    names = fragment.charFormat().anchorNames()
                    if any(name.startswith(prefix) for name in names):
                        ranges.append(
                            (
                                fragment.position(),
                                fragment.position() + fragment.length(),
                            )
                        )
                iterator += 1
            block = block.next()
        return ranges

    def _on_mermaid_rendered(self, code: str, theme: str, image) -> None:
        """渲染完成（GUI 线程）：替换对应占位符/降级图，并提交下一个任务。"""
        self._mermaid_active = max(0, self._mermaid_active - 1)
        if self._mermaid_disabled:
            return
        try:
            if theme == self._theme_key():
                self._replace_mermaid_pending(code, theme, image)
        finally:
            # 延后一拍：替换图片可能引起滚动/贴底，下一个任务按最新视口选择
            self._schedule_mermaid_pump()

    def _image_format_at_cursor(self) -> Optional[QTextImageFormat]:
        """光标处（含前一字符）的图片格式；没有则返回 ``None``。"""
        cursor = self._text_browser.textCursor()
        candidates = [cursor.charFormat()]
        probe = QTextCursor(cursor)
        if probe.movePosition(
            QTextCursor.MoveOperation.PreviousCharacter, QTextCursor.MoveMode.KeepAnchor
        ):
            candidates.append(probe.charFormat())
        for fmt in candidates:
            if fmt.isImageFormat():
                return fmt.toImageFormat()
        return None

    def _image_source_at_cursor(self, url_prefix: str, tip_prefix: str) -> str:
        """光标处图片的源码（``url_prefix`` / ``tip_prefix`` 匹配；否则空串）。"""
        image_format = self._image_format_at_cursor()
        if image_format is None:
            return ""
        if not image_format.name().startswith(url_prefix):
            return ""
        tooltip = image_format.toolTip()
        if tooltip.startswith(tip_prefix):
            return tooltip[len(tip_prefix) :]
        return ""

    def _mermaid_source_at_cursor(self) -> str:
        return self._image_source_at_cursor(_MERMAID_IMAGE_PREFIX, _MERMAID_TIP_PREFIX)

    def _copy_mermaid_at_cursor(self) -> None:
        code = self._mermaid_source_at_cursor()
        if not code:
            return
        QApplication.clipboard().setText(code)
        self.mermaidCopied.emit(code)

    def _image_local_path_at_cursor(self) -> str:
        """光标处本地图片的磁盘路径（远程 / 生成图片返回空串）。"""
        image_format = self._image_format_at_cursor()
        if image_format is None:
            return ""
        url = self._resolve_image_url(image_format.name(), self.document().baseUrl())
        if not url.isLocalFile():
            return ""
        path = url.toLocalFile()
        return path if os.path.isfile(path) else ""

    def _save_image_at_cursor(self) -> None:
        """把光标处的本地图片另存为 PNG / JPEG。"""
        path = self._image_local_path_at_cursor()
        if not path:
            return
        image = QImage(path)
        if image.isNull():
            return
        info = QFileInfo(path)
        suggested = os.path.join(info.absolutePath(), info.completeBaseName() + ".png")
        target, _ = QFileDialog.getSaveFileName(
            self,
            "图片另存为",
            suggested,
            "PNG 图片 (*.png);;JPEG 图片 (*.jpg *.jpeg);;所有文件 (*)",
        )
        if not target:
            return
        image.save(target)

    # -- 主题 --------------------------------------------------------------

    def _applyThemeStyle(self) -> None:
        """应用主题色（样式表 + 调色板），并重新渲染已有内容。"""
        mode = self._theme_mode
        self._text_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicText)
        self._code_text = self._text_color
        # 表格 / 代码背景：与查看器背景预混合成不透明色
        # （QTextDocument 的 CSS 不支持 alpha 通道，且纯 BasicBaseDeep 在
        # 暗色主题下过亮，代码块与表格色块连片会显得"重"）
        background = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicPress)
        self._is_dark_theme = background.lightness() < 128
        # 语义配色 / 语法高亮走 markdown 主题注册表（内置 opencode / github /
        # solarized / dracula，可注册自定义）；背景 / 正文 / 边框仍由 eTheme
        # 令牌提供，保证与 Ela 主题整体协调
        variant = _md_theme_spec(self._md_theme)[
            "dark" if self._is_dark_theme else "light"
        ]
        semantic = variant["semantic"]
        self._token_palette = dict(variant["syntax"])
        self._token_palette.update(self._token_overrides)
        self._link_color = QColor(semantic["link"])
        self._md_heading_color = QColor(semantic["heading"])
        self._md_strong_color = QColor(semantic["strong"])
        self._md_emphasis_color = QColor(semantic["emphasis"])
        self._md_code_color = QColor(semantic["code"])
        self._md_quote_color = QColor(semantic["quote"])
        self._md_list_color = QColor(semantic["list"])
        self._md_mark_color = QColor(semantic["mark"])
        code_alpha = 0.1 if self._is_dark_theme else 0.06
        self._code_bg = self._blend(background, self._text_color, code_alpha)
        self._code_border = self._blend(background, self._text_color, 0.18)
        self._table_header_bg = self._blend(
            background, self._text_color, 0.05 if self._is_dark_theme else 0.035
        )
        self._table_border = self._blend(background, self._text_color, 0.14)
        self._table_stripe_bg = self._blend(
            background, self._text_color, 0.06 if self._is_dark_theme else 0.035
        )
        self._base_bg = QColor(background)
        self._mark_bg = self._blend(
            background, self._md_mark_color, 0.26 if self._is_dark_theme else 0.34
        )
        self._muted_color = self._blend(background, self._text_color, 0.45)
        self._placeholder_color = self._blend(background, self._text_color, 0.38)
        # opencode TUI：引用竖线与 hr 都用正文色
        self._quote_rail_color = QColor(self._text_color)
        self._heading_rule_color = self._blend(
            background, self._text_color, 0.16 if self._is_dark_theme else 0.08
        )
        self._hr_color = QColor(self._text_color)
        self._search_bg = self._blend(
            background, QColor("#ff922b"), 0.4 if self._is_dark_theme else 0.5
        )
        self._inline_code_bg = self._blend(
            background, self._text_color, 0.12 if self._is_dark_theme else 0.07
        )
        self._inline_code_border = self._blend(
            background, self._text_color, 0.2 if self._is_dark_theme else 0.12
        )
        self._code_button_hover_bg = self._blend(background, self._text_color, 0.16)
        self._code_button_press_bg = self._blend(background, self._text_color, 0.24)
        self._diff_add_bg = self._blend(
            self._code_bg, QColor("#2da44e"), 0.16 if self._is_dark_theme else 0.12
        )
        self._diff_del_bg = self._blend(
            self._code_bg, QColor("#cf222e"), 0.14 if self._is_dark_theme else 0.1
        )
        self._diff_hunk_bg = self._blend(
            self._code_bg, QColor("#0969da"), 0.12 if self._is_dark_theme else 0.08
        )
        self._highlight_cache.clear()

        document = self._text_browser.document()
        document.setDefaultStyleSheet(self._document_css())

        palette = self._text_browser.palette()
        palette.setColor(QPalette.ColorRole.Text, self._text_color)
        palette.setColor(QPalette.ColorRole.Link, self._link_color)
        self._text_browser.setPalette(palette)
        setTransparentTextBase(self._text_browser)

        if self._source:
            self._render()
        self.update()
        self._layout_timer.start(0)

    def _document_css(self) -> str:
        """文档默认样式：代码块与行内代码的字体/背景/文字色。"""
        return (
            f"pre, code, tt {{ font-family: '{self._code_font_family}';"
            f" background-color: {self._code_bg.name()};"
            f" color: {self._code_text.name()}; }}"
        )

    def _apply_fragment_colors(self, document: QTextDocument) -> None:
        """为正文 / 链接 / 加粗 / 斜体 / 删除线补上语义色（opencode TUI 风格）。

        Qt Markdown 导入器把链接硬编码为蓝色（内联样式），样式表无法覆盖，
        因此解析后统一改写字符格式；同时给未指定前景色的正文片段显式着色：

        - 链接 → 链接色 + 下划线（TUI 风格；URL 仍走 tooltip）
        - 删除线 → 次级色（保留删除线，比 TUI 的"仅变灰"在 GUI 更清晰）
        - 加粗 → strong 色；斜体 → emphasis 色
        - 列表项 → list 色（**含项目符号**：Qt 的 bullet / 编号用块内首个
          片段的前景色绘制，所以染片段即染标记，不用自绘）
        - 其余正文 → 正文色

        标题 / 行内代码等已有显式前景色的片段**不覆盖**（由各自阶段负责）。
        全部改写合并进一个编辑块，逐片段开销只有几个格式读取。
        """
        edit_cursor = QTextCursor(document)
        edit_cursor.beginEditBlock()

        block = document.begin()
        while block.isValid():
            # 列表项整块取 list 色（bullet / 编号跟随块内首片段前景色）
            in_list = block.textList() is not None
            iterator = block.begin()
            while not iterator.atEnd():
                fragment = iterator.fragment()
                if fragment.isValid():
                    fmt = fragment.charFormat()
                    color: Optional[QColor] = None
                    if fmt.isAnchor() and fmt.anchorHref():
                        color = self._link_color
                    elif fmt.foreground().style() == Qt.BrushStyle.NoBrush:
                        if fmt.fontStrikeOut():
                            color = self._muted_color
                        elif int(fmt.fontWeight()) >= int(QFont.Weight.DemiBold):
                            color = self._md_strong_color
                        elif fmt.fontItalic():
                            color = self._md_emphasis_color
                        elif in_list:
                            color = self._md_list_color
                        else:
                            color = self._text_color
                    if color is not None:
                        edit_cursor.setPosition(fragment.position())
                        edit_cursor.setPosition(
                            fragment.position() + fragment.length(),
                            QTextCursor.MoveMode.KeepAnchor,
                        )
                        char_format = QTextCharFormat()
                        char_format.setForeground(color)
                        if fmt.isAnchor():
                            # opencode TUI：链接带下划线
                            char_format.setFontUnderline(True)
                        href = fmt.anchorHref()
                        if (
                            fmt.isAnchor()
                            and href
                            and not fmt.toolTip()
                            and not href.startswith(_CONTROL_ANCHOR_PREFIXES)
                        ):
                            char_format.setToolTip(href)
                        edit_cursor.mergeCharFormat(char_format)
                iterator += 1
            block = block.next()

        edit_cursor.endEditBlock()

    # -- 图片 / 交互 / 布局 ------------------------------------------------

    def _apply_images(self, document: QTextDocument, resource_doc=None) -> None:
        """处理图片片段：本地加载注册、超宽缩放、远程按开关拦截。"""
        base = document.baseUrl()
        target_doc = resource_doc or document
        max_width = max(self._text_browser.viewport().width() - 24, 120)
        placeholder_fmt = QTextCharFormat()
        placeholder_fmt.setForeground(self._muted_color)
        block = document.begin()
        while block.isValid():
            iterator = block.begin()
            while not iterator.atEnd():
                fragment = iterator.fragment()
                if fragment.isValid():
                    fmt = fragment.charFormat()
                    if fmt.isImageFormat():
                        image_fmt = fmt.toImageFormat()
                        if not image_fmt.name().startswith("elamath://"):
                            self._apply_image_fragment(
                                document,
                                target_doc,
                                fragment,
                                image_fmt,
                                base,
                                max_width,
                                placeholder_fmt,
                            )
                iterator += 1
            block = block.next()
        self._center_standalone_images(document)

    def _center_standalone_images(self, document: QTextDocument) -> None:
        """独占一行的图片居中（Typora 风格；行内公式图片不参与）。"""
        block = document.begin()
        while block.isValid():
            if block.text().strip() == "\ufffc":
                has_image = False
                has_math = False
                iterator = block.begin()
                while not iterator.atEnd():
                    fragment = iterator.fragment()
                    if fragment.isValid() and fragment.charFormat().isImageFormat():
                        if (
                            fragment.charFormat()
                            .toImageFormat()
                            .name()
                            .startswith("elamath://")
                        ):
                            has_math = True
                        else:
                            has_image = True
                    iterator += 1
                if has_image and not has_math:
                    block_format = block.blockFormat()
                    block_format.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    self._apply_block_format(document, block, block_format)
            block = block.next()

    def _apply_image_fragment(
        self,
        document: QTextDocument,
        target_doc: QTextDocument,
        fragment,
        image_fmt: QTextImageFormat,
        base: QUrl,
        max_width: int,
        placeholder_fmt: QTextCharFormat,
    ) -> None:
        """单个图片片段：解析 URL、加载资源、必要时缩放或替换占位。"""
        source = self._resolve_image_url(image_fmt.name(), base)
        if source.scheme() in ("http", "https"):
            if not self._remote_images_enabled:
                self._replace_image_with_placeholder(
                    document, fragment, placeholder_fmt, source.toString()
                )
            return

        image = target_doc.resource(QTextDocument.ResourceType.ImageResource, source)
        if (
            image is not None
            and not isinstance(image, QImage)
            and hasattr(image, "toImage")
        ):
            image = image.toImage()
        if (image is None or image.isNull()) and source.isLocalFile():
            loaded = QImage(source.toLocalFile())
            if not loaded.isNull():
                image = loaded
                target_doc.addResource(
                    QTextDocument.ResourceType.ImageResource, source, image
                )
        if image is None or image.isNull():
            self._replace_image_with_placeholder(
                document, fragment, placeholder_fmt, source.toString()
            )
            return

        width = image.width()
        height = image.height()
        if source.scheme() == "elamermaid":
            # Mermaid 按 2x 超采样渲染，显示尺寸减半
            width /= 2.0
            height /= 2.0
        if width > max_width > 0:
            height = height * max_width / float(width)
            width = max_width
        cursor = QTextCursor(document)
        cursor.setPosition(fragment.position())
        cursor.setPosition(
            fragment.position() + fragment.length(),
            QTextCursor.MoveMode.KeepAnchor,
        )
        scaled = QTextImageFormat()
        scaled.setName(source.toString())
        scaled.setWidth(width)
        scaled.setHeight(height)
        cursor.mergeCharFormat(scaled)

    @staticmethod
    def _resolve_image_url(name: str, base: QUrl) -> QUrl:
        """图片名 → 绝对 URL（兼容 Windows 盘符路径与相对路径）。"""
        if re.match(r"^[A-Za-z]:[\\/]", name):
            return QUrl.fromLocalFile(name)
        source = QUrl(name)
        if source.isRelative() and not base.isEmpty():
            source = base.resolved(source)
        return source

    def _replace_image_with_placeholder(
        self,
        document: QTextDocument,
        fragment,
        placeholder_fmt: QTextCharFormat,
        detail: str = "",
    ) -> None:
        """把无法加载的图片替换为灰字占位（记录到渲染问题）。"""
        if detail:
            self._record_issue("image", detail)
        cursor = QTextCursor(document)
        cursor.setPosition(fragment.position())
        cursor.setPosition(
            fragment.position() + fragment.length(),
            QTextCursor.MoveMode.KeepAnchor,
        )
        cursor.removeSelectedText()
        cursor.insertText("[图片]", placeholder_fmt)

    def _record_issue(self, kind: str, detail: str) -> None:
        """记录一次渲染降级（去重）。"""
        entry = (kind, detail)
        if entry not in self._render_issues:
            self._render_issues.append(entry)

    def eventFilter(self, obj, event) -> bool:  # noqa: N802 (Qt 命名)
        """拦截右键菜单，并在鼠标移动时管理代码复制按钮显隐。"""
        viewport = self._text_browser.viewport()
        if event.type() == QEvent.Type.ContextMenu and obj in (
            self._text_browser,
            viewport,
        ):
            # 右键实际投递到 **viewport**（QAbstractScrollArea 的视口）—— 只拦
            # QTextBrowser 本体的话走的是 Qt 自带菜单（复制 / 复制链接 / 全选），
            # 自建菜单可达性为 0。坐标统一用 globalPos，免得再换算视口偏移。
            self._show_context_menu(event.globalPos())
            return True
        if obj is viewport:
            if event.type() == QEvent.Type.MouseMove:
                pressed = bool(
                    event.buttons()
                    & (
                        Qt.MouseButton.LeftButton
                        | Qt.MouseButton.RightButton
                        | Qt.MouseButton.MiddleButton
                    )
                )
                self._update_code_button_hover(event.pos(), pressed=pressed)
            elif event.type() == QEvent.Type.Leave:
                # 移向复制按钮（viewport 子控件）也会触发 Leave：
                # 按光标实际位置判定，避免按钮在点击前消失
                self._on_viewport_leave()
        elif obj in self._code_buttons:
            if event.type() == QEvent.Type.Leave:
                QTimer.singleShot(0, self._hover_from_cursor)
        return super().eventFilter(obj, event)

    def _on_viewport_leave(self, global_pos=None) -> None:
        """viewport 离开处理：光标仍落在代码块矩形内（如按钮上）时保持显示。"""
        if global_pos is None:
            global_pos = QCursor.pos()
        pos = QPointF(self._text_browser.viewport().mapFromGlobal(global_pos))
        for rect in self._code_button_rects:
            if not rect.isNull() and rect.contains(pos):
                return
        self._hide_code_buttons()

    def _show_context_menu(self, global_pos) -> None:
        # 副屏上 ElaMenu 偶发不按 sizeHint 撑开（只显示第一项）—— execElaMenu 兜底
        execElaMenu(self._create_context_menu(), global_pos)

    def _create_context_menu(self) -> ElaMenu:
        """构建右键菜单（Ela 风格：图标 + 统一行高）。

        只保留只读视图真正可用的动作 —— Qt 标准菜单里的撤销 / 剪切 / 粘贴 /
        删除对本组件没有意义（`setReadOnly(True)`），所以不用
        ``createStandardContextMenu()``，改为自建（对齐 ``terminal_view.py`` 的
        右键菜单写法）。
        """
        browser = self._text_browser
        cursor = browser.textCursor()
        menu = ElaMenu(self)
        menu.setMenuItemHeight(_CONTEXT_MENU_ITEM_HEIGHT)

        copy = menu.addElaIconAction(ElaIconType.IconName.Copy, "复制")
        copy.setEnabled(cursor.hasSelection())
        copy.triggered.connect(browser.copy)
        select_all = menu.addElaIconAction(ElaIconType.IconName.BorderAll, "全选")
        select_all.triggered.connect(browser.selectAll)

        menu.addSeparator()
        copy_code = menu.addElaIconAction(ElaIconType.IconName.Code, "复制代码块")
        copy_code.setEnabled(self._in_code_table(cursor))
        copy_code.triggered.connect(self._copy_code_at_cursor)
        copy_formula = menu.addElaIconAction(
            ElaIconType.IconName.SquareRootVariable, "复制 LaTeX 公式"
        )
        copy_formula.setEnabled(bool(self._formula_latex_at_cursor()))
        copy_formula.triggered.connect(self._copy_formula_at_cursor)
        copy_mermaid = menu.addElaIconAction(
            ElaIconType.IconName.DiagramProject, "复制 Mermaid 源码"
        )
        copy_mermaid.setEnabled(bool(self._mermaid_source_at_cursor()))
        copy_mermaid.triggered.connect(self._copy_mermaid_at_cursor)
        save_image = menu.addElaIconAction(
            ElaIconType.IconName.FloppyDisk, "图片另存为…"
        )
        save_image.setEnabled(bool(self._image_local_path_at_cursor()))
        save_image.triggered.connect(self._save_image_at_cursor)

        menu.addSeparator()
        quote = menu.addElaIconAction(
            ElaIconType.IconName.FileCode, "复制选中为 Markdown"
        )
        quote.setEnabled(cursor.hasSelection())
        quote.triggered.connect(self._copy_selection_markdown)
        copy_all = menu.addElaIconAction(ElaIconType.IconName.ClipboardList, "复制全文")
        copy_all.triggered.connect(self._copy_all)
        return menu

    def _formula_latex_at_cursor(self) -> str:
        """光标处的公式 LaTeX 源码（非公式返回空字符串）。"""
        return self._image_source_at_cursor("elamath://", "LaTeX: ")

    def _copy_formula_at_cursor(self) -> None:
        latex = self._formula_latex_at_cursor()
        if not latex:
            return
        QApplication.clipboard().setText(latex)
        self.formulaCopied.emit(latex)

    @staticmethod
    def _code_table_text(table: QTextTable) -> str:
        """提取代码表内容（优先读取表格式上的原始代码，跳过语言标签行）。"""
        stored = table.format().property(_CODE_TEXT_PROPERTY)
        if isinstance(stored, str):
            return stored
        start = 1 if table.rows() > 1 else 0
        parts = []
        for row in range(start, table.rows()):
            cell = table.cellAt(row, 0)
            cursor = QTextCursor(cell.firstCursorPosition())
            cursor.setPosition(
                cell.lastCursorPosition().position(),
                QTextCursor.MoveMode.KeepAnchor,
            )
            parts.append(cursor.selection().toPlainText())
        return "\n".join(parts)

    def _copy_code_at_cursor(self) -> None:
        frame = self._text_browser.textCursor().currentFrame()
        while frame is not None:
            if isinstance(frame, QTextTable) and self._is_code_table(frame):
                self._copy_text(self._code_table_text(frame))
                return
            frame = frame.parentFrame()

    def _copy_all(self) -> None:
        self._copy_text(self.document().toPlainText())

    def _copy_selection_markdown(self) -> None:
        """复制选中内容为 Markdown 源（并发出 ``selectionQuoted``）。"""
        quote = self.markdownSelection()
        if not quote:
            return
        QApplication.clipboard().setText(quote)
        self.selectionQuoted.emit(quote)

    def _copy_text(self, text: str) -> None:
        QApplication.clipboard().setText(text)
        self.codeCopied.emit(text)

    def _on_layout_refresh(self) -> None:
        """尺寸变化后重排：图片宽度与代码复制按钮位置。"""
        if sip.isdeleted(self) or sip.isdeleted(self._text_browser):
            return
        if self._source:
            self._apply_images(self.document())
        self._sync_code_buttons()
        self._sync_embedded_height()

    def _on_view_scrolled(self, _value: int) -> None:
        self._sync_code_buttons()
        if self._mermaid_jobs and not self._mermaid_priority_timer.isActive():
            self._mermaid_priority_timer.start()

    def _on_document_size_changed(self, _size) -> None:
        self._schedule_layout_refresh()

    def _schedule_layout_refresh(self, delay: int = 80) -> None:
        """前缘去抖：定时器已激活时不重置，避免文档规模抖动造成无限推迟。"""
        if not self._layout_timer.isActive():
            self._layout_timer.start(delay)

    def _sync_code_buttons(self) -> None:
        """同步代码复制按钮：代码块变化时重建，否则仅重新定位。"""
        tables = [
            table
            for table in self._iter_tables(self.document())
            if self._is_code_table(table)
        ]
        same = len(tables) == len(self._code_buttons_tables) and all(
            a == b for a, b in zip(tables, self._code_buttons_tables)
        )
        if same:
            self._position_code_buttons()
        else:
            self._rebuild_code_buttons(tables)

    @staticmethod
    def _iter_tables(document: QTextDocument) -> list:
        """按文档顺序收集全部表格（含嵌套）。"""
        tables = []
        stack = [document.rootFrame()]
        while stack:
            frame = stack.pop()
            for child in frame.childFrames():
                if isinstance(child, QTextTable):
                    tables.append(child)
                stack.append(child)
        tables.sort(key=lambda t: t.firstPosition())
        return tables

    def _rebuild_code_buttons(self, tables: list) -> None:
        """重建全部代码复制按钮（文档重渲染后表对象会失效）。"""
        for button in self._code_buttons:
            button.hide()
            button.deleteLater()
        self._code_buttons = []
        self._code_button_rects = []
        self._code_buttons_tables = list(tables)
        viewport = self._text_browser.viewport()
        for index in range(len(tables)):
            button = FlatIconButton(viewport)
            button.setObjectName("ElaMarkdownCopyButton")
            button.setFixedSize(_CODE_BUTTON_SIZE, _CODE_BUTTON_SIZE)
            button.setIconSize(QSize(14, 14))
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setAutoRaise(True)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            lang = tables[index].format().property(_CODE_LANG_PROPERTY) or ""
            button.setToolTip(f"复制代码 · {lang}" if lang else "复制代码")
            button.clicked.connect(
                lambda _checked=False, i=index: self._copy_code_block(i)
            )
            button.installEventFilter(self)
            button.hide()
            self._apply_code_button_style(button)
            self._code_buttons.append(button)
        self._position_code_buttons()

    def _apply_code_button_style(self, button: QToolButton) -> None:
        """按钮图标与悬浮 / 按下底色（随主题刷新；自绘，不用 QSS）。"""
        button.setIcon(self._code_copy_icon())
        button.setHoverColor(self._code_button_hover_bg)
        button.setPressColor(self._code_button_press_bg)
        button.setCornerRadius(6)

    def _code_copy_icon(self):
        return ElaIcon.getInstance().getElaIcon(
            ElaIconType.IconName.Copy, self._muted_color
        )

    def _code_check_icon(self):
        return ElaIcon.getInstance().getElaIcon(
            ElaIconType.IconName.Check, self._link_color
        )

    def _position_code_buttons(self) -> None:
        """把按钮摆到各代码块右上角（随滚动/尺寸变化）。"""
        viewport_height = self._text_browser.viewport().height()
        self._code_button_rects = []
        for button, table in zip(self._code_buttons, self._code_buttons_tables):
            rect = self._code_table_viewport_rect(table)
            self._code_button_rects.append(rect)
            if rect.isNull() or rect.top() < 0 or rect.top() > viewport_height:
                button.hide()
                continue
            x = int(rect.right() - button.width() - 6)
            y = self._code_button_y(table, rect, button)
            button.move(max(0, x), max(0, y))

    def _code_button_y(self, table: QTextTable, rect: QRectF, button) -> int:
        """复制按钮的纵向位置（无头栏，固定在代码卡右上角）。"""
        return int(rect.top() + 6)

    def _code_table_viewport_rect(self, table: QTextTable) -> QRectF:
        """代码表在 viewport 坐标系中的矩形（用于按钮定位与悬浮判定）。

        Qt 的 ``frameBoundingRect`` 对表格返回的 x/y 会被首个单元格的
        内边距整体平移（宽度与高度可信），因此这里用首个单元格光标位置
        反推左上角；代码表宽度固定 100%，右边界取文档内容右缘。
        """
        if sip.isdeleted(table) or table.rows() < 1 or table.columns() < 1:
            return QRectF()
        layout = self.document().documentLayout()
        frame_rect = layout.frameBoundingRect(table)
        if frame_rect.isNull():
            return QRectF()
        document = self.document()
        cell = table.cellAt(0, 0)
        cell_format = cell.format().toTableCellFormat()
        table_format = table.format()
        border = table_format.border()
        caret = self._text_browser.cursorRect(QTextCursor(cell.firstCursorPosition()))
        left = caret.left() - cell_format.leftPadding() - border
        top = caret.top() - cell_format.topPadding() - border
        right = self._text_browser.viewport().width() - 2 * document.documentMargin()

        # 底边：最后一行文本 + 单元格下内边距 + 边框 + 表格下外边距
        bottom = top + frame_rect.height()
        code_cell = table.cellAt(table.rows() - 1, 0)
        code_format = code_cell.format().toTableCellFormat()
        last_caret = self._text_browser.cursorRect(
            QTextCursor(code_cell.lastCursorPosition().block())
        )
        if last_caret.isValid():
            candidate = (
                last_caret.y()
                + last_caret.height()
                + code_format.bottomPadding()
                + border
                + table_format.bottomMargin()
            )
            bottom = max(top, candidate)
        return QRectF(left, top, max(right - left, 0.0), max(bottom - top, 0.0))

    # -- 自绘装饰（Typora 风格） -------------------------------------------

    def _visible_blocks(self, browser) -> tuple:
        """当前视口内可见的块范围 ``(first, last)``。"""
        document = self.document()
        viewport = browser.viewport()
        first = document.findBlock(browser.cursorForPosition(QPoint(0, 0)).position())
        last = document.findBlock(
            browser.cursorForPosition(
                QPoint(0, max(0, viewport.height() - 1))
            ).position()
        )
        if not first.isValid():
            first = document.begin()
        if not last.isValid():
            last = first
        return first, last

    def _paint_inline_code_backgrounds(self, browser, painter) -> None:
        """行内代码圆角底 + 边框（在文档绘制之前调用，避免盖住文字）。"""
        document = self.document()
        layout = document.documentLayout()
        offset = browser.verticalScrollBar().value()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        first, last = self._visible_blocks(browser)
        block = first
        while block.isValid():
            rect = layout.blockBoundingRect(block)
            if rect.top() - offset > browser.viewport().height():
                break
            self._paint_block_inline_codes(browser, painter, block)
            if block.blockNumber() >= last.blockNumber():
                break
            block = block.next()

    def _paint_block_inline_codes(self, browser, painter, block) -> None:
        """绘制单个块内全部行内代码标记的圆角底与边框。

        坐标一律用 ``cursorRect``（段起点的真实视口位置）反推行原点，
        ``cursorToX`` 只负责段内宽度——列表缩进 / 引用缩进 / 表格单元格
        局部坐标三种场景都成立（曾因 ``cursorRect + cursorToX`` 重复计入
        缩进而错位）。
        """
        text_layout = block.layout()
        if text_layout is None:
            return
        block_start = block.position()
        marks = []
        iterator = block.begin()
        while not iterator.atEnd():
            fragment = iterator.fragment()
            if fragment.isValid() and fragment.charFormat().property(_INLINE_CODE_MARK):
                marks.append((fragment.position() - block_start, fragment.length()))
            iterator += 1
        if not marks:
            return
        document = self.document()
        for index in range(text_layout.lineCount()):
            line = text_layout.lineAt(index)
            line_start = line.textStart()
            line_end = line_start + line.textLength()
            for frag_pos, frag_len in marks:
                segment_start = max(frag_pos, line_start)
                segment_end = min(frag_pos + frag_len, line_end)
                if segment_end <= segment_start:
                    continue
                cursor = QTextCursor(document)
                cursor.setPosition(block_start + segment_start)
                start_rect = browser.cursorRect(cursor)
                if not start_rect.isValid():
                    continue
                origin_x = start_rect.left() - line.cursorToX(segment_start)[0]
                x2 = origin_x + line.cursorToX(segment_end)[0]
                if x2 <= start_rect.left():
                    continue
                background = QRectF(
                    start_rect.left() - _INLINE_CODE_PADDING,
                    start_rect.top() + 1.0,
                    (x2 - start_rect.left()) + 2 * _INLINE_CODE_PADDING,
                    max(1.0, start_rect.height() - 2.0),
                )
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(self._inline_code_bg)
                painter.drawRoundedRect(
                    background, _INLINE_CODE_RADIUS, _INLINE_CODE_RADIUS
                )
                pen = QPen(self._inline_code_border)
                pen.setWidthF(1.0)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(
                    background, _INLINE_CODE_RADIUS, _INLINE_CODE_RADIUS
                )

    def _paint_document_decorations(self, browser, painter) -> None:
        """标题分隔线 / hr / 引用竖线 / 代码卡圆角（文档绘制之后调用）。"""
        document = self.document()
        layout = document.documentLayout()
        offset = browser.verticalScrollBar().value()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        first, last = self._visible_blocks(browser)
        block = first
        while block.isValid():
            rect = layout.blockBoundingRect(block)
            if rect.top() - offset > browser.viewport().height():
                break
            block_format = block.blockFormat()
            level = block_format.headingLevel()
            if level in (1, 2):
                painter.fillRect(
                    QRectF(
                        rect.x(),
                        rect.bottom() - offset - _HEADING_RULE_WIDTH,
                        rect.width(),
                        _HEADING_RULE_WIDTH,
                    ),
                    self._heading_rule_color,
                )
            if block_format.property(_HR_MARK):
                painter.fillRect(
                    QRectF(
                        rect.x(),
                        rect.center().y() - offset - _HR_LINE_WIDTH / 2.0,
                        rect.width(),
                        _HR_LINE_WIDTH,
                    ),
                    self._hr_color,
                )
            quote_level = block_format.property(QTextFormat.BlockQuoteLevel) or 0
            if quote_level:
                rail = block_format.property(_CALLOUT_RAIL_PROPERTY)
                color = QColor(rail) if rail else self._quote_rail_color
                painter.fillRect(
                    QRectF(
                        rect.x()
                        + _QUOTE_RAIL_INSET
                        + (int(quote_level) - 1) * _QUOTE_LEFT_MARGIN,
                        rect.top() - offset,
                        _QUOTE_RAIL_WIDTH,
                        rect.height(),
                    ),
                    color,
                )
            if block.blockNumber() >= last.blockNumber():
                break
            block = block.next()
        self._paint_code_card_chrome(browser, painter)

    def _paint_code_card_chrome(self, browser, painter) -> None:
        """代码软卡片：6px 圆角（无描边，Qt 表格无圆角 API，用四角遮罩补齐）。"""
        viewport_height = browser.viewport().height()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        for table in self._code_buttons_tables:
            rect = self._code_table_viewport_rect(table)
            if rect.isNull() or rect.bottom() < 0 or rect.top() > viewport_height:
                continue
            rounded = QRectF(rect)
            path = QPainterPath()
            path.addRoundedRect(rounded, _CODE_CARD_RADIUS, _CODE_CARD_RADIUS)
            painter.save()
            painter.setClipRect(rect)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self._base_bg)
            outer = QPainterPath()
            outer.addRect(rect)
            painter.drawPath(outer.subtracted(path))
            painter.restore()

    def _update_code_button_hover(self, pos, pressed: bool = False) -> None:
        """鼠标移动时显示所在代码块的复制按钮，其余隐藏。

        :param pressed: 事件是否携带按下按键（拖选文本时不弹按钮）
        """
        if pressed or QApplication.mouseButtons() != Qt.MouseButton.NoButton:
            # 拖选文本期间不弹出按钮，避免遮挡选择
            self._hide_code_buttons()
            return
        for index, rect in enumerate(self._code_button_rects):
            if rect.isNull():
                continue
            if rect.contains(QPointF(pos)):
                self._show_code_button(index)
                return
        self._hide_code_buttons()

    def _show_code_button(self, index: int) -> None:
        viewport_height = self._text_browser.viewport().height()
        for i, button in enumerate(self._code_buttons):
            rect = (
                self._code_button_rects[i]
                if i < len(self._code_button_rects)
                else QRectF()
            )
            visible = (
                i == index and not rect.isNull() and 0 <= rect.top() <= viewport_height
            )
            button.setVisible(visible)

    def _hide_code_buttons(self) -> None:
        for button in self._code_buttons:
            button.hide()

    def _hover_from_cursor(self) -> None:
        pos = self._text_browser.viewport().mapFromGlobal(QCursor.pos())
        self._update_code_button_hover(pos)

    def _copy_code_block(self, index: int) -> None:
        """复制指定代码块并给出短暂的对勾反馈。"""
        if not 0 <= index < len(self._code_buttons_tables):
            return
        table = self._code_buttons_tables[index]
        if sip.isdeleted(table):
            return
        self._copy_text(self._code_table_text(table))
        button = self._code_buttons[index]
        button.setIcon(self._code_check_icon())
        QTimer.singleShot(1000, lambda: self._restore_code_button_icon(button))

    def _restore_code_button_icon(self, button: QToolButton) -> None:
        try:
            button.setIcon(self._code_copy_icon())
        except RuntimeError:
            # 控件已随文档重渲染销毁
            pass

    def resizeEvent(self, event) -> None:  # noqa: N802 (Qt 命名)
        super().resizeEvent(event)
        self._schedule_layout_refresh()

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self._applyThemeStyle()

    def paintEvent(self, _event: Optional[QPaintEvent]) -> None:
        """绘制圆角背景（圆角半径为 0 时绘制普通矩形背景）；嵌入模式跳过。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self._embedded:
            bg_color = eTheme.getThemeColor(
                self._theme_mode, ElaThemeType.ThemeColor.BasicPress
            )
            if self._border_radius > 0:
                path = QPainterPath()
                path.addRoundedRect(
                    QRectF(self.rect()), self._border_radius, self._border_radius
                )
                painter.fillPath(path, bg_color)
            else:
                painter.fillRect(self.rect(), bg_color)
        if self._placeholder and not self._source:
            painter.setPen(self._placeholder_color)
            font = QFont(painter.font())
            font.setPointSizeF(max(self._base_font_point_size, 9.0))
            painter.setFont(font)
            painter.drawText(
                self.rect().adjusted(16, 16, -16, -16),
                int(Qt.AlignmentFlag.AlignCenter) | int(Qt.TextFlag.TextWordWrap),
                self._placeholder,
            )
        self._paint_stream_caret(painter)
        painter.end()

    def _paint_stream_caret(self, painter: QPainter) -> None:
        """流式期间在文档末尾绘制闪烁打字光标。"""
        if not (self._stream_active and self._caret_visible and self._source):
            return
        document = self.document()
        if document.characterCount() <= 1:
            return
        cursor = QTextCursor(document)
        cursor.movePosition(QTextCursor.MoveOperation.End)
        rect = self._text_browser.cursorRect(cursor)
        if not rect.isValid():
            return
        top_left = self._text_browser.viewport().mapTo(self, rect.topLeft())
        painter.fillRect(
            QRectF(float(top_left.x()), float(top_left.y()), 2.0, float(rect.height())),
            self._text_color,
        )
