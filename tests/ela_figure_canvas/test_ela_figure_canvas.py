from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch, ANY


class TestElaFigureCanvasNoMatplotlib:
    def test_placeholder_raises_import_error(self):
        from pyqt5_ela_pro.ela_figure_canvas import ElaFigureCanvas
        with pytest.raises(ImportError):
            ElaFigureCanvas()

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
