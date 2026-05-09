"""
通知提示组件，风格参考 ElaWidgetTools 的 ElaToast。

非模态提示，支持成功/信息/警告/错误四种类型，
自动淡入→停留→淡出→自动关闭。

用法::

    from pyqt5_ela_pro import ElaToast

    ElaToast.success("操作成功")
    ElaToast.error("发生错误")
    ElaToast.info("提示信息")
    ElaToast.warning("警告")
"""

from __future__ import annotations

import traceback
from enum import IntEnum
from typing import Optional

from PyQt5.QtCore import (
    Qt,
    QRect,
    QRectF,
    QPoint,
    QPropertyAnimation,
    QEasingCurve,
    QTimer,
    QAbstractAnimation,
)
from PyQt5.QtGui import QPainter, QPainterPath, QFont, QFontMetrics, QColor, QPaintEvent
from PyQt5.QtWidgets import QWidget, QApplication

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaIconType

from .widget_base import ElaThemeWidget


class _ToastType(IntEnum):
    Success = 0
    Info = 1
    Warning = 2
    Error = 3


class ElaToast(ElaThemeWidget):
    """通知提示。私有构造，使用静态方法创建。"""

    def __init__(
        self,
        toast_type: _ToastType,
        text: str,
        display_msec: int,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(None)

        self._border_radius = 8
        self._display_msec = display_msec
        self._toast_type = toast_type
        self._text = text
        self._shadow_border = 4

        self.setObjectName("ElaToast")
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._icon_font = QFont("ElaAwesome")
        self._text_font = QFont()

        # Size
        self._text_font.setPixelSize(14)
        fm = QFontMetrics(self._text_font)
        tw = fm.horizontalAdvance(text)
        total_w = max(200, min(400, tw + 80))
        self.setFixedHeight(48)
        self.setFixedWidth(total_w + self._shadow_border * 2)

        # Position: centered at top of parent window or screen
        pos = QPoint()
        if parent:
            parent_global = parent.mapToGlobal(QPoint(0, 0))
            pw = parent.width()
            pos = QPoint(
                parent_global.x() + (pw - self.width()) // 2, parent_global.y() + 60
            )
        else:
            screen = QApplication.primaryScreen()
            if screen:
                sg = screen.availableGeometry()
                pos = QPoint(sg.x() + (sg.width() - self.width()) // 2, sg.y() + 60)
        self.move(pos)

    def _present(self) -> None:
        self.show()
        self._run_animation()

    # ── Static public API ─────────────────────────────────

    @staticmethod
    def success(
        text: str, display_msec: int = 2000, parent: Optional[QWidget] = None
    ) -> None:
        toast = ElaToast(_ToastType.Success, text, display_msec, parent)
        toast._present()

    @staticmethod
    def info(
        text: str, display_msec: int = 2000, parent: Optional[QWidget] = None
    ) -> None:
        toast = ElaToast(_ToastType.Info, text, display_msec, parent)
        toast._present()

    @staticmethod
    def warning(
        text: str, display_msec: int = 2000, parent: Optional[QWidget] = None
    ) -> None:
        toast = ElaToast(_ToastType.Warning, text, display_msec, parent)
        toast._present()

    @staticmethod
    def error(
        text: str, display_msec: int = 2000, parent: Optional[QWidget] = None
    ) -> None:
        toast = ElaToast(_ToastType.Error, text, display_msec, parent)
        toast._present()

    # ── Internal ──────────────────────────────────────────

    def _run_animation(self) -> None:
        self._opacity = 0.0
        self._fade_in = QPropertyAnimation(self, b"windowOpacity")
        self._fade_in.setDuration(200)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_in.finished.connect(self._onFadeInFinished)
        self._fade_in.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def _onFadeInFinished(self) -> None:
        QTimer.singleShot(self._display_msec, self._startFadeOut)

    def _startFadeOut(self) -> None:
        self._fade_out = QPropertyAnimation(self, b"windowOpacity")
        self._fade_out.setDuration(300)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade_out.finished.connect(self.close)
        self._fade_out.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    # ── Paint ─────────────────────────────────────────────

    def paintEvent(self, event: QPaintEvent) -> None:
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

            mode = self._theme_mode
            sb = self._shadow_border
            br = self._border_radius
            fg = QRect(sb, sb, self.width() - 2 * sb, self.height() - 2 * sb)

            # Background
            painter.setPen(
                eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.PopupBorder)
            )
            painter.setBrush(
                eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.PopupBase)
            )
            painter.drawRoundedRect(fg, br, br)

            # Indicator & icon
            if self._toast_type == _ToastType.Success:
                ind_color = QColor(0x0F, 0x7B, 0x0F)
                icon_enum = ElaIconType.IconName.Check
            elif self._toast_type == _ToastType.Info:
                ind_color = eTheme.getThemeColor(
                    mode, ElaThemeType.ThemeColor.PrimaryNormal
                )
                icon_enum = ElaIconType.IconName.CircleInfo
            elif self._toast_type == _ToastType.Warning:
                ind_color = QColor(0xF7, 0x93, 0x0E)
                icon_enum = ElaIconType.IconName.CircleExclamation
            else:
                ind_color = eTheme.getThemeColor(
                    mode, ElaThemeType.ThemeColor.StatusDanger
                )
                icon_enum = ElaIconType.IconName.CircleXmark

            # Indicator bar (clip to foreground)
            clip_path = QPainterPath()
            clip_path.addRoundedRect(QRectF(fg), br, br)
            painter.save()
            painter.setClipPath(clip_path)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(ind_color)
            painter.drawRect(QRect(fg.x(), fg.y(), 4, fg.height()))
            painter.restore()

            # Icon
            self._icon_font.setPixelSize(16)
            painter.setFont(self._icon_font)
            painter.setPen(ind_color)
            painter.drawText(
                QRect(fg.x() + 14, fg.y(), 20, fg.height()),
                Qt.AlignmentFlag.AlignCenter,
                chr(int(icon_enum)),
            )

            # Text
            self._text_font.setPixelSize(14)
            painter.setFont(self._text_font)
            painter.setPen(
                eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicText)
            )
            painter.drawText(
                QRect(fg.x() + 42, fg.y(), fg.width() - 52, fg.height()),
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                self._text,
            )
        except Exception:
            print(traceback.format_exc())
