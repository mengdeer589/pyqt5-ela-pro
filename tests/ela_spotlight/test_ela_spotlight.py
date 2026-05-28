from __future__ import annotations

import pytest
from PyQt5.QtWidgets import QWidget

from pyqt5_ela_pro.ela_spotlight import ElaSpotlight


class TestElaSpotlightInit:
    def test_initialization_with_defaults(self):
        parent = QWidget()
        s = ElaSpotlight(parent)
        assert s._border_radius == 8
        assert s._padding == 8
        assert s._overlay_alpha == 120
        assert s._is_circle is False
        assert s._title == ""
        assert s._content == ""
        assert s._is_active is False
        assert s._current_step == -1
        assert s._steps == []
        assert s.isVisible() is False
        parent.deleteLater()
        s.deleteLater()

    def test_has_step_changed_signal(self):
        parent = QWidget()
        s = ElaSpotlight(parent)
        assert hasattr(s, "stepChanged")
        assert callable(s.stepChanged)
        parent.deleteLater()
        s.deleteLater()

    def test_has_finished_signal(self):
        parent = QWidget()
        s = ElaSpotlight(parent)
        assert hasattr(s, "finished")
        assert callable(s.finished)
        parent.deleteLater()
        s.deleteLater()

    def test_spotlight_step_dataclass(self):
        target = QWidget()
        step = ElaSpotlight.SpotlightStep(target, title="标题", content="内容", is_circle=True)
        assert step.target is target
        assert step.title == "标题"
        assert step.content == "内容"
        assert step.is_circle is True
        step.deleteLater() if hasattr(step, 'deleteLater') else None
        target.deleteLater()


class TestElaSpotlightShowSpotlight:
    def test_show_spotlight_sets_single_step(self):
        parent = QWidget()
        s = ElaSpotlight(parent)
        target = QWidget(parent)
        with pytest.MonkeyPatch.context() as m:
            m.setattr(s, 'start', lambda: None)
            s.showSpotlight(target, "知道了")
            assert len(s._steps) == 1
            assert s._prev_btn.isVisible() is False
            assert s._next_btn.text() == "知道了"
        target.deleteLater()
        parent.deleteLater()
        s.deleteLater()


class TestElaSpotlightSetSteps:
    def test_set_steps(self):
        parent = QWidget()
        s = ElaSpotlight(parent)
        step1 = ElaSpotlight.SpotlightStep(QWidget())
        step2 = ElaSpotlight.SpotlightStep(QWidget())
        s.setSteps([step1, step2])
        assert len(s._steps) == 2
        parent.deleteLater()
        s.deleteLater()


class TestElaSpotlightNavigation:
    def test_current_step_initially_negative_one(self):
        parent = QWidget()
        s = ElaSpotlight(parent)
        assert s.currentStep() == -1
        parent.deleteLater()
        s.deleteLater()

    def test_step_count(self):
        parent = QWidget()
        s = ElaSpotlight(parent)
        step1 = ElaSpotlight.SpotlightStep(QWidget())
        step2 = ElaSpotlight.SpotlightStep(QWidget())
        s.setSteps([step1, step2])
        assert s.stepCount() == 2
        parent.deleteLater()
        s.deleteLater()

    def test_next_does_nothing_when_not_started(self):
        parent = QWidget()
        s = ElaSpotlight(parent)
        s.next()
        assert s.currentStep() == -1
        parent.deleteLater()
        s.deleteLater()

    def test_previous_does_nothing_when_not_started(self):
        parent = QWidget()
        s = ElaSpotlight(parent)
        s.previous()
        assert s.currentStep() == -1
        parent.deleteLater()
        s.deleteLater()

    def test_finish_emits_finished(self):
        parent = QWidget()
        s = ElaSpotlight(parent)
        received = []
        s.finished.connect(lambda: received.append(True))
        s.finish()
        assert received == [True]
        parent.deleteLater()
        s.deleteLater()

    def test_finish_hides_widget(self):
        parent = QWidget()
        s = ElaSpotlight(parent)
        s.finish()
        assert s.isVisible() is False
        parent.deleteLater()
        s.deleteLater()

    def test_finish_clears_active(self):
        parent = QWidget()
        s = ElaSpotlight(parent)
        s._is_active = True
        s.finish()
        assert s._is_active is False
        parent.deleteLater()
        s.deleteLater()


class TestElaSpotlightTargetRect:
    def test_get_target_rect_none_target(self):
        parent = QWidget()
        s = ElaSpotlight(parent)
        r = s._getTargetRect(None)
        assert r.isNull()
        parent.deleteLater()
        s.deleteLater()

    def test_get_target_rect_no_parent(self):
        s = ElaSpotlight()
        target = QWidget()
        r = s._getTargetRect(target)
        assert r.isEmpty()
        target.deleteLater()
        s.deleteLater()


class TestElaSpotlightTheme:
    def test_on_theme_changed_updates_mode(self):
        parent = QWidget()
        s = ElaSpotlight(parent)
        from PyQt5ElaWidgetTools import ElaThemeType
        s._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert s._theme_mode == ElaThemeType.ThemeMode.Dark
        parent.deleteLater()
        s.deleteLater()


class TestElaSpotlightDeleteLater:
    def test_delete_later_cleans_up(self):
        parent = QWidget()
        s = ElaSpotlight(parent)
        s.deleteLater()
        parent.deleteLater()
