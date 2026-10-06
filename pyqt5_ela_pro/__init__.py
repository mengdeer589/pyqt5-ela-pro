"""
pyqt5_ela_pro - PyQt5 Extension Widgets Module

Extension components based on PyQt5ElaWidgetTools with custom styling.
"""

from ._version import __version__

# ── Windows 7 DirectWrite 兼容补丁 ───────────────────────────────────────────
# Qt 5 on Windows 7 has a known bug where DirectWrite's CreateFontFaceFromHDC()
# fails for fonts like ElaAwesome / Microsoft YaHei / SimSun, spamming stderr
# with "尚未实现" warnings. Filter them out at the Qt message handler level.
import sys as _sys

if _sys.platform == "win32":
    try:
        _win_ver = _sys.getwindowsversion()
        _is_win7 = _win_ver.major == 6 and _win_ver.minor == 1
    except Exception:
        _is_win7 = False

    if _is_win7:
        from PyQt5.QtCore import qInstallMessageHandler  # noqa: E402

        _saved_handler = qInstallMessageHandler(None)

        def _directwrite_filter(msg_type, context, message):
            if "CreateFontFaceFromHDC() failed" in message:
                return
            if _saved_handler:
                _saved_handler(msg_type, context, message)
            else:
                _sys.stderr.write(message + "\n")

        qInstallMessageHandler(_directwrite_filter)

# ── Functions ────────────────────────────────────────────────────────────────

from .tooltips import (
    set_tooltip,
    remove_tooltip,
)

from .animation import fade_in, fade_out, shake_window

from ._motion import (
    Duration,
    Easing,
    MotionKind,
    MotionMode,
    MotionPolicy,
    idle_loop_running,
    motion,
    start_idle_loop,
    start_transition,
    start_transition_timer,
)

from ._theme import (
    StatusRole,
    accent,
    border,
    borderStrong,
    chartPalette,
    resetAccentColor,
    setAccentColor,
    statusColor,
    surface,
    surfaceDialog,
    surfacePopup,
    surfaceRaised,
    text,
    textDisabled,
    textMuted,
    textOnAccent,
)

from ._ownership import ContentSlot, WidgetOwnership

# ── Fluent 风格新增组件 ──
from .ela_shimmer import (
    ElaShimmer,
    ShimmerElement,
    ShimmerPalette,
    ShimmerShape,
    ShimmerTemplate,
)
from .ela_field import ElaField, FieldStatus
from .ela_avatar import AvatarPresence, AvatarShape, AvatarSize, ElaAvatar
from .ela_selector_bar import (
    ElaSelectorBar,
    SelectorBarItem,
    SelectorBarOverflow,
)

from .svg_icon import (
    svg_to_icon,
    svg_to_image,
    svg_to_pixmap,
    svg_icon_loader,
)

from .splitter import create_ela_splitter

from .notify_popup import show_notify

# ── Components ───────────────────────────────────────────────────────────────

from .widget_base import ElaThemeWidget

from .table_view import ElaDataTable

from .combo_box import (
    ElaSearchBox,
    ElaSearchMultiBox,
)

from .tooltips import (
    ElaToolTipPosition,
    ElaToolTip,
    ElaStateToolTip,
)

from .dialog_base import ElaDialogBase

from .message_dialog import ElaMessageDialog

from .parquet_table import ElaParquetTable

from .splash_screen import ElaSplashScreen

from .terminal_view import (
    AnsiColor,
    AnsiParser,
    ElaTerminalView,
    TerminalLine,
    TerminalSpan,
    TerminalStyle,
    defaultTerminalTheme,
    registerTerminalTheme,
    setDefaultTerminalTheme,
    terminalThemes,
    unregisterTerminalTheme,
)

from .animation import ElaAnimatedMixin

from .taskbar_progress import ElaTaskbarProgress

from .office_viewer import ElaWordViewer, ElaExcelViewer, ElaPowerPointViewer

from .ela_long_press_button import ElaLongPressButton

from .ela_markdown_viewer import (
    ElaMarkdownViewer,
    defaultMarkdownTheme,
    markdownThemes,
    registerMarkdownTheme,
    setDefaultMarkdownTheme,
    unregisterMarkdownTheme,
)

from .ela_tag_line_edit import ElaTagLineEdit

from .ela_confirm_dialog import ElaConfirmDialog

from .ela_dashboard_gauge import ElaDashboardGauge

from .ela_divider import ElaDivider

from .ela_drawer_area import ElaDrawerArea

from .ela_button import ElaButton

from .ela_chip import ElaChip

from .ela_dropdown_button import ElaDropDownButton

from .ela_figure_canvas import ElaFigureCanvas

from .ela_ghost_box import ElaGhostBox

