"""
pyqt5_ela_pro - PyQt5 Extension Widgets Module

Extension components based on PyQt5ElaWidgetTools with custom styling.
"""

__version__ = "1.0.0"

# ── Functions ────────────────────────────────────────────────────────────────

from .tooltips import (
    set_tooltip,
    remove_tooltip,
)

from .animation import fade_in, fade_out, shake_window

from .svg_icon import (
    svg_to_icon,
    svg_to_pixmap,
    svg_icon_loader,
)

from .splitter import create_ela_splitter

from .notify_popup import show_notify

# ── Components ───────────────────────────────────────────────────────────────

from .widget_base import ElaThemeWidget

from .table_view import ElaDataTable

from .scrollable_menu import ElaScrollableMenu

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

from .animation import ElaAnimatedMixin

from .taskbar_progress import ElaTaskbarProgress

from .office_viewer import ElaWordViewer, ElaExcelViewer, ElaPowerPointViewer

from .ela_long_press_button import ElaLongPressButton

from .ela_tag_line_edit import ElaTagLineEdit

from .ela_primary_button import ElaPrimaryButton, ElaThemeToolButton

from .ela_tag_box import ElaTagBox

from .ela_tag_multi_box import ElaTagMultiBox

from .ela_tag_search_box import ElaTagSearchBox

from .ela_tag_search_multi_box import ElaTagSearchMultiBox

from .ela_trend_chart import ElaTrendChart

from .ela_side_drawer import ElaDrawer, ElaDrawerPosition

from .svg_icon import (
    ElaSvgIconLoader,
    ElaSvgButton,
    ElaSvgIconButton,
)

from .window_embedder import ElaWindowEmbedder

from .browser_embedder import ElaBrowserEmbedder

from .splitter import ElaSplitter

from .ela_progress_button import ElaProgressButton

from .notify_popup import ElaNotifyPopup


__all__ = [
    # ── Functions ──
    "fade_in",
    "fade_out",
    "shake_window",
    "set_tooltip",
    "remove_tooltip",
    "svg_to_icon",
    "svg_to_pixmap",
    "svg_icon_loader",
    "create_ela_splitter",
    "show_notify",
    # ── Components ──
    "ElaAnimatedMixin",
    "ElaBrowserEmbedder",
    "ElaDataTable",
    "ElaDialogBase",
    "ElaDrawer",
    "ElaDrawerPosition",
    "ElaExcelViewer",
    "ElaLongPressButton",
    "ElaMessageDialog",
    "ElaNotifyPopup",
    "ElaParquetTable",
    "ElaPowerPointViewer",
    "ElaPrimaryButton",
    "ElaProgressButton",
    "ElaScrollableMenu",
    "ElaSearchBox",
    "ElaSearchMultiBox",
    "ElaSplashScreen",
    "ElaSplitter",
    "ElaStateToolTip",
    "ElaSvgButton",
    "ElaSvgIconButton",
    "ElaSvgIconLoader",
    "ElaTagBox",
    "ElaTagLineEdit",
    "ElaTagMultiBox",
    "ElaTagSearchBox",
    "ElaTagSearchMultiBox",
    "ElaTaskbarProgress",
    "ElaThemeToolButton",
    "ElaThemeWidget",
    "ElaToolTip",
    "ElaToolTipPosition",
    "ElaTrendChart",
    "ElaWindowEmbedder",
    "ElaWordViewer",
    "__version__",
]
