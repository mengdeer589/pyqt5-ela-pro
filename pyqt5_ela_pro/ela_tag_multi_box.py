"""
具名多选下拉框组件。

带有标题标签的多选下拉框，标题在左侧，值在右侧。
继承自 PyQt5ElaWidgetTools.ElaMultiSelectComboBox。
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import QTimer, QPropertyAnimation
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget

from PyQt5ElaWidgetTools import ElaMultiSelectComboBox

from .ela_tag_combo_base import (
    _TagBoxThemeMixin,
    _TagBoxAnimMixin,
    _draw_tag_background,
    _draw_tag_title,
    _draw_tag_arrow,
    _draw_tag_mark,
    _draw_multi_value_text,
)


class ElaTagMultiBox(_TagBoxThemeMixin, _TagBoxAnimMixin, ElaMultiSelectComboBox):
    """具名多选下拉框。

    带有标题标签的多选下拉框，标题在左侧，值在右侧。
    继承自 PyQt5ElaWidgetTools.ElaMultiSelectComboBox。

    :param parent: 父控件
    :param title: 标题文字

    Example::

        combo = ElaTagMultiBox(parent, title="语言")
        combo.addItem("Python")
        combo.addItem("C++")
        combo.addItem("JavaScript")
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "",
    ) -> None:
        super().__init__(parent)
        self._tag_box_init(title)
        self._currentSelection: list[str] = []
        self.setMaxVisibleItems(10)
        QTimer.singleShot(0, self._preInitPopup)

    def _preInitPopup(self) -> None:
        view = self.view()
        if view:
            view.setMinimumHeight(200)

    def _getTargetMarkWidth(self) -> float:
        selected_count = len(self.getCurrentSelection())
        total_count = self.count()
        if total_count <= 0:
            return 0.0
        return (self.width() / 2 - 9) * selected_count / total_count

    def showPopup(self) -> None:
        if self.count() == 0:
            return
        self._expand_mark_width = self._getTargetMarkWidth()
        super().showPopup()

    def hidePopup(self) -> None:
        self._expand_mark_width = 0.0
        super().hidePopup()

    def setCurrentSelection(self, selection):
        if isinstance(selection, str):
            selection = [selection]
        self._currentSelection = list(selection)
        if self._mark_animation.state() == QPropertyAnimation.Running:
            self._mark_animation.stop()
        self._expand_mark_width = self._getTargetMarkWidth()
        self.update()
        super().setCurrentSelection(self._currentSelection)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        content_rect, text_color, _ = _draw_tag_background(painter, self)

        view = self.view()
        is_popup_visible = view.isVisible() if view else False
        mark_width = self._getTargetMarkWidth() if is_popup_visible else self._expand_mark_width
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
