"""聊天头像自定义测试（SVG 数据 / SVG 文件 / QPixmap / 视图与组件透传）。"""

from __future__ import annotations

#: 整圆填充的 SVG（中心像素即填充色，便于断言）
from PyQt5.QtGui import QColor, QImage, QPixmap

from pyqt5_ela_pro.chat import (
    ElaChatBubble,
    ElaChatRole,
    ElaChatView,
    ElaChatWidget,
)

SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30">'
    '<circle cx="15" cy="15" r="15" fill="#ff5500"/></svg>'
)


def _solid_pixmap(color: str) -> QPixmap:
    pixmap = QPixmap(30, 30)
    pixmap.fill(QColor(color))
    return pixmap


def _center_color(widget, qapp) -> str:
    widget.show()
    qapp.processEvents()
    image = widget.grab().toImage()
    return image.pixelColor(image.width() // 2, image.height() // 2).name()


class TestAvatarBadge:
    def test_svg_data_renders_custom_image(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.User)
        bubble.setAvatarImage(SVG)
        avatar = bubble.header().avatar()
        assert avatar.hasCustomImage()
        assert _center_color(avatar, qapp) == "#ff5500"
        bubble.deleteLater()

    def test_svg_file_path(self, qapp, tmp_path):
        path = tmp_path / "avatar.svg"
        path.write_text(SVG, encoding="utf-8")
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        bubble.setAvatarImage(str(path))
        assert bubble.avatarImage() is not None
        assert bubble.header().avatar().hasCustomImage()
        bubble.deleteLater()

    def test_qpixmap_and_qimage_sources(self, qapp):

        bubble = ElaChatBubble(ElaChatRole.User)
        bubble.setAvatarImage(_solid_pixmap("#00aa66"))
        avatar = bubble.header().avatar()
        assert _center_color(avatar, qapp) == "#00aa66"

        image = QImage(30, 30, QImage.Format_ARGB32)
        image.fill(QColor("#2244cc"))
        bubble.setAvatarImage(image)
        assert _center_color(bubble.header().avatar(), qapp) == "#2244cc"
        bubble.deleteLater()

    def test_clear_and_invalid_fall_back_to_icon(self, qapp, tmp_path):
        bubble = ElaChatBubble(ElaChatRole.User)
        bubble.setAvatarImage(SVG)
        assert bubble.header().avatar().hasCustomImage()

        bubble.setAvatarImage(None)
        assert bubble.header().avatar().hasCustomImage() is False
        assert bubble.avatarImage() is None

        # 无效来源不应崩溃，同样回退内置图标
        bubble.setAvatarImage(tmp_path / "missing.svg")
        assert bubble.header().avatar().hasCustomImage() is False
        bubble.deleteLater()

    def test_custom_image_clipped_to_circle(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.User)
        bubble.setAvatarImage(_solid_pixmap("#ff5500"))
        avatar = bubble.header().avatar()
        avatar.show()
        qapp.processEvents()
        image = avatar.grab().toImage()
        # 中心是图片色
        assert (
            image.pixelColor(image.width() // 2, image.height() // 2).name()
            == "#ff5500"
        )
        # 正圆裁切：角点 / 左肩都不应出现图片色（圆角方形时左肩会露出）
        assert image.pixelColor(1, 1).name() != "#ff5500"
        assert image.pixelColor(4, 2).name() != "#ff5500"
        bubble.deleteLater()

    def test_shape_switch_on_bubble(self, qapp):
        bubble = ElaChatBubble(ElaChatRole.Assistant)
        assert bubble.avatarShape() == "circle"
        assert bubble.header().avatarShape() == "circle"

        bubble.setAvatarShape("rounded")
        assert bubble.avatarShape() == "rounded"
        assert bubble.header().avatarShape() == "rounded"
        assert bubble.header().avatar().shape() == "rounded"

        bubble.setAvatarShape("square")
        assert bubble.header().avatar().shape() == "square"

        # 非法值回落默认圆形
        bubble.setAvatarShape("hexagon")
        assert bubble.avatarShape() == "circle"
        assert bubble.header().avatar().shape() == "circle"
        bubble.deleteLater()


class TestViewAndWidgetAvatars:
    def test_view_role_avatars_apply_existing_and_new(self, qapp):
        view = ElaChatView()
        user_id = view.addMessage(ElaChatRole.User, "hi")
        assistant_id = view.addMessage(ElaChatRole.Assistant, "yo")
        assert not view.bubble(user_id).header().avatar().hasCustomImage()

        view.setUserAvatar(SVG)
        view.setAssistantAvatar(_solid_pixmap("#1188dd"))
        assert view.bubble(user_id).header().avatar().hasCustomImage()
        assert view.bubble(assistant_id).header().avatar().hasCustomImage()

        # 后续新增消息自动带上对应角色头像
        later = view.addMessage(ElaChatRole.User, "again")
        assert view.bubble(later).header().avatar().hasCustomImage()
        assert view.userAvatar() == SVG
        assert view.assistantAvatar() is not None

        # 清空后回退内置图标
        view.setUserAvatar(None)
        assert view.bubble(user_id).header().avatar().hasCustomImage() is False
        assert view.userAvatar() is None
        view.deleteLater()

    def test_view_shape_applies_existing_and_new(self, qapp):
        view = ElaChatView()
        user_id = view.addMessage(ElaChatRole.User, "hi")
        assert view.avatarShape() == "circle"
        assert view.bubble(user_id).header().avatar().shape() == "circle"

        view.setAvatarShape("rounded")
        assert view.avatarShape() == "rounded"
        assert view.bubble(user_id).avatarShape() == "rounded"

        # 后续新增消息自动带上形状
        later = view.addMessage(ElaChatRole.Assistant, "yo")
        assert view.bubble(later).avatarShape() == "rounded"

        # 非法值回落默认圆形
        view.setAvatarShape("teardrop")
        assert view.avatarShape() == "circle"
        assert view.bubble(later).header().avatar().shape() == "circle"
        view.deleteLater()

    def test_widget_passthrough(self, qapp):
        chat = ElaChatWidget()
        chat.chatView().setUserAvatar(SVG)
        chat.chatView().setAssistantAvatar(SVG)
        chat.chatView().setAvatarShape("square")
        user_id = chat.addMessage(ElaChatRole.User, "hi")
        assistant_id = chat.addMessage(ElaChatRole.Assistant, "yo")
        assert chat.chatView().userAvatar() == SVG
        assert chat.chatView().assistantAvatar() == SVG
        assert chat.chatView().avatarShape() == "square"
        assert chat.chatView().bubble(user_id).header().avatar().hasCustomImage()
        assert chat.chatView().bubble(user_id).header().avatar().shape() == "square"
        assert chat.chatView().bubble(assistant_id).header().avatar().hasCustomImage()
        chat.deleteLater()
