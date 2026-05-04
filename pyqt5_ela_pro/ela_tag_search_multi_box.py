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
    _TagBoxThemeMixin,
    _TagBoxAnimMixin,
    _pre_init_popup,
    _get_target_mark_width,
    _draw_tag_background,
    _draw_tag_title,
    _draw_tag_arrow,
    _draw_tag_mark,
    _draw_multi_value_text,
)


class ElaTagSearchMultiBox(
    _TagBoxThemeMixin, _TagBoxAnimMixin, ElaSearchMultiBox
):
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
        if self._searchEdit:
            self._applySearchEditPalette()

    def hidePopup(self) -> None:
        self._expand_mark_width = 0.0
        super().hidePopup()

    def setCurrentSelection(self, selection):
        super().setCurrentSelection(selection)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        content_rect, text_color, _ = _draw_tag_background(painter, self)

        view = self.view()
        is_popup_visible = view.isVisible() if view else False
        mark_width = _get_target_mark_width(self) if is_popup_visible else self._expand_mark_width
        _draw_tag_mark(painter, self, mark_width)

        title_rect = _draw_tag_title(
            painter, content_rect, self._title_text,
            self._title_font_size, text_color, self.font(),
        )
        _draw_multi_value_text(
            painter, content_rect, title_rect, self.getCurrentSelection(),
        )
        _draw_tag_arrow(
            painter, content_rect, text_color, self._expand_icon_rotate,
        )

    def deleteLater(self) -> None:
        self._tag_box_delete_later()
        super().deleteLater()
