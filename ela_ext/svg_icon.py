"""
SVG 图标转换模块。

从 PyQt-SiliconUI 的 .icons 文件加载 SVG 图标并转换为 QIcon，
与 ela 组件的 setIcon() 方法配合使用。
"""

from __future__ import annotations

import os
from typing import Optional

from PyQt5.QtCore import QSize, Qt, QRect, QRectF
from PyQt5.QtGui import QPainter, QPixmap, QIcon, QColor
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QPushButton
from PyQt5ElaWidgetTools import eTheme, ElaThemeType


def svg_to_icon(
    svg_data: str,
    size: int = 30,
    color: Optional[str] = None,
) -> QIcon:
    """将 SVG 数据转换为 QIcon。

    :param svg_data: SVG 字符串数据
    :param size: 图标尺寸，默认 30
    :param color: 颜色值（如 "#FF0000"），会替换 SVG 中的 <<<COLOR_CODE>>> 占位符
    :return: QIcon 对象

    Example::

        icon = svg_to_icon(svg_data, size=24, color="#1570A5")
        button.setIcon(icon)
    """
    if color:
        svg_data = svg_data.replace("<<<COLOR_CODE>>>", color)

    renderer = QSvgRenderer(svg_data.encode("utf-8"))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def svg_to_pixmap(
    svg_data: str,
    size: int = 30,
    color: Optional[str] = None,
) -> QPixmap:
    """将 SVG 数据转换为 QPixmap。

    :param svg_data: SVG 字符串数据
    :param size: 图标尺寸，默认 30
    :param color: 颜色值，会替换 SVG 中的 <<<COLOR_CODE>>> 占位符
    :return: QPixmap 对象
    """
    if color:
        svg_data = svg_data.replace("<<<COLOR_CODE>>>", color)

    renderer = QSvgRenderer(svg_data.encode("utf-8"))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    renderer.render(painter)
    painter.end()
    return pixmap


