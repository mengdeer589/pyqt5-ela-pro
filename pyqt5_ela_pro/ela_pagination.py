"""
分页组件，风格参考 ElaWidgetTools 的 ElaPagination。

支持页码导航、省略号、跳转输入框。

用法::

    pag = ElaPagination(parent=self)
    pag.setTotalPages(20)
    pag.setJumperVisible(True)
    pag.currentPageChanged.connect(lambda p: print(f"页码: {p}"))
"""

from __future__ import annotations

import traceback
from typing import Optional

from PyQt5.QtCore import Qt, QRect, QRectF, QSize, pyqtSignal
from PyQt5.QtGui import (
    QPainter,
    QPainterPath,
    QFont,
    QPaintEvent,
    QMouseEvent,
    QIntValidator,
)
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaLineEdit

from ._internal import _ThemeAwareMixin


class ElaPagination(_ThemeAwareMixin, QWidget):
    """分页组件。

    :param parent: 父控件
    """

    currentPageChanged = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._current_page = 1
        self._total_pages = 1
        self._button_size = 28
        self._pager_count = 11
        self._jumper_visible = False
        self._hover_index = -1

        self.setObjectName("ElaPagination")
        self.setMouseTracking(True)
        self.setFixedHeight(self._button_size + 8)
        self._icon_font = QFont("ElaAwesome")

        self._jumper_edit = ElaLineEdit(self)
        self._jumper_edit.setFixedHeight(self._button_size)
        self._jumper_edit.setPlaceholderText("页码")
        self._jumper_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._jumper_edit.setValidator(QIntValidator(1, 9999, self._jumper_edit))
        self._jumper_edit.setVisible(False)
        self._jumper_edit.returnPressed.connect(self._onJumperEntered)

        self._theme_mode = eTheme.getThemeMode()

    def setCurrentPage(self, n: int) -> None:
        if n != self._current_page and 1 <= n <= self._total_pages:
            self._current_page = n
            self.currentPageChanged.emit(n)
            self.update()

    def currentPage(self) -> int:
        return self._current_page

    def setTotalPages(self, n: int) -> None:
        self._total_pages = max(1, n)
        if self._current_page > self._total_pages:
            self._current_page = self._total_pages
        self.updateGeometry()
        self.update()

    def totalPages(self) -> int:
        return self._total_pages

    def setButtonSize(self, n: int) -> None:
        self._button_size = n
        self.setFixedHeight(n + 8)
        self.updateGeometry()
        self.update()

    def buttonSize(self) -> int:
        return self._button_size

    def setPagerCount(self, n: int) -> None:
        self._pager_count = n
        self.update()

    def pagerCount(self) -> int:
        return self._pager_count

    def setJumperVisible(self, v: bool) -> None:
        self._jumper_visible = v
        self._jumper_edit.setVisible(v)
        self.updateGeometry()
        self.update()

    def isJumperVisible(self) -> bool:
        return self._jumper_visible

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    # ── Internal ──────────────────────────────────────────

    def _getVisiblePages(self) -> list[int]:
        total = self._total_pages
        cur = self._current_page
        pc = self._pager_count

        if total <= 0:
            return []
        if total <= pc:
            return list(range(1, total + 1))

        half = (pc - 2) // 2
        left_ellipsis = cur > half + 2
        right_ellipsis = cur < total - half - 1

        pages: list[int] = []
        if not left_ellipsis and right_ellipsis:
            for i in range(1, pc - 1):
                pages.append(i)
            pages.append(-1)  # right ellipsis
            pages.append(total)
        elif left_ellipsis and not right_ellipsis:
            pages.append(1)
            pages.append(-3)  # left ellipsis
            for i in range(total - (pc - 3), total + 1):
                pages.append(i)
        else:
            pages.append(1)
            pages.append(-3)
            side = (pc - 4) // 2
            for i in range(cur - side, cur + side + 1):
                pages.append(i)
            pages.append(-1)
            pages.append(total)
        return pages

    def _getButtonRects(self) -> list[tuple[QRect, int]]:
        rects: list[tuple[QRect, int]] = []
        size = self._button_size
        spacing = 4
        x = 0
        y = 4

        rects.append((QRect(x, y, size, size), 0))  # prev
        x += size + spacing

        for page in self._getVisiblePages():
            rects.append((QRect(x, y, size, size), page))
            x += size + spacing

        rects.append((QRect(x, y, size, size), -2))  # next
        return rects

    def _updateJumperPosition(self) -> None:
        if not self._jumper_edit.isVisible():
            return
        rects = self._getButtonRects()
        if not rects:
            return
        last = rects[-1][0]
        jx = last.x() + last.width() + 12
        jw = 110
        jh = self._button_size
        jy = (self.height() - jh) // 2
        self._jumper_edit.setGeometry(jx, jy, jw, jh)

    def _onJumperEntered(self) -> None:
        text = self._jumper_edit.text().strip()
        if not text:
            return
        try:
            page = int(text)
        except ValueError:
            return
        if 1 <= page <= self._total_pages and page != self._current_page:
            self._current_page = page
            self.currentPageChanged.emit(page)
            self.update()
        self._jumper_edit.clear()

    # ── Events ───────────────────────────────────────────

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        old = self._hover_index
        self._hover_index = -1
        for i, (r, _) in enumerate(self._getButtonRects()):
            if r.contains(event.pos()):
                self._hover_index = i
                break
        if old != self._hover_index:
            self.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
        for r, val in self._getButtonRects():
            if r.contains(event.pos()):
                new_page = self._current_page
                if val == 0 and self._current_page > 1:
                    new_page = self._current_page - 1
                elif val == -2 and self._current_page < self._total_pages:
                    new_page = self._current_page + 1
                elif val == -1:
                    new_page = min(
                        self._current_page + self._pager_count - 2, self._total_pages
                    )
                elif val == -3:
                    new_page = max(self._current_page - (self._pager_count - 2), 1)
                elif val > 0:
                    new_page = val

                if new_page != self._current_page:
                    self._current_page = new_page
                    self.currentPageChanged.emit(new_page)
                    self.update()
                break
        super().mousePressEvent(event)

    # ── Paint ─────────────────────────────────────────────

    def paintEvent(self, event: QPaintEvent) -> None:
        try:
            self._updateJumperPosition()
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

            mode = self._theme_mode
            primary = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.PrimaryNormal)
            base = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBase)
            hover = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicHover)
            disable_bg = eTheme.getThemeColor(
                mode, ElaThemeType.ThemeColor.BasicDisable
            )
            text = eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicText)
            text_dis = eTheme.getThemeColor(
                mode, ElaThemeType.ThemeColor.BasicTextDisable
            )

            for i, (r, val) in enumerate(self._getButtonRects()):
                is_current = val > 0 and val == self._current_page
                is_disabled = (val == 0 and self._current_page <= 1) or (
                    val == -2 and self._current_page >= self._total_pages
                )
                is_hovered = i == self._hover_index

                painter.setPen(Qt.PenStyle.NoPen)
                if is_current:
                    painter.setBrush(primary)
                elif is_disabled:
                    painter.setBrush(disable_bg)
                elif is_hovered:
                    painter.setBrush(hover)
                else:
                    painter.setBrush(base)

                path = QPainterPath()
                path.addRoundedRect(QRectF(r), 6, 6)
                painter.drawPath(path)

                if is_current:
                    painter.setPen(Qt.GlobalColor.white)
                elif is_disabled:
                    painter.setPen(text_dis)
                else:
                    painter.setPen(text)

                if val == 0 or val == -2 or val in (-1, -3):
                    self._icon_font.setPixelSize(16)
                    painter.setFont(self._icon_font)
                    icon_char = (
                        chr(0xEA84)
                        if val == 0
                        else chr(0xEA85)
                        if val == -2
                        else chr(0xEC4D)
                    )
                    painter.drawText(r, Qt.AlignmentFlag.AlignCenter, icon_char)
                else:
                    tf = self.font()
                    tf.setPixelSize(14)
                    painter.setFont(tf)
                    painter.drawText(r, Qt.AlignmentFlag.AlignCenter, str(val))
        except Exception:
            print(traceback.format_exc())

    def sizeHint(self) -> QSize:
        rects = self._getButtonRects()
        tw = rects[-1][0].x() + rects[-1][0].width() if rects else 0
        if self._jumper_visible:
            tw += 12 + 110
        return QSize(tw, self._button_size + 8)
