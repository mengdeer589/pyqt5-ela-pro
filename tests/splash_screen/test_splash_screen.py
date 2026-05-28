"""Tests for splash_screen module: ElaSplashScreen."""

from __future__ import annotations

from PyQt5.QtGui import QPixmap


class TestElaSplashScreen:
    def test_import_and_instantiate(self, qapp):
        from pyqt5_ela_pro.splash_screen import ElaSplashScreen
        splash = ElaSplashScreen()
        assert splash is not None
        splash.deleteLater()

    def test_default_values(self, qapp):
        from pyqt5_ela_pro.splash_screen import ElaSplashScreen
        splash = ElaSplashScreen()
        assert splash.borderRadius() == 12
        assert splash.minimum() == 0
        assert splash.maximum() == 100
        assert splash.value() == 0
        splash.deleteLater()

    def test_set_title(self, qapp):
        from pyqt5_ela_pro.splash_screen import ElaSplashScreen
        splash = ElaSplashScreen()
        splash.setTitle("Test App")
        splash.deleteLater()

    def test_set_subtitle(self, qapp):
        from pyqt5_ela_pro.splash_screen import ElaSplashScreen
        splash = ElaSplashScreen()
        splash.setSubTitle("Version 1.0")
        splash.deleteLater()

    def test_set_status_text(self, qapp):
        from pyqt5_ela_pro.splash_screen import ElaSplashScreen
        splash = ElaSplashScreen()
        splash.setStatusText("正在加载...")
        splash.deleteLater()

    def test_set_value(self, qapp):
        from pyqt5_ela_pro.splash_screen import ElaSplashScreen
        splash = ElaSplashScreen()
        splash.setValue(50)
        assert splash.value() == 50
        splash.deleteLater()

    def test_set_minimum(self, qapp):
        from pyqt5_ela_pro.splash_screen import ElaSplashScreen
        splash = ElaSplashScreen()
        splash.setMinimum(0)
        assert splash.minimum() == 0
        splash.deleteLater()

    def test_set_maximum(self, qapp):
        from pyqt5_ela_pro.splash_screen import ElaSplashScreen
        splash = ElaSplashScreen()
        splash.setMaximum(200)
        assert splash.maximum() == 200
        splash.deleteLater()

    def test_set_border_radius(self, qapp):
        from pyqt5_ela_pro.splash_screen import ElaSplashScreen
        splash = ElaSplashScreen()
        splash.setBorderRadius(24)
        assert splash.borderRadius() == 24
        splash.deleteLater()

    def test_set_logo(self, qapp):
        from pyqt5_ela_pro.splash_screen import ElaSplashScreen
        splash = ElaSplashScreen()
        splash.setLogo(QPixmap())
        splash.deleteLater()

    def test_toggle_progress_bar(self, qapp):
        from pyqt5_ela_pro.splash_screen import ElaSplashScreen
        splash = ElaSplashScreen()
        splash.setShowProgressBar(False)
        assert splash.isShowProgressBar() is False
        splash.setShowProgressBar(True)
        assert splash.isShowProgressBar() is True
        splash.deleteLater()

    def test_toggle_progress_ring(self, qapp):
        from pyqt5_ela_pro.splash_screen import ElaSplashScreen
        splash = ElaSplashScreen()
        splash.setShowProgressRing(False)
        assert splash.isShowProgressRing() is False
        splash.setShowProgressRing(True)
        assert splash.isShowProgressRing() is True
        splash.deleteLater()

    def test_toggle_closable(self, qapp):
        from pyqt5_ela_pro.splash_screen import ElaSplashScreen
        splash = ElaSplashScreen()
        splash.setClosable(True)
        assert splash.isClosable() is True
        splash.deleteLater()

    def test_delete_later_cleans_up(self, qapp):
        from pyqt5_ela_pro.splash_screen import ElaSplashScreen
        splash = ElaSplashScreen()
        splash.deleteLater()
