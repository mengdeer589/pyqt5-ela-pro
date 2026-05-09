from __future__ import annotations

import pytest
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro.ela_timeline import ElaTimeline
from PyQt5ElaWidgetTools import ElaIconType


class TestElaTimelineInit:
    def test_initialization_with_defaults(self):
        t = ElaTimeline()
        assert t._items == []
        assert t._current_step == 0
        t.deleteLater()

    def test_object_name(self):
        t = ElaTimeline()
        assert t.objectName() == "ElaTimeline"
        t.deleteLater()


class TestElaTimelineItem:
    def test_timeline_item_defaults(self):
        item = ElaTimeline.TimelineItem()
        assert item.title == ""
        assert item.content == ""
        assert item.timestamp == ""
        assert item.icon == ElaIconType.IconName.None_

    def test_timeline_item_with_values(self):
        item = ElaTimeline.TimelineItem(
            title="事件", content="描述", timestamp="2024-01-01",
            icon=ElaIconType.IconName.Check,
        )
        assert item.title == "事件"
        assert item.content == "描述"
        assert item.timestamp == "2024-01-01"
        assert item.icon == ElaIconType.IconName.Check


class TestElaTimelineAddItem:
    def test_add_item(self):
        t = ElaTimeline()
        item = ElaTimeline.TimelineItem(title="事件")
        t.addItem(item)
        assert t.itemCount() == 1
        t.deleteLater()

    def test_add_multiple_items(self):
        t = ElaTimeline()
        t.addItem(ElaTimeline.TimelineItem(title="A"))
        t.addItem(ElaTimeline.TimelineItem(title="B"))
        t.addItem(ElaTimeline.TimelineItem(title="C"))
        assert t.itemCount() == 3
        t.deleteLater()


class TestElaTimelineClearItems:
    def test_clear_items(self):
        t = ElaTimeline()
        t.addItem(ElaTimeline.TimelineItem(title="A"))
        t.addItem(ElaTimeline.TimelineItem(title="B"))
        t.clearItems()
        assert t.itemCount() == 0
        t.deleteLater()


class TestElaTimelineItemCount:
    def test_item_count_default(self):
        t = ElaTimeline()
        assert t.itemCount() == 0
        t.deleteLater()

    def test_item_count_after_add(self):
        t = ElaTimeline()
        t.addItem(ElaTimeline.TimelineItem())
        assert t.itemCount() == 1
        t.deleteLater()


class TestElaTimelineCurrentStep:
    def test_current_step_default(self):
        t = ElaTimeline()
        assert t.currentStep() == 0
        t.deleteLater()

    def test_set_current_step(self):
        t = ElaTimeline()
        t.addItem(ElaTimeline.TimelineItem())
        t.addItem(ElaTimeline.TimelineItem())
        t.setCurrentStep(1)
        assert t.currentStep() == 1
        t.deleteLater()

    def test_set_current_step_clamps_negative(self):
        t = ElaTimeline()
        t.addItem(ElaTimeline.TimelineItem())
        t.setCurrentStep(-1)
        assert t.currentStep() == 0
        t.deleteLater()

    def test_set_current_step_clamps_exceeds_max(self):
        t = ElaTimeline()
        t.addItem(ElaTimeline.TimelineItem())
        t.setCurrentStep(10)
        assert t.currentStep() == 0
        t.deleteLater()

    def test_set_current_step_empty_items(self):
        t = ElaTimeline()
        t.setCurrentStep(5)
        assert t.currentStep() == 0
        t.deleteLater()


class TestElaTimelineSizeHint:
    def test_size_hint_empty(self):
        t = ElaTimeline()
        sz = t.sizeHint()
        assert sz == QSize(400, 0)
        t.deleteLater()

    def test_size_hint_with_items(self):
        t = ElaTimeline()
        t.addItem(ElaTimeline.TimelineItem(title="事件"))
        sz = t.sizeHint()
        assert sz.height() > 0
        t.deleteLater()


class TestElaTimelineTheme:
    def test_on_theme_changed_updates_mode(self):
        t = ElaTimeline()
        from PyQt5ElaWidgetTools import ElaThemeType
        t._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert t._theme_mode == ElaThemeType.ThemeMode.Dark
        t.deleteLater()


class TestElaTimelineDeleteLater:
    def test_delete_later_cleans_up(self):
        t = ElaTimeline()
        t.deleteLater()
