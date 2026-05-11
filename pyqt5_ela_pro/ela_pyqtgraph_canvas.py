"""
ElaPlotWidget - 主题感知 pyqtgraph 绘图控件。

基于 pyqtgraph.GraphicsLayoutWidget 封装，自动适配 Ela 深浅色主题。
当 pyqtgraph 未安装时，导入和引用不会报错，仅实例化时抛出 ImportError。

用法::

    from pyqt5_ela_pro import ElaPlotWidget

    pw = ElaPlotWidget(parent=self)
    plot = pw.plot()
    plot.plot([1, 2, 3], [4, 5, 6])
"""

from __future__ import annotations

from PyQt5.QtWidgets import QWidget, QSizePolicy

from PyQt5ElaWidgetTools import eTheme, ElaThemeType

from ._internal import disconnect_theme_signal

# ── Optional pyqtgraph import ──────────────────────────

try:
    import pyqtgraph as pg
except ImportError:
    pg = None


_LIGHT_THEME: dict[str, str] = {
    "background": "#FFFFFF",
    "foreground": "#333333",
    "axis": "#D9D9D9",
    "grid": "#F0F0F0",
    "label": "#333333",
}

_DARK_THEME: dict[str, str] = {
    "background": "#1E1E2E",
    "foreground": "#E0E0E0",
    "axis": "#424242",
    "grid": "#333333",
    "label": "#E0E0E0",
}


if pg is not None:

    class ElaPlotWidget(pg.GraphicsLayoutWidget):
        """主题感知 pyqtgraph 绘图控件。

        自动跟随 Ela 主题切换 Light/Dark 配色。
        基于 ``GraphicsLayoutWidget``，支持多图布局。

        :param parent: 父控件
        """

        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)

            self.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )

            self._theme_mode = eTheme.getThemeMode()
            self._theme_connected = True
            eTheme.themeModeChanged.connect(self._onThemeChanged)
            self._apply_theme()

        # ── Public API ────────────────────────────────────

        def plot(self, *args, **kwargs) -> pg.PlotItem:
            """添加并返回一个 ``PlotItem``。

            :param args: 传递给 ``addPlot`` 的位置参数
            :param kwargs: 传递给 ``addPlot`` 的关键字参数
            :returns: 新建的 PlotItem
            """
            return self.addPlot(*args, **kwargs)

        def setStyle(self, **kwargs) -> None:
            """应用额外的 pyqtgraph 全局配置。

            :param kwargs: pyqtgraph ``setConfigOptions`` 参数
            """
            pg.setConfigOptions(**kwargs)

        # ── Internal ──────────────────────────────────────

        def _apply_theme(self) -> None:
            is_dark = self._theme_mode == ElaThemeType.ThemeMode.Dark
            theme = _DARK_THEME if is_dark else _LIGHT_THEME
            self.setBackground(theme["background"])

        def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
            self._theme_mode = mode
            self._apply_theme()

        def deleteLater(self) -> None:
            if self._theme_connected:
                disconnect_theme_signal(self._onThemeChanged)
                self._theme_connected = False
            super().deleteLater()

else:

    class ElaPlotWidget:  # type: ignore[no-redef]
        """pyqtgraph 未安装时的占位类。"""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "ElaPlotWidget 需要 pyqtgraph，请运行: pip install pyqtgraph"
            )
