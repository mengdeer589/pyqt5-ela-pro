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
| `ElaChartWidget`（`charts/`） | InstructionX_UIKit `charts`（类 ECharts `set_option` 引擎）移植 |
| 蓝图节点图编辑器（`blueprint/`） | InstructionX_UIKit `blueprint` + `anim.painted.SpinnerArc` 移植 |
| `ElaMarkdownViewer` 流式增量渲染 / 公式提取 | InstructionX_UIKit `components.markdown_view` 思路移植；公式渲染为自研 `math_lite.py` |
| `ElaTagBox` / `ElaTagMultiBox` / `ElaTagSearchBox` / `ElaTagSearchMultiBox` / `ElaTagLineEdit` | PyQt-Fluent-Widgets Tag 组件设计参考 |
| `ElaBrowserEmbedder` / `ElaWindowEmbedder` | 自研（Chromium CDP + win32gui） |

## 特性

### 输入组件
- **ElaSearchBox / ElaSearchMultiBox** — 可搜索下拉框，支持中文拼音首字母搜索
- **ElaTagBox / ElaTagMultiBox / ElaTagSearchBox / ElaTagSearchMultiBox** — Tag 风格下拉框变体
- **ElaTagLineEdit** — Tag 风格输入框
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
- **ElaChartWidget** — 类 ECharts 图表引擎（纯 QPainter，21 种系列；大数据降采样需 `tsdownsample`）
- **ElaDashboardGauge** — 仪表盘组件（全 QPainter 自绘，指针动画，颜色分段）
- **ElaPlotWidget** — pyqtgraph 绘图控件（主题感知，可选依赖 pyqtgraph）
- **ElaTimeline** — 时间线（时间戳、标题、正文、可选图标）
- **ElaMarkdownViewer** — Markdown 查看器：主题自适应、Typora 风格排版
  （标题层级字号 / 1.6 倍行高 / 引用块浅底色 / 无边框代码卡片 / 图片居中）、
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
  Mermaid 图渲染（可选依赖 `mermaidx`，无浏览器；缺失时回退代码卡片）、
  任务列表可点击勾选、图片点击信号与预览、本地图片右键另存为、
  表格斑马纹与列宽设置、
  图片基准路径与超宽缩放、远程图片默认拦截、
  搜索 / 缩放 / `exportPdf(path, page_size, margins_mm)` / `printDocument()` 打印、
  `toHtml(embed_images=True)` 单文件导出（图片内嵌 data URI）、
  `markdownSelection()` / `selectionQuoted` 选中内容还原为 Markdown 源（引用回复）、
  锚点跳转可返回上一位置、
  流式追加（`appendMarkdown` / `endStream`，贴底自动跟随、末尾打字光标，
  面向 AI 对话场景）

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
- **ElaBrowserEmbedder** — 嵌入 Chromium 浏览器，支持 `load_url()`、本地文件 Path 加载、CDP 控制

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
  charts/                   # ElaChartWidget 图表引擎（core/axes/系列/组件）
  ela_dashboard_gauge.py    # ElaDashboardGauge
  ela_pyqtgraph_canvas.py   # ElaPlotWidget（可选依赖 pyqtgraph）
  ela_figure_canvas.py      # ElaFigureCanvas（可选依赖 matplotlib）
  ela_info_badge.py         # ElaInfoBadge
  ela_chip.py               # ElaChip
  ela_markdown_viewer.py    # ElaMarkdownViewer（流式 / 公式 / 高亮 / 表格）
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
  example/                  # 组件演示示例
    __main__.py              # 入口（ElaWindow + 加载动画）
    base_page.py             # 示例基类（代码查看器核心）
    basic_container_page.py  # 原生输入/基础/导航控件
    container_display_page.py# 原生容器/展示/对话框/菜单控件
    extension_components_page.py  # pyqt5_ela_pro 扩展组件
    form_button_page.py      # 按钮 & 对话框
    combo_box_page.py        # 9 种下拉框变体
    table_chart_page.py      # 表格、图表
    markdown_page.py         # ElaMarkdownViewer（文本 / 代码 / 公式 / Mermaid 分类 + 流式）
    drawer_tooltip_page.py   # 抽屉、提示
    animation_icon_page.py   # 动画、图标
    application_page.py      # 应用框架
    application_utils_page.py# 辅助组件
    advanced_page.py         # Office 文档预览
    window_embedder_page.py  # 窗口嵌入 + 浏览器嵌入
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
| **ElaChartWidget** | 数据展示 | 类 ECharts 引擎：21 系列 + 交互组件 |
| **ElaDashboardGauge** | 数据展示 | 仪表盘（全自绘，指针动画，颜色分段） |
| **ElaPlotWidget** | 数据展示 | pyqtgraph 绘图控件（主题自适应，可选依赖） |
| **ElaFigureCanvas** | 数据展示 | Matplotlib 画布（主题感知，可选依赖） |
| **ElaTimeline** | 数据展示 | 时间线（时间戳/标题/内容/图标） |
| **ElaMarkdownViewer** | 数据展示 | Markdown 查看器（主题自适应） |
| **ElaChip** | 展示 | 标签纸片（16 色，可关闭/可选择/可点击） |
| **ElaInfoBadge** | 展示 | 角标（Dot/Value/Icon 模式，5 种级别） |
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

将启动一个 ElaWindow 应用，包含以下演示页面（每个组件标题旁均有 `</> 代码` 按钮查看源码）：

| 页面 | 说明 |
|---|---|
| 基础控件 | 原生 PyQt5ElaWidgetTools 输入/基础/导航组件 |
| 容器展示 | 原生容器/展示/对话框/菜单组件 |
| 扩展组件 | pyqt5_ela_pro 扩展组件（ElaDivider/ElaChip/ElaSteps/评分/分页/时间线等） |
| 应用框架 | ElaAppBar、ElaStatusBar |
| 增强按钮 | ElaButton、ElaDropDownButton、ElaSplitButton、ElaToast 等 |
| 下拉框组件 | 全部 9 种下拉框变体 + 空选项演示 |
| 表格与图表 | ElaDataTable（基础/异步/样式/排序）、ElaParquetTable、ElaFigureCanvas |
| Markdown 渲染 | 按「文本与排版 / 代码块 / 数学公式 / Mermaid 图」四块分类展示 + 流式渲染（聊天发送 / 同内容回放） |
| 弹窗与提示 | ElaDrawer、ElaDrawerArea、ElaToolTip、ElaStateToolTip、ElaSpotlight |
| 动画与图标 | 淡入淡出、窗口抖动、ElaAnimatedMixin、SVG 图标浏览器 |
| 应用辅助 | ElaSplashScreen、ElaTaskbarProgress |
| Office 预览 | Word、Excel、PPT 文档嵌入查看 |
| 窗口嵌入 | 外部窗口 + Chromium 浏览器嵌入 |

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
