"""
[pyqt5_ela_pro] 动画与图标组件页面

合并了以下来源的组件:
- pyqt5_ela_pro: 动画、SVG图标组件
- PyQt5ElaWidgetTools: 图标组件
"""

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QListView, QWidget
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5ElaWidgetTools import (
    ElaText,
    ElaIconButton,
    ElaIconType,
    ElaListView,
    ElaLineEdit,
    ElaMessageBar,
    ElaMessageBarType,
    ElaPushButton,
)
from pyqt5_ela_pro import (
    fade_in,
    fade_out,
    ElaAnimatedMixin,
    shake_window,
    ElaDialogBase,
    svg_to_icon,
    svg_to_pixmap,
    svg_icon_loader,
)
from pyqt5_ela_pro.svg_icon import (
    ElaSvgIconLoader,
    ElaSvgButton,
    ElaSvgIconButton,
)
from .base_page import ExamplePage
from .icon_model import T_IconModel
from .icon_delegate import T_IconDelegate
from .es_icon_model import EsIconModel
from .es_icon_delegate import EsIconDelegate


class _AnimatedDemoDialog(ElaAnimatedMixin, ElaDialogBase):
    def __init__(self, parent=None):
        super().__init__("ElaAnimatedMixin 演示", parent)
        content_widget = QWidget(self)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 10, 0, 0)
        info = ElaText(
            "通过 ElaAnimatedMixin 继承获得 fade_in() / fade_out()\n对话框自身拥有动画方法",
            content_widget,
        )
        info.setTextPixelSize(14)
        content_layout.addWidget(info)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        shake_btn = ElaPushButton("抖动", content_widget)
        shake_btn.setFixedWidth(80)
        shake_btn.clicked.connect(self.shake)
        btn_layout.addWidget(shake_btn)
        content_layout.addLayout(btn_layout)
        self.setParamWidget(content_widget)
        self.setFixedHeight(300)
        self.fade_in()

    def shake(self):
        shake_window(self)


