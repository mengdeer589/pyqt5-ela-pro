"""
具名多选下拉框组件�?

带有标题标签的多选下拉框，标题在左侧，值在右侧�?
继承�?PyQt5ElaWidgetTools.ElaMultiSelectComboBox�?
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, QRect, QRectF, QTimer
from PyQt5.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QFontMetrics,
    QTextOption,
    QPen,
    QFont,
)
from PyQt5.QtWidgets import QWidget, QComboBox

from PyQt5ElaWidgetTools import (
    eTheme,
    ElaThemeType,
    ElaIcon,
    ElaIconType,
    ElaMultiSelectComboBox,
)


class ElaTagMultiBox(ElaMultiSelectComboBox):
    """具名多选下拉框�?

    带有标题标签的多选下拉框，标题在左侧，值在右侧�?
    继承�?PyQt5ElaWidgetTools.ElaMultiSelectComboBox�?

    :param parent: 父控�?
    :param title: 标题文字

    Example::

        combo = ElaCapsuleMultiComboBox(parent, title="语言")
        combo.addItem("Python")
        combo.addItem("C++")
        combo.addItem("JavaScript")
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "",
    ) -> None:
        super().__init__(parent)

        self._title_text = title
        self._title_font_size = 13
        self._popup_open = False

        self.setFixedHeight(38)
        self.setMaxVisibleItems(10)

        QTimer.singleShot(0, self._preInitPopup)

    def _preInitPopup(self) -> None:
        view = self.view()
        if view:
            view.setMinimumHeight(200)

    def showPopup(self) -> None:
        self._popup_open = True
        self.update()
        super().showPopup()

    def _fixPopupHeight(self) -> None:
        view = self.view()
        if view:
            container = view.parent()
            if container:
                geo = self.view().geometry()
                container.setFixedHeight(geo.height())

    def hidePopup(self) -> None:
        self._popup_open = False
        self.update()
        super().hidePopup()

    def setTitle(self, title: str) -> None:
        """设置标题文字�?

        :param title: 标题文字
        """
        self._title_text = title
        self.update()

    def title(self) -> str:
        """返回标题文字�?

        :return: 标题文字
        """
        return self._title_text

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

        current_selections = self.getCurrentSelection()
        max_show = 3
        if current_selections:
            if len(current_selections) > max_show:
                display_text = ",".join(current_selections[:max_show]) + "..."
            else:
                display_text = ",".join(current_selections)
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
                    display_text,
                    text_option,
                )

        arrow_rect = QRect(
            content_rect.right() - 25,
            content_rect.top(),
            20,
            content_rect.height(),
        )
        arrow_icon = (
            ElaIconType.IconName.AngleUp
            if self._popup_open
            else ElaIconType.IconName.AngleDown
        )
        icon = ElaIcon.getInstance().getElaIcon(arrow_icon, text_color)
        icon_pixmap = icon.pixmap(17, 17)
        painter.drawPixmap(
            arrow_rect.left() + (arrow_rect.width() - icon_pixmap.width()) // 2,
            arrow_rect.top() + (arrow_rect.height() - icon_pixmap.height()) // 2,
            icon_pixmap,
        )
