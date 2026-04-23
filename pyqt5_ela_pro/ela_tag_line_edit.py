"""
具名输入框组件。

带有标题标签的输入框组件，支持主题适配、焦点状态和错误状态显示。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, QRect, QRectF, QLine
from PyQt5.QtGui import QColor, QPainter, QFontMetrics, QTextOption, QPen, QFont
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaLineEdit, ElaThemeColor


class ElaTagLineEdit(ElaLineEdit):
    """具名输入框。

    带有标题标签的输入框，标题显示在输入框左侧。
    支持主题适配，包含空闲、聚焦、错误三种状态。

    :param parent: 父控件
    :param title: 标题文字

    Example::

        edit = ElaTagLineEdit(parent, title="用户名")
        edit.setText("admin")
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "Untitled",
    ) -> None:
        super().__init__(parent)

        self._title_text = title
        self._title_font_size = 13
        self._is_error = False

        self.setFixedHeight(38)
        self._updateMargins()

        self.textChanged.connect(self._onTextChanged)

    def setTitle(self, title: str) -> None:
        """设置标题文字。

        :param title: 标题文字
        """
        self._title_text = title
        self._updateMargins()
        self.update()

    def title(self) -> str:
        """返回标题文字。

        :return: 标题文字
        """
        return self._title_text

    def setTitleFontSize(self, size: int) -> None:
        """设置标题字体大小。

        :param size: 字体大小（像素）
        """
        self._title_font_size = size
        self._updateMargins()
        self.update()

    def notifyInvalidInput(self) -> None:
        """触发错误状态样式。"""
        self._is_error = True
        self.update()

    def clearError(self) -> None:
        """清除错误状态样式。"""
        self._is_error = False
        self.update()

    def _updateMargins(self) -> None:
        metrics = QFontMetrics(self.font())
        title_width = metrics.horizontalAdvance(self._title_text) + 20
        self.setTextMargins(title_width, 0, 10, 0)

    def _onTextChanged(self, text: str) -> None:
        self.update()

    def _getTitleColor(self) -> QColor:
        current_theme = eTheme.getThemeMode()
        if self._is_error:
            return eTheme.getThemeColor(
                current_theme, ElaThemeType.ThemeColor.StatusDanger
            )
        return eTheme.getThemeColor(current_theme, ElaThemeType.ThemeColor.BasicText)

    def _getBorderColor(self) -> QColor:
        current_theme = eTheme.getThemeMode()
        if self._is_error:
            return eTheme.getThemeColor(
                current_theme, ElaThemeType.ThemeColor.StatusDanger
            )
        if self.hasFocus():
            return eTheme.getThemeColor(
                current_theme, ElaThemeType.ThemeColor.PrimaryNormal
            )
        return eTheme.getThemeColor(
            current_theme, ElaThemeType.ThemeColor.BasicBaseLine
        )

    def _drawTitle(self, painter: QPainter) -> None:
        metrics = QFontMetrics(self.font())
        title_width = metrics.horizontalAdvance(self._title_text) + 20
        title_height = self.height()

        title_rect = QRect(0, 0, title_width, title_height)

        option = QTextOption()
        option.setWrapMode(QTextOption.WrapMode.NoWrap)
        option.setAlignment(
            Qt.Alignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        )

        title_font = QFont(self.font())
        title_font.setPixelSize(self._title_font_size)

        painter.save()
        painter.setFont(title_font)
        painter.setPen(self._getTitleColor())
        painter.drawText(
            QRectF(title_rect.adjusted(10, 0, -10, 0)), self._title_text, option
        )
        painter.restore()

    def _drawBorder(self, painter: QPainter) -> None:
        pen = QPen(self._getBorderColor())
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        y = self.height() - 2
        painter.drawLine(QLine(0, y, self.width(), y))

    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        self._drawBorder(painter)
        self._drawTitle(painter)