"""
具名组合框组件。

带有标题标签的组合框组件，只读模式。
继承自 ElaComboBox，使用 ElaWidgetTools 主题色。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import QEasingCurve
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import ElaComboBox

from .ela_tag_combo_base import (
    _TagBoxThemeMixin,
    _TagBoxAnimMixin,
    _draw_tag_background,
    _draw_tag_title,
    _draw_tag_arrow,
    _draw_tag_mark,
    _draw_single_value_text,
)


class ElaTagBox(_TagBoxThemeMixin, _TagBoxAnimMixin, ElaComboBox):
    """具名组合框。

    带有标题标签的组合框，只读模式。
    继承自 ElaComboBox，使用原生弹出菜单。

    :param parent: 父控件
    :param title: 标题文字

    Example::

        combo = ElaTagBox(parent, title="语言")
        combo.addItems(["Python", "C++", "JavaScript"])
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "",
    ) -> None:
        super().__init__(parent)
        self._tag_box_init(title)
        self.currentIndexChanged.connect(self._onCurrentIndexChanged)

    def showPopup(self) -> None:
        if self.count() == 0:
            return
        target_mark_width = self.width() / 2 - 9
        self._mark_animation.setStartValue(self._expand_mark_width)
        self._mark_animation.setEndValue(target_mark_width)
        self._mark_animation.start()

        self._rotate_animation.setStartValue(self._expand_icon_rotate)
        self._rotate_animation.setEndValue(-180.0)
        self._rotate_animation.start()

        super().showPopup()

    def hidePopup(self) -> None:
        self._mark_animation.setStartValue(self._expand_mark_width)
        self._mark_animation.setEndValue(0.0)
        self._mark_animation.start()

        self._rotate_animation.setStartValue(self._expand_icon_rotate)
        self._rotate_animation.setEndValue(0.0)
        self._rotate_animation.start()

        super().hidePopup()

    def _onCurrentIndexChanged(self, index: int) -> None:
        self.update()

    def paintEvent(self, event) -> None:
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
        self._tag_box_delete_later()
        super().deleteLater()
