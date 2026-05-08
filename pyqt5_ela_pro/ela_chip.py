"""
标签纸片组件，风格参考 ElaWidgetTools 的 ElaTag。

支持 Default / Primary / Success / Warning / Danger 五种颜色，
可关闭、可选择、可点击。

用法::

    from pyqt5_ela_pro import ElaChip

    chip = ElaChip("标签", parent=self)
    chip.setClosable(True)
    chip.closed.connect(lambda: print("关闭"))
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, QRectF, QSize, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPaintEvent, QMouseEvent, QFont
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import eTheme, ElaThemeType

from ._internal import disconnect_theme_signal


# ── Color accent values (matching ElaButton palette) ─────

_CHIP_ACCENT = {
    "primary":   {"light": "#1677ff", "dark": "#1668dc"},
    "danger":    {"light": "#ff4d4f", "dark": "#dc4446"},
    "blue":      {"light": "#1677ff", "dark": "#1668dc"},
    "purple":    {"light": "#722ed1", "dark": "#642ab8"},
    "cyan":      {"light": "#13c2c2", "dark": "#10adad"},
    "green":     {"light": "#52c41a", "dark": "#49aa17"},
    "magenta":   {"light": "#eb2f96", "dark": "#c92980"},
    "pink":      {"light": "#eb2f96", "dark": "#c92980"},
    "red":       {"light": "#f5222d", "dark": "#d91d28"},
    "orange":    {"light": "#fa8c16", "dark": "#d97a13"},
    "yellow":    {"light": "#fadb14", "dark": "#d9bd12"},
    "volcano":   {"light": "#fa541c", "dark": "#d94818"},
    "geekblue":  {"light": "#2f54eb", "dark": "#2a47cc"},
    "lime":      {"light": "#a0d911", "dark": "#8cbd0e"},
    "gold":      {"light": "#faad14", "dark": "#d99612"},
}


def _chip_accent(name: str) -> QColor:
    mode = eTheme.getThemeMode()
    key = "light" if mode == ElaThemeType.ThemeMode.Light else "dark"
    return QColor(_CHIP_ACCENT[name][key])


class ElaChip(QWidget):
    """标签纸片组件。

    支持 16 种颜色主题（同 ElaButton 色系），可关闭、可选择、可点击。

    :param text: 标签文本
    :param parent: 父控件
    """

    class Color:
        Default = 0
        Primary = 1
        Danger = 2
        Blue = 3
        Purple = 4
        Cyan = 5
        Green = 6
        Magenta = 7
        Pink = 8
        Red = 9
        Orange = 10
        Yellow = 11
        Volcano = 12
        Geekblue = 13
        Lime = 14
        Gold = 15

    closed = pyqtSignal()
    clicked = pyqtSignal()
    checkedChanged = pyqtSignal(bool)

    def __init__(
        self,
        text: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self._text = text
        self._border_radius = 4
        self._is_closable = False
        self._is_checkable = False
        self._is_checked = False
        self._chip_color = self.Color.Default
        self._close_btn_width = 16
        self._check_icon_width = 16
        self._padding = 8

        self.setObjectName("ElaChip")
        self.setFixedHeight(28)
        self.setMouseTracking(True)

        self._theme_mode = eTheme.getThemeMode()
        eTheme.themeModeChanged.connect(self._onThemeChanged)

    # ── Public API ────────────────────────────────────────

    def setText(self, text: str) -> None:
        self._text = text
        self._updateGeometry()
        self.update()

    def text(self) -> str:
        return self._text

    def setBorderRadius(self, radius: int) -> None:
        self._border_radius = radius
        self.update()

    def borderRadius(self) -> int:
        return self._border_radius

    def setClosable(self, closable: bool) -> None:
        self._is_closable = closable
        self._updateGeometry()
        self.update()

    def isClosable(self) -> bool:
        return self._is_closable

    def setCheckable(self, checkable: bool) -> None:
        self._is_checkable = checkable
        self._updateGeometry()
        self.update()

    def isCheckable(self) -> bool:
        return self._is_checkable

    def setChecked(self, checked: bool) -> None:
        self._is_checked = checked
        self._updateGeometry()
        self.update()

    def isChecked(self) -> bool:
        return self._is_checked

    def setColor(self, color: int) -> None:
        self._chip_color = color
        self.update()

    def getColor(self) -> int:
        return self._chip_color

    # ── Color name mapping ────────────────────────────────

    _COLOR_NAMES = {
        Color.Default:   "default",
        Color.Primary:   "primary",
        Color.Danger:    "danger",
        Color.Blue:      "blue",
        Color.Purple:    "purple",
        Color.Cyan:      "cyan",
        Color.Green:     "green",
        Color.Magenta:   "magenta",
        Color.Pink:      "pink",
        Color.Red:       "red",
        Color.Orange:    "orange",
        Color.Yellow:    "yellow",
        Color.Volcano:   "volcano",
        Color.Geekblue:  "geekblue",
        Color.Lime:      "lime",
        Color.Gold:      "gold",
    }

    # ── Internal ──────────────────────────────────────────

    def _getBackgroundColor(self) -> QColor:
        mode = eTheme.getThemeMode()
        if self._chip_color == self.Color.Default:
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBase)
        name = self._COLOR_NAMES.get(self._chip_color)
        if name and name in _CHIP_ACCENT:
            color = QColor(_chip_accent(name))
            color.setAlpha(30)
            return color
        return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBase)

    def _getForegroundColor(self) -> QColor:
        mode = eTheme.getThemeMode()
        if self._chip_color == self.Color.Default:
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicText)
        name = self._COLOR_NAMES.get(self._chip_color)
        if name and name in _CHIP_ACCENT:
            return QColor(_chip_accent(name))
        return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicText)

    def _updateGeometry(self) -> None:
        self.updateGeometry()
        self.adjustSize()

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    def deleteLater(self) -> None:
        disconnect_theme_signal(self._onThemeChanged)
        super().deleteLater()

    # ── Events ────────────────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self._is_closable:
                close_x = self.width() - self._close_btn_width - self._padding // 2
                if event.pos().x() >= close_x:
                    self.closed.emit()
                    self.hide()
                    return
            if self._is_checkable:
                self._is_checked = not self._is_checked
                self._updateGeometry()
                self.checkedChanged.emit(self._is_checked)
                self.update()
            self.clicked.emit()
            event.accept()
            return
        super().mousePressEvent(event)

    # ── Paint ─────────────────────────────────────────────

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = self.width()
        h = self.height()
        br = self._border_radius

        bg_color = self._getBackgroundColor()
        fg_color = self._getForegroundColor()

        # Background
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, w, h), br, br)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg_color)
        painter.drawPath(path)

        x_offset = self._padding

        # Check icon
        if self._is_checkable and self._is_checked:
            icon_font = QFont("ElaAwesome")
            icon_font.setPixelSize(12)
            painter.setFont(icon_font)
            painter.setPen(fg_color)
            painter.drawText(
                QRectF(x_offset, 0, self._check_icon_width, h),
                Qt.AlignmentFlag.AlignCenter,
                chr(0xea6c),
            )
            x_offset += self._check_icon_width

        # Text
        text_font = self.font()
        text_font.setPixelSize(13)
        painter.setFont(text_font)
        painter.setPen(fg_color)
        text_width = w - x_offset - self._padding
        if self._is_closable:
            text_width -= self._close_btn_width
        painter.drawText(
            QRectF(x_offset, 0, text_width, h),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self._text,
        )

        # Close button
        if self._is_closable:
            icon_font = QFont("ElaAwesome")
            icon_font.setPixelSize(10)
            painter.setFont(icon_font)
            painter.setPen(fg_color)
            close_x = w - self._close_btn_width - self._padding // 2
            painter.drawText(
                QRectF(close_x, 0, self._close_btn_width, h),
                Qt.AlignmentFlag.AlignCenter,
                chr(0xf4ce),
            )

    def sizeHint(self) -> QSize:
        font = QFont()
        font.setPixelSize(13)
        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self._text)
        w = text_width + self._padding * 2
        if self._is_closable:
            w += self._close_btn_width
        if self._is_checkable and self._is_checked:
            w += self._check_icon_width
        return QSize(max(w, 32), 28)
