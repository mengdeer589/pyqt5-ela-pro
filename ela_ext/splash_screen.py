"""
启动画面组件。

基于 ``QSplashScreen`` 封装，支持渐变背景、标题、副标题和加载进度显示。
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient
from PyQt5.QtWidgets import QSplashScreen


class ElaSplashScreen:
    """启动画面组件。

    :param title: 标题文本。
    :type title: str
    :param subtitle: 副标题文本。
    :type subtitle: str
    :param width: 启动画面宽度，默认 500。
    :type width: int
    :param height: 启动画面高度，默认 350。
    :type height: int
    """

    def __init__(
        self,
        title: str = "ElaWidgetTools",
        subtitle: str = "Fluent UI For QWidget",
        width: int = 500,
        height: int = 350,
    ):
        self._title = title
        self._subtitle = subtitle
        self._width = width
        self._height = height
        self._splash = None
        self._app = None

    def create(self, app):
        """创建并显示启动画面。

        :param app: QApplication 实例。
        :type app: QApplication
        :return: QSplashScreen 实例。
        """
        self._app = app
        pixmap = self._createPixmap()
        self._splash = QSplashScreen(
            pixmap,
            Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint,  # type: ignore
        )
        self._splash.setFont(QFont("Microsoft YaHei", 11))
        self._splash.show()
        self._app.processEvents()
        return self._splash

    def _createPixmap(self) -> QPixmap:
        """创建启动画面背景图。

        :return: 绘制的 QPixmap。
        """
        pixmap = QPixmap(self._width, self._height)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, 0, self._height)
        gradient.setColorAt(0, QColor(0, 120, 215))
        gradient.setColorAt(1, QColor(0, 60, 120))
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self._width, self._height, 0, 0)

        painter.setPen(QColor(255, 255, 255))
        titleFont = QFont("Microsoft YaHei", 28, QFont.Bold)
        painter.setFont(titleFont)
        painter.drawText(
            pixmap.rect().adjusted(0, 80, 0, -120),
            Qt.AlignmentFlag.AlignCenter,
            self._title,
        )

        subtitleFont = QFont("Microsoft YaHei", 14)
        painter.setFont(subtitleFont)
        painter.drawText(
            pixmap.rect().adjusted(0, 150, 0, -80),
            Qt.AlignmentFlag.AlignCenter,
            self._subtitle,
        )

        barY = self._height - 100
        barHeight = 8
        barMargin = 50
        barWidth = self._width - barMargin * 2

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 50))
        painter.drawRoundedRect(barMargin, barY, barWidth, barHeight, 4, 4)

        painter.setBrush(QColor(255, 255, 255))
        painter.drawRoundedRect(barMargin, barY, barWidth // 3, barHeight, 4, 4)

        painter.end()
        return pixmap

    def showMessage(self, message: str) -> None:
        """显示加载消息。

        :param message: 要显示的消息文本。
        :type message: str
        """
        if self._splash:
            self._splash.showMessage(
                message,
                Qt.AlignBottom | Qt.AlignCenter,  # type: ignore[unresolved-attribute]
                QColor(255, 255, 255),
            )
            if self._app:
                self._app.processEvents()

    def finish(self, widget) -> None:
        """关闭启动画面。

        :param widget: 目标窗口，关闭后显示该窗口。
        """
        if self._splash:
            self._splash.finish(widget)
            self._splash.close()
            self._splash = None

    def close(self) -> None:
        """关闭启动画面。"""
        if self._splash:
            self._splash.close()
            self._splash = None
