"""
工具提示组件模块。

提供两种提示组件：

- ``ToolTip``：悬浮提示组件，支持 8 种显示位置
- ``StateToolTip``：带状态指示的提示组件，支持加载中/成功/失败等状态

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
)
from PyQt5.QtWidgets import QWidget, QLabel, QGraphicsOpacityEffect

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaIconType, ElaText


TOOLTIP_BORDER_RADIUS: int = 8
TOOLTIP_SHADOW_BORDER_WIDTH: int = 3
TOOLTIP_LIGHT_BG_COLOR: str = "#ffffff"
TOOLTIP_DARK_BG_COLOR: str = "#202020"
TOOLTIP_FADE_DURATION: int = 200
TOOLTIP_AUTO_CLOSE_DELAY: int = 1000
TOOLTIP_ROTATE_TIMER_INTERVAL: int = 50
TOOLTIP_ROTATE_ANGLE_DELTA: int = 20

STATETOOLTIP_LIGHT_BG_COLOR: str = "#4cc2ff"
STATETOOLTIP_DARK_BG_COLOR: str = "#0067c0"
STATETOOLTIP_TITLE_FONT_SIZE: int = 13
STATETOOLTIP_CONTENT_FONT_SIZE: int = 12
STATETOOLTIP_MIN_WIDTH: int = 200
STATETOOLTIP_HEIGHT: int = 51
STATETOOLTIP_CLOSE_BUTTON_SIZE: int = 12
STATETOOLTIP_ICON_SIZE: int = 16


class ElaToolTipPosition(Enum):
    """提示框相对于目标 widget 的显示位置枚举。"""

    TOP = 0
    """显示在目标上方"""

    BOTTOM = 1
    """显示在目标下方"""

    LEFT = 2
    """显示在目标左侧"""

    RIGHT = 3
    """显示在目标右侧"""

    TOP_LEFT = 4
    """显示在目标左上方"""

    TOP_RIGHT = 5
    """显示在目标右上方"""

    BOTTOM_LEFT = 6
    """显示在目标左下方"""

    BOTTOM_RIGHT = 7
    """显示在目标右下方"""


class ToolTip(QWidget):
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

        font = QFont("Microsoft YaHei", 12)
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
        self, widget: QWidget, position: ElaToolTipPosition = ElaToolTipPosition.TOP
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

        if position == ElaToolTipPosition.TOP:
            x = widgetRect.center().x() - self.width() // 2
            y = widgetRect.top() - self.height() - 6
        elif position == ElaToolTipPosition.BOTTOM:
            x = widgetRect.center().x() - self.width() // 2
            y = widgetRect.bottom() + 6
        elif position == ElaToolTipPosition.LEFT:
            x = widgetRect.left() - self.width() - 6
            y = widgetRect.center().y() - self.height() // 2
        elif position == ElaToolTipPosition.RIGHT:
            x = widgetRect.right() + 6
            y = widgetRect.center().y() - self.height() // 2
        elif position == ElaToolTipPosition.TOP_LEFT:
            x = widgetRect.left()
            y = widgetRect.top() - self.height() - 6
        elif position == ElaToolTipPosition.TOP_RIGHT:
            x = widgetRect.right() - self.width()
            y = widgetRect.top() - self.height() - 6
        elif position == ElaToolTipPosition.BOTTOM_LEFT:
            x = widgetRect.left()
            y = widgetRect.bottom() + 6
        elif position == ElaToolTipPosition.BOTTOM_RIGHT:
            x = widgetRect.right() - self.width()
            y = widgetRect.bottom() + 6
        else:
            x = widgetRect.center().x() - self.width() // 2
            y = widgetRect.top() - self.height() - 6

        self.move(int(x), int(y))
        self.show()


_tooltip_dict: weakref.WeakKeyDictionary[QWidget, ToolTip] = weakref.WeakKeyDictionary()
_filter_dict: weakref.WeakKeyDictionary[QWidget, _TooltipEventFilter] = (
    weakref.WeakKeyDictionary()
)
_cleanup_filter_refs: weakref.WeakKeyDictionary[QWidget, _WidgetCleanupFilter] = (
    weakref.WeakKeyDictionary()
)


class _TooltipEventFilter(QObject):
    """事件过滤器，监听目标 widget 的进入/离开事件以显示或隐藏提示框。

    :param tooltip: 要显示的 ``ToolTip`` 实例。
    :type tooltip: ToolTip
    :param position: 提示框的显示位置。
    :type position: ElaToolTipPosition
    :param target_widget: 安装此过滤器的目标 widget。
    :type target_widget: QWidget
    """

    def __init__(
        self, tooltip: ToolTip, position: ElaToolTipPosition, target_widget: QWidget
    ) -> None:
        super().__init__(target_widget)
        self._tooltip: weakref.ref[ToolTip] = weakref.ref(tooltip)
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
    widget: QWidget, text: str, position: ElaToolTipPosition = ElaToolTipPosition.TOP
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

    tooltip = ToolTip(text, widget.window())
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


class StateToolTip(QWidget):
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
        closedSignal: 提示框被关闭时发射此信号。

    Example::

        tooltip = StateToolTip("正在加载", "请稍候...", self)
        tooltip.closedSignal.connect(on_closed)
        tooltip.show()
    """

    closedSignal = pyqtSignal()

    def __init__(
        self, title: str = "", content: str = "", parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._content = content
        self._isDone = False
        self._rotateAngle = 0
        self._deltaAngle = TOOLTIP_ROTATE_ANGLE_DELTA
        self._borderRadius = TOOLTIP_BORDER_RADIUS
        self._shadowBorderWidth = TOOLTIP_SHADOW_BORDER_WIDTH
        self._currentTheme = eTheme.getThemeMode()
        self._isClosing = False
        self._themeConnection: Any = None

        self._opacityEffect = QGraphicsOpacityEffect(self)
        self._animation = QPropertyAnimation(self._opacityEffect, b"opacity")
        self._rotateTimer = QTimer(self)

        self._titleLabel = ElaText(title, self)
        self._contentLabel = ElaText(content, self)
        self._closeButton = QWidget(self)
        self._closeButton.setFixedSize(
            STATETOOLTIP_CLOSE_BUTTON_SIZE, STATETOOLTIP_CLOSE_BUTTON_SIZE
        )
        self._closeButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self._closeButton.installEventFilter(self)

        self._themeConnection = eTheme.themeModeChanged.connect(
            self._onThemeModeChanged
        )

        self._setupUi()
        self._connectSignals()

    def _setupUi(self) -> None:
        """初始化 UI 组件和样式。"""
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setGraphicsEffect(self._opacityEffect)
        self._opacityEffect.setOpacity(1)

        self._rotateTimer.setInterval(TOOLTIP_ROTATE_TIMER_INTERVAL)
        self._rotateTimer.timeout.connect(self._rotateTimerFlow)

        self._contentLabel.setMinimumWidth(STATETOOLTIP_MIN_WIDTH)

        self._updateContent()
        self._updateSizeAndPositions()

    def _connectSignals(self) -> None:
        """启动旋转定时器。"""
        self._rotateTimer.start()

    def _onThemeModeChanged(self, mode: int) -> None:
        """主题切换时触发重绘。

        :param mode: 当前主题模式。
        :type mode: int
        """
        self._currentTheme = mode
        self.update()

    def _updateContent(self) -> None:
        """更新标题和内容文本及尺寸。"""
        self._titleLabel.setText(self._title)
        self._contentLabel.setText(self._content)

        self._titleLabel.setTextPixelSize(STATETOOLTIP_TITLE_FONT_SIZE)
        self._contentLabel.setTextPixelSize(STATETOOLTIP_CONTENT_FONT_SIZE)

        self._titleLabel.adjustSize()
        self._contentLabel.adjustSize()

        width = max(self._titleLabel.width(), self._contentLabel.width()) + 56
        self.setFixedSize(width, STATETOOLTIP_HEIGHT)

        self._titleLabel.move(32, 9)
        self._contentLabel.move(12, 27)
        self._closeButton.move(self.width() - 24, 19)

    def _updateSizeAndPositions(self) -> None:
        """重新计算内容尺寸和子组件位置。"""
        self._updateContent()

    def setTitle(self, title: str) -> None:
        """设置提示标题。

        :param title: 新的标题文本。
        :type title: str
        """
        self._title = title
        self._titleLabel.setText(title)
        self._titleLabel.adjustSize()
        self._updateSizeAndPositions()

    def setContent(self, content: str) -> None:
        """设置提示内容。

        :param content: 新的内容文本。
        :type content: str
        """
        self._content = content
        self._contentLabel.setText(content)
        self._contentLabel.adjustSize()
        self._updateSizeAndPositions()

    def setState(self, isDone: bool) -> None:
        """设置完成状态。

        设置为 ``True`` 后会切换图标为对勾并在一秒后自动淡出。

        :param isDone: 是否完成。
        :type isDone: bool
        """
        self._isDone = isDone
        self.update()
        if isDone:
            QTimer.singleShot(TOOLTIP_AUTO_CLOSE_DELAY, self._fadeOut)

    def _stopTimerAndAnimation(self) -> None:
        """停止旋转定时器和动画。"""
        if self._rotateTimer.isActive():
            self._rotateTimer.stop()
        if self._animation.state() == QPropertyAnimation.State.Running:
            self._animation.stop()

    def _onCloseButtonClicked(self) -> None:
        """关闭按钮点击处理，发射关闭信号并触发淡出。"""
        self.closedSignal.emit()
        self._fadeOut()

    def _fadeOut(self) -> None:
        """执行淡出动画并在完成后销毁组件。"""
        if self._isClosing:
            return
        self._isClosing = True
        self._stopTimerAndAnimation()
        self._animation.setDuration(TOOLTIP_FADE_DURATION)
        self._animation.setStartValue(1)
        self._animation.setEndValue(0)
        self._animation.finished.connect(self._onFadeOutFinished)
        self._animation.start()

    def _onFadeOutFinished(self) -> None:
        """淡出动画完成后的处理，隐藏并销毁组件。"""
        self._animation.finished.disconnect(self._onFadeOutFinished)
        self.hide()
        self.deleteLater()

    def _rotateTimerFlow(self) -> None:
        """旋转动画更新回调，每 50ms 增加旋转角度。"""
        self._rotateAngle = (self._rotateAngle + self._deltaAngle) % 360
        self.update()

    def eventFilter(self, a0: Optional[QObject], a1: Optional[QEvent]) -> bool:
        """事件过滤器，监听关闭按钮的鼠标点击事件。

        :param a0: 事件源对象。
        :type a0: QObject, optional
        :param a1: 事件对象。
        :type a1: QEvent, optional
        :return: 如果事件被处理则返回 ``True``。
        :rtype: bool
        """
        if a0 == self._closeButton and a1 is not None:
            if a1.type() == QEvent.Type.MouseButtonPress:
                self._onCloseButtonClicked()
                return True
        return super().eventFilter(a0, a1)

    def hideEvent(self, a0: Optional[QHideEvent]) -> None:
        """隐藏事件处理，非关闭流程中停止定时器和动画。

        :param a0: 隐藏事件。
        :type a0: QHideEvent, optional
        """
        if not self._isClosing:
            self._stopTimerAndAnimation()
        super().hideEvent(a0)

    def close(self) -> bool:
        """手动关闭提示框。

        :return: 关闭操作是否成功。
        :rtype: bool
        """
        self._isClosing = True
        self._stopTimerAndAnimation()
        return super().close()

    def deleteLater(self) -> None:
        """停止定时器和动画，断开主题信号，移除事件过滤器，调度删除。"""
        self._stopTimerAndAnimation()
        if self._themeConnection is not None:
            try:
                eTheme.themeModeChanged.disconnect(self._themeConnection)
            except TypeError:
                pass
            self._themeConnection = None
        self._closeButton.removeEventFilter(self)
        super().deleteLater()

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        """绘制状态提示框背景。

        加载状态显示旋转箭头图标，完成状态显示对勾图标。

        :param a0: 绘制事件。
        :type a0: QPaintEvent, optional
        """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        themeMode = self._currentTheme

        if themeMode == ElaThemeType.ThemeMode.Dark:
            bgColor = QColor(STATETOOLTIP_DARK_BG_COLOR)
        else:
            bgColor = QColor(STATETOOLTIP_LIGHT_BG_COLOR)
        painter.setBrush(QBrush(bgColor))
        painter.drawRoundedRect(self.rect(), self._borderRadius, self._borderRadius)

        textColor = eTheme.getThemeColor(themeMode, ElaThemeType.ThemeColor.BasicText)

        if not self._isDone:
            painter.save()
            painter.translate(19, 18)
            painter.rotate(self._rotateAngle)

            iconFont = QFont("ElaAwesome")
            iconFont.setPixelSize(STATETOOLTIP_ICON_SIZE)
            painter.setFont(iconFont)

            painter.setPen(textColor)
            painter.drawText(
                QRectF(-8, -8, 16, 16),
                Qt.AlignmentFlag.AlignCenter,
                chr(ElaIconType.IconName.ArrowRotateRight),
            )
            painter.restore()
        else:
            iconFont = QFont("ElaAwesome")
            iconFont.setPixelSize(STATETOOLTIP_ICON_SIZE)
            painter.setFont(iconFont)

            painter.setPen(textColor)
            painter.drawText(
                QRectF(11, 10, 16, 16),
                Qt.AlignmentFlag.AlignCenter,
                chr(ElaIconType.IconName.BadgeCheck),
            )

    def getSuitablePos(self) -> QPoint:
        """计算一个合适的显示位置，避免与其他 StateToolTip 重叠。

        从父级窗口右上角开始向下遍历，每次向下偏移固定距离，
        直到找到一个没有与现存 StateToolTip 重叠的位置。

        :return: 计算得到的全局坐标位置。
        :rtype: QPoint
        """
        parent = self.parent()
        if parent is None or not isinstance(parent, QWidget):
            return QPoint(0, 0)
        for i in range(10):
            dy = i * (self.height() + 16)
            pos = QPoint(parent.width() - self.width() - 24, 50 + dy)
            widget = parent.childAt(pos + QPoint(2, 2))
            if isinstance(widget, StateToolTip):
                pos += QPoint(0, self.height() + 16)
            else:
                break
        return pos
