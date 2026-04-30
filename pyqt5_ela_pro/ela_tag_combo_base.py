"""
具名组合框共享基础设施。

为 ElaTagBox / ElaTagMultiBox / ElaTagSearchBox / ElaTagSearchMultiBox
提供共用的主题色方法、Qt 属性、动画逻辑和 paintEvent 辅助方法。
"""

from __future__ import annotations

from typing import Protocol

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

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaIcon, ElaIconType


class _TagBoxThemeMixin:
    """标签框主题色方法混入类。"""

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


class _TagBoxAnimMixin:
    """具名组合框动画与属性共享基类。

    提供 expandMarkWidth / expandIconRotate 属性、
    动画初始化、setTitle / title 方法及主题切换支持。
    子类必须在 __init__ 中调用 self._tag_box_init(title)。
    """

    def _tag_box_init(self, title: str = "") -> None:
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

        eTheme.themeModeChanged.connect(self._on_tag_theme_changed)

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

    def setTitle(self, title: str) -> None:
        self._title_text = title
        self.update()

    def title(self) -> str:
        return self._title_text

    def _on_tag_theme_changed(self, *args) -> None:
        self.update()

    def _animate_popup_open(self) -> None:
        """运行展开动画（底部主题色条 + 箭头旋转），供子类 showPopup 调用。"""
        if self.count() == 0:
            return
        target_mark_width = self.width() / 2 - 9
        self._mark_animation.setStartValue(self._expand_mark_width)
        self._mark_animation.setEndValue(target_mark_width)
        self._mark_animation.start()

        self._rotate_animation.setStartValue(self._expand_icon_rotate)
        self._rotate_animation.setEndValue(-180.0)
        self._rotate_animation.start()

    def _animate_popup_close(self) -> None:
        """运行收起动画，供子类 hidePopup 调用。"""
        self._mark_animation.setStartValue(self._expand_mark_width)
        self._mark_animation.setEndValue(0.0)
        self._mark_animation.start()

        self._rotate_animation.setStartValue(self._expand_icon_rotate)
        self._rotate_animation.setEndValue(0.0)
        self._rotate_animation.start()

    def _tag_box_delete_later(self) -> None:
        try:
            eTheme.themeModeChanged.disconnect(self._on_tag_theme_changed)
        except (TypeError, RuntimeError):
            pass


# ── 多选组合框共享辅助函数 ───────────────────────────────────────


def _pre_init_popup(widget) -> None:
    """初始化弹出列表的最小高度。"""
    view = widget.view()
    if view:
        view.setMinimumHeight(200)


def _get_target_mark_width(widget) -> float:
    """根据选中比例计算底部主题色条的目标宽度。"""
    selected_count = len(widget.getCurrentSelection())
    total_count = widget.count()
    if total_count <= 0:
        return 0.0
    return (widget.width() / 2 - 9) * selected_count / total_count


# ── paint 辅助函数 ──────────────────────────────────────────────


class _TagBoxWidgetProtocol(Protocol):
    """_draw_tag_background 所需的 widget 接口约束"""
    def _getBackgroundColor(self) -> QColor: ...
    def _getTitleColor(self) -> QColor: ...
    def _getBorderColor(self) -> QColor: ...
    def width(self) -> int: ...
    def height(self) -> int: ...


def _draw_tag_background(
    painter: QPainter, widget: _TagBoxWidgetProtocol, shadow_border: int = 3
) -> tuple[QRect, QColor, QColor]:
    """绘制圆角背景和底部分隔线。返回 (content_rect, text_color, border_color)。"""
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    content_rect = QRect(
        shadow_border,
        shadow_border,
        widget.width() - 2 * shadow_border,
        widget.height() - 2 * shadow_border,
    )

    bg_color = widget._getBackgroundColor()
    text_color = widget._getTitleColor()
    border_color = widget._getBorderColor()

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

    return content_rect, text_color, border_color


def _draw_tag_title(
    painter: QPainter,
    content_rect: QRect,
    title_text: str,
    title_font_size: int,
    text_color: QColor,
    font,
) -> QRect:
    """绘制标题文本，返回标题区域 QRect。"""
    metrics = QFontMetrics(font)
    title_width = metrics.horizontalAdvance(title_text) + 20

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
    title_font = QFont(font)
    title_font.setPixelSize(title_font_size)
    painter.setFont(title_font)
    painter.setPen(text_color)
    painter.drawText(
        QRectF(title_rect.adjusted(10, 0, -10, 0)),
        title_text,
        title_option,
    )

    return title_rect


def _draw_tag_arrow(
    painter: QPainter,
    content_rect: QRect,
    text_color: QColor,
    rotate_angle: float,
) -> None:
    """绘制旋转箭头图标。"""
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
    transform.rotate(rotate_angle)
    transform.translate(-icon_pixmap.width() / 2, -icon_pixmap.height() / 2)
    painter.setTransform(transform)
    painter.drawPixmap(0, 0, icon_pixmap)
    painter.restore()


def _draw_tag_mark(
    painter: QPainter,
    widget,
    mark_width: float,
) -> None:
    """绘制底部主题色标记线。"""
    if mark_width > 0:
        mark_color = eTheme.getThemeColor(
            eTheme.getThemeMode(), ElaThemeType.ThemeColor.PrimaryNormal
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(mark_color)
        mark_rect = QRectF(
            widget.width() / 2 - mark_width,
            widget.height() - 3,
            mark_width * 2,
            3,
        )
        mark_path = QPainterPath()
        mark_path.addRoundedRect(mark_rect, 1.5, 1.5)
        painter.drawPath(mark_path)


def _draw_single_value_text(
    painter: QPainter,
    content_rect: QRect,
    title_rect: QRect,
    current_text: str,
) -> None:
    """绘制单选组合框的值文本。"""
    if not current_text:
        return
    text_left = title_rect.right()
    text_width = content_rect.right() - 30 - text_left
    if text_width <= 0:
        return
    text_rect = QRect(
        text_left,
        content_rect.top(),
        text_width,
        content_rect.height(),
    )
    text_option = QTextOption()
    text_option.setWrapMode(QTextOption.NoWrap)
    text_option.setAlignment(
        Qt.Alignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
    )
    painter.drawText(QRectF(text_rect), current_text, text_option)


def _draw_multi_value_text(
    painter: QPainter,
    content_rect: QRect,
    title_rect: QRect,
    selections: list[str],
    max_show: int = 3,
) -> None:
    """绘制多选组合框的值文本（逗号分隔，最多显示 max_show 项）。"""
    if not selections:
        return
    if len(selections) > max_show:
        display_text = ",".join(selections[:max_show]) + "..."
    else:
        display_text = ",".join(selections)
    text_left = title_rect.right()
    text_width = content_rect.right() - 30 - text_left
    if text_width <= 0:
        return
    text_rect = QRect(
        text_left,
        content_rect.top(),
        text_width,
        content_rect.height(),
    )
    text_option = QTextOption()
    text_option.setWrapMode(QTextOption.NoWrap)
    text_option.setAlignment(
        Qt.Alignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
    )
    painter.drawText(QRectF(text_rect), display_text, text_option)
