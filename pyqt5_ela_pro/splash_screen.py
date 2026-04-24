"""
启动画面组件。

基于 ``QSplashScreen`` 封装，支持渐变背景、标题、副标题和加载进度显示。
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient
from PyQt5.QtWidgets import QSplashScreen, QApplication


class ElaSplashScreen(QSplashScreen):
    """启动画面组件。

    继承自 QSplashScreen，支持渐变背景、标题、副标题和加载进度显示。

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
        pixmap = self._createPixmap()
        super().__init__(
            pixmap,
            Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint,
        )

    def show(self) -> None:
        """显示启动画面。"""
        super().show()
        QApplication.instance().processEvents()

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
        titleFont = QFont()
        titleFont.setPointSize(28)
        titleFont.setBold(True)
        painter.setFont(titleFont)
        painter.drawText(
            pixmap.rect().adjusted(0, 80, 0, -120),
            Qt.AlignmentFlag.AlignCenter,
            self._title,
        )

        subtitleFont = QFont()
        subtitleFont.setPointSize(14)
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
        super().showMessage(
            message,
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
            QColor(255, 255, 255),
        )
        QApplication.instance().processEvents()

    def finish(self, widget) -> None:
        """关闭启动画面。

        :param widget: 目标窗口，关闭后显示该窗口。
        """
        super().finish(widget)
        self.close()