class AnimationIconPage(ExamplePage):
    """动画与图标组件页面"""

    PAGE_TITLE = "动画与图标"

    def __init__(self, parent=None):
        self._svg_loader = None
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoAnimation(main_layout)
        self._demoIcon(main_layout)
        self._demoSvgIcon(main_layout)

    def _addInfoText(self, text, parent_layout):
        info = ElaText(text, self)
        info.setTextPixelSize(14)
        parent_layout.addWidget(info)

    def _demoAnimation(self, parent_layout):
        parent_layout.addWidget(self._createSectionHeader("=== ela_ext - 动画特效 ==="))
        self._demoFadeInOut(parent_layout)
        self._demoShakeWindow(parent_layout)
        self._demoAnimatedMixin(parent_layout)

    def _demoIcon(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("=== PyQt5ElaWidgetTools - 图标组件 ===")
        )
        self._demoIconBrowser(parent_layout)
        self._demoIconButtons(parent_layout)

    def _demoSvgIcon(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("=== ela_ext - SVG图标组件 ===")
        )
        self._demoSvgIconBrowser(parent_layout)
        self._demoEsButton(parent_layout)
        self._demoEsSvgButton(parent_layout)
        self._demoSvgFunctions(parent_layout)

    def _demoFadeInOut(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("01. ela_ext - fade_in / fade_out 淡入淡出动画")
        )
        self._addInfoText(
            "对任意 QWidget 执行淡入淡出动画，支持动画完成回调", parent_layout
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        fade_in_btn = ElaPushButton("淡入窗口", self)
        fade_in_btn.setFixedWidth(100)
        fade_in_btn.clicked.connect(self._onFadeIn)
        btn_layout.addWidget(fade_in_btn)
        fade_out_btn = ElaPushButton("淡出窗口", self)
        fade_out_btn.setFixedWidth(100)
        fade_out_btn.clicked.connect(self._onFadeOut)
        btn_layout.addWidget(fade_out_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoShakeWindow(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("02. ela_ext - shake_window 窗口抖动")
        )
        self._addInfoText("使窗口产生抖动效果，常用于错误提示", parent_layout)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        shake_btn = ElaPushButton("抖动窗口", self)
        shake_btn.setFixedWidth(100)
        shake_btn.clicked.connect(lambda: shake_window(self))
        btn_layout.addWidget(shake_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _demoAnimatedMixin(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("03. ela_ext - ElaAnimatedMixin 对话框动画混入")
        )
        self._addInfoText(
            "通过继承 ElaAnimatedMixin，对话框自动获得 fade_in() / fade_out() 方法",
            parent_layout,
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        open_btn = ElaPushButton("打开动画对话框", self)
        open_btn.setFixedWidth(120)
        open_btn.clicked.connect(self._openAnimatedDialog)
        btn_layout.addWidget(open_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _onFadeIn(self):
        fade_in(self)

    def _onFadeOut(self):
        fade_out(self)

    def _openAnimatedDialog(self):
        dialog = _AnimatedDemoDialog(self)
        dialog.exec_()

    def _demoIconBrowser(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "01. PyQt5ElaWidgetTools - 图标浏览器 所有可用图标"
            )
        )
        self._addInfoText("一堆常用图标被放置于此，左键单击以复制其枚举", parent_layout)
        parent_layout.addSpacing(10)
        self._iconKeys = [attr for attr in dir(ElaIconType) if not attr.startswith("_")]
        self._iconView = ElaListView(self)
        self._iconView.setIsTransparent(True)
        self._iconView.setFlow(QListView.Flow.LeftToRight)
        self._iconView.setViewMode(QListView.ViewMode.IconMode)
        self._iconView.setResizeMode(QListView.ResizeMode.Adjust)
        self._iconView.clicked.connect(self._onIconClicked)
        self._iconModel = T_IconModel(self)
        self._iconDelegate = T_IconDelegate(self)
        self._iconView.setModel(self._iconModel)
        self._iconView.setItemDelegate(self._iconDelegate)
        self._iconView.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._searchEdit = ElaLineEdit(self)
        self._searchEdit.setPlaceholderText("搜索图标")
        self._searchEdit.setFixedSize(300, 35)
        self._searchEdit.textEdited.connect(self._onSearchEditTextEdit)
        parent_layout.addWidget(self._searchEdit)
        parent_layout.addWidget(self._iconView)
        parent_layout.addSpacing(30)

    def _onIconClicked(self, index: QModelIndex):
        iconName = self._iconModel.getIconNameFromModelIndex(index)
        if not iconName:
            return
        from PyQt5.QtWidgets import QApplication

        QApplication.clipboard().setText(iconName)
        ElaMessageBar.success(
            ElaMessageBarType.PositionPolicy.Top,
            "复制完成",
            f"{iconName}已被复制到剪贴板",
            1000,
            self,
        )

    def _onSearchEditTextEdit(self, searchText: str):
        if not searchText:
            self._iconModel.setIsSearchMode(False)
            self._iconModel.setSearchKeyList([])
            self._iconView.clearSelection()
            self._iconView.viewport().update()
            return
        searchKeyList = []
        for key in self._iconKeys:
            if key.lower().__contains__(searchText.lower()):
                searchKeyList.append(key)
        self._iconModel.setIsSearchMode(True)
        self._iconModel.setSearchKeyList(searchKeyList)
        self._iconView.clearSelection()
        self._iconView.scrollTo(self._iconModel.index(0, 0))
        self._iconView.viewport().update()

    def _demoIconButtons(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("02. PyQt5ElaWidgetTools - 图标按钮 带图标的按钮")
        )
        self._addInfoText("图标按钮组件演示", parent_layout)
        parent_layout.addSpacing(10)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        icon_btn1 = ElaIconButton(ElaIconType.IconName.FloppyDisk, 16, self)
        icon_btn1.setFixedSize(40, 40)
        btn_layout.addWidget(icon_btn1)
        icon_btn2 = ElaIconButton(ElaIconType.IconName.Pencil, 16, self)
        icon_btn2.setFixedSize(40, 40)
        btn_layout.addWidget(icon_btn2)
        icon_btn3 = ElaIconButton(ElaIconType.IconName.Trash, 16, self)
        icon_btn3.setFixedSize(40, 40)
        btn_layout.addWidget(icon_btn3)
        icon_btn4 = ElaIconButton(ElaIconType.IconName.MagnifyingGlass, 16, self)
        icon_btn4.setFixedSize(40, 40)
        btn_layout.addWidget(icon_btn4)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)

    def _getSvgLoader(self):
        if self._svg_loader is None:
            self._svg_loader = ElaSvgIconLoader()
            self._svg_loader.loadFromPackage("fluent_ui_icon_regular.icons")
        return self._svg_loader

    def _demoSvgIconBrowser(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("01. ela_ext - SVG图标浏览器 所有可用图标")
        )
        self._addInfoText("点击图标以复制其名称", parent_layout)
        parent_layout.addSpacing(10)
        from PyQt5.QtCore import Qt, QModelIndex as QModelIndex2

        svg_list_view = ElaListView(self)
        svg_list_view.setIsTransparent(True)
        svg_list_view.setFlow(QListView.Flow.LeftToRight)
        svg_list_view.setViewMode(QListView.ViewMode.IconMode)
        svg_list_view.setFixedHeight(400)
        svg_list_view.setResizeMode(QListView.ResizeMode.Adjust)
        svg_list_view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        loader = self._getSvgLoader()
        icon_names = loader.iconNames()
        svg_model = EsIconModel(icon_names, self)
        svg_delegate = EsIconDelegate(loader, self)
        svg_list_view.setModel(svg_model)
        svg_list_view.setItemDelegate(svg_delegate)
        svg_list_view.clicked.connect(
            lambda index: self._onSvgIconClicked(index, loader)
        )
        svg_search_edit = ElaLineEdit(self)
        svg_search_edit.setPlaceholderText("搜索图标")
        svg_search_edit.setFixedSize(300, 35)
        svg_search_edit.textEdited.connect(
            lambda text: self._onSvgSearchEditTextEdit(text, svg_model, svg_list_view)
        )
        parent_layout.addWidget(svg_search_edit)
        parent_layout.addWidget(svg_list_view)

    def _onSvgIconClicked(self, index: QModelIndex, loader):
        icon_name = index.data()
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

    def _onSvgSearchEditTextEdit(self, searchText: str, model, view):
        if not searchText:
            model.setIsSearchMode(False)
            model.setSearchKeyList([])
            view.clearSelection()
            view.viewport().update()
            return
        loader = self._getSvgLoader()
        all_icon_names = loader.iconNames()
        search_key_list = []
        for name in all_icon_names:
            if searchText.lower() in name.lower():
                search_key_list.append(name)
        model.setIsSearchMode(True)
        model.setSearchKeyList(search_key_list)
        view.clearSelection()
        view.scrollTo(model.index(0, 0))
        view.viewport().update()

    def _demoEsButton(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "02. ela_ext - ElaSvgIconButton 基础 SVG 图标按钮"
            )
        )
        self._addInfoText(
            "继承 ElaPushButton 的外观，使用 SVG 图标，图标颜色与文字一致",
            parent_layout,
        )
        parent_layout.addSpacing(10)
        loader = self._getSvgLoader()
        icons_row_layout = QHBoxLayout()
        icons_row_layout.setSpacing(15)
        from PyQt5ElaWidgetTools import ElaThemeType

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
            btn = ElaSvgIconButton(
                text,
                icon_name=name,
                theme_color=theme_color,
                parent=self,
            )
            btn.setFixedWidth(120)
            icons_row_layout.addWidget(btn)
        icons_row_layout.addStretch()
        parent_layout.addLayout(icons_row_layout)
        parent_layout.addSpacing(30)

    def _demoSvgFunctions(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader(
                "04. ela_ext - svg_to_icon / svg_to_pixmap / svg_icon_loader"
            )
        )
        self._addInfoText(
            "将 SVG 数据转换为 QIcon/QPixmap，获取全局图标加载器",
            parent_layout,
        )
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        icon_btn = ElaPushButton("svg_to_icon", self)
        icon_btn.setFixedWidth(120)
        icon_btn.clicked.connect(self._onDemoSvgToIcon)
        btn_layout.addWidget(icon_btn)

        pixmap_btn = ElaPushButton("svg_to_pixmap", self)
        pixmap_btn.setFixedWidth(120)
        pixmap_btn.clicked.connect(self._onDemoSvgToPixmap)
        btn_layout.addWidget(pixmap_btn)

        loader_btn = ElaPushButton("svg_icon_loader", self)
        loader_btn.setFixedWidth(120)
        loader_btn.clicked.connect(self._onDemoSvgLoader)
        btn_layout.addWidget(loader_btn)

        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)
        parent_layout.addSpacing(20)

    def _onDemoSvgToIcon(self):
        try:
            loader = self._getSvgLoader()
            names = loader.iconNames()
            if names:
                icon = svg_to_icon(names[0], size=48)
                from PyQt5ElaWidgetTools import ElaMessageBar, ElaMessageBarType
                ElaMessageBar.success(
                    ElaMessageBarType.PositionPolicy.Top,
                    "svg_to_icon",
                    f"已将 '{names[0]}' 转换为 QIcon（48x48）",
                    3000, self,
                )
        except Exception as e:
            from PyQt5ElaWidgetTools import ElaMessageBar, ElaMessageBarType
            ElaMessageBar.error(
                ElaMessageBarType.PositionPolicy.Top,
                "svg_to_icon",
                f"失败: {e}",
                3000, self,
            )

    def _onDemoSvgToPixmap(self):
        try:
            loader = self._getSvgLoader()
            names = loader.iconNames()
            if names:
                pixmap = svg_to_pixmap(names[0], size=48)
                from PyQt5ElaWidgetTools import ElaMessageBar, ElaMessageBarType
                ElaMessageBar.success(
                    ElaMessageBarType.PositionPolicy.Top,
                    "svg_to_pixmap",
                    f"已将 '{names[0]}' 转换为 QPixmap（{pixmap.width()}x{pixmap.height()}）",
                    3000, self,
                )
        except Exception as e:
            from PyQt5ElaWidgetTools import ElaMessageBar, ElaMessageBarType
            ElaMessageBar.error(
                ElaMessageBarType.PositionPolicy.Top,
                "svg_to_pixmap",
                f"失败: {e}",
                3000, self,
            )

    def _onDemoSvgLoader(self):
        loader = svg_icon_loader()
        count = len(loader)
        from PyQt5ElaWidgetTools import ElaMessageBar, ElaMessageBarType
        ElaMessageBar.success(
            ElaMessageBarType.PositionPolicy.Top,
            "svg_icon_loader",
            f"全局图标加载器已获取，共 {count} 个图标",
            3000, self,
        )

    def _demoEsSvgButton(self, parent_layout):
        parent_layout.addWidget(
            self._createSectionHeader("03. ela_ext - ElaSvgButton 悬浮/点击主题色效果")
        )
        self._addInfoText("鼠标悬浮和点击时显示半透明主题色背景效果", parent_layout)
        parent_layout.addSpacing(10)
        loader = self._getSvgLoader()
        icons_row_layout = QHBoxLayout()
        icons_row_layout.setSpacing(15)
        from PyQt5ElaWidgetTools import ElaThemeType

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
                icon_name=name,
                theme_color=theme_color,
                parent=self,
            )
            btn.setFixedWidth(120)
            icons_row_layout.addWidget(btn)
        icons_row_layout.addStretch()
        parent_layout.addLayout(icons_row_layout)
        parent_layout.addSpacing(20)
