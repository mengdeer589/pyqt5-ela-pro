"""
具名可搜索下拉框组件。

带有标题标签的可搜索下拉框，继承自 ElaSearchBox，
支持汉字拼音首字母搜索。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtGui import QPainter, QPaintEvent
from PyQt5.QtWidgets import QWidget

from .combo_box import ElaSearchBox
from .ela_tag_combo_base import (
    _TagBoxThemeMixin,
    _TagBoxAnimMixin,
    _draw_tag_background,
    _draw_tag_title,
    _draw_tag_arrow,
    _draw_tag_mark,
    _draw_single_value_text,
)
from ._internal import _adjust_combobox_popup


class ElaTagSearchBox(_TagBoxThemeMixin, _TagBoxAnimMixin, ElaSearchBox):
    """具名可搜索下拉框。

    带有标题标签的可搜索下拉框，支持汉字拼音首字母搜索。
    继承自 ElaSearchBox，使用胶囊样式。

    :param title: 标题文字
    :param parent: 父控件

    Example::

        combo = ElaTagSearchBox(title="语言", parent=parent)
        combo.addItems(["Python", "C++", "JavaScript", "上海", "北京"])
    """

    def __init__(
        self,
        title: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._tag_box_init(title)
        self.currentIndexChanged.connect(self._onCurrentIndexChanged)

    def showPopup(self) -> None:
        if self.count() == 0:
            return
        self._animate_popup_open()
        super().showPopup()
        _adjust_combobox_popup(self)

        if self._searchEdit:
            self._applySearchEditPalette()

    def hidePopup(self) -> None:
        self._animate_popup_close()
        super().hidePopup()

    def _onCurrentIndexChanged(self, index: int) -> None:
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        content_rect, text_color, _ = _draw_tag_background(painter, self)
        _draw_tag_mark(painter, self, self._expand_mark_width)
        title_rect = _draw_tag_title(
            painter, content_rect, self._title_text,
            self._title_font_size, text_color, self.font(),
        )
        _draw_single_value_text(
            painter, content_rect, title_rect, self.currentText(),
        )
        _draw_tag_arrow(
            painter, content_rect, text_color, self._expand_icon_rotate,
        )

    def deleteLater(self) -> None:
        try:
            self.currentIndexChanged.disconnect(self._onCurrentIndexChanged)
        except (TypeError, RuntimeError):
            pass
        self._tag_box_delete_later()
        super().deleteLater()
