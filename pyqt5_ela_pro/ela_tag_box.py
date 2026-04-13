"""
具名组合框组件。

带有标题标签的组合框组件，只读模式。
继承自 ElaComboBox，使用 ElaWidgetTools 主题色。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import (
    Qt,
    QRect,
    QRectF,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
)
from PyQt5.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QFontMetrics,
    QTextOption,
    QPen,
    QFont,
    QTransform,
)
from PyQt5.QtWidgets import QWidget, QStyleOptionComboBox, QStylePainter

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaComboBox, ElaIcon, ElaIconType


class ElaTagBox(ElaComboBox):
    """具名组合框。

    带有标题标签的组合框，只读模式。
    继承自 ElaComboBox，使用原生弹出菜单。

    :param parent: 父控件
    :param title: 标题文字

    Example::

        combo = ElaTagBox(parent, title="语言")
        combo.addItems(["Python", "C++", "JavaScript"])
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "",
    ) -> None:
        super().__init__(parent)

        self._title_text = title
        self._title_font_size = 13
        self._expand_mark_width: float = 0.0
        self._expand_icon_rotate: float = 0.0

        self._mark_animation = QPropertyAnimation(self, b"expandMarkWidth")
        self._mark_animation.setDuration(300)
        self._mark_animation.setEasingCurve(QEasingCurve.InOutSine)

        self._rotate_animation = QPropertyAnimation(self, b"expandIconRotate")
        self._rotate_animation.setDuration(300)
        self._rotate_animation.setEasingCurve(QEasingCurve.InOutSine)

        self.setFixedHeight(38)
        self.currentIndexChanged.connect(self._onCurrentIndexChanged)

    @pyqtProperty(float)
    def expandMarkWidth(self) -> float:
        return self._expand_mark_width

    @expandMarkWidth.setter
    def expandMarkWidth(self, width: float) -> None:
        if self._expand_mark_width != width:
            self._expand_mark_width = width
            self.update()

    @pyqtProperty(float)
    def expandIconRotate(self) -> float:
        return self._expand_icon_rotate

    @expandIconRotate.setter
    def expandIconRotate(self, rotate: float) -> None:
        if self._expand_icon_rotate != rotate:
            self._expand_icon_rotate = rotate
            self.update()

    def showPopup(self) -> None:
        target_mark_width = self.width() / 2 - 9
        self._mark_animation.setStartValue(self._expand_mark_width)
        self._mark_animation.setEndValue(target_mark_width)
        self._mark_animation.start()

        self._rotate_animation.setStartValue(self._expand_icon_rotate)
        self._rotate_animation.setEndValue(-180.0)
        self._rotate_animation.start()

        super().showPopup()

    def hidePopup(self) -> None:
        self._mark_animation.setStartValue(self._expand_mark_width)
        self._mark_animation.setEndValue(0.0)
        self._mark_animation.start()

        self._rotate_animation.setStartValue(self._expand_icon_rotate)
        self._rotate_animation.setEndValue(0.0)
        self._rotate_animation.start()

        super().hidePopup()

    def setTitle(self, title: str) -> None:
        """设置标题文字。

        :param title: 标题文字
        """
        self._title_text = title
        self.update()

    def title(self) -> str:
        """返回标题文字。

        :return: 标题文字
        """
        return self._title_text

    def _onCurrentIndexChanged(self, index: int) -> None:
        self.update()

    def _getTitleColor(self) -> QColor:
        if not self.isEnabled():
            return eTheme.getThemeColor(
                eTheme.getThemeMode(), ElaThemeType.ThemeColor.BasicTextDisable
            )
        return eTheme.getThemeColor(
            eTheme.getThemeMode(), ElaThemeType.ThemeColor.BasicText
        )

    def _getBackgroundColor(self) -> QColor:
        current_theme = eTheme.getThemeMode()
        if not self.isEnabled():
            return eTheme.getThemeColor(
                current_theme, ElaThemeType.ThemeColor.BasicDisable
            )
        if self.hasFocus():
            return eTheme.getThemeColor(
                current_theme, ElaThemeType.ThemeColor.DialogBase
            )
        if self.underMouse():
            return eTheme.getThemeColor(
                current_theme, ElaThemeType.ThemeColor.BasicHover
            )
        return eTheme.getThemeColor(current_theme, ElaThemeType.ThemeColor.BasicBase)

    def _getBorderColor(self) -> QColor:
        if self.hasFocus():
            return eTheme.getThemeColor(
                eTheme.getThemeMode(), ElaThemeType.ThemeColor.PrimaryNormal
            )
        current_theme = eTheme.getThemeMode()
        return eTheme.getThemeColor(
            current_theme, ElaThemeType.ThemeColor.BasicBaseLine
        )

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        shadow_border = 3
        content_rect = QRect(
            shadow_border,
            shadow_border,
            self.width() - 2 * shadow_border,
            self.height() - 2 * shadow_border,
        )

        bg_color = self._getBackgroundColor()
        text_color = self._getTitleColor()
        border_color = self._getBorderColor()

        path = QPainterPath()
        path.addRoundedRect(QRectF(content_rect), 3, 3)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg_color)
        painter.drawPath(path)

        pen = QPen(border_color)
        pen.setWidth(2)
        painter.setPen(pen)
        y = content_rect.bottom()
        painter.drawLine(content_rect.left(), y, content_rect.right(), y)

        if self._expand_mark_width > 0:
            mark_color = eTheme.getThemeColor(
                eTheme.getThemeMode(), ElaThemeType.ThemeColor.PrimaryNormal
            )
            painter.setPen(Qt.NoPen)
            painter.setBrush(mark_color)
            mark_rect = QRectF(
                self.width() / 2 - self._expand_mark_width,
                self.height() - 3,
                self._expand_mark_width * 2,
                3,
            )
            mark_path = QPainterPath()
            mark_path.addRoundedRect(mark_rect, 1.5, 1.5)
            painter.drawPath(mark_path)

        metrics = QFontMetrics(self.font())
        title_width = metrics.horizontalAdvance(self._title_text) + 20

        title_rect = QRect(
            content_rect.left(),
            content_rect.top(),
            title_width,
            content_rect.height(),
        )
        title_option = QTextOption()
        title_option.setWrapMode(QTextOption.NoWrap)
        title_option.setAlignment(
            Qt.Alignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        )
        title_font = QFont(self.font())
        title_font.setPixelSize(self._title_font_size)
        painter.setFont(title_font)
        painter.setPen(text_color)
        painter.drawText(
            QRectF(title_rect.adjusted(10, 0, -10, 0)),
            self._title_text,
            title_option,
        )

        current_text = self.currentText()
        if current_text:
            text_left = title_rect.right()
            text_width = content_rect.right() - 30 - text_left
            if text_width > 0:
                text_rect = QRect(
                    text_left,
                    content_rect.top(),
                    text_width,
                    content_rect.height(),
                )
                text_option = QTextOption()
                text_option.setWrapMode(QTextOption.NoWrap)
                text_option.setAlignment(
                    Qt.Alignment(
                        Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
                    )
                )
                painter.drawText(
                    QRectF(text_rect),
                    current_text,
                    text_option,
                )

        arrow_rect = QRect(
            content_rect.right() - 25,
            content_rect.top(),
            20,
            content_rect.height(),
        )
        icon = ElaIcon.getInstance().getElaIcon(
            ElaIconType.IconName.AngleDown, text_color
        )
        icon_pixmap = icon.pixmap(17, 17)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        transform = QTransform()
        transform.translate(
            arrow_rect.left() + arrow_rect.width() / 2,
            arrow_rect.top() + arrow_rect.height() / 2,
        )
        transform.rotate(self._expand_icon_rotate)
        transform.translate(-icon_pixmap.width() / 2, -icon_pixmap.height() / 2)
        painter.setTransform(transform)
        painter.drawPixmap(0, 0, icon_pixmap)
        painter.restore()