class ElaSvgIconLoader:
    """SVG 图标加载器。

    从 .icons 文件包加载图标，支持颜色替换。

    Example::

        loader = ElaSvgIconLoader()
        loader.loadFromPackage("fluent_ui_icon_regular.icons")

        # 获取图标
        icon = loader.getIcon("ic_fluent_zoom_out_regular", size=24, color="#1570A5")
        button.setIcon(icon)
    """

    _instance: Optional["ElaSvgIconLoader"] = None

    def __init__(self) -> None:
        self._icons: dict[str, str] = {}
        self._default_color: Optional[str] = None

    @classmethod
    def getInstance(cls) -> "ElaSvgIconLoader":
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def setDefaultColor(self, color: str) -> None:
        """设置默认颜色"""
        self._default_color = color

    @property
    def defaultColor(self) -> Optional[str]:
        return self._default_color

    def _getColor(self, color: Optional[str]) -> Optional[str]:
        return color if color is not None else self._default_color

    def loadFromPackage(self, package_name: str) -> None:
        """从图标包文件加载图标。

        :param package_name: 图标包文件名（如 "fluent_ui_icon_regular.icons"）
        """
        package_path = os.path.join(
            os.path.dirname(__file__),
            "icons",
            "packages",
            package_name,
        )
        self.loadFromFile(package_path)

    def loadFromFile(self, path: str) -> None:
        """从文件加载图标。

        :param path: .icons 文件路径
        """
        with open(path, encoding="utf-8") as file:
            for line in file.readlines():
                if line.startswith("##"):
                    continue
                if not line.strip():
                    continue

                line = line.strip()
                if "////" not in line:
                    continue

                icon_name, icon_data = line.split("////", 1)
                self._icons[icon_name] = icon_data

    def append(self, name: str, data: str) -> None:
        """手动添加一个图标"""
        self._icons[name] = data

    def getSvgData(self, name: str, color: Optional[str] = None) -> str:
        """获取 SVG 数据（已替换颜色）"""
        if name not in self._icons:
            raise KeyError(f"Icon '{name}' not found")
        svg_data = self._icons[name]
        final_color = self._getColor(color)
        if final_color:
            svg_data = svg_data.replace("<<<COLOR_CODE>>>", final_color)
        return svg_data

    def getIcon(
        self,
        name: str,
        size: int = 30,
        color: Optional[str] = None,
    ) -> QIcon:
        """获取 QIcon 对象。

        :param name: 图标名称
        :param size: 图标尺寸
        :param color: 颜色值
        :return: QIcon 对象
        """
        svg_data = self.getSvgData(name, color)
        return svg_to_icon(svg_data, size)

    def getPixmap(
        self,
        name: str,
        size: int = 30,
        color: Optional[str] = None,
    ) -> QPixmap:
        """获取 QPixmap 对象。

        :param name: 图标名称
        :param size: 图标尺寸
        :param color: 颜色值
        :return: QPixmap 对象
        """
        svg_data = self.getSvgData(name, color)
        return svg_to_pixmap(svg_data, size)

    def iconExists(self, name: str) -> Optional[str]:
        """检查图标是否存在"""
        return self._icons.get(name)

    def iconNames(self) -> list[str]:
        """获取所有已加载的图标名称"""
        return list(self._icons.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._icons

    def __len__(self) -> int:
        return len(self._icons)


_svgIconLoader: Optional[ElaSvgIconLoader] = None


class ElaSvgButton(QPushButton):
    """支持主题切换的 SVG 图标按钮。

    当主题切换时，自动使用ela主题色更新图标颜色。
    外观与 ElaPushButton 一致，支持鼠标悬浮效果。

    :param text: 按钮文本
    :param icon_name: 图标名称（如 "ic_fluent_zoom_out_regular"）
    :param icon_loader: ElaSvgIconLoader 实例
    :param theme_color: ElaThemeType.ThemeColor 主题色类型
    :param size: 图标尺寸，默认 20
    :param parent: 父控件

    Example::

        loader = ElaSvgIconLoader()
        loader.loadFromPackage("fluent_ui_icon_regular.icons")

        btn = ThemeAwareSvgButton(
            "搜索",
            "ic_fluent_zoom_out_regular",
            loader,
            theme_color=ElaThemeType.ThemeColor.PrimaryNormal,
        )
    """

    def __init__(
        self,
        text: str,
        icon_name: str,
        icon_loader: ElaSvgIconLoader,
        theme_color: ElaThemeType.ThemeColor = ElaThemeType.ThemeColor.PrimaryNormal,
        size: int = 20,
        parent=None,
    ):
        super().__init__(text, parent)
        self._iconName = icon_name
        self._svgIconLoader = icon_loader
        self._themeColor = theme_color
        self._iconSize = size
        self._borderRadius = 3
        self.setIconSize(QSize(size, size))
        fm = self.fontMetrics()
        text_width = fm.width(self.text())
        btn_height = max(size + 18, fm.height() + 18)
        self.setFixedSize(text_width + size + 30, btn_height)
        eTheme.themeModeChanged.connect(self._onThemeModeChanged)

    def _onThemeModeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self.update()

    def _getCurrentBgColor(self) -> QColor:
        mode = eTheme.getThemeMode()
        if not self.isEnabled():
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicDisable)
        if self.isDown():
            theme_color = eTheme.getThemeColor(mode, self._themeColor)
            theme_color.setAlpha(80)
            return theme_color
        if self.underMouse():
            theme_color = eTheme.getThemeColor(mode, self._themeColor)
            theme_color.setAlpha(40)
            return theme_color
        return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBase)

    def _getCurrentTextColor(self) -> QColor:
        mode = eTheme.getThemeMode()
        if not self.isEnabled():
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicTextDisable)
        return eTheme.getThemeColor(mode, self._themeColor)

    def paintEvent(self, event) -> None:
        from PyQt5.QtGui import QPainter, QPainterPath, QPen
        from PyQt5.QtCore import QRectF

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        shadow_border = 3
        rect = QRect(
            shadow_border,
            shadow_border,
            self.width() - 2 * shadow_border,
            self.height() - 2 * shadow_border,
        )

        bg_color = self._getCurrentBgColor()
        text_color = self._getCurrentTextColor()

        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), self._borderRadius, self._borderRadius)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg_color)
        painter.drawPath(path)

        fm = self.fontMetrics()
        text_width = fm.width(self.text())
        icon_size = QSize(self._iconSize, self._iconSize)
        spacing = 4
        total_content_width = icon_size.width() + spacing + text_width
        start_x = (
            shadow_border
            + (self.width() - 2 * shadow_border - total_content_width) // 2
        )
        content_height = self.height() - 2 * shadow_border
        icon_y = shadow_border + (content_height - icon_size.height()) // 2
        text_y = shadow_border

        icon_rect = QRect(start_x, icon_y, icon_size.width(), icon_size.height())
        text_rect = QRect(
            start_x + icon_size.width() + spacing,
            text_y,
            text_width,
            content_height,
        )

        mode = eTheme.getThemeMode()
        icon_color = eTheme.getThemeColor(mode, self._themeColor)
        icon_color_str = icon_color.name()
        if len(icon_color_str) > 7:
            icon_color_str = icon_color_str[:7]
        icon = self._svgIconLoader.getIcon(
            self._iconName,
            size=self._iconSize,
            color=icon_color_str,
        )
        painter.drawPixmap(icon_rect, icon.pixmap(icon_size))

        painter.setPen(text_color)
        painter.setFont(self.font())
        painter.drawText(
            text_rect,
            Qt.Alignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
            self.text(),
        )

    def setBorderRadius(self, radius: int) -> None:
        self._borderRadius = radius
        self.update()

    def setText(self, text: str) -> None:
        super().setText(text)
        fm = self.fontMetrics()
        text_width = fm.width(text)
        btn_height = max(self._iconSize + 18, fm.height() + 18)
        self.setFixedSize(text_width + self._iconSize + 30, btn_height)
        self.update()

    def __del__(self):
        try:
            eTheme.themeModeChanged.disconnect(self._onThemeModeChanged)
        except Exception:
            pass


