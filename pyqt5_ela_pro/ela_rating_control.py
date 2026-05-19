"""
星级评分组件，风格参考 ElaWidgetTools 的 ElaRatingControl。

支持鼠标悬停预览、点击评分、只读模式，支持半星评分。

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

from .widget_base import ElaThemeWidget


class ElaRatingControl(ElaThemeWidget):
    """星级评分组件，支持半星。

    :param parent: 父控件
    """

    ratingChanged = pyqtSignal(float)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._max_rating = 5
        self._rating: float = 0.0
        self._star_size = 24
        self._spacing = 4
        self._is_read_only = False
        self._hovered_star: float = -1.0

        self.setObjectName("ElaRatingControl")
        self.setMouseTracking(True)
        self.setFixedHeight(self._star_size + 4)
        self._icon_font = QFont("ElaAwesome")

    def setMaxRating(self, n: int) -> None:
        """设置最大评分值。

        :param n: 最大评分
        """
        self._max_rating = n
        self.updateGeometry()
        self.update()

    def maxRating(self) -> int:
        """获取最大评分值。

        :returns: 最大评分
        """
        return self._max_rating

    def setRating(self, n: float) -> None:
        """设置当前评分（自动四舍五入到 0.5 的倍数）。

        仅当值变化时发射 ``ratingChanged`` 信号。

        :param n: 评分值
        """
        n = max(0.0, min(float(self._max_rating), n))
        n = round(n * 2) / 2
        if self._rating == n:
            return
        self._rating = n
        self.ratingChanged.emit(n)
        self.update()

    def rating(self) -> float:
        """获取当前评分。

        :returns: 评分值
        """
        return self._rating

    def setStarSize(self, size: int) -> None:
        """设置星号尺寸。

        :param size: 星号尺寸（像素）
        """
        self._star_size = size
        self.setFixedHeight(size + 4)
        self.updateGeometry()
        self.update()

    def starSize(self) -> int:
        """获取星号尺寸。

        :returns: 星号尺寸（像素）
        """
        return self._star_size

    def setSpacing(self, spacing: int) -> None:
        """设置星号间距。

        :param spacing: 间距（像素）
        """
        self._spacing = spacing
        self.updateGeometry()
        self.update()

    def spacing(self) -> int:
        """获取星号间距。

        :returns: 间距（像素）
        """
        return self._spacing

    def setReadOnly(self, ro: bool) -> None:
        """设置是否只读（只读模式下不可交互）。

        :param ro: 是否只读
        """
        self._is_read_only = ro

    def isReadOnly(self) -> bool:
        """当前是否只读。

        :returns: 只读状态
        """
        return self._is_read_only

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._is_read_only:
            super().mouseMoveEvent(event)
            return
        unit = self._star_size + self._spacing
        h = -1.0
        if unit > 0 and event.pos().x() >= 0:
            star_idx = int(event.pos().x() // unit)
            if star_idx < self._max_rating:
                rel_x = event.pos().x() - star_idx * unit
                h = star_idx + (0.5 if rel_x < unit / 2 else 1.0)
        if self._hovered_star != h:
            self._hovered_star = h
            self.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self._is_read_only and self._hovered_star > 0:
            self.setRating(self._hovered_star)
        super().mousePressEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._hovered_star = -1.0
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._icon_font.setPixelSize(self._star_size - 4)
        painter.setFont(self._icon_font)

        effective = self._rating
        if not self._is_read_only and self._hovered_star > 0:
            effective = self._hovered_star

        star_char = chr(int(ElaIconType.IconName.Star))
        primary = eTheme.getThemeColor(
            self._theme_mode, ElaThemeType.ThemeColor.PrimaryNormal
        )
        empty = eTheme.getThemeColor(
            self._theme_mode, ElaThemeType.ThemeColor.BasicBorderDeep
        )

        for i in range(self._max_rating):
            x = i * (self._star_size + self._spacing)
            r = QRect(x, 2, self._star_size, self._star_size)

            if i < int(effective):
                painter.setPen(primary)
                painter.drawText(r, Qt.AlignmentFlag.AlignCenter, star_char)
            elif i == int(effective) and effective - i >= 0.5:
                painter.save()
                painter.setClipRect(QRect(x, 2, self._star_size // 2, self._star_size))
                painter.setPen(primary)
                painter.drawText(r, Qt.AlignmentFlag.AlignCenter, star_char)
                painter.restore()
                painter.save()
                painter.setClipRect(
                    QRect(
                        x + self._star_size // 2,
                        2,
                        self._star_size // 2,
                        self._star_size,
                    )
                )
                painter.setPen(empty)
                painter.drawText(r, Qt.AlignmentFlag.AlignCenter, star_char)
                painter.restore()
            else:
                painter.setPen(empty)
                painter.drawText(r, Qt.AlignmentFlag.AlignCenter, star_char)

    def sizeHint(self) -> QSize:
        w = self._max_rating * (self._star_size + self._spacing) - self._spacing
        return QSize(w, self._star_size + 4)
