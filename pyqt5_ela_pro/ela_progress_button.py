"""
进度显示按钮组件。

继承自 ElaPushButton，支持显示进度条，进度由外部控制。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import pyqtSignal, Qt, QRect, QRectF
from PyQt5.QtGui import QColor, QPainter, QLinearGradient, QPainterPath, QPaintEvent
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaPushButton


class ElaProgressButton(ElaPushButton):
    """进度显示按钮。

    继承自 ElaPushButton，支持显示进度条。
    进度由外部通过 setProgress() 控制，不支持长按。

    :param text: 按钮文本
    :param getProgressColor: 进度条颜色，为 None 时使用主题色
    :param parent: 父控件

    Example::

        button = ElaProgressButton(text="下载", parent=parent)
        button.setProgress(50)  # 显示50%进度
        button.setProgress(100)  # 完成
    """

    progressChanged = pyqtSignal(int)

    def __init__(
        self,
        text: str = "",
        getProgressColor: Optional[QColor] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setText(text)

        self._progress = 0.0
        self._progress_color = QColor()
        self._custom_progress_color = getProgressColor is not None

        self._theme_connection = self._updateProgressColor
        self._updateProgressColor(eTheme.getThemeMode())
        eTheme.themeModeChanged.connect(self._theme_connection)

    def _updateProgressColor(self, mode: ElaThemeType.ThemeMode) -> None:
        if not self._custom_progress_color:
            self._progress_color = eTheme.getThemeColor(
                mode, ElaThemeType.ThemeColor.PrimaryNormal
            )
        self.update()

    def setProgressColor(self, color: QColor) -> None:
        """设置进度条颜色。

        :param color: 进度条颜色
        """
        self._custom_progress_color = True
        self._progress_color = color
        self.update()

    def getProgressColor(self) -> QColor:
        """返回进度条填充颜色。

        :return: 进度条颜色
        """
        return self._progress_color

    def setProgress(self, percent: int) -> None:
        """设置进度百分比 (0-100)。

        :param percent: 进度百分比，范围 0-100
        """
        percent = max(0, min(100, percent))
        self._progress = percent / 100.0
        self.progressChanged.emit(percent)
        self.update()

    def getProgress(self) -> int:
        """获取当前进度 (0-100)。

        :return: 进度百分比
        """
        return int(self._progress * 100)

    def resetProgress(self) -> None:
        """重置进度为0。"""
        self.setProgress(0)

    def deleteLater(self) -> None:
        if self._theme_connection is not None:
            try:
                eTheme.themeModeChanged.disconnect(self._theme_connection)
            except (TypeError, RuntimeError):
                pass
            self._theme_connection = None
        super().deleteLater()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        shadow_border = 3
        rect = QRect(
            shadow_border,
            shadow_border,
            self.width() - 2 * shadow_border,
            self.height() - 2 * shadow_border,
        )

        mode = eTheme.getThemeMode()

        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 3, 3)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBase))
        painter.drawPath(path)

        painter.save()
        painter.setClipPath(path)

        if self._progress < 1.0:
            p = self._progress
            gradient = QLinearGradient(rect.topLeft(), rect.topRight())
            gradient.setColorAt(0, self._progress_color)
            gradient.setColorAt(p, self._progress_color)
            gradient.setColorAt(min(p + 0.001, 1.0), QColor(0, 0, 0, 0))
            gradient.setColorAt(1, QColor(0, 0, 0, 0))
            painter.fillRect(rect, gradient)
        else:
            painter.fillRect(rect, self._progress_color)

        painter.restore()

        if self.isEnabled():
            text_color = eTheme.getThemeColor(
                mode, ElaThemeType.ThemeColor.BasicText
            )
        else:
            text_color = eTheme.getThemeColor(
                mode, ElaThemeType.ThemeColor.BasicTextDisable
            )
        painter.setPen(text_color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
