from __future__ import annotations

import pytest


class TestElaFigureCanvas:
    def test_placeholder_or_real(self):
        from pyqt5_ela_pro.ela_figure_canvas import ElaFigureCanvas, _FigureCanvas
        if _FigureCanvas is None:
            with pytest.raises(ImportError):
                ElaFigureCanvas()
        else:
            from PyQt5.QtWidgets import QApplication
            QApplication.instance() or QApplication([])
            canvas = ElaFigureCanvas()
            assert canvas is not None
            canvas.deleteLater()

    def test_light_rcparams_defined(self):
        from pyqt5_ela_pro.ela_figure_canvas import _LIGHT_RC_PARAMS
        assert "figure.facecolor" in _LIGHT_RC_PARAMS
        assert "axes.facecolor" in _LIGHT_RC_PARAMS
        assert len(_LIGHT_RC_PARAMS) == 8

    def test_dark_rcparams_defined(self):
        from pyqt5_ela_pro.ela_figure_canvas import _DARK_RC_PARAMS
        assert "figure.facecolor" in _DARK_RC_PARAMS
        assert len(_DARK_RC_PARAMS) == 8

    def test_cjk_fonts_defined(self):
        from pyqt5_ela_pro.ela_figure_canvas import _CJK_FONTS
        assert len(_CJK_FONTS) > 0
        assert "Microsoft YaHei" in _CJK_FONTS
