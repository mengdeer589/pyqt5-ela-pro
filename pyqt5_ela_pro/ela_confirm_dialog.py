"""
确认对话框组件，风格参考 ElaWidgetTools 的 ElaMessageDialog。

全 QPainter 自定义绘制，包含标题、正文、确认/取消图标按钮。
支持深浅色主题自适应。

用法::

    from pyqt5_ela_pro import ElaConfirmDialog

    # 模态调用
    if ElaConfirmDialog.show(self, "提示", "确定要删除吗？"):
        # 用户点击了确认

    # 信号方式
    dlg = ElaConfirmDialog(self)
    dlg.setTitle("提示")
    dlg.setContent("确定要退出吗？")
    dlg.confirmed.connect(lambda: print("确认"))
    dlg.cancelled.connect(lambda: print("取消"))
    dlg.show()
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt, QPoint, QRect, QTimer, pyqtSignal, QEvent
from PyQt5.QtGui import QColor, QPainter, QPen, QPaintEvent, QMouseEvent, QFont
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout

from PyQt5ElaWidgetTools import eTheme, ElaThemeType

from ._internal import _ThemeAwareMixin
from .widget_base import ElaThemeWidget


#: 弹框与锚点组件之间的间距（像素）
_CONFIRM_DIALOG_GAP = 5


class _ElaConfirmButton(ElaThemeWidget):
    """确认/取消图标按钮，全 QPainter 自绘。"""

    clicked = pyqtSignal()

    TYPE_CONFIRM = 0
    TYPE_CANCEL = 1

    def __init__(self, button_type: int, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._type = button_type
        self._is_hovered = False
        self._is_pressed = False
        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    def enterEvent(self, event: QEvent) -> None:
        self._is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._is_hovered = False
        self._is_pressed = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._is_pressed:
            self._is_pressed = False
            self.update()
            if self.rect().contains(event.pos()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._is_pressed:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 20))
        elif self._is_hovered:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 10))

        color = eTheme.getThemeColor(
            self._theme_mode, ElaThemeType.ThemeColor.BasicText
        )
        painter.setPen(
            QPen(
                color,
                2,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )

        cx = self.width() // 2
        cy = self.height() // 2

        if self._type == self.TYPE_CONFIRM:
            painter.drawLine(cx - 6, cy, cx - 2, cy + 4)
            painter.drawLine(cx - 2, cy + 4, cx + 6, cy - 4)
        else:
            off = 5
            painter.drawLine(cx - off, cy - off, cx + off, cy + off)
            painter.drawLine(cx - off, cy + off, cx + off, cy - off)


class ElaConfirmDialog(_ThemeAwareMixin, QDialog):
    """确认对话框。

    全 QPainter 自绘，带有标题、正文和两个图标按钮（确认 ✓ / 取消 ✕）。
    支持深浅色主题自适应。

    :param parent: 父组件
    """

    confirmed = pyqtSignal()
    cancelled = pyqtSignal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        position: str = "bottom",
    ) -> None:
        super().__init__(parent)

        self._title = "标题"
        self._content = ""
        self._border_radius = 8
        self._title_pixel_size = 15
        self._content_pixel_size = 13
        self._position = position  # "bottom" or "top"

        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(280, 150)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._confirm_btn = _ElaConfirmButton(_ElaConfirmButton.TYPE_CONFIRM, self)
        self._cancel_btn = _ElaConfirmButton(_ElaConfirmButton.TYPE_CANCEL, self)
        self._confirm_btn.clicked.connect(self._onConfirm)
        self._cancel_btn.clicked.connect(self._onCancel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0)
        btn_layout.addWidget(self._confirm_btn, 1)
        btn_layout.addWidget(self._cancel_btn, 1)
        layout.addLayout(btn_layout)

        self._onThemeChanged(eTheme.getThemeMode())

    # ── Public API ────────────────────────────────────────

    def setTitle(self, title: str) -> None:
        """设置对话框标题文字。

        :param title: 标题文字
        """
        self._title = title
        self.update()

    def title(self) -> str:
        """获取对话框标题文字。

        :returns: 标题文字
        """
        return self._title

    def setContent(self, content: str) -> None:
        """设置对话框正文内容。

        :param content: 正文文字
        """
        self._content = content
        self.update()

    def content(self) -> str:
        """获取对话框正文内容。

        :returns: 正文文字
        """
        return self._content

    def setBorderRadius(self, radius: int) -> None:
        """设置窗口圆角半径。

        :param radius: 圆角半径（像素）
        """
        self._border_radius = radius
        self.update()

    def borderRadius(self) -> int:
        """获取窗口圆角半径。

        :returns: 圆角半径（像素）
        """
        return self._border_radius

    def setPosition(self, position: str) -> None:
        """设置弹窗位置，``"bottom"`` 在父组件下方，``"top"`` 在父组件上方。

        :param position: ``"bottom"`` 或 ``"top"``
        """
        self._position = position
        self.update()

    def position(self) -> str:
        """获取弹窗位置。

        :returns: ``"bottom"`` 或 ``"top"``
        """
        return self._position

    def show(
        self,
        title: str = "",
        message: str = "",
        position: str = "bottom",
    ) -> bool:
        """模态显示确认对话框（类调用）或普通显示（实例调用）。

        类调用：``ElaConfirmDialog.show(parent, title, message, position)``
        返回 ``True`` 表示点击了确认，``False`` 表示取消。
        实例调用：``dlg.show()`` 与 ``QDialog.show`` 行为一致，返回 ``None``。

        :param title: 标题
        :param message: 正文内容
        :param position: 弹窗位置，``"bottom"`` 在下方 / ``"top"`` 在上方
        :return: 类调用时返回是否确认；实例调用时返回 None
        """
        if isinstance(self, ElaConfirmDialog):
            super().show()
            return False
        parent = self
        dialog = ElaConfirmDialog(parent, position=position)
        dialog.setTitle(title)
        dialog.setContent(message)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        result = dialog.exec_()
        return result == QDialog.DialogCode.Accepted

    # ── Internal ──────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        if self.parent():
            QTimer.singleShot(0, self._positionDialog)

    def _positionDialog(self) -> None:
        """把弹框摆到锚点组件附近，并收敛进锚点所在屏幕的工作区。

        ``"bottom"`` 放在锚点下方、``"top"`` 放在上方；一侧放不下翻到另一侧，
        最后水平 / 垂直夹回工作区（与 :meth:`ElaToolTip.showAt` 同一套规则）。
        锚点贴着窗口 / 屏幕边缘时（例如聊天输入区）才不会弹出到屏幕外。

        回归：原先只算「锚点底边 + 5」不做兜底，锚点撑满窗口（整块聊天组件 /
        最大化窗口）时 ``y`` 直接落到屏幕外，弹框整块不可见。
        """
        anchor = self.parent()
        if anchor is None:
            return
        try:
            anchor_rect = QRect(anchor.mapToGlobal(QPoint(0, 0)), anchor.size())
        except (RuntimeError, AttributeError):
            return

        gap = _CONFIRM_DIALOG_GAP
        above = self._position == "top"
        x = anchor_rect.left() - 10
        if above:
            y = anchor_rect.top() - self.height() - gap
        else:
            y = anchor_rect.bottom() + gap + 1

        screen = QApplication.screenAt(anchor_rect.center())
        if screen is None:
            screen = QApplication.primaryScreen()
        if screen is not None:
            area = screen.availableGeometry()
            if above and y < area.top():
                y = anchor_rect.bottom() + gap + 1
            elif not above and y + self.height() - 1 > area.bottom():
                y = anchor_rect.top() - self.height() - gap
            x = max(area.left(), min(x, area.right() - self.width() + 1))
            y = max(area.top(), min(y, area.bottom() - self.height() + 1))
        self.move(int(x), int(y))

    def _onConfirm(self) -> None:
        self.confirmed.emit()
        self.accept()

    def _onCancel(self) -> None:
        self.cancelled.emit()
        self.reject()

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    # ── Paint ─────────────────────────────────────────────

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        mode = self._theme_mode
        w = self.width()
        h = self.height()
        br = self._border_radius

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBase))
        painter.drawRoundedRect(self.rect(), br, br)

        # Title
        title_font = self.font()
        title_font.setPixelSize(self._title_pixel_size)
        title_font.setWeight(QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.setPen(eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicText))
        painter.drawText(
            QRect(15, 15, w - 30, 25),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
            self._title,
        )

        # Content
        content_font = self.font()
        content_font.setPixelSize(self._content_pixel_size)
        content_font.setWeight(QFont.Weight.Normal)
        painter.setFont(content_font)
        content_h = h - 40 - 45 - 15
        if content_h > 0:
            painter.drawText(
                QRect(15, 45, w - 30, content_h),
                Qt.TextFlag.TextWordWrap
                | Qt.AlignmentFlag.AlignLeft
                | Qt.AlignmentFlag.AlignTop,
                self._content,
            )

        # Separator line above buttons
        painter.setPen(
            QPen(eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBorder), 1)
        )
        painter.drawLine(0, h - 40, w, h - 40)
