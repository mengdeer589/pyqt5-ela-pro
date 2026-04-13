from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient
from PyQt5.QtWidgets import QSplashScreen


class SplashScreen:
    def __init__(
        self,
        title="ElaWidgetTools",
        subtitle="Fluent UI For QWidget",
        width=500,
        height=350,
    ):
        self._title = title
        self._subtitle = subtitle
        self._width = width
        self._height = height
        self._splash = None
        self._app = None

    def create(self, app):
        self._app = app
        pixmap = self._createPixmap()
        self._splash = QSplashScreen(
            pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint
        )
        self._splash.setFont(QFont("Microsoft YaHei", 11))
        self._splash.show()
        self._app.processEvents()
        return self._splash

    def _createPixmap(self):
        pixmap = QPixmap(self._width, self._height)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, 0, self._height)
        gradient.setColorAt(0, QColor(0, 120, 215))
        gradient.setColorAt(1, QColor(0, 60, 120))
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self._width, self._height, 0, 0)

        painter.setPen(QColor(255, 255, 255))
        titleFont = QFont("Microsoft YaHei", 28, QFont.Bold)
        painter.setFont(titleFont)
        painter.drawText(
            pixmap.rect().adjusted(0, 80, 0, -120), Qt.AlignCenter, self._title
        )

        subtitleFont = QFont("Microsoft YaHei", 14)
        painter.setFont(subtitleFont)
        painter.drawText(
            pixmap.rect().adjusted(0, 150, 0, -80), Qt.AlignCenter, self._subtitle
        )

        barY = self._height - 100
        barHeight = 8
        barMargin = 50
        barWidth = self._width - barMargin * 2

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 50))
        painter.drawRoundedRect(barMargin, barY, barWidth, barHeight, 4, 4)

        painter.setBrush(QColor(255, 255, 255))
        painter.drawRoundedRect(barMargin, barY, barWidth // 3, barHeight, 4, 4)

        painter.end()
        return pixmap

    def showMessage(self, message: str):
        if self._splash:
            self._splash.showMessage(
                message, Qt.AlignBottom | Qt.AlignCenter, QColor(255, 255, 255)
            )
            if self._app:
                self._app.processEvents()

    def finish(self, widget):
        if self._splash:
            self._splash.finish(widget)
            self._splash.close()
            self._splash = None

    def close(self):
        if self._splash:
            self._splash.close()
            self._splash = None
