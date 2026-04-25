"""
pyqt5_ela_pro - PyQt5 Extension Widgets Module

Extension components based on PyQt5ElaWidgetTools with custom styling.
"""

__version__ = "1.0.0"

from .widget_base import ThemeWidget

from .table_view import ElaDataTable

from .scrollable_menu import ElaScrollableMenu

from .combo_box import (
    ElaSearchBox,
    ElaSearchMultiBox,
)

from .tooltips import (
    ElaToolTipPosition,
    ToolTip,
    set_tooltip,
    remove_tooltip,
    StateToolTip,
)

from .dialog_base import ElaDialogBase

from .message_dialog import ElaMessageDialog

from .parquet_table import ElaParquetTable

from .splash_screen import ElaSplashScreen

from .animation import fade_in, fade_out, shake_window, ElaAnimatedMixin

from .taskbar_progress import ElaTaskbarProgress

from .office_viewer import ElaWordViewer, ElaExcelViewer, ElaPowerPointViewer

from .ela_long_press_button import ElaLongPressButton

from .ela_tag_line_edit import ElaTagLineEdit

from .ela_primary_button import ElaPrimaryButton, ElaToolButton

from .ela_tag_box import ElaTagBox

from .ela_tag_multi_box import ElaTagMultiBox

from .ela_tag_search_box import ElaTagSearchBox

from .ela_tag_search_multi_box import ElaTagSearchMultiBox

from .ela_trend_chart import ElaTrendChart

from .ela_side_drawer import ElaDrawer, ElaDrawerPosition

from .svg_icon import (
    svg_to_icon,
    svg_to_pixmap,
    ElaSvgIconLoader,
    ElaSvgButton,
    ElaSvgIconButton,
    svgIconLoader,
)

from .window_embedder import ElaWindowEmbedder

from .browser_embedder import ElaBrowserEmbedder

from .splitter import ElaSplitter, create_ela_splitter

from .ela_progress_button import ElaProgressButton

from .notify_popup import ElaNotifyPopup, show_notify


__all__ = [
    "__version__",
    "shake_window",
    "ThemeWidget",
    "ElaDataTable",
    "ElaScrollableMenu",
    "ElaSearchBox",
    "ElaSearchMultiBox",
    "ElaToolTipPosition",
    "ToolTip",
    "set_tooltip",
    "remove_tooltip",
    "StateToolTip",
    "ElaDialogBase",
    "ElaMessageDialog",
    "ElaParquetTable",
    "ElaSplashScreen",
    "fade_in",
    "fade_out",
    "ElaAnimatedMixin",
    "ElaTaskbarProgress",
    "ElaWordViewer",
    "ElaExcelViewer",
    "ElaPowerPointViewer",
    "ElaLongPressButton",
    "ElaTagLineEdit",
    "ElaPrimaryButton",
    "ElaToolButton",
    "ElaTagBox",
    "ElaTagMultiBox",
    "ElaTagSearchBox",
    "ElaTagSearchMultiBox",
    "ElaTrendChart",
    "ElaDrawer",
    "ElaDrawerPosition",
    "svg_to_icon",
    "svg_to_pixmap",
    "ElaSvgIconLoader",
    "ElaSvgButton",
    "ElaSvgIconButton",
    "svgIconLoader",
    "ElaWindowEmbedder",
    "ElaBrowserEmbedder",
    "ElaSplitter",
    "create_ela_splitter",
    "ElaProgressButton",
    "ElaNotifyPopup",
    "show_notify",
]
