"""
pyqt5_ela_pro - PyQt5 Extension Widgets Module

Extension components based on PyQt5ElaWidgetTools with custom styling.
"""

__version__ = "1.0.0"

from .utils import shake_window

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

from .parquet_table import ElaParquetTable

from .splash_screen import ElaSplashScreen

from .animation import fade_in, fade_out, ElaAnimatedMixin

from .taskbar_progress import ElaTaskbarProgress

from .office_viewer import ElaWordViewer, ElaExcelViewer, ElaPowerPointViewer

from .ela_long_press_button import ElaLongPressBtn

from .ela_capsule_line_edit import ElaCapsuleLineEdit

from .ela_primary_button import ElaPrimaryBtn, ElaToolBtn

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
    "ElaParquetTable",
    "ElaSplashScreen",
    "fade_in",
    "fade_out",
    "ElaAnimatedMixin",
    "ElaTaskbarProgress",
    "ElaWordViewer",
    "ElaExcelViewer",
    "ElaPowerPointViewer",
    "ElaLongPressBtn",
    "ElaCapsuleLineEdit",
    "ElaPrimaryBtn",
    "ElaToolBtn",
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
]
