"""
具名可搜索多选下拉框组件。

带有标题标签的可搜索多选下拉框，继承自 ElaSearchMultiBox，
支持汉字拼音首字母搜索。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter, QPaintEvent
from PyQt5.QtWidgets import QWidget

from .combo_box import ElaSearchMultiBox
from .ela_tag_combo_base import (
    _TagBoxThemeMixin, _TagBoxAnimMixin,
    _pre_init_popup, _get_target_mark_width,
    _paint_tag_multi,
)
from ._internal import _adjust_combobox_popup


class ElaTagSearchMultiBox(_TagBoxThemeMixin, _TagBoxAnimMixin, ElaSearchMultiBox):
    """具名可搜索多选下拉框。

    带有标题标签的可搜索多选下拉框，支持汉字拼音首字母搜索。
    继承自 ElaSearchMultiBox，使用胶囊样式。

    :param title: 标题文字
    :param parent: 父控件

    Example::

        combo = ElaTagSearchMultiBox(title="语言", parent=parent)
        combo.addItems(["Python", "C++", "JavaScript", "上海", "北京"])
        combo.setCurrentSelection(["Python", "上海"])
    """

    def __init__(
        self,
        title: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._tag_box_init(title)
        self.setMaxVisibleItems(10)
        QTimer.singleShot(0, lambda: _pre_init_popup(self))

    def showPopup(self) -> None:
        if self.count() == 0:
            return
        self._expand_mark_width = _get_target_mark_width(self)
        super().showPopup()
        _adjust_combobox_popup(self)
        if self._searchEdit:
            self._applySearchEditPalette()

    def hidePopup(self) -> None:
        self._expand_mark_width = 0.0
        super().hidePopup()

    def setCurrentSelection(self, selection):
        super().setCurrentSelection(selection)
        self.update()

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        _paint_tag_multi(painter, self)

    def deleteLater(self) -> None:
        self._tag_box_delete_later()
        super().deleteLater()
