from __future__ import annotations


from pyqt5_ela_pro.ela_steps import ElaSteps


class TestElaStepsInit:
    def test_initialization_with_defaults(self):
        s = ElaSteps()
        assert s._current_step == 0
        assert s._step_titles == []
        assert s.step_count == 1
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
        s.step_titles = ["A", "B", "C"]
        s.setCurrentStep(1)
        assert s.currentStep() == 1
        s.deleteLater()

    def test_set_current_step_clamps_negative(self):
        s = ElaSteps()
        s.step_titles = ["A", "B", "C"]
        s.setCurrentStep(-1)
        assert s.currentStep() == 0
        s.deleteLater()

    def test_set_current_step_clamps_exceeds_max(self):
        s = ElaSteps()
        s.step_titles = ["A", "B", "C"]
        s.setCurrentStep(10)
        assert s.currentStep() == 2
        s.deleteLater()

    def test_set_current_step_emits_signal(self):
        s = ElaSteps()
        s.step_titles = ["A", "B", "C"]
        received = []
        s.currentStepChanged.connect(lambda v: received.append(v))
        s.setCurrentStep(2)
        assert 2 in received
        s.deleteLater()

    def test_set_current_step_same_value_no_emit(self):
        s = ElaSteps()
        s.step_titles = ["A", "B", "C"]
        s.setCurrentStep(0)
        received = []
        s.currentStepChanged.connect(lambda v: received.append(v))
        s.setCurrentStep(0)
        assert len(received) == 0
        s.deleteLater()


class TestElaStepsStepTitles:
    def test_step_titles_default(self):
        s = ElaSteps()
        assert s.step_titles == []
        s.deleteLater()

    def test_set_step_titles(self):
        s = ElaSteps()
        s.step_titles = ["步骤一", "步骤二", "步骤三"]
        assert s.step_titles == ["步骤一", "步骤二", "步骤三"]
        s.deleteLater()

    def test_step_count_derives_from_titles(self):
        s = ElaSteps()
        s.step_titles = ["A", "B"]
        assert s.step_count == 2
        s.deleteLater()

    def test_empty_titles_gives_count_1(self):
        s = ElaSteps()
        s.step_titles = []
        assert s.step_count == 1
        s.deleteLater()

    def test_set_step_titles_corrects_current_step(self):
        s = ElaSteps()
        s.step_titles = ["A", "B", "C"]
        s.setCurrentStep(2)
        s.step_titles = ["X"]
        assert s.currentStep() == 0
        s.deleteLater()

    def test_step_titles_returns_copy(self):
        s = ElaSteps()
        s.step_titles = ["A", "B"]
        titles = s.step_titles
        titles.append("C")
        assert s.step_titles == ["A", "B"]
        s.deleteLater()


class TestElaStepsNavigation:
    def test_next_increments_step(self):
        s = ElaSteps()
        s.step_titles = ["A", "B", "C", "D", "E"]
        s.next()
        assert s.currentStep() == 1
        s.deleteLater()

    def test_next_emits_signal(self):
        s = ElaSteps()
        s.step_titles = ["A", "B", "C", "D", "E"]
        received = []
        s.currentStepChanged.connect(lambda v: received.append(v))
        s.next()
        assert 1 in received
        s.deleteLater()

    def test_next_does_not_exceed_max(self):
        s = ElaSteps()
        s.step_titles = ["A", "B"]
        s.next()
        s.next()
        assert s.currentStep() == 1
        s.deleteLater()

    def test_previous_decrements_step(self):
        s = ElaSteps()
        s.step_titles = ["A", "B", "C", "D", "E"]
        s.setCurrentStep(3)
        s.previous()
        assert s.currentStep() == 2
        s.deleteLater()

    def test_previous_emits_signal(self):
        s = ElaSteps()
        s.step_titles = ["A", "B", "C", "D", "E"]
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