class ElaIconButton(QPushButton):
    """使用 SVG 图标的按钮。

    支持主题切换，自动更新图标颜色。

    :param text: 按钮文本
    :param icon_name: 图标名称（如 "ic_fluent_zoom_out_regular"）
    :param icon_loader: ElaSvgIconLoader 实例
    :param theme_color: ElaThemeType.ThemeColor 主题色类型
    :param size: 图标尺寸，默认 16
    :param parent: 父控件

    Example::

        loader = ElaSvgIconLoader()
        loader.loadFromPackage("fluent_ui_icon_regular.icons")

        btn = ElaIconButton(
            "搜索",
            "ic_fluent_zoom_out_regular",
            loader,
            theme_color=ElaThemeType.ThemeColor.PrimaryNormal,
        )
    """

    def __init__(
        self,
        text: str,
        icon_name: str,
        icon_loader: ElaSvgIconLoader,
        theme_color: ElaThemeType.ThemeColor = ElaThemeType.ThemeColor.PrimaryNormal,
        size: int = 16,
        parent=None,
    ):
        super().__init__(text, parent)
        self._iconName = icon_name
        self._svgIconLoader = icon_loader
        self._themeColor = theme_color
        self._iconSize = size
        self._borderRadius = 3
        self.setFixedHeight(38)
        fm = self.fontMetrics()
        text_width = fm.width(text)
        self.setFixedWidth(size + text_width + 20)
        eTheme.themeModeChanged.connect(self._onThemeModeChanged)

    def _onThemeModeChanged(self, mode: ElaThemeType.ThemeMode) -> None:
        self.update()

    def _getCurrentBgColor(self) -> QColor:
        mode = eTheme.getThemeMode()
        if not self.isEnabled():
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicDisable)
        if self.isDown():
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicPress)
        if self.underMouse():
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicHover)
        return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicBase)

    def _getCurrentTextColor(self) -> QColor:
        mode = eTheme.getThemeMode()
        if not self.isEnabled():
            return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicTextDisable)
        return eTheme.getThemeColor(mode, ElaThemeType.ThemeColor.BasicText)

    def paintEvent(self, event) -> None:
        from PyQt5.QtGui import QPainter, QPainterPath, QPen

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        shadow_border = 3
        rect = QRect(
            shadow_border,
            shadow_border,
            self.width() - 2 * shadow_border,
            self.height() - 2 * shadow_border,
        )

        bg_color = self._getCurrentBgColor()
        text_color = self._getCurrentTextColor()

        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), self._borderRadius, self._borderRadius)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg_color)
        painter.drawPath(path)

        fm = self.fontMetrics()
        text_width = fm.width(self.text())
        icon_size = QSize(self._iconSize, self._iconSize)
        spacing = 4
        total_content_width = icon_size.width() + spacing + text_width
        start_x = (
            shadow_border
            + (self.width() - 2 * shadow_border - total_content_width) // 2
        )
        content_height = self.height() - 2 * shadow_border
        icon_y = shadow_border + (content_height - icon_size.height()) // 2
        text_y = shadow_border

        icon_rect = QRect(start_x, icon_y, icon_size.width(), icon_size.height())
        text_rect = QRect(
            start_x + icon_size.width() + spacing,
            text_y,
            text_width,
            content_height,
        )

        icon_color_str = text_color.name()
        if len(icon_color_str) > 7:
            icon_color_str = icon_color_str[:7]
        icon = self._svgIconLoader.getIcon(
            self._iconName,
            size=self._iconSize,
            color=icon_color_str,
        )
        painter.drawPixmap(icon_rect, icon.pixmap(icon_size))

        painter.setPen(text_color)
        painter.setFont(self.font())
        painter.drawText(
            text_rect,
            Qt.Alignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
            self.text(),
        )

    def setSvgIcon(self, icon_name: str, size: int = None) -> None:
        """设置 SVG 图标。

        :param icon_name: 图标名称
        :param size: 图标尺寸，默认使用创建时的尺寸
        """
        self._iconName = icon_name
        if size is not None:
            self._iconSize = size
        self.update()

    def setText(self, text: str) -> None:
        super().setText(text)
        fm = self.fontMetrics()
        text_width = fm.width(text)
        self.setFixedWidth(self._iconSize + text_width + 20)
        self.update()

    def __del__(self):
        try:
            eTheme.themeModeChanged.disconnect(self._onThemeModeChanged)
        except Exception:
            pass


def svgIconLoader() -> ElaSvgIconLoader:
    """获取全局图标加载器实例（自动加载默认图标包）"""
    global _svgIconLoader
    if _svgIconLoader is None:
        _svgIconLoader = ElaSvgIconLoader.getInstance()
        try:
            _svgIconLoader.loadFromPackage("fluent_ui_icon_regular.icons")
        except FileNotFoundError:
            pass
    return _svgIconLoader


__all__ = [
    "svg_to_icon",
    "svg_to_pixmap",
    "ElaSvgIconLoader",
    "ElaSvgButton",
    "ElaIconButton",
    "svgIconLoader",
]
