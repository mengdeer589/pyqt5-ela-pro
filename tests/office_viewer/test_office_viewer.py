from __future__ import annotations

from unittest.mock import patch


from pyqt5_ela_pro.office_viewer import (
    ElaWordViewer,
    ElaExcelViewer,
    ElaPowerPointViewer,
    _BACKEND_PROG_IDS,
)


class TestOfficeViewerProgIds:
    def test_backend_progids_has_office_and_wps(self):
        assert "office" in _BACKEND_PROG_IDS
        assert "wps" in _BACKEND_PROG_IDS

    def test_office_has_word_excel_ppt(self):
        office = _BACKEND_PROG_IDS["office"]
        assert "word" in office
        assert "excel" in office
        assert "ppt" in office

    def test_wps_has_word_excel_ppt(self):
        wps = _BACKEND_PROG_IDS["wps"]
        assert "word" in wps
        assert "excel" in wps
        assert "ppt" in wps


class TestElaOfficeViewerMixin:
    def test_init_defaults(self):
        with patch("pyqt5_ela_pro.office_viewer.QAxWidget"):
            viewer = ElaWordViewer()
            assert viewer._backend == "office"
            assert viewer._loaded is False
            viewer.deleteLater()

    def test_is_loaded_property(self):
        with patch("pyqt5_ela_pro.office_viewer.QAxWidget"):
            viewer = ElaWordViewer()
            assert viewer.is_loaded is False
            viewer._loaded = True
            assert viewer.is_loaded is True
            viewer.deleteLater()

    def test_close_when_not_loaded(self):
        with patch("pyqt5_ela_pro.office_viewer.QAxWidget"):
            viewer = ElaWordViewer()
            viewer.close()
            assert viewer._loaded is False
            viewer.deleteLater()

    def test_close_when_loaded(self):
        with patch("pyqt5_ela_pro.office_viewer.QAxWidget"):
            viewer = ElaWordViewer()
            viewer._loaded = True
            viewer.close()
            assert viewer._loaded is False
            viewer.deleteLater()


class TestElaOfficeViewerSubclasses:
    def test_word_viewer_app_name(self):
        with patch("pyqt5_ela_pro.office_viewer.QAxWidget"):
            viewer = ElaWordViewer()
            assert viewer._appName == "word"
            viewer.deleteLater()

    def test_excel_viewer_app_name(self):
        with patch("pyqt5_ela_pro.office_viewer.QAxWidget"):
            viewer = ElaExcelViewer()
            assert viewer._appName == "excel"
            viewer.deleteLater()

    def test_powerpoint_viewer_app_name(self):
        with patch("pyqt5_ela_pro.office_viewer.QAxWidget"):
            viewer = ElaPowerPointViewer()
            assert viewer._appName == "ppt"
            viewer.deleteLater()

    def test_word_viewer_default_backend(self):
        with patch("pyqt5_ela_pro.office_viewer.QAxWidget"):
            viewer = ElaWordViewer()
            assert viewer._backend == "office"
            viewer.deleteLater()

    def test_word_viewer_wps_backend(self):
        with patch("pyqt5_ela_pro.office_viewer.QAxWidget"):
            viewer = ElaWordViewer(backend="wps")
            assert viewer._backend == "wps"
            viewer.deleteLater()
