"""
ElaFigureCanvas - 主题感知 Matplotlib 画布组件。

基于 FigureCanvasQTAgg 封装，自动适配 Ela 深浅色主题。
当 matplotlib 未安装时，导入和引用不会报错，仅实例化时抛出 ImportError。

用法::

    from pyqt5_ela_pro import ElaFigureCanvas

    canvas = ElaFigureCanvas(parent=self)
    ax = canvas.figure.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QSizePolicy

from PyQt5ElaWidgetTools import eTheme, ElaThemeType

from ._internal import disconnect_theme_signal

# ── Optional matplotlib import ──────────────────────────

try:
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvasQTAgg as _FigureCanvas,
    )
    from matplotlib.figure import Figure
    import matplotlib as mpl
except ImportError:
    _FigureCanvas = None
    Figure = None
    mpl = None


_LIGHT_RCPARAMS: dict = {
    "figure.facecolor": "#FFFFFF",
    "axes.facecolor": "#FFFFFF",
    "axes.edgecolor": "#D9D9D9",
    "axes.labelcolor": "#333333",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "grid.color": "#F0F0F0",
    "text.color": "#333333",
}

_DARK_RCPARAMS: dict = {
    "figure.facecolor": "#1E1E2E",
    "axes.facecolor": "#2A2A3C",
    "axes.edgecolor": "#424242",
    "axes.labelcolor": "#E0E0E0",
    "xtick.color": "#E0E0E0",
    "ytick.color": "#E0E0E0",
    "grid.color": "#333333",
    "text.color": "#E0E0E0",
}

_CJK_FONTS = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans SC",
    "DengXian",
    "Microsoft JhengHei",
]


if _FigureCanvas is not None:

    class ElaFigureCanvas(_FigureCanvas):
        """主题感知 Matplotlib 画布。

        自动跟随 Ela 主题切换 Light/Dark 配色。
        支持所有 FigureCanvasQTAgg 原有功能。

        :param parent: 父控件
        """

        def __init__(
            self,
            parent: Optional[QWidget] = None,
        ) -> None:
            fig = Figure()
            _FigureCanvas.__init__(self, fig)
            if parent is not None:
                self.setParent(parent)

            self.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

            self._theme_mode = eTheme.getThemeMode()
            self._theme_connected = True
            eTheme.themeModeChanged.connect(self._onThemeChanged)
            self.destroyed.connect(self._theme_cleanup)
            self._setup_cjk_font()
            self._apply_theme()

        # ── Public API ────────────────────────────────────

        def setStyle(self, rcparams: dict) -> None:
            """应用额外的 matplotlib rcParams 样式参数。

            :param rcparams: matplotlib rcParams 字典
            """
            if mpl:
                mpl.rcParams.update(rcparams)
            self.draw_idle()

        # ── Internal ──────────────────────────────────────

        def _theme_cleanup(self) -> None:
            if self._theme_connected:
                disconnect_theme_signal(self._onThemeChanged)
                self._theme_connected = False

        @staticmethod
        def _setup_cjk_font() -> None:
            if not mpl:
                return
            existing = mpl.rcParams.get("font.sans-serif", [])
            for f in _CJK_FONTS:
                if f not in existing:
                    existing.insert(0, f)
            mpl.rcParams["font.sans-serif"] = existing
            mpl.rcParams["axes.unicode_minus"] = False

        def deleteLater(self) -> None:
            self._theme_cleanup()
            super().deleteLater()

        def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
            self._theme_mode = mode
            self._apply_theme()
            self.draw_idle()

        def _apply_theme(self) -> None:
            if not mpl:
                return
            is_dark = self._theme_mode == ElaThemeType.ThemeMode.Dark
            rc = _DARK_RCPARAMS if is_dark else _LIGHT_RCPARAMS
            mpl.rcParams.update(rc)
            self.figure.set_facecolor(rc["figure.facecolor"])
            for ax in self.figure.axes:
                ax.set_facecolor(rc["axes.facecolor"])
                ax.tick_params(
                    colors=rc["xtick.color"],
                    which="both",
                )
                for spine in ax.spines.values():
                    spine.set_color(rc["axes.edgecolor"])


else:

    class ElaFigureCanvas:  # type: ignore[no-redef]
        """matplotlib 未安装时的占位类。"""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "ElaFigureCanvas 需要 matplotlib，请运行: uv pip install matplotlib"
            )