from .ela_group_box import ElaGroupBox

from .ela_info_badge import ElaInfoBadge

from .ela_pagination import ElaPagination

from .ela_password_edit import ElaPasswordEdit

from .ela_pyqtgraph_canvas import ElaPlotWidget

from .ela_progress_button import ElaProgressButton

from .ela_rating_control import ElaRatingControl

from .ela_side_drawer import ElaDrawer, ElaDrawerPosition

from .ela_split_button import ElaSplitButton

from .ela_spotlight import ElaSpotlight

from .ela_steps import ElaSteps

from .ela_timeline import ElaTimeline

from .ela_toast import ElaToast

from .ela_upload_area import ElaUploadArea

from .charts import ElaChartWidget

from .chat import (
    AttachmentStrip,
    ContextToolGroupCard,
    ElaChatAsyncWorker,
    ElaChatAttachment,
    ElaChatAvatarSource,
    ElaChatBubble,
    ElaChatInput,
    ElaChatInputDock,
    ElaChatMessage,
    ElaChatMockBackend,
    ElaChatMockChunk,
    ElaChatMockUsage,
    ElaChatPart,
    ElaChatPartKind,
    ElaChatQueueDock,
    ElaChatReasoningStyle,
    ElaChatRole,
    ElaChatSessionInfo,
    ElaChatStats,
    ElaChatStatus,
    ElaChatStatusBar,
    ElaChatStreamBinder,
    ElaChatSuggestion,
    ElaChatToolBar,
    ElaChatToolButton,
    ElaChatToolCall,
    ElaChatToolStatus,
    ElaChatTurnSummary,
    ElaChatView,
    ElaChatWidget,
    ErrorCard,
    MessageActions,
    MessageHeader,
    MessageMeta,
    ReasoningBlock,
    StatsBadge,
    SuggestionPopup,
    ThinkingRow,
    ToolCallCard,
    ToolGroupPanel,
)

from .menu_item import ElaMenuItem

from .ela_tray_icon import ElaTrayIcon

from .selection_assistant import (
    ElaClipboardCapture,
    ElaMouseMonitor,
    ElaSelectionAssistant,
    ElaSelectionPopup,
    ElaSelectionResultDialog,
)

from .ela_tag_box import ElaTagBox

from .ela_tag_multi_box import ElaTagMultiBox

from .ela_tag_search_box import ElaTagSearchBox

from .ela_tag_search_multi_box import ElaTagSearchMultiBox

from .notify_popup import ElaNotifyPopup

from .svg_icon import (
    ElaSvgIconLoader,
)

from .window_embedder import ElaWindowEmbedder

from .browser_embedder import ElaBrowserEmbedder

from .splitter import ElaSplitter

from .blueprint import (
    ElaBlueprintCanvas,
    ElaBlueprintGraph,
    ElaBlueprintNode,
    ElaEdge,
    ElaEdgeWidget,
    ElaExecutionController,
    ElaNodeContextMenu,
    ElaNodeCreationMenu,
    ElaNodeRegistry,
    ElaNodeSpec,
    ElaNodeWidget,
    ElaPin,
    ElaPinDirection,
    ElaPinHandle,
    ElaTempWire,
    PIN_COLORS,
    bezier_path,
    format_elapsed,
    gl_available,
    pin_color,
    register_node_type,
    register_pin_type,
    types_compatible,
)


