from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QAction, QMenu
from PyQt5ElaWidgetTools import (
    ElaWindow,
    ElaContentDialog,
    ElaMenuBar,
    ElaIconType,
    ElaAppBarType,
    ElaMenu,
    ElaToolBar,
    ElaToolButton,
    ElaProgressBar,
    ElaDockWidget,
    ElaStatusBar,
    ElaText,
    ElaNavigationType,
    ElaProgressRing,
    ElaSuggestBox,
    eTheme,
    ElaThemeType,
    ElaWindowType,
ElaNavigationRouter
)

from ExamplePage.T_About import T_About
from ExamplePage.T_BaseComponents import T_BaseComponents
from ExamplePage.T_Card import T_Card
from ExamplePage.T_Graphics import T_Graphics
from ExamplePage.T_Home import T_Home
from ExamplePage.T_Icon import T_Icon
from ExamplePage.T_ListView import T_ListView
from ExamplePage.T_LogWidget import T_LogWidget
from ExamplePage.T_Navigation import T_Navigation
from ExamplePage.T_Popup import T_Popup
from ExamplePage.T_Setting import T_Setting
from ExamplePage.T_TableView import T_TableView
from ExamplePage.T_TreeView import T_TreeView
from ExamplePage.T_UpdateWidget import T_UpdateWidget


