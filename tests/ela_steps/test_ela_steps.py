"""``ElaSteps`` 测试：初值 / 当前步夹取 / 标题列表 / 前进后退 / 主题。"""

from __future__ import annotations

import pytest
from PyQt5ElaWidgetTools import ElaThemeType

from pyqt5_ela_pro.ela_steps import ElaSteps

_FIVE = ["A", "B", "C", "D", "E"]
_THREE = ["A", "B", "C"]


@pytest.fixture
def s(make):
    return make(ElaSteps)


class TestElaStepsInit:
    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("_current_step", 0),
            ("_step_titles", []),
        ],
    )
    def test_initialization_with_defaults(self, s, attr, expected):
        assert getattr(s, attr) == expected

    def test_step_count_defaults_to_one(self, s):
        assert s.step_count == 1

    def test_has_current_step_changed_signal(self, s):
        assert hasattr(s, "currentStepChanged")
        assert callable(s.currentStepChanged)

    def test_fixed_height(self, s):
        assert s.height() == 70


class TestElaStepsCurrentStep:
    def test_current_step_default(self, s):
        assert s.currentStep() == 0

    def test_set_current_step(self, s):
        s.step_titles = _THREE
        s.setCurrentStep(1)
        assert s.currentStep() == 1

    @pytest.mark.parametrize(
        ("requested", "expected"),
        [(-1, 0), (10, 2)],
        ids=["below-min", "above-max"],
    )
    def test_set_current_step_clamps(self, s, requested, expected):
        s.step_titles = _THREE
        s.setCurrentStep(requested)
        assert s.currentStep() == expected

    def test_set_current_step_emits_signal(self, s):
        s.step_titles = _THREE
        received = []
        s.currentStepChanged.connect(lambda v: received.append(v))
        s.setCurrentStep(2)
        assert 2 in received

    def test_set_current_step_same_value_no_emit(self, s):
        s.step_titles = _THREE
        s.setCurrentStep(0)
        received = []
        s.currentStepChanged.connect(lambda v: received.append(v))
        s.setCurrentStep(0)
        assert len(received) == 0


class TestElaStepsStepTitles:
    def test_step_titles_default(self, s):
        assert s.step_titles == []

    def test_set_step_titles(self, s):
        s.step_titles = ["步骤一", "步骤二", "步骤三"]
        assert s.step_titles == ["步骤一", "步骤二", "步骤三"]

    @pytest.mark.parametrize(
        ("titles", "expected"),
        [([], 1), (["A", "B"], 2)],
        ids=["empty", "two-titles"],
    )
    def test_step_count_derives_from_titles(self, s, titles, expected):
        s.step_titles = titles
        assert s.step_count == expected

    def test_set_step_titles_corrects_current_step(self, s):
        s.step_titles = _THREE
        s.setCurrentStep(2)
        s.step_titles = ["X"]
        assert s.currentStep() == 0

    def test_step_titles_returns_copy(self, s):
        s.step_titles = ["A", "B"]
        titles = s.step_titles
        titles.append("C")
        assert s.step_titles == ["A", "B"]


class TestElaStepsNavigation:
    @pytest.mark.parametrize(
        ("titles", "start", "navs", "expected"),
        [
            (_FIVE, None, ["next"], 1),
            (["A", "B"], None, ["next", "next"], 1),
            (_FIVE, 3, ["previous"], 2),
            ([], None, ["previous"], 0),
        ],
        ids=["next", "next-clamped-at-max", "previous", "previous-clamped-at-min"],
    )
    def test_navigation(self, s, titles, start, navs, expected):
        s.step_titles = titles
        if start is not None:
            s.setCurrentStep(start)
        for name in navs:
            getattr(s, name)()
        assert s.currentStep() == expected

    @pytest.mark.parametrize(
        ("start", "nav", "emitted"),
        [(None, "next", 1), (3, "previous", 2)],
        ids=["next", "previous"],
    )
    def test_navigation_emits_signal(self, s, start, nav, emitted):
        s.step_titles = _FIVE
        if start is not None:
            s.setCurrentStep(start)
        received = []
        s.currentStepChanged.connect(received.append)
        getattr(s, nav)()
        assert emitted in received


class TestElaStepsTheme:
    def test_on_theme_changed_updates_mode(self, s):
        s._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert s._theme_mode == ElaThemeType.ThemeMode.Dark


class TestElaStepsDeleteLater:
    def test_delete_later_cleans_up(self, s):
        s.deleteLater()
