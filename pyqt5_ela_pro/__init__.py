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
    ElaSearchableComboBox,
    ElaSearchableMultiComboBox,
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

from .ela_capsule_combo_box import ElaCapsuleComboBox

from .ela_capsule_multi_combo_box import ElaCapsuleMultiComboBox

from .ela_capsule_searchable_combo_box import ElaCapsuleSearchableComboBox

from .ela_capsule_searchable_multi_combo_box import ElaCapsuleSearchableMultiComboBox

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
    "ElaSearchableComboBox",
    "ElaSearchableMultiComboBox",
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
    "ElaCapsuleComboBox",
    "ElaCapsuleMultiComboBox",
    "ElaCapsuleSearchableComboBox",
    "ElaCapsuleSearchableMultiComboBox",
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
