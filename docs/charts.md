# 图表 API 规范

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


---

**可运行示例**：`example/charts_page.py`；`ElaChartWidget` 的能力速览（21 系列 / 交互 / 大数据）见 README「核心能力」。
