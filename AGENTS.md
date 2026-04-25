# AGENTS.md

## Project Overview

`pyqt5_ela_pro` is a PyQt5 extension widget library based on `PyQt5-ElaWidgetTools`.

## Package Structure

- `pyqt5_ela_pro/` — main package (importable as `from pyqt5_ela_pro import ...`)
- `pyqt5_ela_pro/example/` — widget demo examples (runnable via `python -m pyqt5_ela_pro.example`)
- `example/` — separate standalone demo app using `PyQt5ElaWidgetTools` directly

## Dependencies

- `PyQt5>=5.15.0`

## Installing Dependencies

If you need to install a library, use `uv pip install xxx`.
- `PyQt5-ElaWidgetTools>=0.8.0` (external package, not in this repo)
- `pypinyin>=0.50.0`

Dev: `pytest`, `black`, `flake8`

## Running the Example

```powershell
# Run pyqt5_ela_pro widget examples
uv run python -m pyqt5_ela_pro.example

# Run the standalone demo (from repo root)
cd example && uv run python main.py
```

## Platform

Windows AMD64 only (per `uv.lock` required-markers).

## No Test Infrastructure

No `tests/` directory exists. pytest is listed in dev dependencies but no test commands are configured.

## Linting/Type Checking

No `ruff`, `mypy`, or other linting configs found. Run manually if needed:
```powershell
ty check pyqt5_ela_pro/
ruff format pyqt5_ela_pro/
```

## Build

```powershell
uv build --wheel
```

## ElaWindow 组件使用说明

`ElaWindow` 是一个基于 `QMainWindow` 的主题窗口，使用前必须先调用 `eApp.init()`。

### 基本用法

```python
from PyQt5.QtWidgets import QApplication
from PyQt5ElaWidgetTools import eApp, ElaWindow

app = QApplication(sys.argv)
eApp.init()                          # 必须优先调用

class MyWindow(ElaWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("标题")
        self.resize(1200, 800)
        self.setUserInfoCardTitle("用户名")
        self.setUserInfoCardSubTitle("user@email.com")
        # 添加导航页面
        self.addPageNode("页面A", some_widget)
        self.addPageNode("页面B", another_widget)

window = MyWindow()
window.show()
```

### 页面导航管理

核心方法：

| 方法 | 说明 |
|---|---|
| `addPageNode(name, widget, parentKey=None, icon=None)` | 添加一个导航页，parentKey 指定父级分组 |
| `addExpanderNode(name, icon, parentKey=None)` | 添加一个可展开的分组节点，返回 `(key, key)` |
| `addPageNodeKeyPoints(name, widget, parentKey, keyPoints, icon=None)` | 添加带角标数的页面节点 |
| `addFooterNode(name, widget, keyPoints, icon=None)` | 添加底部导航节点 |
| `expandNavigationNode(key)` | 展开指定导航分组 |
| `navigation(key)` | 编程式导航到指定页面 |
| `setCentralWidget(widget)` | 替换整个导航区域为单页面（无导航树） |

### 页面层级结构示例

```python
# 1) 顶层页面
self.addPageNode("首页", home_page, icon=ElaIconType.IconName.House)

# 2) 带分组的页面
group_key, _ = self.addExpanderNode("工具组", ElaIconType.IconName.Folder)
self.addPageNode("工具A", tool_a_page, group_key)
self.addPageNode("工具B", tool_b_page, group_key, ElaIconType.IconName.Doc)
self.addPageNodeKeyPoints("工具C", tool_c_page, group_key, 3, ElaIconType.IconName.Doc)
self.expandNavigationNode(group_key)

# 3) 底部固定节点
_, setting_key = self.addFooterNode("设置", setting_page, 0, ElaIconType.IconName.Gear)
```

### 窗口配置

```python
self.setCentralCustomWidget(widget)        # 设置 AppBar 与页面之间的自定义区域
self.setCustomWidget(area, widget)         # 在 AppBar 指定区域嵌入控件
self.setCustomMenu(menu)                   # 设置 AppBar 菜单
self.setWindowPaintMode(mode)              # 设置窗口绘制模式
self.setStackSwitchMode(mode)              # 设置页面切换动画模式
self.setNavigationBarDisplayMode(mode)     # 设置导航栏显示模式
self.setIsDefaultClosed(False)             # 禁用默认关闭（配合自定义关闭对话框）
self.moveToCenter()                        # 窗口居中
```

### 信号连接

```python
self.userInfoCardClicked.connect(callback)       # 用户信息卡片点击
self.navigationNodeClicked.connect(callback)     # 导航节点点击
self.closeButtonClicked.connect(callback)        # 关闭按钮点击
self.pWindowPaintModeChanged.connect(callback)   # 窗口绘制模式改变
self.pStackSwitchModeChanged.connect(callback)   # 页面切换模式改变
```

### 关键注意事项

1. `addPageNode` 的第一个参数 `name` 会同时作为导航树的显示文本和页面的默认 key
2. 使用 `addExpanderNode` / `addPageNode` 构建导航树时，会**自动隐藏**左侧导航栏中的默认标题区域
3. 如果不需要导航树（单页面应用），使用 `setCentralWidget(widget)` 替代 `addPageNode`
4. `eApp.init()` **必须在**创建任何 `ElaWindow` 实例之前调用
5. 主题切换使用 `eTheme.setThemeMode(ElaThemeType.ThemeMode.Dark/Light)`

## Gotchas

- `example/mainwindow.py:62` contains a hardcoded user path: `C:\Users\11737\Pictures\冥契\過去未来1.jpg`
- `example/beforemain.py` runs before the main window — check it when debugging startup issues
- The `icons/packages/fluent_ui_icon_regular.icons` file is a custom binary format used by `svg_icon.py`
