"""
启动画面组件。

基于 ``QSplashScreen`` 封装，支持渐变背景、标题、副标题和加载进度显示。
"""

from typing import Optional

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
        self._progress = 0.0
        self._base_pixmap: Optional[QPixmap] = None
        self._bar_margin = 50
        self._bar_height = 8
        self._bar_y = self._height - 100
        self._bar_width = self._width - self._bar_margin * 2
        self._build_base_pixmap()
        super().__init__(
            self._build_progress_pixmap(),
            Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint,
        )

    def show(self) -> None:
        """显示启动画面。"""
        super().show()
        QApplication.instance().processEvents()

    def _build_base_pixmap(self) -> None:
        """创建启动画面背景层（渐变背景 + 文字），缓存以便进度更新时复用。"""
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
        painter.end()
        self._base_pixmap = pixmap

    def _build_progress_pixmap(self) -> QPixmap:
        """基于缓存的背景层叠加进度条，返回最终 pixmap。"""
        pixmap = self._base_pixmap.copy() if self._base_pixmap else QPixmap(self._width, self._height)
        painter = QPainter(pixmap)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 50))
        painter.drawRoundedRect(
            self._bar_margin, self._bar_y, self._bar_width, self._bar_height, 4, 4
        )

        fillWidth = int(self._bar_width * self._progress)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRoundedRect(
            self._bar_margin, self._bar_y, fillWidth, self._bar_height, 4, 4
        )
        painter.end()
        return pixmap

    def setProgress(self, percent: float) -> None:
        """设置进度条百分比。

        :param percent: 进度百分比，范围 0.0 ~ 1.0。
        :type percent: float
        """
        self._progress = max(0.0, min(1.0, percent))
        pixmap = self._build_progress_pixmap()
        self.setPixmap(pixmap)
        self.repaint()
        QApplication.instance().processEvents()

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
