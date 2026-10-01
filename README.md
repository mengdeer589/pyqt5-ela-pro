# pyqt5-ela-pro

PyQt5 extension widget library based on PyQt5ElaWidgetTools.

## 背景

本库基于 [Liniyous/ElaWidgetTools](https://github.com/Liniyous/ElaWidgetTools)（C++ Qt Widgets 组件库）进行 Python 移植与扩展开发，
其 Python 绑定为 [PyQt5-ElaWidgetTools](https://github.com/HIllya51/PyElaWidgetTools)。
**大量组件参照了 [ElaWidgetTools](https://github.com/RainbowCandyX/ElaWidgetTools)（RainbowCandyX 的 fork）的 C++ 源码实现**，
包括 ElaSplitter、ElaPagination、ElaToast、ElaSpotlight、ElaSteps、ElaTimeline、
ElaRatingControl、ElaInfoBadge、ElaChip、ElaDropDownButton、ElaSplitButton、
ElaPasswordEdit、ElaConfirmDialog、ElaMarkdownViewer、ElaUploadArea、ElaSplashScreen 等。
同时参考了 [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) 和
[PyQt-SiliconUI](https://github.com/ChinaIceF/PyQt-SiliconUI) 的部分组件设计思路，
在 **Minimax** 与 **DeepSeek** 模型的辅助下完成。

其中 **ElaChartWidget 图表引擎**、**蓝图节点图编辑器（Blueprint）** 与
**ElaMarkdownViewer 的流式增量渲染 / 公式占位嵌入方案** 移植自
[InstructionX_UIKit](https://github.com/KKPIP-Tech/InstructionX_UIKit)（PySide6 → PyQt5；
原库无 LICENSE），移植时统一 `Ela*` 命名并适配 Ela 主题。

## 组件来源

| 组件 / 模块 | 来源 |
|---|---|
| 输入、容器、展示、对话框等原生组件 | 上游 [ElaWidgetTools](https://github.com/Liniyous/ElaWidgetTools) C++ + [PyQt5-ElaWidgetTools](https://github.com/HIllya51/PyElaWidgetTools) 绑定 |
| `ElaSplitter`、`ElaPagination`、`ElaToast`、`ElaSpotlight`、`ElaSteps`、`ElaTimeline`、`ElaRatingControl`、`ElaInfoBadge`、`ElaChip`、`ElaDropDownButton`、`ElaSplitButton`、`ElaPasswordEdit`、`ElaConfirmDialog`、`ElaMarkdownViewer`、`ElaUploadArea`、`ElaSplashScreen` | [ElaWidgetTools（RainbowCandyX fork）](https://github.com/RainbowCandyX/ElaWidgetTools) C++ 源码移植 |
| `ElaDrawer` | PyQt-SiliconUI `SiLayerDrawer` 设计 |
| `ElaDrawerArea` | 上游 `PyQt5ElaWidgetTools.ElaDrawerArea` 子类化修复（自定义标题栏点击展开/收起） |
| `ElaButton`、`ElaDivider`、`ElaChip` 等 | Ant Design 风格自研（对照 ElaWidgetTools 既有组件） |
| `ElaChartWidget`（`charts/`） | InstructionX_UIKit `charts`（类 ECharts `setOption` 引擎）移植 |
| 蓝图节点图编辑器（`blueprint/`） | InstructionX_UIKit `blueprint` + `anim.painted.SpinnerArc` 移植 |
| `ElaMarkdownViewer` 流式增量渲染 / 公式提取 | InstructionX_UIKit `components.markdown_view` 思路移植；公式渲染为自研 `math_lite.py` |
| `ElaChatWidget` / `ElaChatView` / `ElaChatInput` / `ElaChatBubble` / `ElaChatToolBar` / `ElaChatStreamBinder` / `ElaChatAsyncWorker` / `ElaChatMockBackend` / `ElaChatStatusBar`（`chat/`） | 自研（交互参考 ChatGPT；助手消息复用 `ElaMarkdownViewer` 嵌入模式；分层输入区与富消息结构参考 Agent Chat 聊天页设计；工具卡 / 补全 / 排队 / Shell 交互对齐 opencode 会话 UI） |
| `ElaTerminalView` / `AnsiParser`（`terminal_view.py`） | 自研（纯展示组件，不执行命令；只负责把 ANSI 原始输出渲染成带样式的行） |
| `ElaTrayIcon`（`ela_tray_icon.py`） | 自研（`QSystemTrayIcon` 薄封装：三态图标 / 气泡通知降级 / ElaMenu 右键菜单） |
| `ElaMenuItem`（`menu_item.py`） | 自研（菜单项数据模型，划词动作条与托盘菜单共用） |
| `ElaTagBox` / `ElaTagMultiBox` / `ElaTagSearchBox` / `ElaTagSearchMultiBox` / `ElaTagLineEdit` | PyQt-Fluent-Widgets Tag 组件设计参考 |
| `ElaBrowserEmbedder` / `ElaWindowEmbedder` | 自研（Chromium CDP + win32gui） |

## 特性

### 输入组件
- **ElaSearchBox / ElaSearchMultiBox** — 可搜索下拉框，支持中文原文 / 全拼 / 首字母搜索（`bj` → 北京），空格分隔多关键词
- **ElaGhostBox** — 幽灵下拉框（透明无边框触发器 / 分组标题行 / 弹层底部固定按钮区，继承搜索与拼音过滤；搜索可用 `setSearchVisible(False)` 关闭）
- **ElaTagBox / ElaTagMultiBox / ElaTagSearchBox / ElaTagSearchMultiBox** — Tag 风格下拉框变体
- **ElaTagLineEdit** — 带「上置标题」的输入框，参数顺序跟全库一致：`ElaTagLineEdit(parent, title)`（标题默认空串）
- **ElaPasswordEdit** — 密码输入框（密码可见切换、焦点动画）
- **ElaRatingControl** — 星级评分（支持半星、鼠标悬停预览、只读模式）
- **ElaUploadArea** — 文件上传区域（拖拽 + 点击选择，后缀/大小/数量校验）
- 所有下拉框组件均提供 `items` 属性获取选项列表

### 按钮
- **ElaButton** — 统一按钮组件（6 种变体、16 色主题、Ant Design 风格）
- **ElaDropDownButton** — 下拉按钮（点击弹出 ElaMenu）
- **ElaSplitButton** — 拆分按钮（主操作 + 下拉菜单）
- **ElaLongPressButton** — 长按触发（防误触）
- **ElaProgressButton** — 含进度指示的按钮
- **ElaSvgButton / ElaSvgIconButton** — 基于 SVG 图标的按钮

### 弹窗与提示
- **ElaMessageDialog** — 消息确认对话框
- **ElaConfirmDialog** — 全 QPainter 自绘确认对话框（支持上/下弹出）
- **ElaDialogBase** — 可定制按钮的对话框基类
- **ElaToast** — 非模态通知提示（成功/信息/警告/错误，淡入淡出动画）
- **ElaNotifyPopup** — 右下角弹出通知
- **ElaToolTip / ElaStateToolTip** — 自定义工具提示、状态提示
- **ElaSpotlight** — 引导遮罩（多步高亮提示，支持单目标/多步骤）

### 数据展示
- **ElaDataTable** — 数据表格（支持排序、样式、对齐）
- **ElaParquetTable** — Parquet 文件分页查看（内置 ElaPagination 翻页，需 `polars`）
- **ElaChartWidget** — 类 ECharts 图表引擎（纯 QPainter，21 种系列，含
  GitHub 风格日历热力：周×星期年历网格、空日底格、富 tooltip、周起点/色带可配；
  交互开关：`setInteractive(False)` 一键静态化，`setInteractionEnabled("dataZoom", False)`
  逐项开关（提示框 / 图例 / 缩放 / 刷选 / 时间轴 / 工具箱）；
  大数据降采样需 `tsdownsample`）
- **ElaDashboardGauge** — 仪表盘组件（全 QPainter 自绘，指针动画，颜色分段）
- **ElaPlotWidget** — pyqtgraph 绘图控件（主题感知，可选依赖 pyqtgraph）
- **ElaTimeline** — 时间线（时间戳、标题、正文、可选图标）
- **ElaMarkdownViewer** — Markdown 查看器：主题自适应、Typora 结构排版
  （标题层级字号 / 1.6 倍行高 / 引用块浅底色 / 无边框代码卡片 / 图片居中）、
  **多套 markdown 配色主题**（内置 `opencode`（默认）/ `github` / `solarized` /
  `dracula`，按浅 / 深自动取变体；`setMarkdownTheme(name)` 切换、
  `markdownThemes()` 枚举、`registerMarkdownTheme(name, light, dark)` 注册自定义、
  `setDefaultMarkdownTheme(name)` 改新实例默认、`setCodeTokenColors` 单键覆盖）、
  GFM 语法（表格 / 任务列表 / 删除线）、
  GitHub Alert 提示块（`> [!NOTE]` 等）、脚注跳转与回跳、`[toc]` 目录与标题锚点、
  行内高亮 `==text==` / 上下标 `~x~` `^x^` / emoji 短代码、
  代码语法高亮与语言标签（可选 Pygments）、代码块悬停复制按钮、行号与超长折叠、
  推理块（` … `）与 `<details>` 折叠（流式未闭合显示「思考中…」）、
  `diff` 围栏行级着色、YAML front matter 自动剥离、链接悬浮显示地址、
  `renderIssues()` 渲染降级记录、
  行内与块级数学公式（零依赖 `math_lite`：矩阵 / `align` / `gather` / `cases` /
  `\binom` / `\substack` / `\mathbb`，`\boxed` / `\overbrace` / `\xrightarrow` /
  `\boldsymbol` / `\textcolor` / `\cancel`，极限算子自动堆叠，
  `\newcommand` / `\def` 宏展开，中文按系统字体回退；
  未收录命令容错为字面文本、结构性错误才回退源码）、
  公式 / Mermaid 悬浮显示源码、点击或右键复制、
  Mermaid 图渲染（可选依赖 `mermaidx`，无浏览器；缺失时回退代码卡片；
  按视口距离优先渲染可见图、主题切换先用旧主题图顶替、光栅化倍率随显示宽度
  自适应、可选引擎预热 `setMermaidPrewarm(True)`）、
  任务列表可点击勾选、图片点击信号与预览、本地图片右键另存为、
  表格斑马纹与列宽设置、
  图片基准路径与超宽缩放、远程图片默认拦截、
  搜索 / 缩放 / `exportPdf(path, pageSize, marginsMm)` / `printDocument()` 打印、
  `toHtml(embedImages=True)` 单文件导出（图片内嵌 data URI）、
  `markdownSelection()` / `selectionQuoted` 选中内容还原为 Markdown 源（引用回复）、
  锚点跳转可返回上一位置、
  流式追加（`appendMarkdown` / `endStream`，贴底自动跟随、末尾打字光标，
  面向 AI 对话场景）

### AI 对话
> 交互对齐 opencode 会话 UI，实现件优先复用 Ela 原生组件
> （`ElaFlowLayout` / `ElaIconButton` / `ElaDropDownButton` / `ElaMenu` /
> `ElaListView` / `ElaScrollPageArea` / `ElaProgressRing` / `ElaToggleButton`）。

- **ElaChatWidget** — ChatGPT 风格聊天组件（自研，`pyqt5_ela_pro.chat`）：
  可选头部（标题 / 清空）+ 消息列表 + 分层输入区 + 排队 dock + 输入区 dock；
  命令式流式 API（`sendUserMessage` → `beginAssistantMessage` →
  `appendText` → `endAssistantMessage`，`stopGeneration` 停止并保留
  已输出内容）；多步骤生成（`beginStep` / `beginText` /
  `endText`）、思考流式（`beginReasoning` / `appendReasoning` /
  `endReasoning`）、工具调用（`addToolCall` / `setToolCallResult`，每步独立
  工具面板）、步骤用量（`setStepStats`）与耗时
  （`setMessageDuration`）、错误（`setMessageError`）；消息管理
  `removeMessage` / `updateMessage` / `count` / `toolCalls`；
  宿主操作 `undoMessage`（撤回：删除该条及其后 + 原文 / 附件回填）/
  `regenerateFrom`（重生准备：删除原回答并返回前置用户消息）/
  `retryMessage`（重试准备：**保留消息位置**，只清错误，同参数重发）；
  排队 `sendNextQueued` / `setAutoSendQueue`（回合结束自动续发队首，默认开）；
  steer 插话 `steerMessage` / `drainSteer` / `setSteerEnabled`（生成中把新
  指令送进这一轮，在 `beginStep` 安全边界投递，而非等整轮跑完）；
  `messages()` 返回只读 `ElaChatMessage` 快照（助手消息含步骤化
  `parts` 时间线，`messageUpdated` 信号同步快照变化）；
  信号 `messageSubmitted` / `messageSubmittedFull` / `stopRequested` /
  `generationStarted` / `generationFinished` / `messageUpdated` /
  `copyRequested` / `undoRequested` / `regenerateRequested` / `retryRequested` /
  `permissionRequested` / `permissionReplied` / `steerReady` / `steerChanged` /
  `attachmentsChanged` / `queueChanged` / `mentionSelected` /
  `modeChanged` / `suggestionClicked` / `cleared`；头像自定义
  `setUserAvatar(source)` / `setAssistantAvatar(source)`（含已存在与后续消息），
  形状 `setAvatarShape("circle" | "rounded" | "square")`（默认圆形）
- **工具结果富渲染（`registerToolRenderer`）** — 宿主按工具名注册渲染器，库只
  替换工具卡的**内容区**（头部 / 折叠 / 错误竖线 / 忙碌环 / 展开策略仍由
  `ToolCallCard` 负责，故现有工具卡回归行为不变）：
  `registerToolRenderer(name, factory, *, subtitle=None, groupable=None)`；
  工厂签名 `(ToolRenderContext) -> QWidget`，返回 `None` 落回默认纯文本；
  可选实现 `updateToolResult(result, status)` 接收结果推送。
  `subtitle(arguments) -> (键, 值)` 的键会自动从参数摘要排除（防「3 个文件
  files=[...]」重复）；给上下文工具（read / glob / grep / list）注册默认退出
  分组（否则被分组卡绕过）。库内**不内置**任何具体渲染器 —— diff / 图片 /
  终端输出都由宿主实现。**渲染器里的每个 `ColorText` 都要显式
  `setTextPixelSize`** —— 不设就是 `ElaText` 的默认字号（实测 **28px**），比
  chat 的 11-14px 标尺大一大截，整张卡的比例会崩
- **工具审批（`beginPermission` / `resolvePermission`）** — **交互与记录分离**
  （对齐 opencode 的 `session-question-dock`）：
  - 等待用户操作 → `ElaChatPermissionDock`（**输入区上方**，输入区照常可用，
    不顶替它）；答完 → 时间线上该 part 的**原位**留下一张
    `PermissionRecord`，**默认折叠成一行**（与 `工具调用 (N)` 同一套折叠交互）。
    两者是**不同的 widget** —— 交互是大控件，记录是一行摘要，排版需求正好相反。
  - 一次只放一张；后到的**排队**（「还有 N 个待答复」），不顶掉用户正在答的那张。
    排队的卡**从未被 show 过**（建卡时无 parent，卡片自己不 show，显示时机只归
    dock —— 否则 Qt 会把无父控件当顶层窗口弹出来，用户看到「小窗一闪」）。
  - **两种形态由 `permission.questions` 是否为空决定**（**这就是判据，勿另设
    标志位**）：
    - **批准型**（`questions` 为空）：允许一次（实心强调色）/ 始终允许（描边）/
      拒绝…（危险色）—— **按重要性分档**，不是三个等权重的文字按钮；可带反馈；
    - **问答型**（`questions` 非空）：**逐题向导** —— 标题行（「需要你回答 ·
      短标签」+ 右侧「N / M」+ 可点的进度段胶囊，**仅多题时出现**），题面
      （14px 主文本色），候选卡（每项**两行**：标题 + 说明，
      `ElaChatOption{label, description}`；单选 = `ElaRadioButton` 圆点、
      多选 = `ElaCheckBox` 方框，**标记是真控件不是自绘**），末行是「输入自己的
      答案」，页脚 忽略 / 上一步 / 下一步|提交（**都是 `ElaButton`**，不印快捷键
      提示但快捷键照常生效）。大量 diff 按「行数 + 单行长度」双上限折叠。
      键盘：`1`–`9` 选中对应行（与焦点在哪一行无关）、`Space` 切换（多选）、
      `↑↓←→` / `Home` / `End` 移焦点、`Ctrl+⏎` 下一步 / 提交、`Alt+←` 上一步、
      `Esc` 忽略。
    - **选项区是普通容器，不封顶也不滚动**：`QScrollArea.sizeHint()` 是个无意义
      的小值，会把内容压扁（实测 166px 压到 69px、第二个选项切掉半截），而内层
      滚动区滚到头后事件会冒泡到外层（滚选项会连消息区一起动）。候选行是普通
      控件、行高固定，容器的 `sizeHint` 就是内容高度。

  **组件只画卡 + 收集回复 + 发信号，绝不阻塞**（Qt 里挂起等用户点按钮会卡死
  事件循环）：宿主收 `permissionRequested` 自行挂起后端，收 `permissionReplied`
  自行恢复；「始终允许」的规则持久化也归宿主（`resources` 模式串原样交出）。
  未答复的审批在回合中止 / 消息删除时自动作废，不留死卡。
  `beginPermission` 收到**已经是落定态**的 request（宿主重放后端历史）时直接落
  成记录卡：不进 dock、不发 `permissionRequested`。

  问答型的 `answer` 是 `json.dumps({key: str | [str, ...]})`：**单选塌缩成标量**、
  **多选发整个数组**、**未答题整条不进 payload**（不是空串也不是空数组 ——
  空数组会被模型读成「用户答了『一个都不选』」）、**自定义答案与候选项互斥**。
  读未塌缩的原始分组形式用 `view.permissionAnswers(messageId, requestId)`
  （「答到一半还没提交」时看进度）。取还在 dock 里等回复的卡用
  `view.interactivePermissionCard(messageId, requestId)`（`permissionCard` 只返回
  时间线上的**记录卡**，等待期间是 `None`）。
  强调色取自 `eTheme` 主题令牌，**不硬编码 opencode 的品牌色**（本库可换肤）
- **上下文压缩表达（`beginCompaction` / `appendCompactionSummary` /
  `endCompaction`）** — 时间线上的分隔卡：**折叠态就露出摘要首行**（自己按
  字符数截断），点开看全文；`endCompaction(..., historyCount=N)` 给了条数才写
  「已压缩 N 条历史」，**没给就说「已压缩历史」**（`0` 的含义是「不知道」，不是
  「压了 0 条」）。**库不实现压缩算法**（摘要模板 / 收缩循环 / 词元估算都依赖
  provider 侧），只负责「能表达 + 能持久化」；压不压、压哪段由宿主决定
- **上下文占用指示器（`view.setContextUsage(used, window, costUsd)`）** —
  右上角小圆环（非进度条：占用是标量不是过程），三档配色（<60% 弱化 /
  60~85% 警示 / >85% 危险），hover 显示花费 / 百分比 / 词元数。数据全由宿主
  提供，**不进 `ElaChatStats`**（那个字段的 `merge()` 是各步求和语义，上下文
  占用是当前值）
- **成本（`ElaChatStats.cost_usd` / `ModelPricing` / `stats_cost`）** —
  定价表不烤进库（价格会变、还分上下文长度阶梯），库只提供换算纯函数：
  `output` 与 `reasoning` 同价、按输入侧总量选阶梯档、最后除以 1e6。
  宿主也可以自己算好直接填 `cost_usd`
- **ElaChatView** — 消息列表：用户气泡右对齐（可选中纯文本、最大宽度可调）、
  助手消息按步骤化分段组织（思考段 → 正文段（可多段）→ 每步工具面板 →
  步骤用量徽标），正文复用 `ElaMarkdownViewer` **嵌入模式**（透明背景 /
  隐藏滚动条 / 高度贴合内容（文末空白不计入高度），公式 / Mermaid /
  代码高亮能力一致）、
  系统消息居中弱化；
  贴底自动跟随（10px 判定）+ 上滚暂停 + 离底 >400px 才显示「回到底部」；
  展开 / 收起工具卡时暂停跟随（`holdFollow`），视口保持不动不跳动；
  嵌套滚动区（Markdown / 工具输出）防脱离；turn 间隔节奏；空态标题 /
  副标题 / 建议按钮列表；多步骤流式 API（`beginStep` / `beginText` /
  `appendText` / `endText` / `setStepStats`）与消息动作透传（均带消息 id）；
  错误类型单独存字段（`setMessageError(id, msg, errorType)` /
  `messageError(id)`），错误卡据此决定是否点亮「重试」（限流 / 超时 / 网络
  类可重试，参数错误 / 鉴权失败 / 内容过滤不点）；
  上下文占用圆环 `setContextUsage(used, window, costUsd)`；
  头像自定义 `setUserAvatar` / `setAssistantAvatar`（SVG / 路径 / `QPixmap` 等）、
  形状 `setAvatarShape`（默认圆形 / `rounded` / `square`）
- **ElaChatInput** — 单卡片输入区（对齐 opencode：附件条 / 多行输入 / 工具栏
  同在一个圆角卡片内——`inputSurface()`；聚焦时边框转强调色，空草稿时发送
  按钮置灰）；卡片上方是补全浮层（`@` 引用，provider 接口）；
  附件条（`ElaChip` / 图片缩略卡，拖放 + 粘贴图片 + 去重）；
  多行输入（默认 3–8 行，`Enter` 发送 / `Shift+Enter` 换行，IME 安全；
  Shell 模式切换高度不跳变）；工具栏（默认扁平图标按钮：回形针（上传）
  + 右侧发送 / 停止；`+` 菜单与 Shell 开关默认隐藏，可用
  `setMenuVisible` / `setShellVisible` 启用、`addMenuItem` 自动显示 `+`）；
  **发送 / 停止同按钮**：流式中草稿为空才显示「停止」，有草稿仍为「发送」
  （默认交由宿主排队，`setQueueEnabled` 可关）；`Esc` / `Ctrl+G` 停止；
  `!` 进入 Shell 模式（等宽字体、左组控件禁用）；
  上传路径：`attachments()` 快照（含 `path`）/ `attachmentPaths()` 路径列表 /
  `attachmentsChanged` 信号 / 提交时 `messageSubmittedFull(text, attachments)`
- **ElaChatToolBar / ElaChatToolButton** — 可复用水平工具栏：
  `leading` / `trailing` 两段，追加 `addButton` / `addWidget` /
  `addSeparator` 与插入版 `insertButton` / `insertWidget` /
  `insertSeparator(before)`（落在参照项所在分区），动态状态
  `setItemVisible` / `setItemEnabled`（`removeItem` 会销毁控件、
  `clear(zone)` 分段清空；zone 非法值抛 `ValueError`），事件
  `toolTriggered(key)` / `toolToggled(key, checked)`；图标按钮为
  `ElaIconButton`（原生方形 / `IsSelected`），文字按钮为 `ElaButton`；
  `compact` 模式供消息底部操作栏复用
- **ElaChatBubble** — 步骤化消息气泡（可独立复用）：头部（头像 + 名称 +
  时间 / 状态；头像支持内置图标与自定义图 `setAvatarImage`——SVG 数据 /
  SVG 或位图路径 / `bytes` / `QPixmap` / `QImage` / `QIcon`，默认圆形裁切，
  `setAvatarShape` 可切圆角方形 / 直角方形）、
  内容分段（按加入顺序组成时间线：`ElaChatPart` 的
  reasoning / text / tool / stats 四类，正文段可多段；另有 `Permission`（审批 / 问答向导）、`Compaction`
   （压缩分隔）、`Synthetic`（steer 回执）三种「非正文段」—— **它们的 `text`
   都不并入 `message.text`**：插话是旁注、摘要是历史的替代物，并进去等于算两遍）、思考段
  （`ReasoningBlock` 折叠块，或 `setReasoningStyle("inline")` 内联
  + `ThinkingRow` 思考行，逐段跟随位置）、每步工具面板（外层
  `ToolGroupPanel`「工具调用 (N)」，运行中显示 `(已完成/总数)`；
  内部 `ToolCallCard` 默认折叠、pending 锁定、参数摘要、失败转错误卡；
  `ContextToolGroupCard` 自动归并 read/glob/grep/list 并显示计数）、
  步骤用量（`setStepStats` 追加 `StatsBadge`）、附件条
  （`AttachmentStrip`）、底部（`MessageMeta` 整轮耗时 +
  `MessageActions` 悬停淡入的复制 / 撤回 / 重新生成，占位不变、
  消息区不跳动，按钮带 ElaToolTip 提示）；助手流式
  `beginStream` / `appendText` / `endStream`（`streamFinished` 信号），
  `parts()` 返回当前分段快照
- **ElaChatQueueDock / ElaChatInputDock** — 输入区上方 dock：
  排队消息（N 条 + 预览 + 立即发送 / 编辑 / 移除，`enqueueMessage` /
  `sendQueuedNow` / `editQueuedMessage`）与通用替换 dock
  （权限 / 提问卡片，`setDockWidget`）
- **ElaChatStreamBinder** — 流式事件 → 组件映射器（宿主接入推荐入口）：
  构造传 `worker` 即**自动接线**（`llmStarted` / `chunkReceived` /
  `toolStarted` / `toolEnded` / `statsReady` / `emptyTurn`，也可稍后
  `connectWorker(worker)`）；`startTurn(prompt, regenerate=False)` 与
  `finish(status)` 对称地闭环回合（建助手消息 + `beginTurn` + 驱动后端，
  后端未就绪返回 `False` 且不建空消息）；`shutdownOnClose(window)`
  在窗口关闭 / 销毁时自动 `worker.shutdown()`（宿主免写 `closeEvent`）；
  细粒度 API：`beginTurn` /
  `beginRound`（第 2 轮起自动分步）、`reasoning` / `answer` /
  `stream(chunk)`（同一轮思考复用一块、正文自动结束思考段）；
  `toolStart(callId, name, arguments)` / `toolEnd(callId, result, ok=None)`
  （`ok=None` 按 `"Error:"` 前缀推断失败）与便捷方法
  `toolCallStarted(toolCall)` / `toolCallEnded(toolCall, result)`
  （直接接 OpenAI 风格 `tool_call` dict 信号）；`stats(usage, ttftMs, tps)`
  （兼容 OpenAI `usage` / `ElaChatStats`）、`error` / `emptyTurn`；
  `cancel()` 记录停止（收尾思考段），此后 `finish(status=None)` 自动按
  `Stopped` / `Done` 收尾（显式传参优先）；`finish(status)`（补整轮耗时、
  结束消息、返回 `ElaChatTurnSummary` 摘要：状态 / 是否输出过正文 /
  `finish_reason` / 耗时，幂等）
- **ElaChatAsyncWorker** — 异步后端 worker 基类（QThread + asyncio 事件
  循环 + 命令队列 + 取消收尾），信号契约与 `ElaChatMockBackend` 同构；
  子类只需实现 `_setup()`（初始化后端）、`_stream_turn(prompt)`（异步
  分片迭代器）与可选的 `_rollback_turn` / `_after_turn` / `_reset_backend`，
  线程安全命令 `ask` / `regenerate` / `reset` / `cancel` / `shutdown`
- **ElaChatMockBackend** — 模拟后端（QTimer，无线程 / 无模型服务）：
  信号与真实 worker 同构（`ready` / `llmStarted` / `chunkReceived` /
  `toolStarted` / `toolEnded` / `statsReady` / `turnFinished` 等），
  `ask` / `regenerate` / `cancel` / `reset` / `setThinkLevel("off" |
  "normal" | "deep")` / `setReplyProvider(provider)` / `setTickMs`
  （`0` 快进）；两步回合覆盖思考 → 上下文工具 → 统计 → 失败工具 → 正文
- **ElaChatStatusBar** — 宿主状态栏：左侧弱化信息（`setInfo`，
  模型 / 服务地址）+ 右侧状态文本（`setStatus(text, level)`，
  `info` / `busy` / `success` / `error` 四档语义配色），
  `setBusy(True)` 状态前显示 `ElaProgressRing`
- **ElaMarkdownViewer 嵌入模式** — `setEmbeddedMode(True)`：透明背景、
  隐藏滚动条、高度随文档（含流式）自适应、滚轮事件交给外层容器；
  `setEmbeddedExtra(px)` 调整高度余量，`setEmbeddedTrimBottom(True)`
  让高度贴合内容（文末段落下边距不计入，聊天正文 / 内联思考默认启用）
- **持久化 / 会话 bundle** — 消息 / 分段 / 工具 / 用量 / 附件成对
  `toDict()` / `fromDict()`（纯 JSON、容错、带 `SCHEMA_VERSION`）；JSON 文本
  统一走 `jsonDumps` / `jsonLoads` / `jsonBackend`：**装了 `orjson` 自动用
  orjson**（`pip install pyqt5-ela-pro[orjson]`），否则标准库 json，两套后端
  同为紧凑 UTF-8、`allow_nan=False` 语义一致；读回
  `view.addMessageFromDict()`（保留 id）或 `view.restoreMessages(items,
  preserveIds=True)`（批量渐进渲染，重号先校验后写入）；整会话
  `view.exportSession(session, extra)` / `view.importSession(bundle,
  clear=True)`（bundle = session 元数据 + messages + 外观选项，clear 时保留
  原 id）；`ElaChatSessionInfo` 提供会话元数据快照 + `toDict/fromDict`；
  回合中途崩溃用 `ElaChatTurnJournal` 追加写事件流恢复（示例见
  `chat/__init__.py` docstring）
- **多话题（架构 B）** — 组件是单话题视图，多话题按「一话题一 widget」放大：
  `ElaTabBar` 做话题列表 + `QStackedWidget` 切页（完整参考实现见
  `example/chat_session_page.py`：懒建页面 / 切页不中止生成 / 归档恢复 /
  外观偏好传播）；组件侧只用 `setCurrentSessionId()` 记一个纯标记，
  会话列表归宿主

**接入真实 AI 后端（推荐：交给 ElaChatStreamBinder）**：

```python
from pyqt5_ela_pro.chat import ElaChatStatus, ElaChatStreamBinder

binder = ElaChatStreamBinder(chat, worker=worker)     # 自动接机械信号
binder.shutdownOnClose(window)                        # 关窗自动收尾后端

worker.ready.connect(on_ready)                        # UI 状态归宿主
worker.failed.connect(on_failed)
worker.errorOccurred.connect(on_error)
worker.turnFinished.connect(on_turn_finished)

def on_submit(text, attachments):
    if not binder.startTurn(text):                    # 建消息 + 重置计时 + ask
        status_bar.setStatus("后端未就绪", level="error")

def on_turn_finished():
    summary = binder.finish()          # cancel 过自动 Stopped，否则 Done
    if summary.status == ElaChatStatus.Stopped:
        status_bar.setStatus("已停止（保留已输出内容）")
    elif summary.isEmptyReply():
        status_bar.setStatus("模型未返回正文", level="error")

def on_stop():                         # chat.stopRequested → 宿主停止
    binder.cancel()                    # 记录停止 + 收尾思考段
    worker.cancel()                    # 中止后端数据流
```

未接后端时可先用 `ElaChatMockBackend` 跑通 UI（信号同构，直接替换
`worker`）；真实异步后端（OpenAI 兼容流式 SDK 等）可继承
`ElaChatAsyncWorker`，只写 `_setup()` / `_stream_turn()` 即可获得线程、
事件循环、命令队列与取消收尾；停止按钮连接 `binder.cancel()` +
`worker.cancel()`（组件只负责 UI 收尾，`binder.finish()` 会自动按
`Stopped` 收尾）。

**宿主侧会话操作**（组件内完成，后端中止 / 历史回滚仍归宿主）：

```python
target = chat.undoMessage(messageId)          # 删该条及其后 + 原文/附件回填
userMessage = chat.regenerateFrom(messageId)  # 删原回答，返回前置用户消息
chat.setAutoSendQueue(True)                   # 回合结束自动续发队首（默认开）
chat.sendNextQueued()                         # 或手动触发
```

**参数约定**：`ElaChatView` 层方法以 `messageId` 为首位参数；
`ElaChatWidget` / `ElaChatInput` 层把 `messageId` 放在末尾可选
（缺省取当前流式消息 / 最后一条）。

**派生字段**：助手消息以 `parts` 为唯一内容来源，`text` / `reasoning` /
`tool_calls` / `stats` 由 `withParts()` 重算（详见 `ElaChatMessage` docstring）。

### 划词助手（Windows 全局）
- **ElaSelectionAssistant** — 全局划词助手（`selection_assistant/`，纯 ctypes
  无 pywin32 依赖，Win7+）：`ElaMouseMonitor` 采用**轮询式**全局鼠标监视
  （`GetAsyncKeyState` + `GetCursorPos`，主线程 QTimer 默认 15ms，**不使用
  `WH_MOUSE_LL` 全局钩子**——钩子回调阻塞会拖死整机鼠标输入）；拖选松开 /
  双击选词后模拟 `Ctrl+C` 读取选中文本（**不预先改动剪贴板**，成功后按需
  恢复原文本），在落点附近弹出动作条；信号 `selectionCaptured(text, pos)` /
  `actionTriggered(actionId, text, pos)` / `popupShown` / `popupHidden` /
  `enabledChanged` / `errorOccurred`；**动作条菜单项完全由宿主定义**
  （`setActions` 传 `ElaMenuItem` 列表，可启用 / 禁用 / 排序，
  组件不内置任何动作，未定义时只发 `selectionCaptured` 不弹窗）、
  `setMinSelectionLength`、`setDragThreshold`；外观（紧凑模式 / 偏移）走
  `popup()`，取词参数（剪贴板恢复 / 各类延迟）走 `capture()`；
  `setEnabled(True)` 启动监视，失败发 `errorOccurred` 并保持禁用
- **ElaSelectionPopup** — 动作条浮窗（`Tool | 无边框 | 置顶 | 不接受焦点`，
  `WA_ShowWithoutActivating` 不抢源应用焦点）：`popupAt(pos)` 以落点为锚、
  越界自动翻转并收敛到屏幕工作区；点击动作后自动隐藏并发出
  `actionTriggered(actionId)`；按钮悬停提示走库内 `ElaToolTip` 并显示在
  动作条**下方**（不遮挡上方选中文字，也不使用原生 `QToolTip`）；可独立复用
- **ElaMouseMonitor / ElaClipboardCapture** — 监视与取词后端（可注入假实现，
  测试无需真实输入）；`ElaClipboardCapture` 通过「基准文本 + 轮询变化」
  取词，失败时剪贴板从未被改动

```python
from PyQt5.QtWidgets import QApplication
from PyQt5ElaWidgetTools import ElaIconType
from pyqt5_ela_pro import ElaMenuItem, ElaSelectionAssistant

assistant = ElaSelectionAssistant(parent)
assistant.setActions([                              # 菜单项由宿主定义
    ElaMenuItem("copy", "复制", ElaIconType.IconName.Copy),
    ElaMenuItem("search", "搜索", ElaIconType.IconName.MagnifyingGlass),
])
assistant.actionTriggered.connect(on_action)        # (actionId, text, pos)

def on_action(actionId, text, pos):
    if actionId == "copy":
        QApplication.clipboard().setText(text)      # 行为全由宿主实现

assistant.setEnabled(True)
```

> 限制：终端 / 受保护程序可能取不到词；若选中文本与剪贴板原内容完全相同，
> 无法与「未复制」区分；剪贴板恢复只还原文本，图片等非文本格式不保留；
> 轮询式监视（默认 15ms）可能漏检极快点击，且无法检测滚轮（动作条改由
> 下一次点击 / 新划词隐藏）。

### 导航与布局
- **ElaDivider** — 分割线（水平/垂直，支持文字，实线/虚线）
- **ElaGroupBox** — 分组框（圆角边框、居中标题）
- **ElaSteps** — 步骤条（多步引导，已完成/当前/待办三种状态）
- **ElaPagination** — 分页（页码按钮、省略号、跳转输入框）
- **ElaSplitter** — 主题感知分割器（自定义 Handle 带 grip 悬停效果）
- **ElaDrawer** — 四方向侧边抽屉

### 标签与角标
- **ElaChip** — 标签纸片（16 色，同 ElaButton 色系，可关闭/可选择/可点击）
- **ElaInfoBadge** — 角标（Dot / Value / Icon 三种模式，5 种严重级别）

### 文档查看
- **ElaWordViewer、ElaExcelViewer、ElaPowerPointViewer** — 通过 ActiveX 嵌入 Office 文档查看

### 窗口嵌入
- **ElaWindowEmbedder** — 通过 win32gui 嵌入外部窗口
- **ElaBrowserEmbedder** — 嵌入 Chromium 浏览器，支持 `load_url()`、本地文件 Path 加载、CDP 控制；多实例共用一个浏览器进程（`debug_port` / `browser_args` 以首个实例为准，冲突会在 `logMessage` 里提示）

### 动画工具
- **fade_in / fade_out** — 淡入淡出动画
- **shake_window** — 窗口抖动
- **ElaAnimatedMixin** — 为对话框注入 `fade_in()` / `fade_out()` 方法

### 其他
- **ElaSplashScreen** — 应用启动屏（全 QPainter 自绘，主题感知，淡入淡出动画，可拖动）
- **ElaTaskbarProgress** — Windows 任务栏进度
- **ElaSvgIconLoader** — 二进制 SVG 图标加载器
- **ElaThemeWidget** — 主题感知基类，自动响应暗色/亮色切换
- **ElaFigureCanvas** — Matplotlib 画布（主题感知，自动适配暗色/亮色）

### 内建示例 - 代码查看器
每个示例组件的标题旁都有 `</> 代码` 按钮，点击弹出带 **VS Code Dark 语法高亮** 的源码对话框：
- 关键字（蓝）、内建函数（紫）、字符串（橙）、数字（浅绿）、注释（绿斜体）
- 类名（青）、方法调用（黄）、属性（浅蓝）、运算符（灰）
- 深色代码背景，自适应 Ela 主题

## 安装

当前仅支持本地安装（尚未发布到 PyPI）：

```bash
# 使用 uv
uv pip install -e .

# 或使用 pip
pip install -e .

# 安装全部可选能力（窗口嵌入 / Office 预览 / Markdown 高亮 / 图表降采样）
pip install -e ".[all]"
```

## 快速开始

```python
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
from PyQt5ElaWidgetTools import eApp, ElaWindow

from pyqt5_ela_pro import ElaButton, show_notify, fade_in

app = QApplication(sys.argv)
eApp.init()

class MainWindow(ElaWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyqt5-ela-pro")
        self.resize(1000, 700)

        page = QWidget(self)
        layout = QVBoxLayout(page)
        btn = ElaButton("Hello, pyqt5-ela-pro", variant="solid", color="primary")
        btn.clicked.connect(lambda: show_notify("提示", "按钮被点击了！"))
        layout.addWidget(btn)

        self.addPageNode("首页", page)

window = MainWindow()
window.show()
sys.exit(app.exec_())
```

## 项目结构

```
pyqt5_ela_pro/              # 核心组件包
  __init__.py               # 组件导出
  _internal.py              # 内部工具函数（_ThemeAwareMixin 等）
  _colors.py                # 共享颜色面板（ElaButton / ElaChip 共用）
  widget_base.py            # ElaThemeWidget 基类
  animation.py              # fade_in / fade_out / shake_window / ElaAnimatedMixin
  svg_icon.py               # SVG 图标加载器 + ElaSvgButton / ElaSvgIconButton
  combo_box.py              # ElaSearchBox / ElaSearchMultiBox
  table_view.py             # ElaDataTable
  #
  # 输入组件
  ela_tag_line_edit.py      # ElaTagLineEdit
  ela_tag_box.py            # ElaTagBox
  ela_tag_multi_box.py      # ElaTagMultiBox
  ela_tag_search_box.py     # ElaTagSearchBox
  ela_tag_search_multi_box.py   # ElaTagSearchMultiBox
  ela_tag_combo_base.py     # Tag 下拉框共享基类
  ela_password_edit.py      # ElaPasswordEdit
  ela_rating_control.py     # ElaRatingControl
  ela_upload_area.py        # ElaUploadArea
  #
  # 按钮组件
  ela_button.py             # ElaButton（6 变体 × 16 色）
  ela_dropdown_button.py    # ElaDropDownButton
  ela_split_button.py       # ElaSplitButton
  ela_long_press_button.py  # ElaLongPressButton
  ela_progress_button.py    # ElaProgressButton
  ela_confirm_dialog.py     # ElaConfirmDialog
  ela_group_box.py          # ElaGroupBox
  #
  # 弹窗与提示
  dialog_base.py            # ElaDialogBase
  message_dialog.py         # ElaMessageDialog
  ela_toast.py              # ElaToast
  notify_popup.py           # ElaNotifyPopup
  tooltips.py               # ElaToolTip / ElaStateToolTip
  ela_spotlight.py          # ElaSpotlight
  #
  # 导航与布局
  ela_side_drawer.py        # ElaDrawer
  ela_divider.py            # ElaDivider
  ela_steps.py              # ElaSteps
  ela_pagination.py         # ElaPagination
  splitter.py               # ElaSplitter
  #
  # 展示组件
  ela_timeline.py           # ElaTimeline
  terminal_view.py          # ElaTerminalView 终端输出（ANSI 解析 / 搜索 / 导出）
  ela_tray_icon.py          # ElaTrayIcon 托盘图标（三态 / 通知 / 菜单）
  menu_item.py              # ElaMenuItem 菜单项模型（划词 + 托盘共用）
  charts/                   # ElaChartWidget 图表引擎（core/axes/系列/组件）
  ela_dashboard_gauge.py    # ElaDashboardGauge
  ela_pyqtgraph_canvas.py   # ElaPlotWidget（可选依赖 pyqtgraph）
  ela_figure_canvas.py      # ElaFigureCanvas（可选依赖 matplotlib）
  ela_info_badge.py         # ElaInfoBadge
  ela_chip.py               # ElaChip
  ela_markdown_viewer.py    # ElaMarkdownViewer（流式 / 公式 / 高亮 / 表格）
  chat/                     # ElaChatWidget 聊天组件（消息分段模型 / 步骤化气泡 / 列表 / 分层输入区 / 工具栏 / 补全 / dock / 工具渲染器注册表 / 定价换算）
  selection_assistant/      # 划词助手（轮询式全局鼠标监视 / 模拟 Ctrl+C 取词 / 动作条浮窗）
  math_lite.py              # 零依赖 LaTeX 数学公式轻量渲染（矩阵/cases/组合数/字母表）
  ela_drawer_area.py        # ElaDrawerArea（上游组件点击标题栏展开/收起修复）
  blueprint/                # 蓝图节点图编辑器（移植自 InstructionX_UIKit）
  parquet_table.py          # ElaParquetTable
  #
  # 窗口
  splash_screen.py          # ElaSplashScreen
  window_embedder.py        # ElaWindowEmbedder
  browser_embedder.py       # ElaBrowserEmbedder
  office_viewer.py          # ElaWordViewer / ElaExcelViewer / ElaPowerPointViewer
  taskbar_progress.py       # ElaTaskbarProgress
  #
  example/                  # 组件演示示例（侧边栏两级：分组 -> 页面）
    __main__.py              # 入口（ElaWindow + 两级侧边栏 + 加载画面）
    base_page.py             # 示例基类（代码查看器核心）
    # —— 基础组件（按「用户会怎么找」分，不按「控件 vs 容器」分）——
    input_select_page.py     # 文本 / 数值 / 日期 / 勾选 + 密码框 / 上传 / 引导
    combo_box_page.py        # 下拉框全变体
    container_layout_page.py # 滚动区 / 抽屉 / 分隔 / 分组 / 流式布局
    views_list_page.py       # 树 / 表 / 列表 / 选项卡
    buttons_menus_page.py    # 按钮全族 + 菜单
    progress_feedback_page.py# 进度 / 状态标记 / 卡片
    # —— 数据与图表 ——
    data_table_page.py       # ElaDataTable（基础 / 异步 / 样式 / 排序）、ElaParquetTable
    chart_lib_page.py        # pyqtgraph / matplotlib / 仪表盘 / GraphicsView
    charts_page.py           # ElaChartWidget 图表引擎
    # —— 内容渲染 ——
    markdown_page.py         # ElaMarkdownViewer（文本 / 代码 / 公式 / Mermaid 分类 + 流式）
    advanced_page.py         # Office 文档预览（Word / Excel / PPT）
    # —— AI 对话 ——
    chat_demo_kit.py         # 聊天示例页共用零件（_ScriptPlayer 脚本播放器 / 只读聊天 / 说明行）
    chat_overview_page.py    # 聊天组件总览（预填 + 可重播 + 外观开关）
    chat_input_page.py       # 输入区能力（工具栏 / 附件 / @ 引用 / 清空 / 新建话题 / 排队干预）
    chat_agent_page.py       # Agent 能力（富渲染 / 审批批准型 / 审批问答型 / steer / 压缩 / 成本 / 重试）
    chat_session_page.py     # 会话管理（一话题一 widget：懒建 / 切页不中止 / 归档恢复）
    chat_persist_page.py     # 持久化与性能（回合日志重放 / 会话导入导出 / 大消息量三条开关）
    chat_guide_page.py       # 聊天组件 API 指南（代码为 llm_test 源码快照）
    # —— 窗口与应用外壳 ——
    application_page.py      # 应用框架（AppBar / StatusBar / NavigationBar）
    drawer_tooltip_page.py   # 弹窗与提示（ToolTip / Toast / 通知 / 对话框）
    app_shell_page.py        # 启动与托盘（启动画面 / 任务栏进度 / 托盘）
    # —— 系统交互与嵌入 ——
    embed_page.py            # 窗口嵌入 / 浏览器嵌入 / 多 URL 测试台
    terminal_page.py         # 终端输出（只读）
    selection_page.py        # 划词助手（全局划词 / 动作配置 / 事件日志与宿主实现）
    # —— 动效与图形 ——
    animation_icon_page.py   # 动画、图标
    blueprint_page.py        # 节点图编辑器
    tray_host.py             # ElaTrayHost 应用级宿主骨架（不进组件库）
```

## 组件一览

### 工具函数

| 函数 | 说明 |
|---|---|
| `fade_in(widget, duration)` | 淡入动画 |
| `fade_out(widget, duration)` | 淡出动画 |
| `shake_window(widget)` | 窗口抖动效果 |
| `set_tooltip(widget, text, position, theme)` | 设置自定义工具提示 |
| `remove_tooltip(widget)` | 移除自定义工具提示 |
| `svg_to_icon(path, size)` | SVG 文件转 QIcon |
| `svg_to_pixmap(path, size)` | SVG 文件转 QPixmap |
| `svg_icon_loader(path)` | SVG 图标加载器 |
| `create_ela_splitter(widgets, orientation, ...)` | 创建主题感知分割器 |
| `show_notify(title, text, ...)` | 弹出通知 |

### 组件类

| 组件 | 分类 | 说明 |
|---|---|---|
| **ElaThemeWidget** | 基类 | 主题感知基础控件 |
| **ElaAnimatedMixin** | 动画 | 注入 `fade_in()` / `fade_out()` 方法的混入类 |
| **ElaSearchBox** | 输入 | 可搜索单选下拉框 |
| **ElaSearchMultiBox** | 输入 | 可搜索多选下拉框 |
| **ElaTagBox** | 输入 | Tag 样式单选下拉框 |
| **ElaTagMultiBox** | 输入 | Tag 样式多选下拉框 |
| **ElaTagSearchBox** | 输入 | Tag + 搜索 单选下拉框 |
| **ElaTagSearchMultiBox** | 输入 | Tag + 搜索 多选下拉框 |
| **ElaTagLineEdit** | 输入 | Tag 风格输入框 |
| **ElaPasswordEdit** | 输入 | 密码输入框（可见切换，继承 ElaLineEdit） |
| **ElaRatingControl** | 输入 | 星级评分（支持半星，可悬停预览） |
| **ElaUploadArea** | 输入 | 文件上传区域（拖拽+点击，后缀/大小/数量校验） |
| **ElaButton** | 按钮 | 统一按钮（6 变体 × 16 色，Ant Design 风格） |
| **ElaDropDownButton** | 按钮 | 下拉按钮（点击弹出 ElaMenu） |
| **ElaSplitButton** | 按钮 | 拆分按钮（主操作 + 下拉菜单） |
| **ElaLongPressButton** | 按钮 | 长按触发按钮 |
| **ElaProgressButton** | 按钮 | 含进度指示的按钮 |
| **ElaSvgButton** | 按钮 | SVG 推按钮 |
| **ElaSvgIconButton** | 按钮 | SVG 图标工具按钮 |
| **ElaMessageDialog** | 弹窗 | 消息确认对话框 |
| **ElaConfirmDialog** | 弹窗 | 全 QPainter 自绘确认对话框 |
| **ElaDialogBase** | 弹窗 | 可定制按钮的对话框基类 |
| **ElaToast** | 弹窗 | 通知提示（成功/信息/警告/错误，淡入淡出自动关闭） |
| **ElaNotifyPopup** | 弹窗 | 弹出通知控件 |
| **ElaToolTip** | 提示 | 自定义工具提示 |
| **ElaStateToolTip** | 提示 | 状态提示控件 |
| **ElaToolTipPosition** | 枚举 | 提示位置枚举 |
| **ElaDrawer** | 导航 | 四方向侧边抽屉 |
| **ElaDrawerPosition** | 枚举 | 抽屉方向枚举 |
| **ElaSteps** | 导航 | 步骤条（多步引导，前进/后退） |
| **ElaPagination** | 导航 | 分页（页码按钮、省略号、跳转输入框） |
| **ElaSpotlight** | 导航 | 引导遮罩（单目标/多步骤，淡入淡出） |
| **ElaDivider** | 布局 | 分割线（水平/垂直/文字/虚线） |
| **ElaSplitter** | 布局 | 主题感知分割器（定制 Handle，悬停变色） |
| **ElaGroupBox** | 布局 | 分组框（圆角边框、居中标题、可放置子控件） |
| **ElaDataTable** | 数据展示 | 数据表格控件 |
| **ElaParquetTable** | 数据展示 | Parquet 文件分页查看 |
| **ElaChartWidget** | 数据展示 | 类 ECharts 引擎：21 系列 + 交互组件（含日历热力） |
| **ElaDashboardGauge** | 数据展示 | 仪表盘（全自绘，指针动画，颜色分段） |
| **ElaPlotWidget** | 数据展示 | pyqtgraph 绘图控件（主题自适应，可选依赖） |
| **ElaFigureCanvas** | 数据展示 | Matplotlib 画布（主题感知，可选依赖） |
| **ElaTimeline** | 数据展示 | 时间线（时间戳/标题/内容/图标） |
| **ElaMarkdownViewer** | 数据展示 | Markdown 查看器（主题自适应） |
| **ElaChatWidget** | AI 对话 | ChatGPT 风格聊天组件（步骤化消息 + 分层输入区 + 流式 / 停止） |
| **ElaChatView** | AI 对话 | 聊天消息列表（分段时间线 / 贴底跟随 / 空态建议 / 回到底部） |
| **ElaChatInput** | AI 对话 | 分层输入区（补全 / 附件 / 拖放粘贴 / 发送↔停止 / Shell 模式） |
| **ElaChatToolBar** | AI 对话 | 可复用聊天工具栏（自定义按钮 / 控件 / 分隔线，两段布局） |
| **ElaChatBubble** | AI 对话 | 步骤化消息气泡（分段：思考 / 正文 / 每步工具面板 / 步骤统计 / 底部操作） |
| **ElaChatQueueDock** | AI 对话 | 排队消息 dock（立即发送 / 编辑 / 移除，宿主驱动发送时机） |
| **ElaChatInputDock** | AI 对话 | 输入区替换 dock（权限 / 提问等卡片） |
| **ElaChatStreamBinder** | AI 对话 | 流式事件 → 组件映射器（步骤 / 思考 / 工具 / 统计 / 耗时 / 摘要） |
| **ElaChatAsyncWorker** | AI 对话 | 异步后端 worker 基类（QThread + asyncio + 命令队列 + 取消收尾） |
| **ElaChatMockBackend** | AI 对话 | 模拟后端（QTimer，无模型服务跑通全链路，信号与真实 worker 同构） |
| **ElaChatStatusBar** | AI 对话 | 宿主状态栏（信息 + 四档语义状态 + busy 指示） |
| **ElaSelectionAssistant** | 划词助手 | 全局划词监听 + 取词（模拟 Ctrl+C）+ 动作条，纯信号宿主实现行为 |
| **ElaSelectionPopup** | 划词助手 | 动作条浮窗（置顶 / 不抢焦点 / 越界收敛，可独立复用） |
| **ElaMouseMonitor** | 划词助手 | 轮询式全局鼠标监视（主线程 QTimer，信号坐标物理像素） |
| **ElaClipboardCapture** | 划词助手 | 模拟 Ctrl+C 异步取词（不预先改动剪贴板，可恢复原文本） |
| **ElaChip** | 展示 | 标签纸片（16 色，可关闭/可选择/可点击） |
| **ElaInfoBadge** | 展示 | 角标（Dot/Value/Icon 模式，5 种级别） |
| **ElaTerminalView** | 展示 | 终端输出（ANSI 色彩 / 行号 / 自动滚动 / 搜索过滤 / 选区复制 / 导出；`append` 吃 str 与 bytes） |
| **ElaTrayIcon** | 系统 | Windows 托盘图标（三态图标 / 气泡通知 / ElaMenu 右键菜单） |
| **ElaWordViewer** | 文档查看 | Word 文档嵌入查看 |
| **ElaExcelViewer** | 文档查看 | Excel 文件嵌入查看 |
| **ElaPowerPointViewer** | 文档查看 | PPT 文件嵌入查看 |
| **ElaWindowEmbedder** | 窗口嵌入 | 嵌入外部应用窗口 |
| **ElaBrowserEmbedder** | 窗口嵌入 | 嵌入 Chromium 浏览器，支持 CDP |
| **ElaSplashScreen** | 窗口 | 应用启动屏（全 QPainter 自绘，淡入淡出） |
| **ElaTaskbarProgress** | 工具 | Windows 任务栏进度 |
| **ElaSvgIconLoader** | 图标 | 二进制 SVG 图标加载器 |

## 运行示例

项目内建了组件展示示例：

```bash
python -m pyqt5_ela_pro.example
```

> 运行示例需要安装 `pywin32`（`pip install pywin32`），窗口嵌入和浏览器嵌入功能依赖于此。

将启动一个 ElaWindow 应用。侧边栏是**两级**的：一级是可折叠的分组，
展开后是页面（每个组件标题旁均有 `</> 代码` 按钮查看源码）。

分组依据是「这组页面回答的是同一个问题」，而不是「这是哪一类控件」——
后者会让同一族控件散在几页里（读者无法预测某个组件在哪一页）。

**基础组件**

| 页面 | 说明 |
|---|---|
| 输入与选择 | ElaLineEdit / ElaPlainTextEdit / ElaSpinBox / ElaDoubleSpinBox / ElaSlider / ElaCalendar / ElaCalendarPicker / ElaCheckBox / ElaRadioButton / ElaToggleSwitch / ElaRoller / ElaPasswordEdit / **ElaTagLineEdit** / ElaUploadArea / ElaSpotlight |
| 下拉框组件 | 全部下拉框变体（ElaComboBox / MultiSelect / SearchBox / TagBox / GhostBox…）+ 空选项演示 |
| 容器与布局 | ElaScrollArea / **ElaScrollPage** / ElaDrawerArea / ElaDrawer / ElaSplitter / ElaDivider / ElaGroupBox / ElaFlowLayout |
| 视图与列表 | ElaTreeView / ElaTableView / ElaListView / ElaSuggestBox / ElaKeyBinder / ElaPivot / ElaTabBar / ElaTabWidget / ElaBreadcrumbBar / ElaScrollBar / ElaToolBar |
| 按钮与菜单 | ElaPushButton / ElaToolButton / ElaIconButton / **ElaToggleButton** / ElaButton / ElaLongPressButton / ElaProgressButton / ElaSplitButton / ElaDropDownButton / SVG 图标按钮 / ElaMenu / ElaMenuBar |
| 进度与反馈 | ElaProgressBar / ElaProgressRing / ElaLCDNumber / ElaMessageButton / ElaInfoBadge / ElaChip / ElaSteps / ElaRatingControl / ElaPagination / ElaTimeline / 各类卡片 |

**数据与图表**

| 页面 | 说明 |
|---|---|
| 表格 | ElaDataTable（基础 / 异步 / 样式 / 排序）、ElaParquetTable |
| 图表（第三方库） | ElaPlotWidget（实时波形）、ElaFigureCanvas（静态图）、ElaDashboardGauge、GraphicsScene / View |
| ElaChartWidget 图表引擎 | 本库自带图表引擎的完整 API：10 组图表、采样、交互、tooltip |

**内容渲染**

| 页面 | 说明 |
|---|---|
| Markdown 渲染 | 按「文本与排版 / 代码块 / 数学公式 / Mermaid 图」四块分类展示 + 流式渲染 |
| Office 文档预览 | Word、Excel、PPT 文档嵌入查看 |

**AI 对话**（按**能力域**切，不按「应用场景」切 —— 同一组件的能力不该被打散在几页里）

聊天组件有些能力**只在流式过程中可见**（推理逐步浮现、工具卡忙碌环、底部行
隐藏、统计徽标落定），所以这五页统一是「**预填 + 可重播**」：页面构造完就有
内容，滚动即看完全貌；每节一个「重播流式」按钮把过程重走一遍。共用零件在
`example/chat_demo_kit.py`。

| 页面 | 回答的问题 | 说明 |
|---|---|---|
| 聊天组件总览 | 长什么样 | 预填一整轮（用户消息 + 附件 → 推理 → 正文 → 每步工具面板（成功 + 失败）→ 统计徽标 → 脚注），可重播；另有推理形态 / 工具分组 / 统计模式 / 免责声明 / 头像形状 / 正文限宽等外观开关 |
| 输入区能力 | 怎么接 | 一个真能用的 `ElaChatMockBackend` + `ElaChatStreamBinder`；六节：工具栏自定义 / 附件（文件·图片·粘贴·拖放）/ `@` 引用 / 清空上下文（二次确认）/ 新建话题 / 排队·撤回·重新生成·停止 |
| Agent 能力 | agent 多了什么 | 工具结果富渲染（`registerToolRenderer`）、审批·批准型、审批·问答型（逐题向导）、steer 插话、历史压缩、成本与上下文占用、手动重试 |
| 会话管理 | 多话题怎么管 | 一话题一 widget + `ElaTabBar`：切页不中止生成、归档（`exportSession` + 先 `abortTurn`）/ 恢复（`importSession`）、外观偏好在话题间传播 |
| 持久化与性能 | 怎么落库 | 回合日志（`ElaChatTurnJournal`，实时与重放并排对照 + 脏数据容错）、会话导出导入（`preserveIds` 先全量校验）、大消息量三条开关（延迟重排 / `beginBatch` / 视口挂起） |

**窗口与应用外壳**

| 页面 | 说明 |
|---|---|
| 应用框架 | ElaAppBar、ElaStatusBar、ElaNavigationBar |
| 弹窗与提示 | ElaToolTip、ElaStateToolTip、ElaToast、通知气泡、ElaMessageDialog / ElaConfirmDialog / ElaDialog / **ElaContentDialog** / **ElaColorDialog** |
| 启动与托盘 | ElaSplashScreen、ElaTaskbarProgress、ElaTrayIcon / ElaTrayHost |

**系统交互与嵌入**

| 页面 | 说明 |
|---|---|
| 外部内容嵌入 | ElaWindowEmbedder（01）/ ElaBrowserEmbedder（02）/ 多 URL 测试台（03） |
| 终端输出 | 只读终端视图：ANSI 颜色、跨分片转义、过滤、导出 |
| 划词助手 | ElaSelectionAssistant：全局划词（拖选 / 双击选词）、动作条（启停 / 动作勾选 / 紧凑模式 / 剪贴板恢复 / 最小长度）、手动弹出、事件日志与宿主 copy 实现 |

**动效与图形 / 参考文档**

| 页面 | 说明 |
|---|---|
| 动画与图标 | 淡入淡出、窗口抖动、ElaAnimatedMixin、图标浏览器、SVG 图标 |
| 节点图编辑器 | ElaBlueprintCanvas 节点图编辑器 |
| 聊天组件 API 指南 | 用 `ElaMarkdownViewer` 渲染的接入指南：组件栈与 worker 契约、四步接入（`llm_test/main.py` 全文）、API 速查、真实后端（`agent_demo.py` 全文）、运行与依赖 |

## 图表 API 规范

图表家族（`ElaChartWidget` / `ElaPlotWidget` / `ElaFigureCanvas` / `ElaDashboardGauge`）
统一 **camelCase** 命名；`ElaChartWidget` 的实例接口与 **ECharts 对齐**，
配置 / 控制 / 事件三层如下。

**配置与查询**

| 方法 | 说明 |
|---|---|
| `setOption(option, notMerge=False, lazyUpdate=False)` | **默认合并**（ECharts 语义）：dict 深合并；`series` / `dataZoom` / `graphic` 按 `id` → `name` → 下标逐项合并（未匹配旧项保留、新项追加）；其余 list 整体替换。`notMerge=True` 全量替换并重置图例选择；`lazyUpdate=True` 延迟到下一事件循环重建。返回 self |
| `getOption()` | 当前 option 深拷贝（`options` 帧保留，当前帧已合并） |
| `seriesRenderers` / `coords` / `components` | 渲染器 / 坐标系 / 组件实例列表（属性） |
| `palette()` / `colorForSeries(series)` | 当前调色板 / 指定系列主色 |
| `primaryCoord()` / `coordFor(seriesOpt)` | 主坐标系 / 按系列解析坐标系 |
| `hitItem(pos)` / `hoverInfo()` | 坐标 → ECharts click params / 当前悬停命中 |
| `convertToPixel(finder, value)` / `convertFromPixel(finder, value)` / `containPixel(finder, value)` | 数据 ↔ 像素换算与命中判定（finder：`"grid"` / `{"seriesIndex": 0}` 等） |
| `getWidth()` / `getHeight()` / `getDevicePixelRatio()` | 尺寸查询 |

**控制**

| 方法 | 说明 |
|---|---|
| `resize(opts=None)` / `resize(w, h)` | 重排；dict 形式 `{"width":…, "height":…}`，也兼容 QWidget 两参数 |
| `dispatchAction(payload)` | `legendToggleSelect` / `legendSelect` / `legendUnSelect` / `legendAllSelect` / `legendInverseSelect` / `dataZoom`（`start/end` 或 `startValue/endValue`）/ `restore` / `showTip` / `hideTip` / `highlight` / `downplay` / `timelineChange` / `timelinePlayChange`；返回是否识别 |
| `setInteractive(bool)` / `interactiveEnabled()` | 交互总开关（静态化整图） |
| `setInteractionEnabled(feature, bool)` / `isInteractionEnabled(feature)` | 逐项开关：`tooltip` / `legend` / `dataZoom` / `brush` / `timeline` / `toolbox` |
| `showLoading(type="default", opts=None)` / `hideLoading()` / `isLoading` | 加载遮罩（`text` / `color` / `textColor` / `maskColor` / `fontSize` / `showSpinner` / `spinnerRadius` / `lineWidth`） |
| `appendData({"seriesIndex"|"seriesName"|"seriesId", "data": …})` | 追加数据点（保留过渡动画） |
| `getDataURL(opts=None)` | 导出 `data:image/png;base64,…`（`type` / `pixelRatio` / `backgroundColor`） |
| `saveImage(path=None)` | 文件版导出 PNG（扩展；`path=None` 弹保存对话框） |
| `clear()` | 清空（等价 `setOption({}, notMerge=True)`） |
| `dispose()` / `isDisposed()` | 销毁（停定时器 / 断主题 / deleteLater）与状态查询 |

**事件**

ECharts 事件名经 `on(eventName, handler)` / `off(eventName=None, handler=None)`
注册（handler 收 ECharts params dict，异常被吞掉并告警，不会终止进程）：

| 事件名 | 载荷 | 触发 |
|---|---|---|
| `click` | params（`componentType` / `seriesType` / `seriesIndex` / `seriesName` / `name` / `dataIndex` / `data` / `value` / `color` / `offsetX` / `offsetY`） | 点击命中数据项 |
| `legendselectchanged` | `{name, selected}` | 图例点击切换系列 |
| `datazoom` | `{start, end, batch}` | 缩放窗口变化（滚轮 / 拖拽 / 平移 / restore） |
| `timelinechanged` | `{currentIndex}` | 时间轴换帧（含自动播放） |
| `brushselected` | `{batch, selected}` | 刷选变化 |
| `restore` / `highlight` / `downplay` | 对应 params | 动作触发 |
| `finished` | `{}` | 动画播放完毕 |

同时保留 Qt 信号（宿主可直接 connect）：`legendToggled(str, bool)` /
`dataZoomChanged(float, float)` / `timelineChanged(int)` / `itemClicked(dict)` /
`toolboxTriggered(str)` / `brushChanged(list)` / `finished()`。
`selectchanged`（选中态）本轮未实现。

**扩展（自定义系列 / 组件）**

```python
from pyqt5_ela_pro.charts import (
    SeriesRenderer, registerSeries, chartToken,
)

class MySeries(SeriesRenderer):
    optionKey = "line"           # 或注册自己的 "myType"

    def hitTest(self, pos): ...  # 返回 {"name", "value", "series"[可选 text/title]}
    def valueAtIndex(self, i): ...
    def layout(self, rect): ...
    def paint(self, p, animT): ...   # 颜色经 chartToken("color.primary") 取主题令牌

registerSeries("myType", MySeries)   # 同名覆盖会告警
```

**数据格式**（与系列 `data` 一致）：`number` / `[x, y]` / `[x, y, value]` /
`{"value": [...], "tooltip": {"formatter": "自定义文案"}, "itemStyle": {"color": "#..."}, ...}`；
坐标系由 `coordinateSystem` 声明（缺省 `grid`，可选 `polar` / `singleAxis` / `calendar`）。

**ECharts 兼容要点**

- **配色**：默认调色板为 ECharts 官方 9 色（`ECHARTS_PALETTE`），可用顶层
  `"color": [...]` 覆盖；系列 `itemStyle.color` / 数据项 `itemStyle.color`
  逐级优先。
- **通用键**：`itemStyle`（`color` / `opacity` / `borderColor` / `borderWidth` /
  `borderRadius`）、直角系列 `label`（`show` / `formatter` 模板或回调 /
  `fontSize` / `color` / `position`）、`line.stack` + `areaStyle.color`（渐变
  colorStops）、`barGap` / `barCategoryGap`、`emphasis` / `blur`（命中项
  `emphasis.itemStyle.color`、未命中项 `blur.itemStyle.opacity`，缺省加亮 / 淡化）、
  `silent`（跳过命中）、`animation`（系列级关闭动画）、`id`（合并匹配键）。
- **坐标轴键**：`boundaryGap` / `inverse` / `scale` / `nameLocation` / `nameGap` /
  `interval` / `minInterval` / `maxInterval` / `splitNumber` /
  `axisLabel`（`show` / `interval` / `rotate` / `formatter` / `color` / `fontSize`）/
  `axisTick` / `axisLine` / `splitLine` / `splitArea`；`grid` 支持
  `show` / `containLabel` / `borderColor` / `borderWidth` / `backgroundColor`。
- **tooltip 键**：`formatter`（模板 / callable）/ `valueFormatter` /
  `axisPointer.type`（`line` / `shadow` / `cross` / `none`）/ `backgroundColor` /
  `borderColor` / `borderWidth` / `textStyle`；数据项可用
  `{"value": …, "tooltip": {"formatter": …}}` 覆盖单点文案。
- **timeline**：顶层 `baseOption` + `options` 帧，`timeline.currentIndex`
  指定初始帧；`goto()` / `dispatchAction({"type": "timelineChange"})` 换帧时
  `baseOption` 深合并帧 option 并保留过渡动画。
- **交互**：
  - `sunburst` / `treemap`：点击父级扇区/矩形下钻，点击中心孔 / 空白 / 面包屑
    返回，`resetDrill()` 直接回顶层；
  - `graph`：`draggable: true` 时按住节点拖拽（拖拽后位置固定，
    `resetPositions()` 复位）；`roam` 开启滚轮缩放 + 空白拖拽平移
    （`resetRoam()` 复位）；
  - `map`：`roam: true` 开启滚轮缩放（0.2~6）、拖拽平移，`resetRoam()` 复位；
  - 其余交互统一由 `setInteractive` / `setInteractionEnabled` 管控。
- **布局排布**：竖直 `visualMap` 占右侧条带、`timeline` 最底、`dataZoom` 与
  横向 `visualMap` 依次上移，坐标系自动避开，互不遮挡。

## 依赖

| 依赖 | 必需 | 用途 |
|---|---|---|
| Python >= 3.8 | 是 | — |
| PyQt5 >= 5.15.0 | 是 | 界面框架 |
| PyQt5-ElaWidgetTools == 0.12.1 | 是 | 上游基础组件库 |
| pypinyin >= 0.50.0 | 是 | 拼音搜索支持 |
| pywin32 | 否（`[all]`） | 窗口嵌入 / 浏览器嵌入 / 任务栏进度 |
| comtypes | 否（`[all]`） | Office 文档预览（ActiveX） |
| pygments | 否（`[all]`） | `ElaMarkdownViewer` 代码语法高亮（缺失自动降级） |
| tsdownsample | 否（`[all]`） | `ElaChartWidget` 大数据降采样（缺失自动降级） |
| mermaidx | 否（`[all]`，Python≥3.10） | `ElaMarkdownViewer` Mermaid 图渲染（无浏览器；缺失回退代码卡片） |
| polars | 否 | Parquet 文件查看 |
| pyqtgraph | 否 | ElaPlotWidget 图表 |
| matplotlib | 否 | ElaFigureCanvas 图表 |

## 设计原则

- **全 QPainter 自绘** — 所有组件通过 `QPainter` 在 `paintEvent` 中自定义绘制，不使用 QSS
- **主题感知** — 组件自动响应 `eTheme.setThemeMode(Dark/Light)` 切换
- **C++ 移植** — 大量组件参照 [ElaWidgetTools](https://github.com/RainbowCandyX/ElaWidgetTools) C++ 源码移植
- **One-section-per-method** — 示例代码中每个 `_demoXxx` 方法对应一个独立组件演示节，便于代码查看器精确定位源码

## 平台

Windows AMD64。

## 许可证

MIT
