# pyqt5-ela-pro

PyQt5 extension widget library based on PyQt5ElaWidgetTools.

## 背景

本库基于 [PyQt5-ElaWidgetTools](https://github.com/anomalyco/PyQt5-ElaWidgetTools) 进行扩展开发，同时参考了 [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) 和 [PyQt-SiliconUI](https://github.com/AlexCode1314/PyQt-SiliconUI) 的部分组件设计思路，在 **Minimax** 与 **DeepSeek** 模型的辅助下完成。

## 特性

- **搜索式下拉框** — ElaSearchBox / ElaSearchMultiBox，支持中文拼音首字母搜索
- **Tag 风格组件** — ElaTagLineEdit、ElaTagBox / ElaTagMultiBox / ElaTagSearchBox / ElaTagSearchMultiBox
- **增强按钮** — ElaPrimaryButton、ElaThemeToolButton、ElaLongPressButton、ElaProgressButton、ElaSvgButton、ElaSvgIconButton
- **外部窗口嵌入** — ElaWindowEmbedder（通过 win32gui 嵌入外部窗口）、ElaBrowserEmbedder（嵌入 Chromium 浏览器）
- **Office 文档查看** — ElaWordViewer、ElaExcelViewer、ElaPowerPointViewer
- **数据展示** — ElaDataTable、ElaParquetTable、ElaTrendChart（趋势图）
- **SVG 图标系统** — ElaSvgIconLoader 加载自定义二进制图标格式，ElaSvgButton / ElaSvgIconButton 展示
- **主题感知** — ElaThemeWidget 基类自动响应暗色/亮色主题切换
- **动画工具** — fade_in / fade_out / shake_window / ElaAnimatedMixin
- **弹窗与提示** — ElaMessageDialog、ElaNotifyPopup、ElaToolTip / ElaStateToolTip
- **侧边抽屉** — ElaDrawer（支持左/右/上/下四个方向）
- **Windows 任务栏进度** — ElaTaskbarProgress
- **启动屏** — ElaSplashScreen
- **分割器** — ElaSplitter

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

        page = QWidget()
        layout = QVBoxLayout(page)
        btn = ElaPrimaryButton("Hello, pyqt5-ela-pro")
        btn.clicked.connect(lambda: show_notify("提示", "按钮被点击了！"))
        layout.addWidget(btn)

        self.addPageNode("首页", page)

window = MainWindow()
window.show()
sys.exit(app.exec_())
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
| `create_ela_splitter(orientation, widgets)` | 创建主题感知分割器 |
| `show_notify(title, text, ...)` | 弹出通知 |

### 组件类

| 组件 | 分类 | 说明 |
|---|---|---|
| **ElaThemeWidget** | 基类 | 主题感知基础控件 |
| **ElaAnimatedMixin** | 动画 | 动画混入类 |
| **ElaSearchBox** | 输入 | 可搜索单选下拉框 |
| **ElaSearchMultiBox** | 输入 | 可搜索多选下拉框 |
| **ElaTagBox** | 输入 | Tag 样式单选下拉框 |
| **ElaTagMultiBox** | 输入 | Tag 样式多选下拉框 |
| **ElaTagSearchBox** | 输入 | Tag + 搜索 单选下拉框 |
| **ElaTagSearchMultiBox** | 输入 | Tag + 搜索 多选下拉框 |
| **ElaTagLineEdit** | 输入 | Tag 风格输入框 |
| **ElaPrimaryButton** | 按钮 | 主风格按钮 |
| **ElaThemeToolButton** | 按钮 | 主题感知工具栏按钮 |
| **ElaLongPressButton** | 按钮 | 长按触发按钮 |
| **ElaProgressButton** | 按钮 | 含进度指示的按钮 |
| **ElaSvgButton** | 按钮 | SVG 推按钮 |
| **ElaSvgIconButton** | 按钮 | SVG 图标工具按钮 |
| **ElaDataTable** | 数据展示 | 数据表格控件 |
| **ElaParquetTable** | 数据展示 | Parquet 文件查看 |
| **ElaTrendChart** | 数据展示 | 趋势折线图 |
| **ElaWordViewer** | 文档查看 | Word 文档嵌入查看 |
| **ElaExcelViewer** | 文档查看 | Excel 文件嵌入查看 |
| **ElaPowerPointViewer** | 文档查看 | PPT 文件嵌入查看 |
| **ElaWindowEmbedder** | 窗口嵌入 | 嵌入外部应用窗口 |
| **ElaBrowserEmbedder** | 窗口嵌入 | 嵌入 Chromium 浏览器 |
| **ElaDrawer** | 导航 | 侧边抽屉面板 |
| **ElaDrawerPosition** | 枚举 | 抽屉方向枚举 |
| **ElaScrollableMenu** | 菜单 | 可滚动弹出菜单 |
| **ElaToolTip** | 提示 | 自定义工具提示 |
| **ElaStateToolTip** | 提示 | 状态提示控件 |
| **ElaToolTipPosition** | 枚举 | 提示位置枚举 |
| **ElaMessageDialog** | 弹窗 | 消息确认对话框 |
| **ElaDialogBase** | 弹窗 | 对话框基类 |
| **ElaNotifyPopup** | 弹窗 | 弹出通知控件 |
| **ElaSplashScreen** | 窗口 | 启动屏 |
| **ElaSplitter** | 布局 | 主题感知分割器 |
| **ElaTaskbarProgress** | 工具 | Windows 任务栏进度 |
| **ElaSvgIconLoader** | 图标 | SVG 图标加载器 |

## 运行示例

项目内建了组件展示示例：

```bash
python -m pyqt5_ela_pro.example
```

> 运行示例需要安装 `pywin32`（`pip install pywin32`），窗口嵌入和浏览器嵌入功能依赖于此。

将启动一个 ElaWindow 应用，包含以下演示页面：

- 基础组件 — pyqt5-elawidgettools 原生组件展示
- 表单与按钮 — 增强按钮 & Tag 输入框
- 下拉框组件 — 全部 8 种下拉框变体
- 表格与图表 — ElaDataTable、ElaTrendChart
- 抽屉与提示 — ElaDrawer、ElaToolTip、ElaStateToolTip
- 动画与图标 — fade_in/out、shake_window、SVG 图标浏览器
- 窗口嵌入 — 外部窗口嵌入演示
- 应用级组件 — 启动屏、任务栏进度等
- 浏览器嵌入 — Chromium 浏览器嵌入

## 依赖

- Python >= 3.8
- PyQt5 >= 5.15.0
- PyQt5-ElaWidgetTools >= 0.8.0
- pypinyin >= 0.50.0
- pywin32（运行示例及使用窗口嵌入功能时需要）

## 平台

Windows AMD64。

## 许可证

MIT
