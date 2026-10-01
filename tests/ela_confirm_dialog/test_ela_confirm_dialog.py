"""``ElaConfirmDialog`` 测试：初值 / 文本属性 / 定位 / 按钮 / 主题。"""

from __future__ import annotations

import pytest
from PyQt5.QtCore import QEvent, QPoint, QRect, Qt
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5ElaWidgetTools import ElaThemeType

from pyqt5_ela_pro.ela_confirm_dialog import ElaConfirmDialog, _ElaConfirmButton


@pytest.fixture
def parent(make):
    return make(QWidget)


@pytest.fixture
def dlg(make, parent):
    return make(ElaConfirmDialog, parent)


@pytest.fixture
def confirm_btn(make):
    return make(_ElaConfirmButton, _ElaConfirmButton.TYPE_CONFIRM)


class TestElaConfirmDialogInit:
    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ("_title", "标题"),
            ("_content", ""),
            ("_border_radius", 8),
            ("_position", "bottom"),
            ("_title_pixel_size", 15),
            ("_content_pixel_size", 13),
        ],
    )
    def test_default_state(self, dlg, attr, expected):
        assert getattr(dlg, attr) == expected

    @pytest.mark.parametrize("position", ["top", "bottom"])
    def test_initialization_with_position(self, make, parent, position):
        dlg = make(ElaConfirmDialog, parent, position=position)
        assert dlg._position == position
        assert dlg.position() == position

    def test_minimum_size(self, dlg):
        assert dlg.minimumWidth() == 280
        assert dlg.minimumHeight() == 150

    @pytest.mark.parametrize("attr", ["_confirm_btn", "_cancel_btn"])
    def test_has_button(self, dlg, attr):
        assert hasattr(dlg, attr)

    def test_frameless_window_hint(self, dlg):
        assert dlg.windowFlags() & Qt.WindowType.FramelessWindowHint

    def test_translucent_background(self, dlg):
        assert dlg.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)


class TestElaConfirmDialogSignals:
    @pytest.mark.parametrize("name", ["confirmed", "cancelled"])
    def test_declares_signal(self, dlg, name):
        assert callable(getattr(dlg, name))

    @pytest.mark.parametrize(
        ("slot", "signal"), [("_onConfirm", "confirmed"), ("_onCancel", "cancelled")]
    )
    def test_slot_emits(self, dlg, slot, signal):
        received = []
        getattr(dlg, signal).connect(lambda: received.append(True))
        getattr(dlg, slot)()
        assert received == [True]


class TestElaConfirmDialogTextProps:
    """``setTitle`` / ``setContent`` / ``setBorderRadius`` / ``setPosition``
    四组 setter/getter 形状一致，参数化掉。"""

    @pytest.mark.parametrize(
        ("setter", "getter", "value"),
        [
            (ElaConfirmDialog.setTitle, ElaConfirmDialog.title, "确认删除？"),
            (ElaConfirmDialog.setTitle, ElaConfirmDialog.title, ""),
            (
                ElaConfirmDialog.setContent,
                ElaConfirmDialog.content,
                "确定要删除此项目吗？",
            ),
            (ElaConfirmDialog.setContent, ElaConfirmDialog.content, ""),
            (ElaConfirmDialog.setBorderRadius, ElaConfirmDialog.borderRadius, 16),
            (ElaConfirmDialog.setPosition, ElaConfirmDialog.position, "top"),
            (ElaConfirmDialog.setPosition, ElaConfirmDialog.position, "bottom"),
        ],
    )
    def test_setter_roundtrip(self, dlg, setter, getter, value):
        setter(dlg, value)
        assert getter(dlg) == value

    @pytest.mark.parametrize(
        ("getter", "expected"),
        [
            (ElaConfirmDialog.borderRadius, 8),
            (ElaConfirmDialog.position, "bottom"),
        ],
    )
    def test_getter_default(self, dlg, getter, expected):
        assert getter(dlg) == expected


class TestElaConfirmDialogTheme:
    def test_on_theme_changed_updates_mode(self, dlg):
        dlg._onThemeChanged(ElaThemeType.ThemeMode.Dark)
        assert dlg._theme_mode == ElaThemeType.ThemeMode.Dark


