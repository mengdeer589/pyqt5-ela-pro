# pyqt5-ela-pro

PyQt5 extension widget library based on PyQt5ElaWidgetTools.

## 背景

本库基于 [PyQt5-ElaWidgetTools](https://github.com/HIllya51/PyElaWidgetTools) 进行扩展开发，同时参考了 [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) 和 [PyQt-SiliconUI](https://github.com/ChinaIceF/PyQt-SiliconUI) 的部分组件设计思路，在 **Minimax** 与 **DeepSeek** 模型的辅助下完成。

## 特性

### 输入组件
- **ElaSearchBox / ElaSearchMultiBox** — 可搜索下拉框，支持中文拼音首字母搜索
- **ElaTagBox / ElaTagMultiBox / ElaTagSearchBox / ElaTagSearchMultiBox** — Tag 风格下拉框变体
- **ElaTagLineEdit** — Tag 风格输入框
- 所有下拉框组件均提供 `items` 属性获取选项列表

### 按钮
- **ElaPrimaryButton** — 主色调按钮
- **ElaThemeToolButton** — 主题感知工具栏按钮
- **ElaLongPressButton** — 长按触发（防误触）
- **ElaProgressButton** — 含进度指示的按钮
- **ElaSvgButton / ElaSvgIconButton** — 基于 SVG 图标的按钮

### 数据展示
- **ElaDataTable** — 数据表格（支持排序、样式、对齐）
- **ElaParquetTable** — Parquet 文件分页查看
- **ElaTrendChart** — 趋势图（多曲线、散点图、交互操作）

### 文档查看
- **ElaWordViewer、ElaExcelViewer、ElaPowerPointViewer** — 通过 ActiveX 嵌入 Office 文档查看

### 窗口嵌入
- **ElaWindowEmbedder** — 通过 win32gui 嵌入外部窗口
- **ElaBrowserEmbedder** — 嵌入 Chromium 浏览器，支持 `load_url()`、本地文件 Path 加载、CDP 控制

### 动画工具
- **fade_in / fade_out** — 淡入淡出动画
- **shake_window** — 窗口抖动
- **ElaAnimatedMixin** — 为对话框注入 `fade_in()` / `fade_out()` 方法

### 弹窗与提示
- **ElaMessageDialog** — 消息确认对话框
- **ElaDialogBase** — 可定制按钮的对话框基类
- **ElaNotifyPopup** — 右下角弹出通知
- **ElaToolTip / ElaStateToolTip** — 自定义工具提示、状态提示

### 其他
- **ElaDrawer** — 四方向侧边抽屉
- **ElaSplashScreen** — 应用启动屏
- **ElaTaskbarProgress** — Windows 任务栏进度
- **ElaSplitter** — 主题感知分割器
- **ElaSvgIconLoader** — 二进制 SVG 图标加载器
- **ElaThemeWidget** — 主题感知基类，自动响应暗色/亮色切换
- 所有样式通过 **QPalette + QTextCharFormat** 实现，不使用 QSS

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
```

## 快速开始

```python
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
from PyQt5ElaWidgetTools import eApp, ElaWindow

from pyqt5_ela_pro import ElaPrimaryButton, show_notify, fade_in

app = QApplication(sys.argv)
eApp.init()

class MainWindow(ElaWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("pyqt5-ela-pro")
        self.resize(1000, 700)

        page = QWidget(self)
        layout = QVBoxLayout(page)
        btn = ElaPrimaryButton("Hello, pyqt5-ela-pro")
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
  __init__.py
  ela_tag_box.py
  ela_tag_multi_box.py
  ela_tag_search_box.py
  ela_tag_search_multi_box.py
  ela_tag_line_edit.py
  combo_box.py
  ela_primary_button.py
  ela_theme_tool_button.py
  ela_long_press_button.py
  ela_progress_button.py
  svg_icon.py
  table_view.py
  parquet_table.py
  ela_trend_chart.py
  window_embedder.py
  browser_embedder.py
  office_viewer.py
  tooltips.py
  notify_popup.py
  message_dialog.py
  dialog_base.py
  ela_side_drawer.py
  ela_splitter.py
  taskbar_progress.py
  splash_screen.py
  widget_base.py
  animation.py
  example/                  # 组件演示示例
    __main__.py              # 入口（ElaWindow + splash）
    base_page.py             # 示例基类（代码查看器核心）
    basic_container_page.py  # 42 个基础控件演示
    form_button_page.py      # 按钮 & 输入框
    combo_box_page.py        # 9 种下拉框变体
    table_chart_page.py      # 表格、图表
    drawer_tooltip_page.py   # 抽屉、提示
    animation_icon_page.py   # 动画、图标
    application_page.py      # 应用框架
    application_utils_page.py# 辅助组件
    advanced_page.py         # Office 文档预览
    window_embedder_page.py  # 窗口嵌入
    browser_page.py          # 浏览器嵌入
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
| **ElaPrimaryButton** | 按钮 | 主色调按钮 |
| **ElaThemeToolButton** | 按钮 | 主题感知工具栏按钮 |
| **ElaLongPressButton** | 按钮 | 长按触发按钮 |
| **ElaProgressButton** | 按钮 | 含进度指示的按钮 |
| **ElaSvgButton** | 按钮 | SVG 推按钮 |
| **ElaSvgIconButton** | 按钮 | SVG 图标工具按钮 |
| **ElaDataTable** | 数据展示 | 数据表格控件 |
| **ElaParquetTable** | 数据展示 | Parquet 文件分页查看 |
| **ElaTrendChart** | 数据展示 | 折线图 / 散点图 |
| **ElaWordViewer** | 文档查看 | Word 文档嵌入查看 |
| **ElaExcelViewer** | 文档查看 | Excel 文件嵌入查看 |
| **ElaPowerPointViewer** | 文档查看 | PPT 文件嵌入查看 |
| **ElaWindowEmbedder** | 窗口嵌入 | 嵌入外部应用窗口 |
| **ElaBrowserEmbedder** | 窗口嵌入 | 嵌入 Chromium 浏览器，支持 CDP |
| **ElaDrawer** | 导航 | 四方向侧边抽屉 |
| **ElaDrawerPosition** | 枚举 | 抽屉方向枚举 |
| **ElaToolTip** | 提示 | 自定义工具提示 |
| **ElaStateToolTip** | 提示 | 状态提示控件 |
| **ElaToolTipPosition** | 枚举 | 提示位置枚举 |
| **ElaMessageDialog** | 弹窗 | 消息确认对话框 |
| **ElaDialogBase** | 弹窗 | 可定制按钮的对话框基类 |
| **ElaNotifyPopup** | 弹窗 | 弹出通知控件 |
| **ElaSplashScreen** | 窗口 | 应用启动屏 |
| **ElaSplitter** | 布局 | 主题感知分割器 |
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
| 基础控件 | 原生 PyQt5ElaWidgetTools 组件：输入框、按钮、滑块、日历、卡片、菜单等 |
| 应用框架 | ElaAppBar、ElaStatusBar |
| 增强按钮 | ElaPrimaryButton、ElaTagLineEdit、长按按钮、进度按钮、SVG 按钮等 |
| 下拉框组件 | 全部 9 种下拉框变体 + 空选项演示 |
| 表格与图表 | ElaDataTable（基础/异步/样式/排序）、ElaParquetTable、ElaTrendChart |
| 弹窗与提示 | ElaDrawer、ElaToolTip、ElaStateToolTip |
| 动画与图标 | 淡入淡出、窗口抖动、SVG 图标浏览器等 |
| 应用辅助 | ElaSplashScreen、ElaTaskbarProgress |
| Office 文档预览 | Word、Excel、PPT 文档嵌入查看 |
| 窗口嵌入 | 外部窗口嵌入演示 |
| 浏览器嵌入 | Chromium 浏览器嵌入（多实例、本地文件） |

## 依赖

| 依赖 | 必需 | 用途 |
|---|---|---|
| Python >= 3.8 | 是 | — |
| PyQt5 >= 5.15.0 | 是 | 界面框架 |
| PyQt5-ElaWidgetTools >= 0.8.0 | 是 | 上游基础组件库 |
| pypinyin >= 0.50.0 | 是 | 拼音搜索支持 |
| pywin32 | 否 | 窗口嵌入 / 浏览器嵌入 |
| polars | 否 | Parquet 文件查看 |

## 设计原则

- **不使用 QSS** — 所有样式通过 `QPalette`、`QTextCharFormat` 等 Qt 原生 API 实现，确保主题切换一致性
- **主题感知** — 组件自动响应 `eTheme.setThemeMode(Dark/Light)` 切换
- **One-section-per-method** — 示例代码中每个 `_demoXxx` 方法对应一个独立组件演示节，便于代码查看器精确定位源码

## 平台

Windows AMD64。

## 许可证

MIT
