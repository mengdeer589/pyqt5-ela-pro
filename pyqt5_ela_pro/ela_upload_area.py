"""
上传区域组件，风格参考 ElaWidgetTools 的 ElaUploadArea。

支持拖拽文件和点击选择文件。

用法::

    area = ElaUploadArea(parent=self)
    area.filesSelected.connect(lambda paths: print(f"选择了: {paths}"))
"""

from __future__ import annotations

import traceback
from typing import Optional

from PyQt5.QtCore import Qt, QRectF, QFileInfo, QEvent, pyqtSignal
from PyQt5.QtGui import (
    QPainter,
    QPainterPath,
    QPen,
    QFont,
    QPaintEvent,
    QMouseEvent,
    QEnterEvent,
)
from PyQt5.QtWidgets import QWidget, QFileDialog, QApplication
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent, QDragLeaveEvent

from PyQt5ElaWidgetTools import eTheme, ElaThemeType, ElaIconType

from .widget_base import ElaThemeWidget


class ElaUploadArea(ElaThemeWidget):
    """文件上传区域。

    支持拖拽和点击选择文件，可配置后缀过滤、大小限制、数量限制。

    :param parent: 父控件
    """

    filesSelected = pyqtSignal(list)
    fileAdded = pyqtSignal(str)
    fileRemoved = pyqtSignal(str)
    fileRejected = pyqtSignal(str, str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._title = "拖拽文件到此处"
        self._sub_title = "或点击选择文件"
        self._border_radius = 8
        self._accepted_suffixes: list[str] = []
        self._max_file_count = 0
        self._max_file_size = 0
        self._is_multiple = True
        self._dialog_title = ""
        self._mime_filter = ""
        self._file_paths: list[str] = []
        self._is_drag_over = False
        self._is_hover = False
        self._is_pressed = False

        self.setObjectName("ElaUploadArea")
        self.setMinimumSize(260, 160)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._icon_font = QFont("ElaAwesome")
        self._title_font = QFont()
        self._sub_font = QFont()
        self._fi_font = QFont("ElaAwesome")
        self._x_font = QFont("ElaAwesome")

    # ── Public API ────────────────────────────────────────

    def setTitle(self, text: str) -> None:
        """设置拖拽区标题文字。

        :param text: 标题文字
        """
        self._title = text
        self.update()

    def title(self) -> str:
        """获取拖拽区标题文字。

        :returns: 标题文字
        """
        return self._title

    def setSubTitle(self, text: str) -> None:
        """设置拖拽区副标题文字。

        :param text: 副标题文字
        """
        self._sub_title = text
        self.update()

    def subTitle(self) -> str:
        """获取拖拽区副标题文字。

        :returns: 副标题文字
        """
        return self._sub_title

    def setBorderRadius(self, r: int) -> None:
        """设置圆角半径。

        :param r: 圆角半径（像素）
        """
        self._border_radius = r
        self.update()

    def borderRadius(self) -> int:
        """获取圆角半径。

        :returns: 圆角半径（像素）
        """
        return self._border_radius

    def setAcceptedSuffixes(self, suffixes: list[str]) -> None:
        """设置可接受的文件后缀列表。

        :param suffixes: 后缀列表，如 ``[".txt", ".py"]``
        """
        self._accepted_suffixes = list(suffixes)

    def acceptedSuffixes(self) -> list[str]:
        """获取可接受的文件后缀列表。

        :returns: 后缀列表
        """
        return self._accepted_suffixes

    def setMaxFileCount(self, n: int) -> None:
        """设置最大文件数量（0 表示不限制）。

        :param n: 最大数量
        """
        self._max_file_count = n

    def maxFileCount(self) -> int:
        """获取最大文件数量。

        :returns: 最大数量
        """
        return self._max_file_count

    def setMaxFileSize(self, size: int) -> None:
        """设置单个文件最大字节数（0 表示不限制）。

        :param size: 最大字节数
        """
        self._max_file_size = size

    def maxFileSize(self) -> int:
        """获取单个文件最大字节数。

        :returns: 最大字节数
        """
        return self._max_file_size

    def setMultiple(self, multi: bool) -> None:
        """设置是否允许选择多个文件。

        :param multi: 是否多选
        """
        self._is_multiple = multi

    def isMultiple(self) -> bool:
        """当前是否允许选择多个文件。

        :returns: 多选状态
        """
        return self._is_multiple

    def setDialogTitle(self, title: str) -> None:
        """设置文件选择对话框标题。

        :param title: 对话框标题
        """
        self._dialog_title = title

    def dialogTitle(self) -> str:
        """获取文件选择对话框标题。

        :returns: 对话框标题
        """
        return self._dialog_title

    def setAcceptedMimeFilter(self, filter_str: str) -> None:
        """设置文件选择对话框的 MIME 过滤字符串。

        :param filter_str: MIME 过滤字符串，如 ``"Text (*.txt)"``
        """
        self._mime_filter = filter_str

    def acceptedMimeFilter(self) -> str:
        """获取文件选择对话框的 MIME 过滤字符串。

        :returns: MIME 过滤字符串
        """
        return self._mime_filter

    def selectedFiles(self) -> list[str]:
        """获取已选择的文件路径列表。

        :returns: 文件路径列表
        """
        return list(self._file_paths)

    def clearFiles(self) -> None:
        """清空已选择的文件列表。"""
        self._file_paths.clear()
        self.update()

    # ── Internal ──────────────────────────────────────────

    def _onThemeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self._theme_mode = mode
        self.update()

    def _validateFile(self, file_path: str) -> tuple[bool, str]:
        info = QFileInfo(file_path)
        if not info.exists():
            return False, "文件不存在"
        if self._accepted_suffixes:
            suffix = info.suffix().lower()
            if suffix not in [s.lower() for s in self._accepted_suffixes]:
                return False, f"不支持的文件类型: {suffix}"
        if self._max_file_size > 0 and info.size() > self._max_file_size:
            return False, "文件过大"
        if self._max_file_count > 0 and len(self._file_paths) >= self._max_file_count:
            return False, "已达到最大文件数量"
        if file_path in self._file_paths:
            return False, "文件已存在"
        return True, ""

    def _addFiles(self, paths: list[str]) -> None:
        added: list[str] = []
        for p in paths:
            ok, reason = self._validateFile(p)
            if ok:
                self._file_paths.append(p)
                added.append(p)
                self.fileAdded.emit(p)
            else:
                self.fileRejected.emit(p, reason)
        if added:
            self.filesSelected.emit(self._file_paths)
            self.update()

    def _removeFile(self, index: int) -> None:
        if 0 <= index < len(self._file_paths):
            removed = self._file_paths.pop(index)
            self.fileRemoved.emit(removed)
            self.filesSelected.emit(self._file_paths)
            self.update()

    def _openFileDialog(self) -> None:
        title = self._dialog_title if self._dialog_title else "选择文件"
        filter_str = self._mime_filter
        if not filter_str and self._accepted_suffixes:
            patterns = ["*." + s for s in self._accepted_suffixes]
            filter_str = f"允许的文件 ({' '.join(patterns)})"
        if self._is_multiple:
            files, _ = QFileDialog.getOpenFileNames(self, title, "", filter_str)
        else:
            f, _ = QFileDialog.getOpenFileName(self, title, "", filter_str)
            files = [f] if f else []
        if files:
            self._addFiles(files)

    # ── Events ────────────────────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            self._is_drag_over = True
            self.update()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()

    def dragLeaveEvent(self, _event: QDragLeaveEvent) -> None:
        self._is_drag_over = False
        self.update()

    def dropEvent(self, event: QDropEvent) -> None:
        event.accept()
        self._is_drag_over = False
        paths: list[str] = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                paths.append(url.toLocalFile())
        if paths:
            if not self._is_multiple and len(paths) > 1:
                paths = paths[:1]
            self._addFiles(paths)
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._is_pressed = True

        # Check if clicking on an X button to remove a file
        if self._file_paths:
            start_y = 46
            lh = 22
            max_display = min(
                len(self._file_paths), max(1, (self.height() - start_y - 10) // lh)
            )
            cy = event.pos().y()
            cx = event.pos().x()
            for i in range(max_display):
                iy = start_y + i * lh
                if iy <= cy < iy + lh and self.width() - 28 <= cx <= self.width() - 12:
                    self._removeFile(i)
                    self._is_pressed = False
                    return
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._is_pressed and self.rect().contains(event.pos()):
            self._openFileDialog()
        self._is_pressed = False
        self.update()

    def enterEvent(self, _event: QEnterEvent) -> None:
        self._is_hover = True
        self.update()

    def leaveEvent(self, _event: QEvent) -> None:
        self._is_hover = False
        self.update()

    # ── Paint ─────────────────────────────────────────────

    def paintEvent(self, _event: QPaintEvent) -> None:
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

            mode = self._theme_mode
            br = self._border_radius
            rect = QRectF(1, 1, self.width() - 2, self.height() - 2)
            path = QPainterPath()
            path.addRoundedRect(rect, br, br)

            if self._is_drag_over:
                painter.setPen(
                    QPen(
                        eTheme.getThemeColor(
                            mode, ElaThemeType.ThemeColor.PrimaryNormal
                        ),
                        2,
                        Qt.PenStyle.DashLine,
                    )
                )
                painter.setBrush(
                    eTheme.getThemeColor(
                        mode, ElaThemeType.ThemeColor.BasicBaseDeepAlpha
                    )
                )
            elif self._is_hover:
                painter.setPen(
                    QPen(
                        eTheme.getThemeColor(
                            mode, ElaThemeType.ThemeColor.BasicBorderHover
                        ),
                        2,
                        Qt.PenStyle.DashLine,
                    )
                )
                painter.setBrush(
                    eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicHoverAlpha)
                )
            else:
                painter.setPen(
                    QPen(
                        eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBorder),
                        2,
                        Qt.PenStyle.DashLine,
                    )
                )
                painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

            cy = self.height() // 2

            if not self._file_paths:
                self._icon_font.setPixelSize(36)
                painter.setFont(self._icon_font)
                painter.setPen(
                    eTheme.getThemeColor(
                        mode,
                        ElaThemeType.ThemeColor.PrimaryNormal
                        if self._is_drag_over
                        else ElaThemeType.ThemeColor.BasicTextNoFocus,
                    )
                )
                painter.drawText(
                    QRectF(0, cy - 48, self.width(), 40),
                    Qt.AlignmentFlag.AlignCenter,
                    chr(int(ElaIconType.IconName.CloudArrowUp)),
                )

                self._title_font.setPixelSize(15)
                self._title_font.setBold(True)
                painter.setFont(self._title_font)
                painter.setPen(
                    eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicText)
                )
                painter.drawText(
                    QRectF(0, cy, self.width(), 24),
                    Qt.AlignmentFlag.AlignCenter,
                    self._title,
                )

                self._sub_font.setPixelSize(12)
                painter.setFont(self._sub_font)
                painter.setPen(
                    eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicTextNoFocus)
                )
                painter.drawText(
                    QRectF(0, cy + 26, self.width(), 20),
                    Qt.AlignmentFlag.AlignCenter,
                    self._sub_title,
                )
            else:
                self._icon_font.setPixelSize(24)
                painter.setFont(self._icon_font)
                painter.setPen(
                    eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicTextNoFocus)
                )
                painter.drawText(
                    QRectF(0, 12, self.width(), 28),
                    Qt.AlignmentFlag.AlignCenter,
                    chr(int(ElaIconType.IconName.CloudArrowUp)),
                )

                start_y = 46
                lh = 22
                max_display = min(
                    len(self._file_paths), max(1, (self.height() - start_y - 10) // lh)
                )

                for i in range(max_display):
                    info = QFileInfo(self._file_paths[i])
                    display = info.fileName()

                    # File icon
                    self._fi_font.setPixelSize(12)
                    painter.setFont(self._fi_font)
                    painter.setPen(
                        eTheme.getThemeColor(
                            mode, ElaThemeType.ThemeColor.PrimaryNormal
                        )
                    )
                    painter.drawText(
                        QRectF(12, start_y + i * lh, 16, lh),
                        Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter,
                        chr(int(ElaIconType.IconName.File)),
                    )

                    # Filename
                    painter.setFont(QApplication.font())
                    painter.setPen(
                        eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicText)
                    )
                    name_r = QRectF(32, start_y + i * lh, self.width() - 60, lh)
                    elided = painter.fontMetrics().elidedText(
                        display, Qt.TextElideMode.ElideMiddle, int(name_r.width())
                    )
                    painter.drawText(
                        name_r,
                        Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                        elided,
                    )

                    # X button
                    self._x_font.setPixelSize(10)
                    painter.setFont(self._x_font)
                    painter.setPen(
                        eTheme.getThemeColor(
                            mode, ElaThemeType.ThemeColor.BasicTextNoFocus
                        )
                    )
                    painter.drawText(
                        QRectF(self.width() - 28, start_y + i * lh, 16, lh),
                        Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter,
                        chr(int(ElaIconType.IconName.Xmark)),
                    )

                if len(self._file_paths) > max_display:
                    painter.setFont(QApplication.font())
                    painter.setPen(
                        eTheme.getThemeColor(
                            mode, ElaThemeType.ThemeColor.BasicTextNoFocus
                        )
                    )
                    painter.drawText(
                        QRectF(0, start_y + max_display * lh, self.width(), lh),
                        Qt.AlignmentFlag.AlignCenter,
                        f"...还有 {len(self._file_paths) - max_display} 个文件",
                    )
        except Exception:
            print(traceback.format_exc())
