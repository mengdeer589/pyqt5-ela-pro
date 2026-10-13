# 性能探针（随库分发）

两个**宿主可直接跑**的探针，用来分辨「这笔开销是我的代码、是 Qt 版本、还是绑定（sip vs
shiboken）」。判读方法、实测基线与四条宿主配方见 [`docs/performance.md`](../../docs/performance.md)。

```powershell
python tools/perf/bench_micro.py       # 底层原语：对象创建 / C++→Python 虚调用 / 方法调用 / 信号
python tools/perf/bench_components.py  # 本库组件的构造成本表（per-instance + 是否原生子窗口）
```

## `bench_micro.py`：把绑定与 Qt 版本分开

同一个脚本可在三种环境里跑，对比出两块：

| 对比 | 差反映的是 |
|---|---|
| PyQt5（sip + Qt5）↔ PyQt6（sip + Qt6） | **Qt 版本**内核差异（实测 `QWidget()` ≈1.5×、字体度量 1.6×） |
| PyQt6（sip + Qt6）↔ PySide6（shiboken + Qt6） | **绑定**差异（实测 `QWidget()` **5.5×**、`QLabel` 3.7×；`Signal.connect` 反而快 2×） |

关键判读（2026-10 实测，Win11）：凡是不碰 QWidget 构造的操作（值类型、纯 C++ 调用、
无参 getter）两栈基本持平；**凡是要造控件的都会跳 5~7 倍**。慢机上放大更狠（Win7 VM 上
同一探针是 **15×**），所以「老机器更卡」是预期行为。

## `bench_components.py`：组件构造成本

按「单实例构造 + `deleteLater()`」的中位值给出 ms/实例（含子控件数、是否创建原生子窗口），
用来判断「哪些组件适合大量实例化、哪些要在启动期少建」。示例结论（Qt 6.8.4）：
`ColorText` 0.033ms / `ElaButton` 0.067ms 可以按需大量建；`ElaField` 0.42ms、
`ElaMarkdownViewer` 0.73ms、`ElaChatView` 1.50ms、`ElaTerminalView` 4.27ms 属重组件，
启动期只建可见的那几个。
