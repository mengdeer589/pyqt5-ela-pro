"""
工具提示组件模块。

提供两种提示组件：

- ``ElaToolTip``：悬浮提示组件，支持 8 种显示位置
- ``ElaStateToolTip``：带状态指示的提示组件，支持加载中/成功/失败等状态

``set_tooltip`` 和 ``remove_tooltip`` 函数用于为任意 ``QWidget`` 绑定或解除
悬浮提示，使用弱引用字典管理，不会阻止 widget 被垃圾回收。
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional
import weakref

from PyQt5.QtCore import (
    QPropertyAnimation,
    Qt,
    QTimer,
    pyqtSignal,
    QPoint,
    QRect,
    QRectF,
    QObject,
    QEvent,
)
from PyQt5.QtGui import (
    QPainter,
    QFont,
    QBrush,
    QColor,
    QPaintEvent,
    QHideEvent,
    QMouseEvent, QPen, QPainterPath,
)
from PyQt5.QtWidgets import QWidget, QLabel, QGraphicsDropShadowEffect

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaIconType, ElaText


TOOLTIP_BORDER_RADIUS: int = 8
TOOLTIP_SHADOW_BORDER_WIDTH: int = 3
TOOLTIP_LIGHT_BG_COLOR: str = "#ffffff"
TOOLTIP_DARK_BG_COLOR: str = "#202020"
TOOLTIP_FADE_DURATION: int = 200
TOOLTIP_AUTO_CLOSE_DELAY: int = 1000
TOOLTIP_ROTATE_TIMER_INTERVAL: int = 50
TOOLTIP_ROTATE_ANGLE_DELTA: int = 20

STATETOOLTIP_BORDER_RADIUS: int = 10
STATETOOLTIP_TITLE_FONT_SIZE: int = 13
STATETOOLTIP_CONTENT_FONT_SIZE: int = 12
STATETOOLTIP_MIN_WIDTH: int = 200
STATETOOLTIP_MAX_WIDTH: int = 360
STATETOOLTIP_HEIGHT: int = 56
STATETOOLTIP_CLOSE_BUTTON_SIZE: int = 20
STATETOOLTIP_ICON_SIZE: int = 16
STATETOOLTIP_ACCENT_WIDTH: int = 4
STATETOOLTIP_SUCCESS_COLOR_LIGHT: str = "#4CAF50"
STATETOOLTIP_SUCCESS_COLOR_DARK: str = "#66BB6A"


class ElaToolTipPosition(Enum):
    """提示框相对于目标 widget 的显示位置枚举。"""

    Top = 0
    """显示在目标上方"""

    Bottom = 1
    """显示在目标下方"""

    Left = 2
    """显示在目标左侧"""

    Right = 3
    """显示在目标右侧"""

    TopLeft = 4
    """显示在目标左上方"""

    TopRight = 5
    """显示在目标右上方"""

    BottomLeft = 6
    """显示在目标左下方"""

    BottomRight = 7
    """显示在目标右下方"""


class ElaToolTip(QWidget):
    """轻量级悬浮提示组件。

    绘制一个带圆角和阴影的背景框，内部包含文本。
    通过 :py:meth:`showAt` 指定目标 widget 和显示位置。

    :param text: 提示文本内容。
    :type text: str
    :param parent: 父级 widget，默认为 ``None``（顶级窗口）。
    :type parent: QWidget, optional
    """

    def __init__(self, text: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._text = text
        self._borderRadius = TOOLTIP_BORDER_RADIUS
        self._shadowBorderWidth = TOOLTIP_SHADOW_BORDER_WIDTH
        self._currentTheme = eTheme.getThemeMode()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.Tool  # type: ignore[arg-type]
            | Qt.WindowType.FramelessWindowHint  # type: ignore[arg-type]
            | Qt.WindowType.WindowStaysOnTopHint  # type: ignore[arg-type]
        )

        self._label = QLabel(text, self)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        font = QFont()
        font.setPixelSize(12)
        self._label.setFont(font)

        self._updateSize()

    def _updateSize(self) -> None:
        """根据标签内容更新 tooltip 的固定尺寸。"""
        self._label.adjustSize()
        width = self._label.width() + 24
        height = self._label.height() + 16
        self.setFixedSize(width, height)
        self._label.move(12, 8)

    def setText(self, text: str) -> None:
        """设置提示文本。

        :param text: 新的提示文本。
        :type text: str
        """
        self._text = text
        self._label.setText(text)
        self._updateSize()

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        """绘制提示框背景和阴影。

        :param a0: 绘制事件。
        :type a0: QPaintEvent, optional
        """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        themeMode = self._currentTheme

        eTheme.drawEffectShadow(
            painter, self.rect(), self._shadowBorderWidth, self._borderRadius
        )

        bgColor = eTheme.getThemeColor(themeMode, ElaThemeType.ThemeColor.BasicBase)
        painter.setBrush(QBrush(bgColor))
        painter.drawRoundedRect(
            QRect(3, 3, self.width() - 6, self.height() - 6),
            self._borderRadius,
            self._borderRadius,
        )

    def showAt(
        self, widget: QWidget, position: ElaToolTipPosition = ElaToolTipPosition.Top
    ) -> None:
        """在指定 widget 附近显示提示框。

        根据 *position* 计算提示框的理想位置，使其位于目标 widget
        的上、下、左、右或其他角落位置。

        :param widget: 目标 widget，提示框将显示在其附近。
        :type widget: QWidget
        :param position: 相对于目标 widget 的显示位置，默认为 ``TOP``。
        :type position: ElaToolTipPosition
        """
        if not self.isWindow():
            self.setParent(None)

        try:
            globalPos = widget.mapToGlobal(QPoint(0, 0))
        except (RuntimeError, AttributeError):
            return
        widgetRect = QRect(globalPos, widget.size())

        if position == ElaToolTipPosition.Top:
            x = widgetRect.center().x() - self.width() // 2
            y = widgetRect.top() - self.height() - 6
        elif position == ElaToolTipPosition.Bottom:
            x = widgetRect.center().x() - self.width() // 2
            y = widgetRect.bottom() + 6
        elif position == ElaToolTipPosition.Left:
            x = widgetRect.left() - self.width() - 6
            y = widgetRect.center().y() - self.height() // 2
        elif position == ElaToolTipPosition.Right:
            x = widgetRect.right() + 6
            y = widgetRect.center().y() - self.height() // 2
        elif position == ElaToolTipPosition.Top_LEFT:
            x = widgetRect.left()
            y = widgetRect.top() - self.height() - 6
        elif position == ElaToolTipPosition.Top_RIGHT:
            x = widgetRect.right() - self.width()
            y = widgetRect.top() - self.height() - 6
        elif position == ElaToolTipPosition.Bottom_LEFT:
            x = widgetRect.left()
            y = widgetRect.bottom() + 6
        elif position == ElaToolTipPosition.Bottom_RIGHT:
            x = widgetRect.right() - self.width()
            y = widgetRect.bottom() + 6
        else:
            x = widgetRect.center().x() - self.width() // 2
            y = widgetRect.top() - self.height() - 6

        self.move(int(x), int(y))
        self.show()


_tooltip_dict: weakref.WeakKeyDictionary[QWidget, ElaToolTip] = weakref.WeakKeyDictionary()
_filter_dict: weakref.WeakKeyDictionary[QWidget, _TooltipEventFilter] = (
    weakref.WeakKeyDictionary()
)
_cleanup_filter_refs: weakref.WeakKeyDictionary[QWidget, _WidgetCleanupFilter] = (
    weakref.WeakKeyDictionary()
)


class _TooltipEventFilter(QObject):
    """事件过滤器，监听目标 widget 的进入/离开事件以显示或隐藏提示框。

    :param tooltip: 要显示的 ``ElaToolTip`` 实例。
    :type tooltip: ElaToolTip
    :param position: 提示框的显示位置。
    :type position: ElaToolTipPosition
    :param target_widget: 安装此过滤器的目标 widget。
    :type target_widget: QWidget
    """

    def __init__(
        self, tooltip: ElaToolTip, position: ElaToolTipPosition, target_widget: QWidget
    ) -> None:
        super().__init__(target_widget)
        self._tooltip: weakref.ref[ElaToolTip] = weakref.ref(tooltip)
        self._position = position

    def eventFilter(self, a0: Optional[QObject], a1: Optional[QEvent]) -> bool:
        """事件过滤实现。进入时显示提示框，离开时隐藏。

        :param a0: 事件源对象。
        :type a0: QObject, optional
        :param a1: 事件对象。
        :type a1: QEvent, optional
        :return: 通常返回 ``False`` 表示不拦截事件。
        :rtype: bool
        """
        tooltip = self._tooltip()
        if tooltip is None or a0 is None or a1 is None:
            return False
        if a1.type() == QEvent.Type.Enter:
            if isinstance(a0, QWidget):
                tooltip.showAt(a0, self._position)
        elif a1.type() == QEvent.Type.Leave:
            tooltip.hide()
        return False


class _WidgetCleanupFilter(QObject):
    """当目标 widget 被销毁时自动清理对应的 tooltip 字典条目。"""

    def __init__(self, widget: QWidget) -> None:
        super().__init__(widget)
        self._widget_ref = weakref.ref(widget, self._on_widget_destroyed)
        _cleanup_filter_refs[widget] = self

    def _on_widget_destroyed(self, ref: weakref.ref) -> None:
        """widget 销毁时的回调，清理全局字典。

        :param ref: 指向已销毁 widget 的弱引用。
        :type ref: weakref.ref
        """
        obj = ref()
        if obj is not None:
            remove_tooltip_from_dict(obj)


def remove_tooltip_from_dict(widget: QWidget) -> None:
    """从全局字典中移除指定 widget 对应的 tooltip 并销毁。

    此函数为内部使用，通常不需要直接调用。
    :py:func:`remove_tooltip` 会自动调用本函数。

    :param widget: 目标 widget。
    :type widget: QWidget
    """
    if widget in _tooltip_dict:
        tooltip = _tooltip_dict.pop(widget)
        try:
            tooltip.hide()
            tooltip.deleteLater()
        except RuntimeError:
            pass
    if widget in _filter_dict:
        _filter_dict.pop(widget)


def set_tooltip(
    widget: QWidget, text: str, position: ElaToolTipPosition = ElaToolTipPosition.Top
) -> None:
    """为指定 widget 绑定悬浮提示。

    在 widget 上安装事件过滤器，当鼠标进入时自动显示提示框，
    离开时隐藏。多次调用同一 widget 会先移除旧提示再创建新提示。

    :param widget: 要绑定提示的 widget。
    :type widget: QWidget
    :param text: 提示文本内容。
    :type text: str
    :param position: 提示框相对于 widget 的显示位置，默认为 ``TOP``。
    :type position: ElaToolTipPosition

    Example::

        btn = QPushButton("Hover me")
        set_tooltip(btn, "这是一段提示文字", ToolTipPosition.TOP)
    """
    if widget in _tooltip_dict:
        remove_tooltip(widget)

    tooltip = ElaToolTip(text, widget.window())
    _tooltip_dict[widget] = tooltip

    filter_instance = _TooltipEventFilter(tooltip, position, widget)
    _filter_dict[widget] = filter_instance
    widget.installEventFilter(filter_instance)

    _WidgetCleanupFilter(widget)


def remove_tooltip(widget: QWidget) -> None:
    """解除指定 widget 的悬浮提示绑定。

    :param widget: 要解除提示绑定的 widget。
    :type widget: QWidget
    """
    if widget in _filter_dict:
        widget.removeEventFilter(_filter_dict[widget])
        del _filter_dict[widget]
    if widget in _tooltip_dict:
        tooltip = _tooltip_dict.pop(widget)
        tooltip.hide()
        tooltip.deleteLater()
    if widget in _cleanup_filter_refs:
        del _cleanup_filter_refs[widget]


class ElaStateToolTip(QWidget):
    """带状态指示的提示组件。

    支持两种状态：加载中（显示旋转图标）和完成（显示对勾图标）。
    提供淡出动画和关闭信号。

    :param title: 提示标题。
    :type title: str
    :param content: 提示内容文本。
    :type content: str
    :param parent: 父级 widget。
    :type parent: QWidget, optional

    Signals:
        closed: 提示框被关闭时发射此信号。

    Example::

        tooltip = ElaStateToolTip("正在加载", "请稍候...", self)
        tooltip.closed.connect(on_closed)
        tooltip.show()
    """

    closed = pyqtSignal()

    def __init__(
        self, title: str = "", content: str = "", parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._content = content
        self._isDone = False
        self._rotateAngle = 0
        self._deltaAngle = TOOLTIP_ROTATE_ANGLE_DELTA
        self._borderRadius = STATETOOLTIP_BORDER_RADIUS
        self._currentTheme = eTheme.getThemeMode()
        self._isClosing = False
        self._destroyed = False
        self._closeBtnHovered = False
        self._themeConnection: Any = None

        self._animation = QPropertyAnimation(self, b"windowOpacity")
        self._rotateTimer = QTimer(self)

        self._titleLabel = ElaText(title, self)
        self._contentLabel = ElaText(content, self)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        shadow.setBlurRadius(20)
        self.setGraphicsEffect(shadow)

        self._themeConnection = eTheme.themeModeChanged.connect(
            self._onThemeModeChanged
        )

        self.setMouseTracking(True)
        self._setup_ui()
        self._connectSignals()

    def _setup_ui(self) -> None:
        self._rotateTimer.setInterval(TOOLTIP_ROTATE_TIMER_INTERVAL)
        self._rotateTimer.timeout.connect(self._rotateTimerFlow)

        self._contentLabel.setMinimumWidth(STATETOOLTIP_MIN_WIDTH)
        self._contentLabel.setWordWrap(True)
        self._contentLabel.setMaximumWidth(STATETOOLTIP_MAX_WIDTH)

        self._updateContent()
        self._updateSizeAndPositions()

    def _connectSignals(self) -> None:
        self._rotateTimer.start()

    def _onThemeModeChanged(self, mode: int) -> None:
        self._currentTheme = mode
        self.update()

    def _getAccentColor(self) -> QColor:
        if self._isDone:
            mode = self._currentTheme
            return (
                QColor(STATETOOLTIP_SUCCESS_COLOR_DARK)
                if mode == ElaThemeType.ThemeMode.Dark
                else QColor(STATETOOLTIP_SUCCESS_COLOR_LIGHT)
            )
        return eTheme.getThemeColor(
            self._currentTheme, ElaThemeType.ThemeColor.PrimaryNormal
        )

    def _drawCloseButton(self, painter: QPainter) -> None:
        btn_size = STATETOOLTIP_CLOSE_BUTTON_SIZE
        btn_x = self.width() - btn_size - 12
        btn_y = 8
        btn_rect = QRect(btn_x, btn_y, btn_size, btn_size)

        if self._closeBtnHovered:
            hover_bg = eTheme.getThemeColor(
                self._currentTheme, ElaThemeType.ThemeColor.BasicHover
            )
            painter.save()
            painter.setBrush(hover_bg)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(btn_rect)
            painter.restore()

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        text_color = eTheme.getThemeColor(
            self._currentTheme, ElaThemeType.ThemeColor.BasicText
        )
        line_pen = QPen(text_color, 2, Qt.PenStyle.SolidLine)
        painter.setPen(line_pen)

        margin = 6
        painter.drawLine(
            btn_x + margin, btn_y + margin,
            btn_x + btn_size - margin, btn_y + btn_size - margin,
        )
        painter.drawLine(
            btn_x + btn_size - margin, btn_y + margin,
            btn_x + margin, btn_y + btn_size - margin,
        )
        painter.restore()

    def _updateContent(self) -> None:
        self._titleLabel.setText(self._title)
        self._contentLabel.setText(self._content)

        self._titleLabel.setTextPixelSize(STATETOOLTIP_TITLE_FONT_SIZE)
        self._contentLabel.setTextPixelSize(STATETOOLTIP_CONTENT_FONT_SIZE)

        self._titleLabel.adjustSize()
        self._contentLabel.adjustSize()

        content_max_w = (
            self._contentLabel.width()
            if self._contentLabel.width() <= STATETOOLTIP_MAX_WIDTH
            else STATETOOLTIP_MAX_WIDTH
        )
        width = max(
            self._titleLabel.width() + 60,
            content_max_w + 56,
            STATETOOLTIP_MIN_WIDTH,
        )
        height = max(
            self._titleLabel.height() + self._contentLabel.height() + 32,
            STATETOOLTIP_HEIGHT,
        )
        self.setFixedSize(width, height)

        icon_area = 28
        self._titleLabel.move(
            STATETOOLTIP_ACCENT_WIDTH + icon_area + 8, 10
        )
        self._contentLabel.move(
            STATETOOLTIP_ACCENT_WIDTH + icon_area + 8,
            10 + self._titleLabel.height() + 4,
        )
        self._contentLabel.setFixedWidth(
            width - STATETOOLTIP_ACCENT_WIDTH - icon_area - 8 - STATETOOLTIP_CLOSE_BUTTON_SIZE - 12
        )

    def _updateSizeAndPositions(self) -> None:
        self._updateContent()

    def _checkValid(self) -> bool:
        if self._destroyed:
            return False
        try:
            self.isWidgetType()
            return True
        except RuntimeError:
            self._destroyed = True
            return False

    def setTitle(self, title: str) -> None:
        if not self._checkValid():
            return
        self._title = title
        self._titleLabel.setText(title)
        self._titleLabel.adjustSize()
        self._updateSizeAndPositions()

    def setContent(self, content: str) -> None:
        if not self._checkValid():
            return
        self._content = content
        self._contentLabel.setText(content)
        self._contentLabel.adjustSize()
        self._updateSizeAndPositions()

    def setState(self, isDone: bool) -> None:
        if not self._checkValid():
            return
        self._isDone = isDone
        self.update()
        if isDone:
            QTimer.singleShot(TOOLTIP_AUTO_CLOSE_DELAY, self._fadeOut)

    def _stopTimerAndAnimation(self) -> None:
        if self._rotateTimer.isActive():
            self._rotateTimer.stop()
        if self._animation.state() == QPropertyAnimation.State.Running:
            self._animation.stop()

    def _onCloseButtonClicked(self) -> None:
        self.closed.emit()
        self._fadeOut()

    def _fadeOut(self) -> None:
        if self._isClosing or not self._checkValid():
            return
        self._isClosing = True
        self._stopTimerAndAnimation()
        self._animation.setDuration(TOOLTIP_FADE_DURATION)
        self._animation.setStartValue(1)
        self._animation.setEndValue(0)
        self._animation.finished.connect(self._onFadeOutFinished)
        self._animation.start()

    def _onFadeOutFinished(self) -> None:
        if not self._checkValid():
            return
        try:
            self._animation.finished.disconnect(self._onFadeOutFinished)
        except TypeError:
            pass
        self.closed.emit()
        self.hide()
        self.deleteLater()

    def _rotateTimerFlow(self) -> None:
        if not self._checkValid():
            return
        self._rotateAngle = (self._rotateAngle + self._deltaAngle) % 360
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        btn_size = STATETOOLTIP_CLOSE_BUTTON_SIZE
        btn_x = self.width() - btn_size - 12
        btn_y = 8
        btn_rect = QRect(btn_x, btn_y, btn_size, btn_size)
        hovered = btn_rect.contains(event.pos())
        if hovered != self._closeBtnHovered:
            self._closeBtnHovered = hovered
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        if self._closeBtnHovered:
            self._closeBtnHovered = False
            self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        btn_size = STATETOOLTIP_CLOSE_BUTTON_SIZE
        btn_x = self.width() - btn_size - 12
        btn_y = 8
        btn_rect = QRect(btn_x, btn_y, btn_size, btn_size)
        if (
            event.button() == Qt.MouseButton.LeftButton
            and btn_rect.contains(event.pos())
        ):
            self._onCloseButtonClicked()
            return
        super().mousePressEvent(event)

    def hideEvent(self, a0: Optional[QHideEvent]) -> None:
        if not self._isClosing:
            self._stopTimerAndAnimation()
        super().hideEvent(a0)

    def close(self) -> bool:
        self._isClosing = True
        self._stopTimerAndAnimation()
        return super().close()

    def deleteLater(self) -> None:
        self._destroyed = True
        self._stopTimerAndAnimation()
        if self._themeConnection is not None:
            try:
                eTheme.themeModeChanged.disconnect(self._themeConnection)
            except TypeError:
                pass
            self._themeConnection = None
        super().deleteLater()

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        if not self._checkValid():
            return
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        themeMode = self._currentTheme
        r = self._borderRadius
        w, h = self.width(), self.height()

        bg_color = eTheme.getThemeColor(
            themeMode, ElaThemeType.ThemeColor.PopupBase
        )
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, r, r)
        painter.fillPath(path, bg_color)

        accent_color = self._getAccentColor()
        painter.save()
        painter.setClipRect(0, 0, w, h)
        painter.setBrush(accent_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(
            0, 0, STATETOOLTIP_ACCENT_WIDTH, h, r, r
        )
        painter.drawRect(
            STATETOOLTIP_ACCENT_WIDTH - 2, 0,
            4, h,
        )
        painter.restore()

        text_color = eTheme.getThemeColor(
            themeMode, ElaThemeType.ThemeColor.BasicText
        )
        icon_area_x = STATETOOLTIP_ACCENT_WIDTH + 6
        icon_area_y = h // 2

        if not self._isDone:
            painter.save()
            painter.translate(icon_area_x + 14, icon_area_y)
            painter.rotate(self._rotateAngle)
            iconFont = QFont("ElaAwesome")
            iconFont.setPixelSize(STATETOOLTIP_ICON_SIZE)
            painter.setFont(iconFont)
            painter.setPen(text_color)
            painter.drawText(
                QRectF(-8, -8, 16, 16),
                Qt.AlignmentFlag.AlignCenter,
                chr(ElaIconType.IconName.ArrowRotateRight),
            )
            painter.restore()
        else:
            painter.save()
            painter.translate(icon_area_x + 14, icon_area_y)
            iconFont = QFont("ElaAwesome")
            iconFont.setPixelSize(STATETOOLTIP_ICON_SIZE)
            painter.setFont(iconFont)
            painter.setPen(accent_color)
            painter.drawText(
                QRectF(-8, -8, 16, 16),
                Qt.AlignmentFlag.AlignCenter,
                chr(ElaIconType.IconName.BadgeCheck),
            )
            painter.restore()

        self._drawCloseButton(painter)
        painter.end()

    def getSuitablePos(self) -> QPoint:
        if not self._checkValid():
            return QPoint(0, 0)
        parent = self.parent()
        if parent is None or not isinstance(parent, QWidget):
            return QPoint(0, 0)
        for i in range(10):
            dy = i * (self.height() + 16)
            pos = QPoint(parent.width() - self.width() - 24, 50 + dy)
            widget = parent.childAt(pos + QPoint(2, 2))
            if isinstance(widget, ElaStateToolTip):
                pos += QPoint(0, self.height() + 16)
            else:
                break
        return pos