class MainWindow(ElaWindow):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.initWindow()
        self.initEdgeLayout()
        self.initContent()
        _closeDialog = ElaContentDialog(self)
        _closeDialog.rightButtonClicked.connect(self.closeWindow)
        _closeDialog.middleButtonClicked.connect(
            lambda: (_closeDialog.close(), self.showMinimized())
        )
        self.setIsDefaultClosed(False)
        self.closeButtonClicked.connect(lambda: _closeDialog.exec())
        self.moveToCenter()

    def initWindow(self):
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.resize(1200, 740)

        self.setUserInfoCardPixmap(
            QPixmap(r"C:\Users\11737\Pictures\冥契\過去未来1.jpg")
        )
        self.setUserInfoCardTitle("Ela Tool")
        self.setUserInfoCardSubTitle("Liniyous@gmail.com")
        self.setWindowTitle("ElaWidgetTool")

        centralStack = ElaText("这是一个主窗口堆栈页面", self)
        centralStack.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        centralStack.setTextPixelSize(32)
        centralStack.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addCentralWidget(centralStack)

        # 自定义AppBar菜单
        appBarMenu = ElaMenu(self)
        appBarMenu.setMenuItemHeight(27)
        appBarMenu.addAction("跳转到一级主要堆栈").triggered.connect(
            lambda: self.setCurrentStackIndex(0)
        )
        appBarMenu.addAction("跳转到二级主要堆栈").triggered.connect(
            lambda: self.setCurrentStackIndex(1)
        )
        appBarMenu.addAction("更改页面切换特效(Scale)").triggered.connect(
            lambda: self.setStackSwitchMode(ElaWindowType.StackSwitchMode.Scale)
        )

        from PyQt5ElaWidgetTools import ElaWindowType

        appBarMenu.addElaIconAction(
            ElaIconType.IconName.GearComplex, "自定义主窗口设置"
        ).triggered.connect(lambda: self.navigation(self._settingKey))
        appBarMenu.addSeparator()
        appBarMenu.addElaIconAction(
            ElaIconType.IconName.MoonStars, "更改项目主题"
        ).triggered.connect(
            lambda: eTheme.setThemeMode(
                ElaThemeType.ThemeMode.Dark
                if eTheme.getThemeMode() == ElaThemeType.ThemeMode.Light
                else ElaThemeType.ThemeMode.Light
            )
        )
        appBarMenu.addAction("使用原生菜单").triggered.connect(
            lambda: self.setCustomMenu(None)
        )
        self.setCustomMenu(appBarMenu)

        # 堆栈独立自定义窗口
        centralCustomWidget = QWidget(self)
        centralCustomWidgetLayout = QHBoxLayout(centralCustomWidget)
        centralCustomWidgetLayout.setContentsMargins(13, 15, 9, 6)

        leftButton = ElaToolButton(self)
        leftButton.setElaIcon(ElaIconType.IconName.AngleLeft)
        leftButton.setEnabled(False)
        leftButton.clicked.connect(
            lambda: ElaNavigationRouter.getInstance().navigationRouteBack()
        )

        rightButton = ElaToolButton(self)
        rightButton.setElaIcon(ElaIconType.IconName.AngleRight)
        rightButton.setEnabled(False)
        rightButton.clicked.connect(
            lambda: ElaNavigationRouter.getInstance().navigationRouteForward()
        )

        ElaNavigationRouter.getInstance().navigationRouterStateChanged.connect(
            lambda routeMode: self._onNavigationRouterStateChanged(
                routeMode, leftButton, rightButton
            )
        )

        self._windowSuggestBox = ElaSuggestBox(self)
        self._windowSuggestBox.setFixedHeight(32)
        self._windowSuggestBox.setPlaceholderText("搜索关键字")
        self._windowSuggestBox.suggestionClicked.connect(
            lambda suggestData: self.navigation(
                suggestData.getSuggestData().get("ElaPageKey", "")
            )
        )

        progressBusyRingText = ElaText("系统运行中", self)
        progressBusyRingText.setIsWrapAnywhere(False)
        progressBusyRingText.setTextPixelSize(15)

        progressBusyRing = ElaProgressRing(self)
        progressBusyRing.setBusyingWidth(4)
        progressBusyRing.setFixedSize(28, 28)
        progressBusyRing.setIsBusying(True)

        centralCustomWidgetLayout.addWidget(leftButton)
        centralCustomWidgetLayout.addWidget(rightButton)
        centralCustomWidgetLayout.addWidget(self._windowSuggestBox)
        centralCustomWidgetLayout.addStretch()
        centralCustomWidgetLayout.addWidget(progressBusyRingText)
        centralCustomWidgetLayout.addWidget(progressBusyRing)
        self.setCentralCustomWidget(centralCustomWidget)

    def initEdgeLayout(self):

        menuBar = ElaMenuBar(self)
        menuBar.setFixedHeight(30)
        customWidget = QWidget(self)
        customLayout = QVBoxLayout(customWidget)
        customLayout.setContentsMargins(0, 0, 0, 0)
        customLayout.addWidget(menuBar)
        customLayout.addStretch()
        self.setCustomWidget(ElaAppBarType.CustomArea.MiddleArea, customWidget)
        # self.setCustomWidgetMaximumWidth(500)

        menuBar.addElaIconAction(ElaIconType.IconName.AtomSimple, "动作菜单")
        iconMenu = menuBar.addMenu(ElaIconType.IconName.Aperture, "图标菜单")
        iconMenu.setMenuItemHeight(27)
        iconMenu.addElaIconAction(
            ElaIconType.IconName.BoxCheck,
            "排序方式",
            QKeySequence.StandardKey.SelectAll,
        )
        iconMenu.addElaIconAction(ElaIconType.IconName.Copy, "复制")
        iconMenu.addElaIconAction(ElaIconType.IconName.MagnifyingGlassPlus, "显示设置")
        iconMenu.addSeparator()
        iconMenu.addElaIconAction(ElaIconType.IconName.ArrowRotateRight, "刷新")
        iconMenu.addElaIconAction(ElaIconType.IconName.ArrowRotateLeft, "撤销")
        menuBar.addSeparator()
        shortCutMenu = ElaMenu("快捷菜单(&A)", self)
        shortCutMenu.setMenuItemHeight(27)
        shortCutMenu.addElaIconAction(
            ElaIconType.IconName.BoxCheck, "排序方式", QKeySequence.StandardKey.Find
        )
        shortCutMenu.addElaIconAction(ElaIconType.IconName.Copy, "复制")
        shortCutMenu.addElaIconAction(
            ElaIconType.IconName.MagnifyingGlassPlus, "显示设置"
        )
        shortCutMenu.addSeparator()
        shortCutMenu.addElaIconAction(ElaIconType.IconName.ArrowRotateRight, "刷新")
        shortCutMenu.addElaIconAction(ElaIconType.IconName.ArrowRotateLeft, "撤销")
        menuBar.addMenu(shortCutMenu)

        menuBar.addMenu("样例菜单(&B)").addElaIconAction(
            ElaIconType.IconName.ArrowRotateRight, "样例选项"
        )
        menuBar.addMenu("样例菜单(&C)").addElaIconAction(
            ElaIconType.IconName.ArrowRotateRight, "样例选项"
        )
        menuBar.addMenu("样例菜单(&E)").addElaIconAction(
            ElaIconType.IconName.ArrowRotateRight, "样例选项"
        )
        menuBar.addMenu("样例菜单(&F)").addElaIconAction(
            ElaIconType.IconName.ArrowRotateRight, "样例选项"
        )
        menuBar.addMenu("样例菜单(&G)").addElaIconAction(
            ElaIconType.IconName.ArrowRotateRight, "样例选项"
        )

        toolBar = ElaToolBar("工具栏", self)
        toolBar.setAllowedAreas(
            Qt.ToolBarArea.TopToolBarArea | Qt.ToolBarArea.BottomToolBarArea
        )
        toolBar.setToolBarSpacing(3)
        toolBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        toolBar.setIconSize(QSize(25, 25))
        toolButton1 = ElaToolButton(self)
        toolButton1.setElaIcon(ElaIconType.IconName.BadgeCheck)
        toolBar.addWidget(toolButton1)
        toolButton2 = ElaToolButton(self)
        toolButton2.setElaIcon(ElaIconType.IconName.ChartUser)
        toolBar.addWidget(toolButton2)
        toolBar.addSeparator()
        toolButton3 = ElaToolButton(self)
        toolButton3.setElaIcon(ElaIconType.IconName.Bluetooth)
        toolButton3.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolButton3.setText("Bluetooth")
        toolBar.addWidget(toolButton3)
        toolButton4 = ElaToolButton(self)
        toolButton4.setElaIcon(ElaIconType.IconName.BringFront)
        toolBar.addWidget(toolButton4)
        toolBar.addSeparator()
        toolButton5 = ElaToolButton(self)
        toolButton5.setElaIcon(ElaIconType.IconName.ChartSimple)
        toolBar.addWidget(toolButton5)
        toolButton6 = ElaToolButton(self)
        toolButton6.setElaIcon(ElaIconType.IconName.FaceClouds)
        toolBar.addWidget(toolButton6)
        toolButton8 = ElaToolButton(self)
        toolButton8.setElaIcon(ElaIconType.IconName.Aperture)
        toolBar.addWidget(toolButton8)
        toolButton9 = ElaToolButton(self)
        toolButton9.setElaIcon(ElaIconType.IconName.ChartMixed)
        toolBar.addWidget(toolButton9)
        toolButton10 = ElaToolButton(self)
        toolButton10.setElaIcon(ElaIconType.IconName.Coins)
        toolBar.addWidget(toolButton10)
        toolButton11 = ElaToolButton(self)
        toolButton11.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolButton11.setElaIcon(ElaIconType.IconName.AlarmPlus)
        toolButton11.setText("AlarmPlus")
        toolBar.addWidget(toolButton11)
        toolButton12 = ElaToolButton(self)
        toolButton12.setElaIcon(ElaIconType.IconName.Crown)
        toolBar.addWidget(toolButton12)
        test = QAction(self)
        test.setMenu(QMenu(self))

        progressBar = ElaProgressBar(self)
        progressBar.setMinimum(0)
        progressBar.setMaximum(0)
        progressBar.setFixedWidth(350)
        toolBar.addWidget(progressBar)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolBar)

        logDockWidget = ElaDockWidget("日志信息", self)
        logDockWidget.setWidget(T_LogWidget(self))
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, logDockWidget)
        self.resizeDocks([logDockWidget], [200], Qt.Orientation.Horizontal)

        updateDockWidget = ElaDockWidget("更新内容", self)
        updateDockWidget.setWidget(T_UpdateWidget(self))
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, updateDockWidget)
        self.resizeDocks([updateDockWidget], [200], Qt.Orientation.Horizontal)

        statusBar = ElaStatusBar(self)
        statusText = ElaText("初始化成功！", self)
        statusText.setTextPixelSize(14)
        statusBar.addWidget(statusText)
        self.setStatusBar(statusBar)

    def initContent(self):
        self._homePage = T_Home(self)
        self._elaScreenPage = QWidget()  # T_ElaScreen(self) - Windows only
        self._iconPage = T_Icon(self)
        self._baseComponentsPage = T_BaseComponents(self)
        self._graphicsPage = T_Graphics(self)
        self._navigationPage = T_Navigation(self)
        self._popupPage = T_Popup(self)
        self._cardPage = T_Card(self)
        self._listViewPage = T_ListView(self)
        self._tableViewPage = T_TableView(self)
        self._treeViewPage = T_TreeView(self)
        self._settingPage = T_Setting(self)

        self.addPageNode("HOME", self._homePage, ElaIconType.IconName.House)

        # Windows DXGI (only on Windows)
        _, testKey_1 = self.addExpanderNode("ElaDxgi", ElaIconType.IconName.TvMusic)
        self.addPageNodeKeyPoints(
            "ElaScreen",
            self._elaScreenPage,
            testKey_1,
            3,
            ElaIconType.IconName.ObjectGroup,
        )

        self.addPageNode(
            "ElaBaseComponents",
            self._baseComponentsPage,
            ElaIconType.IconName.CabinetFiling,
        )

        _, _viewKey = self.addExpanderNode(
            "ElaView", ElaIconType.IconName.CameraViewfinder
        )
        self.addPageNodeKeyPoints(
            "ElaListView", self._listViewPage, _viewKey, 9, ElaIconType.IconName.List
        )
        self.addPageNode(
            "ElaTableView", self._tableViewPage, _viewKey, ElaIconType.IconName.Table
        )
        self.addPageNode(
            "ElaTreeView", self._treeViewPage, _viewKey, ElaIconType.IconName.ListTree
        )
        self.expandNavigationNode(_viewKey)

        self.addPageNodeKeyPoints(
            "ElaGraphics", self._graphicsPage, 9, ElaIconType.IconName.Paintbrush
        )
        self.addPageNode("ElaCard", self._cardPage, ElaIconType.IconName.Cards)
        self.addPageNode(
            "ElaNavigation", self._navigationPage, ElaIconType.IconName.LocationArrow
        )
        self.addPageNode("ElaPopup", self._popupPage, ElaIconType.IconName.Envelope)
        self.addPageNodeKeyPoints(
            "ElaIcon", self._iconPage, 99, ElaIconType.IconName.FontCase
        )

        # Test nodes
        _, testKey_2 = self.addExpanderNode(
            "TEST_EXPAND_NODE1", ElaIconType.IconName.Acorn
        )
        _, testKey_1 = self.addExpanderNode(
            "TEST_EXPAND_NODE2", testKey_2, ElaIconType.IconName.Acorn
        )
        self.addPageNode(
            "TEST_NODE3", QWidget(self), testKey_1, ElaIconType.IconName.Acorn
        )
        for i in range(10):
            _, testKey_1 = self.addExpanderNode(
                f"TEST_EXPAND_NODE{i + 4}", testKey_2, ElaIconType.IconName.Acorn
            )
        _, testKey_1 = self.addExpanderNode(
            "TEST_EXPAND_NODE14", ElaIconType.IconName.Acorn
        )
        _, testKey_1 = self.addExpanderNode(
            "TEST_EXPAND_NODE5", ElaIconType.IconName.Acorn
        )
        _, testKey_1 = self.addExpanderNode(
            "TEST_EXPAND_NODE16", ElaIconType.IconName.Acorn
        )

        _, _aboutKey = self.addFooterNode("About", None, 0, ElaIconType.IconName.User)
        self._aboutPage = T_About()

        self._aboutPage.hide()

        def __(nodeType: ElaNavigationType.NavigationNodeType, nodeKey: str):
            if _aboutKey == nodeKey:
                self._aboutPage.setFixedSize(400, 400)
                self._aboutPage.show()

        self.navigationNodeClicked.connect(__)
        _, _settingKey = self.addFooterNode(
            "Setting", self._settingPage, 0, ElaIconType.IconName.GearComplex
        )

        self.userInfoCardClicked.connect(
            lambda: self.navigation(self._homePage.property("ElaPageKey"))
        )

        # Connect T_Home signals
        self._homePage.elaScreenNavigation.connect(
            lambda: self.navigation(self._elaScreenPage.property("ElaPageKey"))
        )
        self._homePage.elaBaseComponentNavigation.connect(
            lambda: self.navigation(self._baseComponentsPage.property("ElaPageKey"))
        )
        self._homePage.elaSceneNavigation.connect(
            lambda: self.navigation(self._graphicsPage.property("ElaPageKey"))
        )
        self._homePage.elaIconNavigation.connect(
            lambda: self.navigation(self._iconPage.property("ElaPageKey"))
        )
        self._homePage.elaCardNavigation.connect(
            lambda: self.navigation(self._cardPage.property("ElaPageKey"))
        )

    # #ifdef Q_OS_WIN
    #     connect(_homePage, &T_Home::elaScreenNavigation, self, [=]() {
    #         self.navigation(_elaScreenPage.property("ElaPageKey").toString());
    #     });
    # #endif
    #     connect(_homePage, &T_Home::elaBaseComponentNavigation, self, [=]() {
    #         self.navigation(_baseComponentsPage.property("ElaPageKey").toString());
    #     });
    #     connect(_homePage, &T_Home::elaSceneNavigation, self, [=]() {
    #         self.navigation(_graphicsPage.property("ElaPageKey").toString());
    #     });
    #     connect(_homePage, &T_Home::elaIconNavigation, self, [=]() {
    #         self.navigation(_iconPage.property("ElaPageKey").toString());
    #     });
    #     connect(_homePage, &T_Home::elaCardNavigation, self, [=]() {
    #         self.navigation(_cardPage.property("ElaPageKey").toString());
    #     });
    #     qDebug() << "已注册的事件列表" << ElaEventBus::getInstance().getRegisteredEventsName();

    def _onNavigationRouterStateChanged(self, routeMode, leftButton, rightButton):
        from PyQt5ElaWidgetTools import ElaNavigationRouterType

        if routeMode == ElaNavigationRouterType.RouteMode.BackValid:
            leftButton.setEnabled(True)
        elif routeMode == ElaNavigationRouterType.RouteMode.BackInvalid:
            leftButton.setEnabled(False)
        elif routeMode == ElaNavigationRouterType.RouteMode.ForwardValid:
            rightButton.setEnabled(True)
        elif routeMode == ElaNavigationRouterType.RouteMode.ForwardInvalid:
            rightButton.setEnabled(False)
