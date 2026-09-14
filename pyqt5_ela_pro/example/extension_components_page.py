"""
[pyqt5_ela_pro] 扩展组件展示页面

包含 pyqt5_ela_pro 自定义扩展组件。
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from PyQt5ElaWidgetTools import ElaText, ElaPushButton, ElaIconType, ElaFlowLayout
from pyqt5_ela_pro import (
    ElaThemeWidget,
    ElaPasswordEdit,
    ElaDivider,
    ElaGroupBox,
    ElaInfoBadge,
    ElaChip,
    ElaSteps,
    ElaRatingControl,
    ElaPagination,
    ElaTimeline,
    ElaUploadArea,
    ElaSpotlight,
    create_ela_splitter,
)
from .base_page import ExamplePage


class ExtensionComponentsPage(ExamplePage):
    """pyqt5_ela_pro 扩展组件页面"""

    PAGE_TITLE = "扩展组件"

    def __init__(self, parent=None):
        super().__init__(parent)

    def _addDemoContent(self, main_layout):
        self._demoPasswordEdit(main_layout)
        self._demoSplitter(main_layout)
        self._demoDivider(main_layout)
        self._demoGroupBox(main_layout)
        self._demoInfoBadge(main_layout)
        self._demoChip(main_layout)
        self._demoSteps(main_layout)
        self._demoRatingControl(main_layout)
        self._demoPagination(main_layout)
        self._demoTimeline(main_layout)
        self._demoUploadArea(main_layout)
        self._demoSpotlight(main_layout)
        self._demoFlowLayout(main_layout)

    def _demoPasswordEdit(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "01. pyqt5_ela_pro - ElaPasswordEdit 密码输入框", self._demoPasswordEdit
            )
        )
        self._addInfoText("带密码可见切换和底部强调线动画的密码输入框", parent_layout)
        edit_layout = QHBoxLayout()
        edit_layout.setSpacing(15)
        pwd = ElaPasswordEdit(self)
        pwd.setPlaceholderText("请输入密码")
        pwd.setFixedWidth(200)
        edit_layout.addWidget(pwd)
        pwd_disabled = ElaPasswordEdit(self)
        pwd_disabled.setPlaceholderText("禁用状态")
        pwd_disabled.setFixedWidth(200)
        pwd_disabled.setEnabled(False)
        edit_layout.addWidget(pwd_disabled)
        edit_layout.addStretch()
        parent_layout.addLayout(edit_layout)
        parent_layout.addSpacing(20)

    def _demoSplitter(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "02. pyqt5_ela_pro - ElaSplitter 分隔器", self._demoSplitter
            )
        )
        self._addInfoText(
            "ELA 主题风格的分割器，支持水平和垂直方向，自动响应主题切换",
            parent_layout,
        )
        widget1 = ElaThemeWidget(self)
        widget1.setMinimumSize(50, 50)
        layout1 = QVBoxLayout(widget1)
        text1 = ElaText("面板 1", widget1)
        text1.setAlignment(Qt.AlignCenter)
        layout1.addWidget(text1)

        widget2 = ElaThemeWidget(self)
        widget2.setMinimumSize(50, 50)
        layout2 = QVBoxLayout(widget2)
        text2 = ElaText("面板 2", widget2)
        text2.setAlignment(Qt.AlignCenter)
        layout2.addWidget(text2)

        widget3 = ElaThemeWidget(self)
        widget3.setMinimumSize(50, 50)
        layout3 = QVBoxLayout(widget3)
        text3 = ElaText("面板 3", widget3)
        text3.setAlignment(Qt.AlignCenter)
        layout3.addWidget(text3)

        splitter = create_ela_splitter([widget1, widget2, widget3], Qt.Horizontal)
        splitter.setMinimumHeight(80)
        parent_layout.addWidget(splitter)
        parent_layout.addSpacing(12)

        # Vertical splitter
        v1 = ElaThemeWidget(self)
        v1.setMinimumSize(50, 50)
        l1 = QVBoxLayout(v1)
        t1 = ElaText("面板 A", v1)
        t1.setAlignment(Qt.AlignCenter)
        l1.addWidget(t1)

        v2 = ElaThemeWidget(self)
        v2.setMinimumSize(50, 50)
        l2 = QVBoxLayout(v2)
        t2 = ElaText("面板 B", v2)
        t2.setAlignment(Qt.AlignCenter)
        l2.addWidget(t2)

        vsplitter = create_ela_splitter([v1, v2], Qt.Vertical)
        vsplitter.setMinimumHeight(160)
        parent_layout.addWidget(vsplitter)
        parent_layout.addSpacing(20)

    def _demoDivider(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "03. pyqt5_ela_pro - ElaDivider 分割线", self._demoDivider
            )
        )
        self._addInfoText(
            "Ant Design 风格分割线，支持水平/垂直、带文字、实线/虚线",
            parent_layout,
        )
        parent_layout.addSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(20)
        for t, o in [("Left", "left"), ("Center", "center"), ("Right", "right")]:
            col = QVBoxLayout()
            lbl = ElaText(t, self)
            lbl.setTextPixelSize(12)
            col.addWidget(lbl)
            col.addWidget(ElaDivider(text=t, orientation=o, parent=self))
            row.addLayout(col)
        row.addStretch()
        parent_layout.addLayout(row)
        parent_layout.addSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(20)
        col = QVBoxLayout()
        l1 = ElaText("Plain", self)
        l1.setTextPixelSize(12)
        col.addWidget(l1)
        col.addWidget(ElaDivider(parent=self))
        row.addLayout(col)
        col = QVBoxLayout()
        l2 = ElaText("Dashed", self)
        l2.setTextPixelSize(12)
        col.addWidget(l2)
        col.addWidget(ElaDivider(variant="dashed", parent=self))
        row.addLayout(col)
        col = QVBoxLayout()
        l3 = ElaText("Dashed w/ text", self)
        l3.setTextPixelSize(12)
        col.addWidget(l3)
        col.addWidget(ElaDivider(text="OR", variant="dashed", parent=self))
        row.addLayout(col)
        row.addStretch()
        parent_layout.addLayout(row)
        parent_layout.addSpacing(12)

        row = QHBoxLayout()
        row.setSpacing(20)
        info = ElaText("Vertical:", self)
        info.setTextPixelSize(12)
        row.addWidget(info)
        for t, o in [("Top", "top"), ("Center", "center"), ("Bottom", "bottom")]:
            w = QWidget(self)
            w.setFixedSize(60, 100)
            wl = QHBoxLayout(w)
            wl.addStretch()
            wl.addWidget(ElaDivider(text=t, orientation=o, vertical=True, parent=w))
            wl.addStretch()
            row.addWidget(w)
        row.addStretch()
        parent_layout.addLayout(row)
        parent_layout.addSpacing(20)

    def _demoGroupBox(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "04. pyqt5_ela_pro - ElaGroupBox 分组框", self._demoGroupBox
            )
        )
        self._addInfoText(
            "Ant Design 风格分组框，圆角边框 + 居中标题，支持放置子控件",
            parent_layout,
        )
        parent_layout.addSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(20)

        gb1 = ElaGroupBox("基本信息", parent=self)
        gb1.setFixedSize(220, 160)
        l1 = QVBoxLayout(gb1)
        l1.setContentsMargins(12, 20, 12, 12)
        l1.setSpacing(6)
        name_label = ElaText("姓名: 张三", gb1)
        name_label.setTextPixelSize(13)
        l1.addWidget(name_label)
        age_label = ElaText("年龄: 28", gb1)
        age_label.setTextPixelSize(13)
        l1.addWidget(age_label)
        city_label = ElaText("城市: 北京", gb1)
        city_label.setTextPixelSize(13)
        l1.addWidget(city_label)
        row.addWidget(gb1)

        gb2 = ElaGroupBox("联系方式", parent=self)
        gb2.setFixedSize(220, 160)
        l2 = QVBoxLayout(gb2)
        l2.setContentsMargins(12, 20, 12, 12)
        l2.setSpacing(6)
        email_label = ElaText("邮箱: user@example.com", gb2)
        email_label.setTextPixelSize(13)
        l2.addWidget(email_label)
        phone_label = ElaText("电话: 138-0000-0000", gb2)
        phone_label.setTextPixelSize(13)
        l2.addWidget(phone_label)
        row.addWidget(gb2)

        row.addStretch()
        parent_layout.addLayout(row)
        parent_layout.addSpacing(20)

    def _demoInfoBadge(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "05. pyqt5_ela_pro - ElaInfoBadge 角标", self._demoInfoBadge
            )
        )
        self._addInfoText(
            "5 种严重级别 (Attention / Informational / Success / Caution / Critical) × 3 种模式",
            parent_layout,
        )
        parent_layout.addSpacing(10)

        severity_names = [
            ("Attention", ElaInfoBadge.Severity.Attention),
            ("Informational", ElaInfoBadge.Severity.Informational),
            ("Success", ElaInfoBadge.Severity.Success),
            ("Caution", ElaInfoBadge.Severity.Caution),
            ("Critical", ElaInfoBadge.Severity.Critical),
        ]

        row = QHBoxLayout()
        row.setSpacing(30)
        for name, sev in severity_names:
            container = QWidget()
            cl = QVBoxLayout(container)
            cl.setContentsMargins(0, 0, 0, 0)
            cl.setSpacing(4)
            btn = ElaPushButton(name, container)
            btn.setFixedWidth(110)
            badge = ElaInfoBadge(parent=container)
            badge.setSeverity(sev)
            badge.attachTo(btn)
            cl.addWidget(btn)
            row.addWidget(container)
        row.addStretch()
        parent_layout.addLayout(row)
        parent_layout.addSpacing(12)

        row = QHBoxLayout()
        row.setSpacing(30)
        for i, (name, sev) in enumerate(severity_names):
            container = QWidget()
            cl = QVBoxLayout(container)
            cl.setContentsMargins(0, 0, 0, 0)
            cl.setSpacing(4)
            btn = ElaPushButton(name, container)
            btn.setFixedWidth(110)
            badge = ElaInfoBadge(value=(i + 1) * 20, parent=container)
            badge.setSeverity(sev)
            badge.attachTo(btn)
            cl.addWidget(btn)
            row.addWidget(container)
        row.addStretch()
        parent_layout.addLayout(row)
        parent_layout.addSpacing(12)

        row = QHBoxLayout()
        row.setSpacing(30)
        container = QWidget()
        cl = QVBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(4)
        btn = ElaPushButton("溢出", container)
        btn.setFixedWidth(110)
        badge = ElaInfoBadge(value=150, parent=container)
        badge.setSeverity(ElaInfoBadge.Severity.Caution)
        badge.attachTo(btn)
        cl.addWidget(btn)
        row.addWidget(container)
        container = QWidget()
        cl = QVBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(4)
        btn = ElaPushButton("图标", container)
        btn.setFixedWidth(110)
        badge = ElaInfoBadge(icon=ElaIconType.IconName.BadgeCheck, parent=container)
        badge.setSeverity(ElaInfoBadge.Severity.Success)
        badge.attachTo(btn)
        cl.addWidget(btn)
        row.addWidget(container)
        container = QWidget()
        cl = QVBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(4)
        btn = ElaPushButton("齿轮", container)
        btn.setFixedWidth(110)
        badge = ElaInfoBadge(icon=ElaIconType.IconName.Gear, parent=container)
        badge.setSeverity(ElaInfoBadge.Severity.Informational)
        badge.attachTo(btn)
        cl.addWidget(btn)
        row.addWidget(container)
        row.addStretch()
        parent_layout.addLayout(row)
        parent_layout.addSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(15)
        container = QWidget()
        cl = QVBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(4)
        target_btn = ElaPushButton("目标按钮", container)
        target_btn.setFixedWidth(110)
        demo_badge = ElaInfoBadge(value=7, parent=container)
        demo_badge.setSeverity(ElaInfoBadge.Severity.Attention)
        demo_badge.attachTo(target_btn)
        cl.addWidget(target_btn)
        row.addWidget(container)
        add_btn = ElaPushButton("添加", container)
        add_btn.setFixedWidth(70)
        add_btn.clicked.connect(lambda: demo_badge.attachTo(target_btn))
        row.addWidget(add_btn)
        remove_btn = ElaPushButton("移除", container)
        remove_btn.setFixedWidth(70)
        remove_btn.clicked.connect(demo_badge.detach)
        row.addWidget(remove_btn)
        row.addStretch()
        parent_layout.addLayout(row)
        parent_layout.addSpacing(20)

    def _demoChip(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "06. pyqt5_ela_pro - ElaChip 标签纸片", self._demoChip
            )
        )
        self._addInfoText(
            "16 种颜色（同 ElaButton 色系）+ 可关闭 / 可选择",
            parent_layout,
        )
        parent_layout.addSpacing(10)

        colors = [
            ("Default", ElaChip.Color.Default),
            ("Primary", ElaChip.Color.Primary),
            ("Blue", ElaChip.Color.Blue),
            ("Purple", ElaChip.Color.Purple),
            ("Cyan", ElaChip.Color.Cyan),
            ("Green", ElaChip.Color.Green),
            ("Magenta", ElaChip.Color.Magenta),
            ("Pink", ElaChip.Color.Pink),
            ("Red", ElaChip.Color.Red),
            ("Danger", ElaChip.Color.Danger),
            ("Orange", ElaChip.Color.Orange),
            ("Yellow", ElaChip.Color.Yellow),
            ("Volcano", ElaChip.Color.Volcano),
            ("Geekblue", ElaChip.Color.Geekblue),
            ("Lime", ElaChip.Color.Lime),
            ("Gold", ElaChip.Color.Gold),
        ]

        row = QHBoxLayout()
        row.setSpacing(8)
        for name, c in colors:
            chip = ElaChip(name, parent=self)
            chip.setColor(c)
            row.addWidget(chip)
        row.addStretch()
        parent_layout.addLayout(row)
        parent_layout.addSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(8)
        for name, c in colors:
            chip = ElaChip(name, parent=self)
            chip.setColor(c)
            chip.setClosable(True)
            row.addWidget(chip)
        row.addStretch()
        parent_layout.addLayout(row)
        parent_layout.addSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(8)
        for name, c in colors:
            chip = ElaChip(name, parent=self)
            chip.setColor(c)
            chip.setCheckable(True)
            chip.setChecked(True)
            row.addWidget(chip)
        row.addStretch()
        parent_layout.addLayout(row)
        parent_layout.addSpacing(20)

    def _demoSteps(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "07. pyqt5_ela_pro - ElaSteps 步骤条", self._demoSteps
            )
        )
        steps = ElaSteps(parent=self)
        steps.step_titles = ["第一步", "第二步", "第三步", "第四步", "第五步", "第六步", "第七步"]
        steps.currentStepChanged.connect(lambda v: print(f"步骤: {v + 1}"))
        parent_layout.addWidget(steps)
        nav = QHBoxLayout()
        prev_btn = ElaPushButton("上一步", self)
        prev_btn.clicked.connect(steps.previous)
        nav.addWidget(prev_btn)
        next_btn = ElaPushButton("下一步", self)
        next_btn.clicked.connect(steps.next)
        nav.addWidget(next_btn)
        nav.addStretch()
        parent_layout.addLayout(nav)
        parent_layout.addSpacing(20)

    def _demoRatingControl(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "08. pyqt5_ela_pro - ElaRatingControl 评分", self._demoRatingControl
            )
        )
        rating = ElaRatingControl(parent=self)
        rating.ratingChanged.connect(lambda v: print(f"评分: {v}"))
        parent_layout.addWidget(rating)
        parent_layout.addSpacing(20)

    def _demoPagination(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "09. pyqt5_ela_pro - ElaPagination 分页", self._demoPagination
            )
        )
        pag = ElaPagination(parent=self)
        pag.setTotalPages(100)
        pag.setJumperVisible(True)
        pag.currentPageChanged.connect(lambda p: print(f"跳转到第 {p} 页"))
        parent_layout.addWidget(pag)
        parent_layout.addSpacing(20)

    def _demoTimeline(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "10. pyqt5_ela_pro - ElaTimeline 时间线", self._demoTimeline
            )
        )
        timeline = ElaTimeline(parent=self)
        timeline.addItem(
            ElaTimeline.TimelineItem(
                title="创建项目",
                content="项目框架初始化完成",
                timestamp="2024-01-01",
                icon=ElaIconType.IconName.FloppyDisk,
            )
        )
        timeline.addItem(
            ElaTimeline.TimelineItem(
                title="开发阶段",
                content="核心功能开发中",
                timestamp="2024-02-15",
            )
        )
        timeline.addItem(
            ElaTimeline.TimelineItem(
                title="测试阶段",
                content="进行集成测试",
                timestamp="2024-03-20",
            )
        )
        timeline.setMinimumHeight(200)
        parent_layout.addWidget(timeline)
        nav = QHBoxLayout()
        for i, label in enumerate(["创建项目", "开发阶段", "测试阶段"]):
            btn = ElaPushButton(label, self)
            btn.setFixedWidth(90)
            btn.clicked.connect(lambda checked, idx=i: timeline.setCurrentStep(idx))
            nav.addWidget(btn)
        nav.addStretch()
        parent_layout.addLayout(nav)
        parent_layout.addSpacing(20)

    def _demoUploadArea(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "11. pyqt5_ela_pro - ElaUploadArea 上传区域", self._demoUploadArea
            )
        )
        upload = ElaUploadArea(parent=self)
        upload.setFixedSize(300, 180)
        upload.filesSelected.connect(lambda paths: print(f"选择文件: {paths}"))
        upload.fileRejected.connect(
            lambda path, reason: print(f"拒绝: {path} ({reason})")
        )
        parent_layout.addWidget(upload)
        parent_layout.addSpacing(20)

    def _demoSpotlight(self, parent_layout):
        parent_layout.addLayout(
            self._createHeaderRow(
                "12. pyqt5_ela_pro - ElaSpotlight 引导遮罩", self._demoSpotlight
            )
        )
        self._addInfoText("单目标聚光 + 多步骤引导", parent_layout)

        row = QHBoxLayout()
        row.setSpacing(15)
        single_btn = ElaPushButton("单目标聚光", self)
        single_btn.setFixedWidth(110)
        single_target = ElaPushButton("高亮目标", self)
        single_target.setFixedWidth(110)
        row.addWidget(single_target)
        row.addWidget(single_btn)
        row.addStretch()
        parent_layout.addLayout(row)

        def _on_single():
            s = ElaSpotlight(self)
            s._title = "提示"
            s._content = "这是一个单目标引导示例"
            s.showSpotlight(single_target, "知道了")

        single_btn.clicked.connect(_on_single)
        parent_layout.addSpacing(12)

        self._addInfoText("多步骤引导，依次高亮下方三个按钮", parent_layout)
        spot_btn1 = ElaPushButton("第一步", self)
        spot_btn1.setFixedWidth(100)
        spot_btn2 = ElaPushButton("第二步", self)
        spot_btn2.setFixedWidth(100)
        spot_btn3 = ElaPushButton("第三步", self)
        spot_btn3.setFixedWidth(100)
        launch_btn = ElaPushButton("开始引导", self)
        launch_btn.setFixedWidth(100)
        spot_layout = QHBoxLayout()
        spot_layout.setSpacing(15)
        spot_layout.addWidget(spot_btn1)
        spot_layout.addWidget(spot_btn2)
        spot_layout.addWidget(spot_btn3)
        spot_layout.addWidget(launch_btn)
        spot_layout.addStretch()
        parent_layout.addLayout(spot_layout)

        def _on_multi():
            s = ElaSpotlight(self)
            s.setSteps(
                [
                    ElaSpotlight.SpotlightStep(
                        spot_btn1, "第一步", "点击此按钮开始操作", False
                    ),
                    ElaSpotlight.SpotlightStep(
                        spot_btn2, "第二步", "配置相关参数", False
                    ),
                    ElaSpotlight.SpotlightStep(
                        spot_btn3, "第三步", "确认并完成", False
                    ),
                ]
            )
            s.finished.connect(lambda: print("多步引导结束"))
            s.start()

        launch_btn.clicked.connect(_on_multi)
        parent_layout.addSpacing(20)

    def _demoFlowLayout(self, parent_layout):
        from PyQt5.QtWidgets import QWidget

        parent_layout.addLayout(
            self._createHeaderRow(
                "13. PyQt5ElaWidgetTools - ElaFlowLayout 流式布局", self._demoFlowLayout
            )
        )
        self._addInfoText(
            "自适应换行的流式布局容器，控件超出容器宽度时自动折行", parent_layout
        )
        container = QWidget(self)
        flow = ElaFlowLayout(container)
        colors = [
            ("#1677ff", "#e6f4ff"), ("#52c41a", "#f6ffed"), ("#fa8c16", "#fff7e6"),
            ("#722ed1", "#f9f0ff"), ("#13c2c2", "#e6fffb"), ("#eb2f96", "#fff0f6"),
            ("#fa541c", "#fff2e8"), ("#2f54eb", "#f0f5ff"), ("#a0d911", "#fcffe6"),
            ("#fadb14", "#feffe6"), ("#f5222d", "#fff1f0"), ("#0067c0", "#e5eff9"),
        ]
        for i, (border, bg) in enumerate(colors):
            btn = ElaPushButton(f"标签 {i + 1}", container)
            btn.setFixedWidth(80 + (i % 3) * 30)
            flow.addWidget(btn)
        container.setLayout(flow)
        parent_layout.addWidget(container)
        parent_layout.addSpacing(20)