class TestElaConfirmButton:
    @pytest.mark.parametrize(
        "btn_type", [_ElaConfirmButton.TYPE_CONFIRM, _ElaConfirmButton.TYPE_CANCEL]
    )
    def test_button_type(self, make, btn_type):
        btn = make(_ElaConfirmButton, btn_type)
        assert btn._type == btn_type

    def test_initial_state(self, confirm_btn):
        assert confirm_btn._is_hovered is False
        assert confirm_btn._is_pressed is False

    def test_button_has_clicked_signal(self, confirm_btn):
        assert hasattr(confirm_btn, "clicked")

    def test_button_has_hand_cursor(self, confirm_btn):
        assert confirm_btn.cursor().shape() == Qt.CursorShape.PointingHandCursor

    def test_button_fixed_height(self, confirm_btn):
        assert confirm_btn.height() == 40

    def test_button_enter_leave_events(self, confirm_btn):
        confirm_btn.enterEvent(QEvent(QEvent.Type.Enter))
        assert confirm_btn._is_hovered is True
        confirm_btn.leaveEvent(QEvent(QEvent.Type.Leave))
        assert confirm_btn._is_hovered is False


class TestElaConfirmDialogPlacement:
    """弹框定位：贴着锚点摆放，放不下时翻边 + 夹回屏幕工作区。

    回归：锚点贴窗口 / 屏幕底边（聊天输入区、最大化窗口里的整块聊天组件）
    时，只按「锚点底边 + 间距」摆放会把弹框整块算到屏幕外 —— 用户点击后
    什么都看不到。
    """

    @staticmethod
    def _anchor(make, qapp, window_rect):
        """在指定全局位置造一个窗口 + 内部锚点控件，返回锚点控件。"""
        parent = make(QWidget)
        parent.setWindowFlags(Qt.WindowType.Window)
        parent.setGeometry(window_rect)
        parent.show()
        anchor = make(QWidget, parent)
        anchor.setGeometry(10, 10, 120, 60)
        qapp.processEvents()
        return anchor

    @staticmethod
    def _anchor_rect(anchor):
        return QRect(anchor.mapToGlobal(QPoint(0, 0)), anchor.size())

    @staticmethod
    def _dialog(make, qapp, anchor, position):
        dialog = make(ElaConfirmDialog, anchor, position=position)
        dialog.resize(280, 150)
        dialog.show()
        qapp.processEvents()
        dialog._positionDialog()
        return dialog

    def test_sits_below_anchor_when_there_is_room(self, make, qapp):
        area = QApplication.primaryScreen().availableGeometry()
        anchor = self._anchor(
            make, qapp, QRect(area.left() + 80, area.top() + 80, 240, 200)
        )
        dialog = self._dialog(make, qapp, anchor, "bottom")

        assert dialog.y() == self._anchor_rect(anchor).bottom() + 6
        assert area.contains(dialog.frameGeometry())
        dialog.close()

    def test_flips_above_when_anchor_sits_on_bottom_edge(self, make, qapp):
        """不允许为了留在屏幕内把弹框压回锚点身上（必须真的翻到上方）。"""
        area = QApplication.primaryScreen().availableGeometry()
        anchor = self._anchor(
            make, qapp, QRect(area.left() + 80, area.bottom() - 140, 400, 140)
        )
        dialog = self._dialog(make, qapp, anchor, "bottom")

        assert area.contains(dialog.frameGeometry())
        assert dialog.y() + dialog.height() <= self._anchor_rect(anchor).top() + 1
        dialog.close()

    def test_flips_below_when_anchor_sits_on_top_edge(self, make, qapp):
        area = QApplication.primaryScreen().availableGeometry()
        anchor = self._anchor(make, qapp, QRect(area.left() + 80, area.top(), 400, 140))
        dialog = self._dialog(make, qapp, anchor, "top")

        assert area.contains(dialog.frameGeometry())
        assert dialog.y() >= self._anchor_rect(anchor).bottom()
        dialog.close()

    def test_horizontal_position_clamped_into_screen(self, make, qapp):
        area = QApplication.primaryScreen().availableGeometry()
        anchor = self._anchor(
            make, qapp, QRect(area.right() - 120, area.top() + 80, 120, 200)
        )
        dialog = self._dialog(make, qapp, anchor, "bottom")

        assert dialog.x() >= area.left()
        assert dialog.x() + dialog.width() <= area.right() + 1
        dialog.close()


class TestElaConfirmDialogDeleteLater:
    def test_delete_later_cleans_up(self, make, parent):
        make(ElaConfirmDialog, parent).deleteLater()
