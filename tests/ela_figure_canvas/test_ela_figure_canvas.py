from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch, ANY


class TestElaFigureCanvasNoMatplotlib:
    def test_placeholder_raises_import_error(self):
        with patch.dict("sys.modules", {"matplotlib": None}):
            import importlib
            import pyqt5_ela_pro.ela_figure_canvas as fc
            importlib.reload(fc)
            with pytest.raises(ImportError):
                fc.ElaFigureCanvas()
            fc._FigureCanvas = None
            importlib.reload(fc)

    def test_light_rcparams_defined(self):
        from pyqt5_ela_pro.ela_figure_canvas import _LIGHT_RCPARAMS
        assert "figure.facecolor" in _LIGHT_RCPARAMS
        assert "axes.facecolor" in _LIGHT_RCPARAMS
        assert len(_LIGHT_RCPARAMS) == 8

    def test_dark_rcparams_defined(self):
        from pyqt5_ela_pro.ela_figure_canvas import _DARK_RCPARAMS
        assert "figure.facecolor" in _DARK_RCPARAMS
        assert len(_DARK_RCPARAMS) == 8

    def test_cjk_fonts_defined(self):
        from pyqt5_ela_pro.ela_figure_canvas import _CJK_FONTS
        assert len(_CJK_FONTS) > 0
        assert "Microsoft YaHei" in _CJK_FONTS


@pytest.mark.usefixtures("qapp")
class TestElaFigureCanvasWithMatplotlib:
    @pytest.fixture(autouse=True)
    def _reload_with_mocks(self):
        import importlib
        import pyqt5_ela_pro.ela_figure_canvas as fc_mod
        with patch.object(fc_mod, "_FigureCanvas") as mock_fc:
            with patch.object(fc_mod, "mpl") as mock_mpl:
                with patch.object(fc_mod, "Figure") as mock_fig:
                    mock_rcparams = MagicMock()
                    mock_mpl.rcParams = mock_rcparams
                    mock_fig_instance = MagicMock()
                    mock_fig.return_value = mock_fig_instance
                    mock_fig_instance.axes = []
                    mock_fig_instance.get_axes.return_value = []
                    mock_fc_instance = MagicMock()
                    mock_fc.return_value = mock_fc_instance
                    importlib.reload(fc_mod)
                    yield {
                        "mod": fc_mod,
                        "mpl": mock_mpl,
                        "fig_instance": mock_fig_instance,
                    }

    def test_initialization(self, _reload_with_mocks):
        mod = _reload_with_mocks["mod"]
        canvas = mod.ElaFigureCanvas()
        assert canvas is not None
        canvas.deleteLater()

    def test_set_style_runs_without_error(self, _reload_with_mocks):
        mod = _reload_with_mocks["mod"]
        canvas = mod.ElaFigureCanvas()
        canvas.setStyle({"font.size": 12})
        canvas.deleteLater()

    def test_apply_theme_light(self, _reload_with_mocks):
        mod = _reload_with_mocks["mod"]
        from PyQt5ElaWidgetTools import ElaThemeType
        canvas = mod.ElaFigureCanvas()
        canvas._theme_mode = ElaThemeType.ThemeMode.Light
        canvas._apply_theme()
        canvas.deleteLater()

    def test_delete_later_cleans_up(self, _reload_with_mocks):
        mod = _reload_with_mocks["mod"]
        canvas = mod.ElaFigureCanvas()
        canvas.deleteLater()
