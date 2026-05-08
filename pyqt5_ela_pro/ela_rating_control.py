"""
星级评分组件，风格参考 ElaWidgetTools 的 ElaRatingControl。

支持鼠标悬停预览、点击评分、只读模式。

用法::

    rating = ElaRatingControl(parent=self)
    rating.ratingChanged.connect(lambda v: print(f"评分: {v}"))
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal, QEvent
from PyQt5.QtGui import QPainter, QPaintEvent, QMouseEvent, QFont
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaIconType

from ._internal import disconnect_theme_signal


class ElaRatingControl(QWidget):
    """星级评分组件。

    :param parent: 父控件
    """

    ratingChanged = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._max_rating = 5
        self._rating = 0
        self._star_size = 24
        self._spacing = 4
        self._is_read_only = False
        self._hovered_star = -1

        self.setObjectName("ElaRatingControl")
        self.setMouseTracking(True)
        self.setFixedHeight(self._star_size + 4)

        self._theme_mode = eTheme.getThemeMode()
        eTheme.themeModeChanged.connect(self._onThemeChanged)

    def setMaxRating(self, n: int) -> None:
        self._max_rating = n
        self.updateGeometry()
        self.update()

    def getMaxRating(self) -> int:
        return self._max_rating

    def setRating(self, n: int) -> None:
        if self._rating == n:
            return
        self._rating = n
        self.ratingChanged.emit(n)
        self.update()

    def getRating(self) -> int:
        return self._rating

    def setStarSize(self, size: int) -> None:
        self._star_size = size
        self.setFixedHeight(size + 4)
        self.updateGeometry()
        self.update()

    def getStarSize(self) -> int:
        return self._star_size

    def setSpacing(self, spacing: int) -> None:
        self._spacing = spacing
        self.updateGeometry()
        self.update()

    def getSpacing(self) -> int:
        return self._spacing

    def setReadOnly(self, ro: bool) -> None:
        self._is_read_only = ro

    def isReadOnly(self) -> bool:
        return self._is_read_only

    def _onThemeChanged(self, mode) -> None:
        self._theme_mode = mode
        self.update()

    def deleteLater(self) -> None:
        disconnect_theme_signal(self._onThemeChanged)
        super().deleteLater()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._is_read_only:
            super().mouseMoveEvent(event)
            return
        unit = self._star_size + self._spacing
        h = -1
        if unit > 0 and event.pos().x() >= 0:
            h = event.pos().x() // unit
            if h >= self._max_rating:
                h = -1
        if self._hovered_star != h:
            self._hovered_star = h
            self.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self._is_read_only and self._hovered_star >= 0:
            self.setRating(self._hovered_star + 1)
        super().mousePressEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._hovered_star = -1
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        icon_font = QFont("ElaAwesome")
        icon_font.setPixelSize(self._star_size - 4)
        painter.setFont(icon_font)

        effective = self._rating
        if not self._is_read_only and self._hovered_star >= 0:
            effective = self._hovered_star + 1

        for i in range(self._max_rating):
            x = i * (self._star_size + self._spacing)
            r = QRect(x, 2, self._star_size, self._star_size)
            painter.setPen(eTheme.getThemeColor(self._theme_mode, ElaThemeType.ThemeColor.PrimaryNormal)
                           if i < effective
                           else eTheme.getThemeColor(self._theme_mode, ElaThemeType.ThemeColor.BasicBorderDeep))
            painter.drawText(r, Qt.AlignmentFlag.AlignCenter, chr(int(ElaIconType.IconName.Star)))

    def sizeHint(self) -> QSize:
        w = self._max_rating * (self._star_size + self._spacing) - self._spacing
        return QSize(w, self._star_size + 4)
