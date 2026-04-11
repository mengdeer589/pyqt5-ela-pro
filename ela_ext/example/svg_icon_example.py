"""
[ela_ext] SVG 图标组件演示页面

展示如何使用 svg_icon 模块加载和显示 PyQt-SiliconUI 的 Fluent 图标，
并支持主题切换。
"""

from __future__ import annotations

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListView,
)
from PyQt5.QtGui import QFont

from PyQt5ElaWidgetTools import (
    ElaText,
    eTheme,
    ElaThemeType,
    ElaListView,
    ElaLineEdit,
    ElaMessageBar,
    ElaMessageBarType,
)

from ela_ext.svg_icon import (
    ElaSvgIconLoader,
    ElaSvgButton,
    ElaIconButton,
)
from .base_page import ExamplePage
from .es_icon_model import EsIconModel
from .es_icon_delegate import EsIconDelegate


class SvgIconComponentsPage(ExamplePage):
    """SVG 图标组件演示页面"""

    PAGE_TITLE = "SVG 图标组件"

    def __init__(self, parent=None):
        self._svg_buttons: list[ElaSvgButton] = []
        self._svg_loader = ElaSvgIconLoader()
        self._svg_loader.loadFromPackage("fluent_ui_icon_regular.icons")
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoSvgIconBrowser(main_layout)
        self._demoEsButton(main_layout)
        self._demoEsSvgButton(main_layout)
        self._demoAllColors(main_layout)

    def _demoEsButton(self, parent_layout):
        section = ElaText("01. ElaIconButton - 基础 SVG 图标按钮", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText(
            "继承 ElaPushButton 的外观，使用 SVG 图标，图标颜色与文字一致",
            self,
        )
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        icons_row_layout = QHBoxLayout()
        icons_row_layout.setSpacing(15)

        svg_buttons = [
            (
                "ic_fluent_zoom_out_regular",
                "搜索",
                ElaThemeType.ThemeColor.PrimaryNormal,
            ),
            (
                "ic_fluent_settings_regular",
                "设置",
                ElaThemeType.ThemeColor.PrimaryNormal,
            ),
            ("ic_fluent_delete_regular", "删除", ElaThemeType.ThemeColor.StatusDanger),
            ("ic_fluent_save_regular", "保存", ElaThemeType.ThemeColor.PrimaryNormal),
        ]

        for name, text, theme_color in svg_buttons:
            btn = ElaIconButton(
                text,
                name,
                self._svg_loader,
                theme_color=theme_color,
                parent=self,
            )
            btn.setFixedWidth(120)
            icons_row_layout.addWidget(btn)

        icons_row_layout.addStretch()
        parent_layout.addLayout(icons_row_layout)
        parent_layout.addSpacing(30)

    def _demoEsSvgButton(self, parent_layout):
        section = ElaText("02. ElaSvgButton - 悬浮/点击主题色效果", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText(
            "鼠标悬浮和点击时显示半透明主题色背景效果",
            self,
        )
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        icons_row_layout = QHBoxLayout()
        icons_row_layout.setSpacing(15)

        theme_buttons = [
            (
                "ic_fluent_zoom_out_regular",
                "搜索",
                ElaThemeType.ThemeColor.PrimaryNormal,
            ),
            (
                "ic_fluent_settings_regular",
                "设置",
                ElaThemeType.ThemeColor.PrimaryNormal,
            ),
            ("ic_fluent_delete_regular", "删除", ElaThemeType.ThemeColor.StatusDanger),
            ("ic_fluent_edit_regular", "编辑", ElaThemeType.ThemeColor.PrimaryPress),
            ("ic_fluent_copy_regular", "复制", ElaThemeType.ThemeColor.PrimaryNormal),
        ]

        for name, text, theme_color in theme_buttons:
            btn = ElaSvgButton(
                text,
                name,
                self._svg_loader,
                theme_color=theme_color,
                parent=self,
            )
            btn.setFixedWidth(120)
            self._svg_buttons.append(btn)
            icons_row_layout.addWidget(btn)

        icons_row_layout.addStretch()
        parent_layout.addLayout(icons_row_layout)
        parent_layout.addSpacing(30)

    def _demoAllColors(self, parent_layout):
        section = ElaText("03. 可用的 ThemeColor 按钮颜色", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText(
            "适合做按钮的 ThemeColor：PrimaryNormal, StatusDanger",
            self,
        )
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        all_colors = [
            (
                "ic_fluent_zoom_out_regular",
                "PrimaryN",
                ElaThemeType.ThemeColor.PrimaryNormal,
            ),
            (
                "ic_fluent_delete_regular",
                "Danger",
                ElaThemeType.ThemeColor.StatusDanger,
            ),
        ]

        icons_row_layout = QHBoxLayout()
        icons_row_layout.setSpacing(15)

        for name, text, theme_color in all_colors:
            btn = ElaSvgButton(
                text,
                name,
                self._svg_loader,
                theme_color=theme_color,
                parent=self,
            )
            btn.setFixedWidth(120)
            self._svg_buttons.append(btn)
            icons_row_layout.addWidget(btn)

        icons_row_layout.addStretch()
        parent_layout.addLayout(icons_row_layout)
        parent_layout.addSpacing(30)

    def _demoSvgIconBrowser(self, parent_layout):
        section = ElaText("04. SVG 图标浏览器 - 所有可用图标", self)
        section.setTextPixelSize(18)
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        section.setFont(font)
        parent_layout.addWidget(section)

        info = ElaText("点击图标以复制其名称", self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)
        parent_layout.addSpacing(10)

        self._es_icon_view = ElaListView(self)
        self._es_icon_view.setIsTransparent(True)
        self._es_icon_view.setFlow(QListView.Flow.LeftToRight)
        self._es_icon_view.setViewMode(QListView.ViewMode.IconMode)
        self._es_icon_view.setFixedHeight(400)
        self._es_icon_view.setResizeMode(QListView.ResizeMode.Adjust)
        self._es_icon_view.clicked.connect(self._onEsIconClicked)

        icon_names = self._svg_loader.iconNames()
        self._es_icon_model = EsIconModel(icon_names, self)
        self._es_icon_delegate = EsIconDelegate(self._svg_loader, self)
        self._es_icon_view.setModel(self._es_icon_model)
        self._es_icon_view.setItemDelegate(self._es_icon_delegate)
        self._es_icon_view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self._es_search_edit = ElaLineEdit(self)
        self._es_search_edit.setPlaceholderText("搜索图标")
        self._es_search_edit.setFixedSize(300, 35)
        self._es_search_edit.textEdited.connect(self._onEsSearchEditTextEdit)
        self._es_search_edit.focusIn.connect(self._onEsSearchEditTextEdit)

        parent_layout.addWidget(self._es_search_edit)
        parent_layout.addWidget(self._es_icon_view)

    def _onEsIconClicked(self, index: QModelIndex):
        icon_name = self._es_icon_model.getIconNameFromModelIndex(index)
        if not icon_name:
            return
        from PyQt5.QtWidgets import QApplication

        QApplication.clipboard().setText(icon_name)
        ElaMessageBar.success(
            ElaMessageBarType.PositionPolicy.Top,
            "复制完成",
            f"{icon_name}已被复制到剪贴板",
            1000,
            self,
        )

    def _onEsSearchEditTextEdit(self, searchText: str):
        if not searchText:
            self._es_icon_model.setIsSearchMode(False)
            self._es_icon_model.setSearchKeyList([])
            self._es_icon_view.clearSelection()
            self._es_icon_view.viewport().update()
            return

        all_icon_names = self._svg_loader.iconNames()
        search_key_list = []
        for name in all_icon_names:
            if searchText.lower() in name.lower():
                search_key_list.append(name)

        self._es_icon_model.setIsSearchMode(True)
        self._es_icon_model.setSearchKeyList(search_key_list)
        self._es_icon_view.clearSelection()
        self._es_icon_view.scrollTo(self._es_icon_model.index(0, 0))
        self._es_icon_view.viewport().update()
