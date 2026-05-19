"""
角标组件，风格参考 ElaWidgetTools 的 ElaInfoBadge。

支持 Dot（圆点）、Value（数值）、Icon（图标）三种模式，
5 种严重级别颜色，可附加到任意目标控件的右上角。

用法::

    from pyqt5_ela_pro import ElaInfoBadge

    badge = ElaInfoBadge(parent=self)
    badge.attachTo(some_button)

    badge_val = ElaInfoBadge(value=5, parent=self)
    badge_val.attachTo(some_button)

    badge_icon = ElaInfoBadge(icon=ElaIconType.IconName.Gear, parent=self)
    badge_icon.attachTo(some_button)
"""

from __future__ import annotations

from enum import IntEnum
from typing import Optional

from PyQt5.QtCore import Qt, QRectF, QSize, QEvent
from PyQt5.QtGui import QColor, QPainter, QPen, QFont, QFontMetrics, QPaintEvent
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaIconType

from .widget_base import ElaThemeWidget


class ElaInfoBadge(ElaThemeWidget):
    """角标组件。

    可附加到任意控件的右上角，支持 Dot / Value / Icon 三种显示模式，
    以及 Attention / Informational / Success / Caution / Critical 五种严重级别。

    :param value: 数值模式时的初始值，为 ``None`` 时不启用数值模式
    :param icon: 图标模式时的图标，为 ``None`` 时不启用图标模式
    :param parent: 父控件
    """

    class BadgeMode(IntEnum):
        Dot = 0
        Value = 1
        Icon = 2

    class Severity(IntEnum):
        Attention = 0
        Informational = 1
        Success = 2
        Caution = 3
        Critical = 4

    def __init__(
        self,
        value: Optional[int] = None,
        icon: Optional[ElaIconType.IconName] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self._badge_mode = self.BadgeMode.Dot
        self._severity = self.Severity.Attention
        self._value = 0
        self._max_value = 99
        self._icon: ElaIconType.IconName = ElaIconType.IconName.None_
        self._target: Optional[QWidget] = None

        self.setObjectName("ElaInfoBadge")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._icon_font = QFont("ElaAwesome")

        if value is not None:
            self._badge_mode = self.BadgeMode.Value
            self._value = value
        elif icon is not None:
            self._badge_mode = self.BadgeMode.Icon
            self._icon = icon

    # ── Public API ────────────────────────────────────────

    def setBadgeMode(self, mode: int) -> None:
        """设置角标显示模式。

        :param mode: ``ElaInfoBadge.BadgeMode`` 枚举值
        """
        self._badge_mode = mode
        self._updateGeometry()
        self.update()

    def badgeMode(self) -> int:
        """获取当前角标模式。

        :returns: ``ElaInfoBadge.BadgeMode`` 枚举值
        """
        return self._badge_mode

    def setValue(self, value: int) -> None:
        """设置数值模式下的显示值。

        :param value: 数值
        """
        self._value = value
        self._updateGeometry()
        self.update()

    def value(self) -> int:
        """获取当前显示值。

        :returns: 数值
        """
        return self._value

    def setMaxValue(self, max_value: int) -> None:
        """设置数值上限（超出时显示 ``{max_value}+``）。

        :param max_value: 上限值
        """
        self._max_value = max_value
        self.update()

    def maxValue(self) -> int:
        """获取数值上限。

        :returns: 上限值
        """
        return self._max_value

    def setElaIcon(self, icon: ElaIconType.IconName) -> None:
        """设置图标模式下的图标。

        :param icon: ElaAwesome 图标名称
        """
        self._icon = icon
        self.update()

    def elaIcon(self) -> ElaIconType.IconName:
        """获取当前图标。

        :returns: ElaAwesome 图标名称
        """
        return self._icon

    def setSeverity(self, severity: int) -> None:
        """设置严重级别（影响角标颜色）。

        :param severity: ``ElaInfoBadge.Severity`` 枚举值
        """
        self._severity = severity
        self.update()

    def severity(self) -> int:
        """获取当前严重级别。

        :returns: ``ElaInfoBadge.Severity`` 枚举值
        """
        return self._severity

    def attachTo(self, target: QWidget) -> None:
        """将角标附加到目标控件的右上角。

        :param target: 目标控件
        """
        if self._target:
            self._target.removeEventFilter(self)
        self._target = target
        if target:
            self.setParent(target)
            target.installEventFilter(self)
            self.raise_()
            self._updateGeometry()
            self._updatePosition()
            self.show()

    def detach(self) -> None:
        """从当前目标控件上移除角标并隐藏。"""
        if self._target:
            self._target.removeEventFilter(self)
        self._target = None
        self.hide()

    # ── Internal ──────────────────────────────────────────

    def _getSeverityColor(self) -> QColor:
        mode = eTheme.getThemeMode()
        if self._severity == self.Severity.Attention:
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.StatusDanger)
        if self._severity == self.Severity.Informational:
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.PrimaryNormal)
        if self._severity == self.Severity.Success:
            return QColor(0x0F, 0x7B, 0x0F)
        if self._severity == self.Severity.Caution:
            return QColor(0x9D, 0x5D, 0x00)
        return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.StatusDanger)

    def _updateGeometry(self) -> None:
        self.updateGeometry()
        self.adjustSize()

    def _updatePosition(self) -> None:
        if self._target:
            self.move(self._target.width() - self.width() - 2, 2)
            self.raise_()

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    def deleteLater(self) -> None:
        self._theme_cleanup()
        if self._target:
            self._target.removeEventFilter(self)
        super().deleteLater()

    def eventFilter(self, watched, event) -> bool:
        if watched == self._target and event.type() in (
            QEvent.Type.Resize,
            QEvent.Type.Move,
        ):
            self._updatePosition()
            self.raise_()
        return super().eventFilter(watched, event)

    # ── Paint ─────────────────────────────────────────────

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        badge_color = self._getSeverityColor()
        r = QRectF(1, 1, self.width() - 2, self.height() - 2)

        if self._badge_mode == self.BadgeMode.Dot:
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            painter.setBrush(badge_color)
            painter.drawEllipse(r)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(r.adjusted(1, 1, -1, -1))

        elif self._badge_mode == self.BadgeMode.Value:
            h = r.height()
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            painter.setBrush(badge_color)
            painter.drawRoundedRect(r, h / 2.0, h / 2.0)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(r, h / 2.0, h / 2.0)

            text = (
                str(self._value)
                if self._value <= self._max_value
                else f"{self._max_value}+"
            )
            font = self.font()
            font.setPixelSize(10)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)

        elif self._badge_mode == self.BadgeMode.Icon:
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            painter.setBrush(badge_color)
            painter.drawEllipse(r)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(r)

            self._icon_font.setPixelSize(int(self.height() * 0.55))
            painter.setFont(self._icon_font)
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(
                self.rect(), Qt.AlignmentFlag.AlignCenter, chr(int(self._icon))
            )

    def sizeHint(self) -> QSize:
        if self._badge_mode == self.BadgeMode.Dot:
            return QSize(10, 10)
        if self._badge_mode == self.BadgeMode.Value:
            text = (
                str(self._value)
                if self._value <= self._max_value
                else f"{self._max_value}+"
            )
            font = QFont()
            font.setPixelSize(10)
            font.setBold(True)
            fm = QFontMetrics(font)
            tw = fm.horizontalAdvance(text)
            w = max(16, tw + 8)
            return QSize(w, 16)
        return QSize(16, 16)