__all__ = [
    # ── 动效策略 ──
    "motion",
    "MotionMode",
    "MotionKind",
    "MotionPolicy",
    "Duration",
    "Easing",
    "start_transition",
    "start_transition_timer",
    "start_idle_loop",
    "idle_loop_running",
    # ── 语义令牌 ──
    "StatusRole",
    "surface",
    "surfaceRaised",
    "surfacePopup",
    "surfaceDialog",
    "border",
    "borderStrong",
    "text",
    "textMuted",
    "textDisabled",
    "textOnAccent",
    "accent",
    "statusColor",
    "chartPalette",
    "setAccentColor",
    "resetAccentColor",
    # ── 内容所有权 ──
    "WidgetOwnership",
    "ContentSlot",
    # ── 骨架屏 ──
    "ElaShimmer",
    "ShimmerShape",
    "ShimmerTemplate",
    "ShimmerElement",
    "ShimmerPalette",
    # ── 表单字段 ──
    "ElaField",
    "FieldStatus",
    # ── 头像 ──
    "ElaAvatar",
    "AvatarSize",
    "AvatarShape",
    "AvatarPresence",
    # ── 分段控件 ──
    "ElaSelectorBar",
    "SelectorBarItem",
    "SelectorBarOverflow",
    # ── Functions ──
    "fade_in",
    "fade_out",
    "shake_window",
    "set_tooltip",
    "remove_tooltip",
    "svg_to_icon",
    "svg_to_image",
    "svg_to_pixmap",
    "svg_icon_loader",
    "create_ela_splitter",
    "show_notify",
    # ── Components ──
    "ElaAnimatedMixin",
    "ElaBlueprintCanvas",
    "ElaBlueprintGraph",
    "ElaBlueprintNode",
    "ElaBrowserEmbedder",
    "ElaButton",
    "ElaChartWidget",
    "ElaChatAsyncWorker",
    "ElaChatAttachment",
    "ElaChatAvatarSource",
    "ElaChatBubble",
    "ElaChatInput",
    "ElaChatInputDock",
    "ElaChatMessage",
    "ElaChatMockBackend",
    "ElaChatMockChunk",
    "ElaChatMockUsage",
    "ElaChatPart",
    "ElaChatPartKind",
    "ElaChatQueueDock",
    "ElaChatReasoningStyle",
    "ElaChatRole",
    "ElaChatSessionInfo",
    "ElaChatStats",
    "ElaChatStatus",
    "ElaChatStatusBar",
    "ElaChatStreamBinder",
    "ElaChatSuggestion",
    "ElaChatToolBar",
    "ElaChatToolButton",
    "ElaChatToolCall",
    "ElaChatToolStatus",
    "ElaChatTurnSummary",
    "ElaChatView",
    "ElaChatWidget",
    "ElaChip",
    "ElaClipboardCapture",
    "ElaConfirmDialog",
    "ElaDashboardGauge",
    "ElaDataTable",
    "ElaDialogBase",
    "ElaDivider",
    "ElaDrawer",
    "ElaDrawerArea",
    "ElaDrawerPosition",
    "ElaDropDownButton",
    "ElaEdge",
    "ElaEdgeWidget",
    "ElaExcelViewer",
    "ElaExecutionController",
    "ElaFigureCanvas",
    "ElaGhostBox",
    "ElaGroupBox",
    "ElaInfoBadge",
    "ElaLongPressButton",
    "ElaMarkdownViewer",
    "ElaMenuItem",
    "markdownThemes",
    "defaultMarkdownTheme",
    "setDefaultMarkdownTheme",
    "registerMarkdownTheme",
    "unregisterMarkdownTheme",
    "ElaMessageDialog",
    "ElaMouseMonitor",
    "ElaNodeContextMenu",
    "ElaNodeCreationMenu",
    "ElaNodeRegistry",
    "ElaNodeSpec",
    "ElaNodeWidget",
    "ElaNotifyPopup",
    "ElaParquetTable",
    "ElaPasswordEdit",
    "ElaPin",
    "ElaPinDirection",
    "ElaPinHandle",
    "ElaPlotWidget",
    "ElaPagination",
    "ElaPowerPointViewer",
    "ElaProgressButton",
    "ElaRatingControl",
    "ElaSearchBox",
    "ElaSearchMultiBox",
    "ElaSelectionAssistant",
    "ElaSelectionPopup",
    "ElaSelectionResultDialog",
    "ElaSplashScreen",
    "ElaSplitButton",
    "ElaSplitter",
    "ElaSpotlight",
    "ElaStateToolTip",
    "ElaSteps",
    "ElaSvgIconLoader",
    "ElaTagBox",
    "ElaTagLineEdit",
    "ElaTagMultiBox",
    "ElaTagSearchBox",
    "ElaTagSearchMultiBox",
    "ElaTaskbarProgress",
    "ElaTempWire",
    "ElaTerminalView",
    "ElaThemeWidget",
    "ElaTrayIcon",
    "ElaTimeline",
    "ElaToast",
    "ElaToolTip",
    "ElaToolTipPosition",
    "ElaUploadArea",
    "ElaWindowEmbedder",
    "ElaWordViewer",
    "ContextToolGroupCard",
    "ToolGroupPanel",
    "ToolCallCard",
    "MessageHeader",
    "MessageActions",
    "MessageMeta",
    "ReasoningBlock",
    "ThinkingRow",
    "StatsBadge",
    "SuggestionPopup",
    "AttachmentStrip",
    "ErrorCard",
    "PIN_COLORS",
    "bezier_path",
    "format_elapsed",
    "gl_available",
    "pin_color",
    "register_node_type",
    "register_pin_type",
    "types_compatible",
    # ── 终端组件 ──
    "AnsiColor",
    "AnsiParser",
    "TerminalLine",
    "TerminalSpan",
    "TerminalStyle",
    "defaultTerminalTheme",
    "registerTerminalTheme",
    "setDefaultTerminalTheme",
    "terminalThemes",
    "unregisterTerminalTheme",
    "__version__",
]
