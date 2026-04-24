"""
具名多选下拉框组件。

带有标题标签的多选下拉框，标题在左侧，值在右侧。
继承自 PyQt5ElaWidgetTools.ElaMultiSelectComboBox。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import (
    Qt,
    QRect,
    QRectF,
    QTimer,
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

from PyQt5.QtWidgets import QWidget, QComboBox

from PyQt5ElaWidgetTools import (
    eTheme,
    ElaThemeType,
    ElaIcon,
    ElaIconType,
    ElaMultiSelectComboBox,
)

from .ela_tag_box import _TagBoxThemeMixin


class ElaTagMultiBox(_TagBoxThemeMixin, ElaMultiSelectComboBox):
    """具名多选下拉框。

    带有标题标签的多选下拉框，标题在左侧，值在右侧。
    继承自 PyQt5ElaWidgetTools.ElaMultiSelectComboBox。

    :param parent: 父控件
    :param title: 标题文字

    Example::

        combo = ElaTagMultiBox(parent, title="语言")
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
        self._expand_mark_width: float = 0.0
        self._expand_icon_rotate: float = 0.0
        self._currentSelection: list[str] = []

        self._mark_animation = QPropertyAnimation(self, b"expandMarkWidth")
        self._mark_animation.setDuration(300)
        self._mark_animation.setEasingCurve(QEasingCurve.InOutSine)

        self._rotate_animation = QPropertyAnimation(self, b"expandIconRotate")
        self._rotate_animation.setDuration(300)
        self._rotate_animation.setEasingCurve(QEasingCurve.InOutSine)

        self.setFixedHeight(38)
        self.setMaxVisibleItems(10)

        QTimer.singleShot(0, self._preInitPopup)

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

    def _preInitPopup(self) -> None:
        view = self.view()
        if view:
            view.setMinimumHeight(200)

    def _getTargetMarkWidth(self) -> float:
        selected_count = len(self.getCurrentSelection())
        total_count = self.count()
        if total_count <= 0:
            return 0.0
        return (self.width() / 2 - 9) * selected_count / total_count

    def showPopup(self) -> None:
        self._expand_mark_width = self._getTargetMarkWidth()
        super().showPopup()

    def hidePopup(self) -> None:
        self._expand_mark_width = 0.0
        super().hidePopup()

    def setCurrentSelection(self, selection):
        if isinstance(selection, str):
            selection = [selection]
        self._currentSelection = list(selection)
        if self._mark_animation.state() == QPropertyAnimation.Running:
            self._mark_animation.stop()
        self._expand_mark_width = self._getTargetMarkWidth()
        self.update()
        super().setCurrentSelection(self._currentSelection)

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

        view = self.view()
        is_popup_visible = view.isVisible() if view else False
        if is_popup_visible:
            mark_width = self._getTargetMarkWidth()
        else:
            mark_width = self._expand_mark_width
        if mark_width > 0:
            mark_color = eTheme.getThemeColor(
                eTheme.getThemeMode(), ElaThemeType.ThemeColor.PrimaryNormal
            )
            painter.setPen(Qt.NoPen)
            painter.setBrush(mark_color)
            mark_rect = QRectF(
                self.width() / 2 - mark_width,
                self.height() - 3,
                mark_width * 2,
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
