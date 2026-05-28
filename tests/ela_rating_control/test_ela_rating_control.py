from __future__ import annotations

from PyQt5.QtCore import Qt

from pyqt5_ela_pro.ela_rating_control import ElaRatingControl


class TestElaRatingControlInit:
    def test_initialization_with_defaults(self):
        r = ElaRatingControl()
        assert r._max_rating == 5
        assert r._rating == 0.0
        assert r._star_size == 24
        assert r._spacing == 4
        assert r._is_read_only is False
        assert r._hovered_star == -1.0
        r.deleteLater()

    def test_has_rating_changed_signal(self):
        r = ElaRatingControl()
        assert hasattr(r, "ratingChanged")
        assert callable(r.ratingChanged)
        r.deleteLater()

    def test_mouse_tracking_enabled(self):
        r = ElaRatingControl()
        assert r.hasMouseTracking() is True
        r.deleteLater()


class TestElaRatingControlRating:
    def test_rating_default(self):
        r = ElaRatingControl()
        assert r.rating() == 0.0
        r.deleteLater()

    def test_set_rating(self):
        r = ElaRatingControl()
        r.setRating(3.5)
        assert r.rating() == 3.5
        r.deleteLater()

    def test_set_rating_emits_signal(self):
        r = ElaRatingControl()
        received = []
        r.ratingChanged.connect(lambda v: received.append(v))
        r.setRating(4.0)
        assert 4.0 in received
        r.deleteLater()

    def test_set_rating_same_value_no_emit(self):
        r = ElaRatingControl()
        r.setRating(3.0)
        received = []
        r.ratingChanged.connect(lambda v: received.append(v))
        r.setRating(3.0)
        assert len(received) == 0
        r.deleteLater()

    def test_set_rating_clamps_negative(self):
        r = ElaRatingControl()
        r.setRating(-1.0)
        assert r.rating() == 0.0
        r.deleteLater()

    def test_set_rating_clamps_exceeds_max(self):
        r = ElaRatingControl()
        r.setRating(10.0)
        assert r.rating() == 5.0
        r.deleteLater()

    def test_set_rating_rounds_to_half(self):
        r = ElaRatingControl()
        r.setRating(3.7)
        assert r.rating() == 3.5
        r.deleteLater()

    def test_set_rating_full_with_half(self):
        r = ElaRatingControl()
        r.setRating(3.3)
        assert r.rating() == 3.5
        r.deleteLater()


class TestElaRatingControlMaxRating:
    def test_max_rating_default(self):
        r = ElaRatingControl()
        assert r.maxRating() == 5
        r.deleteLater()

    def test_set_max_rating(self):
        r = ElaRatingControl()
        r.setMaxRating(10)
        assert r.maxRating() == 10
        r.deleteLater()

    def test_set_max_rating_updates_geometry(self):
        r = ElaRatingControl()
        r.setMaxRating(3)
        old_w = r.width()
        r.setMaxRating(10)
        assert r.width() >= old_w
        r.deleteLater()


class TestElaRatingControlStarSize:
    def test_star_size_default(self):
        r = ElaRatingControl()
        assert r.starSize() == 24
        r.deleteLater()

    def test_set_star_size(self):
        r = ElaRatingControl()
        r.setStarSize(32)
        assert r.starSize() == 32
        r.deleteLater()

    def test_set_star_size_updates_height(self):
        r = ElaRatingControl()
        r.setStarSize(40)
        assert r.height() >= 40
        r.deleteLater()


class TestElaRatingControlSpacing:
    def test_spacing_default(self):
        r = ElaRatingControl()
        assert r.spacing() == 4
        r.deleteLater()

    def test_set_spacing(self):
        r = ElaRatingControl()
        r.setSpacing(8)
        assert r.spacing() == 8
        r.deleteLater()


class TestElaRatingControlReadOnly:
    def test_read_only_default(self):
        r = ElaRatingControl()
        assert r.isReadOnly() is False
        r.deleteLater()

    def test_set_read_only(self):
        r = ElaRatingControl()
        r.setReadOnly(True)
        assert r.isReadOnly() is True
        r.deleteLater()

    def test_read_only_prevents_rating_change(self):
        r = ElaRatingControl()
        r.setReadOnly(True)
        r._hovered_star = 3.0
        from PyQt5.QtCore import QPoint, QEvent
        from PyQt5.QtGui import QMouseEvent
        event = QMouseEvent(
            QEvent.Type.MouseButtonPress, QPoint(50, 12),
            Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        r.mousePressEvent(event)
        assert r.rating() == 0.0
        r.deleteLater()


class TestElaRatingControlHover:
    def test_hover_initially_negative(self):
        r = ElaRatingControl()
        assert r._hovered_star == -1.0
        r.deleteLater()

    def test_leave_event_resets_hover(self):
        r = ElaRatingControl()
        r._hovered_star = 3.0
        from PyQt5.QtCore import QEvent
        r.leaveEvent(QEvent(QEvent.Type.Leave))
        assert r._hovered_star == -1.0
        r.deleteLater()


class TestElaRatingControlTheme:
    def test_on_theme_changed_updates_mode(self):
        r = ElaRatingControl()
        from PyQt5ElaWidgetTools import ElaThemeType
        r._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert r._theme_mode == ElaThemeType.ThemeMode.Dark
        r.deleteLater()


class TestElaRatingControlDeleteLater:
    def test_delete_later_cleans_up(self):
        r = ElaRatingControl()
        r.deleteLater()
