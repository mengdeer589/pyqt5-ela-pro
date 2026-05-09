from __future__ import annotations

import pytest

from pyqt5_ela_pro.ela_steps import ElaSteps


class TestElaStepsInit:
    def test_initialization_with_defaults(self):
        s = ElaSteps()
        assert s._current_step == 0
        assert s._step_count == 3
        assert s._step_titles == []
        s.deleteLater()

    def test_has_current_step_changed_signal(self):
        s = ElaSteps()
        assert hasattr(s, "currentStepChanged")
        assert callable(s.currentStepChanged)
        s.deleteLater()

    def test_fixed_height(self):
        s = ElaSteps()
        assert s.height() == 70
        s.deleteLater()


class TestElaStepsCurrentStep:
    def test_current_step_default(self):
        s = ElaSteps()
        assert s.currentStep() == 0
        s.deleteLater()

    def test_set_current_step(self):
        s = ElaSteps()
        s.setCurrentStep(1)
        assert s.currentStep() == 1
        s.deleteLater()

    def test_set_current_step_clamps_negative(self):
        s = ElaSteps()
        s.setCurrentStep(-1)
        assert s.currentStep() == 0
        s.deleteLater()

    def test_set_current_step_clamps_exceeds_max(self):
        s = ElaSteps()
        s.setCurrentStep(10)
        assert s.currentStep() == 2
        s.deleteLater()


class TestElaStepsStepCount:
    def test_step_count_default(self):
        s = ElaSteps()
        assert s.stepCount() == 3
        s.deleteLater()

    def test_set_step_count(self):
        s = ElaSteps()
        s.setStepCount(5)
        assert s.stepCount() == 5
        s.deleteLater()

    def test_set_step_count_clamps_to_min_1(self):
        s = ElaSteps()
        s.setStepCount(0)
        assert s.stepCount() == 1
        s.deleteLater()


class TestElaStepsStepTitles:
    def test_step_titles_default(self):
        s = ElaSteps()
        assert s.stepTitles() == []
        s.deleteLater()

    def test_set_step_titles(self):
        s = ElaSteps()
        s.setStepTitles(["步骤一", "步骤二", "步骤三"])
        assert s.stepTitles() == ["步骤一", "步骤二", "步骤三"]
        s.deleteLater()

    def test_set_step_titles_updates_count(self):
        s = ElaSteps()
        s.setStepTitles(["A", "B"])
        assert s.stepCount() == 2
        s.deleteLater()

    def test_set_step_titles_empty_updates_count_to_1(self):
        s = ElaSteps()
        s.setStepTitles([])
        assert s.stepCount() == 1
        s.deleteLater()


class TestElaStepsNavigation:
    def test_next_increments_step(self):
        s = ElaSteps()
        s.setStepCount(5)
        s.next()
        assert s.currentStep() == 1
        s.deleteLater()

    def test_next_emits_signal(self):
        s = ElaSteps()
        s.setStepCount(5)
        received = []
        s.currentStepChanged.connect(lambda v: received.append(v))
        s.next()
        assert 1 in received
        s.deleteLater()

    def test_next_does_not_exceed_max(self):
        s = ElaSteps()
        s.setStepCount(2)
        s.next()
        s.next()
        assert s.currentStep() == 1
        s.deleteLater()

    def test_previous_decrements_step(self):
        s = ElaSteps()
        s.setStepCount(5)
        s.setCurrentStep(3)
        s.previous()
        assert s.currentStep() == 2
        s.deleteLater()

    def test_previous_emits_signal(self):
        s = ElaSteps()
        s.setStepCount(5)
        s.setCurrentStep(3)
        received = []
        s.currentStepChanged.connect(lambda v: received.append(v))
        s.previous()
        assert 2 in received
        s.deleteLater()

    def test_previous_does_not_go_below_zero(self):
        s = ElaSteps()
        s.previous()
        assert s.currentStep() == 0
        s.deleteLater()


class TestElaStepsTheme:
    def test_on_theme_changed_updates_mode(self):
        s = ElaSteps()
        from PyQt5ElaWidgetTools import ElaThemeType
        s._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert s._theme_mode == ElaThemeType.ThemeMode.Dark
        s.deleteLater()


class TestElaStepsDeleteLater:
    def test_delete_later_cleans_up(self):
        s = ElaSteps()
        s.deleteLater()
