"""
引导遮罩组件，风格参考 ElaWidgetTools 的 ElaSpotlight。

在父控件上叠加半透明遮罩，高亮目标区域，显示提示卡片。

用法::

    spotlight = ElaSpotlight(parent=self)
    spotlight.showSpotlight(target_btn, "点击此处开始")
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, QRectF, QPoint, QPointF, QSizeF, QObject, pyqtSignal, QPropertyAnimation, QEasingCurve, QAbstractAnimation, QEvent
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QColor, QPaintEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaText, ElaTextType, ElaPushButton

from ._internal import disconnect_theme_signal


class ElaSpotlight(QWidget):
    """引导遮罩。

    覆盖在父控件之上，用遮罩突出显示目标控件，并显示提示文字。

    :param parent: 父控件
    """

    stepChanged = pyqtSignal(int)
    finished = pyqtSignal()

    class SpotlightStep:
        def __init__(self, target: QWidget, title: str = "", content: str = "", is_circle: bool = False):
            self.target = target
            self.title = title
            self.content = content
            self.is_circle = is_circle

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._border_radius = 8
        self._padding = 8
        self._overlay_alpha = 120
        self._is_circle = False
        self._title = ""
        self._content = ""
        self._spotlight_rect = QRectF()
        self._opacity = 1.0
        self._steps: list[ElaSpotlight.SpotlightStep] = []
        self._current_step = -1
        self._is_active = False

        self.setVisible(False)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        # Tip widget with title, content, buttons
        self._tip_widget = QWidget(self)
        self._tip_widget.setVisible(False)

        self._tip_title = ElaText(self._tip_widget)
        self._tip_title.setTextStyle(ElaTextType.TextStyle.BodyStrong)

        self._tip_content = ElaText(self._tip_widget)
        self._tip_content.setTextStyle(ElaTextType.TextStyle.Body)
        self._tip_content.setWordWrap(True)

        self._step_indicator = ElaText(self._tip_widget)
        self._step_indicator.setTextStyle(ElaTextType.TextStyle.Caption)

        self._prev_btn = ElaPushButton("上一步", self._tip_widget)
        self._prev_btn.setFixedSize(70, 30)
        self._prev_btn.setBorderRadius(4)
        self._prev_btn.clicked.connect(self.previous)

        self._next_btn = ElaPushButton("下一步", self._tip_widget)
        self._next_btn.setFixedSize(70, 30)
        self._next_btn.setBorderRadius(4)
        self._next_btn.clicked.connect(self._onNextClicked)

        tip_layout = QVBoxLayout(self._tip_widget)
        tip_layout.setContentsMargins(16, 12, 16, 12)
        tip_layout.setSpacing(6)
        tip_layout.addWidget(self._tip_title)
        tip_layout.addWidget(self._tip_content)
        tip_layout.addSpacing(4)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        btn_layout.addWidget(self._step_indicator)
        btn_layout.addStretch()
        btn_layout.addWidget(self._prev_btn)
        btn_layout.addWidget(self._next_btn)
        tip_layout.addLayout(btn_layout)

        self._theme_mode = eTheme.getThemeMode()
        eTheme.themeModeChanged.connect(self._onThemeChanged)

    # ── Public API ────────────────────────────────────────

    def showSpotlight(self, target: QWidget, button_text: str = "知道了") -> None:
        step = self.SpotlightStep(target, self._title, self._content, self._is_circle)
        self._steps = [step]
        self._prev_btn.setVisible(False)
        self._next_btn.setText(button_text)
        self._step_indicator.setVisible(False)
        self.start()

    def setSteps(self, steps: list[SpotlightStep]) -> None:
        self._steps = steps

    def start(self) -> None:
        if not self._steps or not self.parent():
            return
        parent = self.parent()
        self.setGeometry(0, 0, parent.width(), parent.height())
        parent.installEventFilter(self)
        self.setVisible(True)
        self.raise_()

        self._spotlight_rect = QRectF()
        self._opacity = 0.0
        fade_in = QPropertyAnimation(self, b"windowOpacity")
        fade_in.valueChanged.connect(lambda: self.update())
        fade_in.setDuration(300)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        fade_in.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

        self._is_active = True
        self._showStep(0)

    def next(self) -> None:
        if self._current_step < len(self._steps) - 1:
            self._showStep(self._current_step + 1)

    def previous(self) -> None:
        if self._current_step > 0:
            self._showStep(self._current_step - 1)

    def finish(self) -> None:
        self._is_active = False
        self._tip_widget.setVisible(False)
        self.setVisible(False)
        if self.parent():
            self.parent().removeEventFilter(self)
        self.finished.emit()

    def currentStep(self) -> int:
        return self._current_step

    def stepCount(self) -> int:
        return len(self._steps)

    # ── Internal ──────────────────────────────────────────

    def _onNextClicked(self) -> None:
        if self._current_step >= len(self._steps) - 1:
            self.finish()
        else:
            self.next()

    def _getTargetRect(self, target: QWidget) -> QRectF:
        if not target or not self.parent():
            return QRectF()
        tl = target.mapTo(self.parent(), QPoint(0, 0))
        r = QRectF(QPointF(tl), QSizeF(target.size()))
        r.adjust(-self._padding, -self._padding, self._padding, self._padding)
        return r

    def _showStep(self, index: int) -> None:
        if index < 0 or index >= len(self._steps):
            return
        self._current_step = index
        step = self._steps[index]
        self._is_circle = step.is_circle

        self._tip_title.setText(step.title)
        self._tip_title.setVisible(bool(step.title))
        self._tip_content.setText(step.content)
        self._tip_content.setVisible(bool(step.content))

        if len(self._steps) > 1:
            self._prev_btn.setVisible(self._current_step > 0)
            self._next_btn.setText("完成" if self._current_step >= len(self._steps) - 1 else "下一步")
            self._step_indicator.setVisible(True)
            self._step_indicator.setText(f"{self._current_step + 1} / {len(self._steps)}")

        target_rect = self._getTargetRect(step.target)

        self._spotlight_rect = target_rect
        self.update()
        self._updateTipPosition()
        self._tip_widget.setVisible(True)
        self._tip_widget.raise_()
        self.stepChanged.emit(self._current_step)

    def _updateTipPosition(self) -> None:
        if not self.parent() or self._current_step < 0:
            return
        self._tip_widget.adjustSize()
        tw = min(300, self.width() - 40)
        self._tip_widget.setFixedWidth(tw)
        self._tip_widget.adjustSize()

        th = self._tip_widget.sizeHint().height()
        margin = 12
        spot = self._spotlight_rect
        tx = int(spot.center().x() - tw / 2)
        ty = int(spot.bottom() + margin)

        if ty + th > self.height() - 10:
            ty = int(spot.top() - th - margin)
        tx = max(10, min(tx, self.width() - tw - 10))
        ty = max(10, ty)

        self._tip_widget.move(tx, ty)

        mode = eTheme.getThemeMode()
        bg = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.DialogBase).name()
        border = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.PopupBorder).name()
        self._tip_widget.setStyleSheet(f"background-color: {bg}; border-radius: 8px; border: 1px solid {border};")

    def _onThemeChanged(self, mode) -> None:
        self._theme_mode = mode
        self.update()

    def deleteLater(self) -> None:
        disconnect_theme_signal(self._onThemeChanged)
        super().deleteLater()

    # ── Events ────────────────────────────────────────────

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched == self.parent() and event.type() == QEvent.Type.Resize:
            self.setGeometry(0, 0, self.parent().width(), self.parent().height())
            if self._is_active and 0 <= self._current_step < len(self._steps):
                self._spotlight_rect = self._getTargetRect(self._steps[self._current_step].target)
                self._updateTipPosition()
        return super().eventFilter(watched, event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self._spotlight_rect.isValid() and not self._spotlight_rect.contains(event.pos()):
            if len(self._steps) <= 1:
                self.finish()
        event.accept()

    def paintEvent(self, event: QPaintEvent) -> None:
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            overlay = QPainterPath()
            overlay.addRect(QRectF(self.rect()))

            if self._spotlight_rect.isValid():
                hole = QPainterPath()
                if self._is_circle:
                    r = max(self._spotlight_rect.width(), self._spotlight_rect.height()) / 2.0
                    hole.addEllipse(self._spotlight_rect.center(), r, r)
                else:
                    hole.addRoundedRect(self._spotlight_rect, self._border_radius, self._border_radius)
                overlay = overlay.subtracted(hole)

            alpha = int(self._overlay_alpha * self._opacity)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 0, 0, alpha))
            painter.drawPath(overlay)

            if self._spotlight_rect.isValid():
                mode = eTheme.getThemeMode()
                border_color = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.PrimaryNormal)
                painter.setPen(QPen(border_color, 2))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                if self._is_circle:
                    r = max(self._spotlight_rect.width(), self._spotlight_rect.height()) / 2.0
                    painter.drawEllipse(self._spotlight_rect.center(), r, r)
                else:
                    painter.drawRoundedRect(self._spotlight_rect, self._border_radius, self._border_radius)
        except Exception as e:
            print(f"ElaSpotlight paint error: {e}")
