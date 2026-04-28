"""
长按按钮组件。

按住按钮一段时间后才能触发点击事件的按钮组件，
带有进度条动画显示。继承自 ElaPushButton。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import pyqtSignal, QTimer, Qt, QRect, QRectF, QPoint, QSize
from PyQt5.QtGui import QColor, QPainter, QLinearGradient, QPainterPath, QFontMetrics, QPaintEvent, QMouseEvent, QPen
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaPushButton, ElaIcon, ElaIconType


class ElaLongPressButton(ElaPushButton):
    """长按按钮。

    按住按钮一段时间（默认 500ms）后才能触发点击事件的按钮。
    按压过程中会显示进度条填充动画。

    继承自 ElaPushButton，支持主题适配和图标。

    :param duration: 触发长按所需的时长（毫秒），默认 500ms
    :param text: 按钮文本
    :param icon: 图标名称
    :param iconSize: 图标大小，默认 16
    :param parent: 父控件

    Example::

        button = ElaLongPressButton(duration=800, text="长按保存", icon=ElaIconType.IconName.FloppyDisk, parent=parent)
        button.longPressed.connect(lambda: print("长按完成！"))
    """

    longPressed = pyqtSignal()
    progressChanged = pyqtSignal(float)

    def __init__(
        self,
        duration: int = 500,
        text: Optional[str] = None,
        icon: Optional[ElaIconType.IconName] = None,
        iconSize: int = 16,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setText(text if text is not None else "长按触发")

        self._duration = duration
        self._progress = 0.0
        self._triggered = False
        self._progress_color = QColor()
        self._icon_name = None
        self._icon_size = iconSize

        if icon is not None:
            self.setElaIcon(icon, iconSize)

        self._mouse_pressed_timer = QTimer(self)
        self._mouse_pressed_timer.setInterval(16)
        self._mouse_pressed_timer.timeout.connect(self._onMousePressed)

        self._go_backwards_timer = QTimer(self)
        self._go_backwards_timer.setSingleShot(True)
        self._go_backwards_timer.setInterval(500)
        self._go_backwards_timer.timeout.connect(self._resetProgress)

        self._theme_connection = self._updateProgressColor
        self._updateProgressColor(eTheme.getThemeMode())
        eTheme.themeModeChanged.connect(self._theme_connection)

    def setDuration(self, ms: int) -> None:
        """设置长按触发所需的时长（毫秒）。

        :param ms: 时长，必须大于 0
        """
        if ms > 0:
            self._duration = ms

    def duration(self) -> int:
        """返回长按触发所需的时长（毫秒）。

        :return: 时长（毫秒）
        """
        return self._duration

    def setProgressColor(self, color: QColor) -> None:
        """设置进度条填充颜色。

        :param color: 进度条颜色
        """
        self._progress_color = color
        self.update()

    def setElaIcon(self, iconName, iconSize: int = 16) -> None:
        """设置图标。

        :param iconName: 图标名称
        :param iconSize: 图标大小，默认 16
        """
        self._icon_name = iconName
        self._icon_size = iconSize
        self.setIcon(ElaIcon.getInstance().getElaIcon(iconName, QColor(255, 255, 255)))
        self.setIconSize(QSize(iconSize, iconSize))
        self.update()

    def _getCurrentBgColor(self) -> QColor:
        mode = eTheme.getThemeMode()
        if not self.isEnabled():
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicDisable)
        if self.isDown():
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicPress)
        if self.underMouse():
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicHover)
        return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBase)

    def _updateProgressColor(self, mode: ElaThemeType.ThemeMode) -> None:
        self._progress_color = eTheme.getThemeColor(
            mode, ElaThemeType.ThemeColor.PrimaryNormal
        )
        self.update()

    def deleteLater(self) -> None:
        if self._theme_connection is not None:
            try:
                eTheme.themeModeChanged.disconnect(self._theme_connection)
            except (TypeError, RuntimeError):
                pass
            self._theme_connection = None
        self._mouse_pressed_timer.stop()
        self._go_backwards_timer.stop()
        super().deleteLater()

    def getProgressColor(self) -> QColor:
        """返回进度条填充颜色。

        :return: 进度条颜色
        """
        return self._progress_color

    def progress(self) -> float:
        """返回当前进度值。

        :return: 进度值，范围 0.0 ~ 1.0
        """
        return self._progress

    def _stepLength(self) -> float:
        steps = self._duration / 16.0
        return 1.0 / steps if steps >= 1 else 1.0

    def _onMousePressed(self) -> None:
        new_progress = min(1.0, self._progress + self._stepLength())

        if new_progress >= 1.0:
            self._triggered = True
            self._mouse_pressed_timer.stop()
            self._go_backwards_timer.stop()
            self._progress = 0.0
            self.progressChanged.emit(1.0)
            self.longPressed.emit()
            self.update()
        else:
            self._progress = new_progress
            self.progressChanged.emit(self._progress)
            self.update()

    def _goBackwards(self, delay: int = 0) -> None:
        self._go_backwards_timer.setInterval(delay)
        self._go_backwards_timer.start()

    def _resetProgress(self) -> None:
        self._progress = 0.0
        self._triggered = False
        self.progressChanged.emit(0.0)
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self.isEnabled():
            return
        super().mousePressEvent(event)
        if not self._mouse_pressed_timer.isActive():
            self._mouse_pressed_timer.start()
            self._go_backwards_timer.stop()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        self._mouse_pressed_timer.stop()
        self._go_backwards_timer.start()

    def paintEvent(self, event: QPaintEvent) -> None:
        if self._progress <= 0:
            super().paintEvent(event)
            return

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
        bg_color = self._getCurrentBgColor()

        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 3, 3)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg_color)
        painter.drawPath(path)

        border_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBaseLine)
        border_pen = QPen(border_color, 1)
        painter.setPen(border_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        painter.save()
        painter.setClipPath(path)

        p = min(self._progress, 1.0)
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        gradient.setColorAt(0, self._progress_color)
        gradient.setColorAt(p, self._progress_color)
        gradient.setColorAt(min(p + 0.05, 1.0), QColor(0, 0, 0, 0))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(rect, gradient)

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
