"""
Mermaid 渲染支持（可选依赖 `mermaidx <https://pypi.org/project/mermaidx/>`_）。

mermaidx 在进程内用 QuickJS 运行**真实的 mermaid.js v11**（无浏览器 / 无 Node），
再用 resvg 光栅化为 PNG；本模块把它包装成 Qt 友好的异步渲染器：

- ``QThreadPool`` 后台渲染（CPU 密集，避免阻塞 UI 线程）；
- 结果经 ``rendered`` 信号回到 GUI 线程（跨线程 emit 自动排队）；
- ``(code, theme)`` 维度的 LRU 缓存 + in-flight 去重，流式重渲染不重复出图；
- 采用 mermaid ``base`` 主题 + :data:`MERMAID_THEME_VARIABLES` 内置美化配色
  （GitHub 风格，跟随查看器亮/暗主题），可用
  :meth:`ElaMermaidRenderer.set_theme_variables` 覆盖；
- 未安装 mermaidx 时 ``available()`` 为 ``False``，调用方回退为代码块；
- 支持 ``set_renderer(callable)`` 注入自定义渲染器（测试或替换后端）。

用法::

    renderer = ElaMermaidRenderer(parent)
    known, image = renderer.lookup(code, "dark")
    renderer.request(code, "dark", lambda img: ...)   # 结果回调（GUI 线程）
"""

from __future__ import annotations

import sys
from collections import OrderedDict
from typing import Callable, Optional

from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal
from PyQt5.QtGui import QImage

__all__ = [
    "ElaMermaidRenderer",
    "mermaidx_available",
    "mermaidx_error",
    "MERMAID_THEME_VARIABLES",
]

#: 渲染使用的 mermaid 基准主题（搭配 themeVariables 自定义配色）
_MERMAID_BASE_THEME = "base"
#: 内置美化主题变量（GitHub 风格；「light」/「dark」对应查看器主题）
MERMAID_THEME_VARIABLES = {
    "light": {
        "fontSize": "14px",
        "primaryColor": "#F6F8FA",
        "primaryBorderColor": "#C9D1D9",
        "primaryTextColor": "#1F2328",
        "secondaryColor": "#EEF2F7",
        "tertiaryColor": "#FFFFFF",
        "lineColor": "#57606A",
        "textColor": "#1F2328",
        "edgeLabelBackground": "#F8F8F8",
        "clusterBkg": "#FFFFFF",
        "clusterBorder": "#D0D7DE",
        "titleColor": "#1F2328",
        "noteBkgColor": "#FFF8C5",
        "noteTextColor": "#1F2328",
        "noteBorderColor": "#D4A72C",
        "actorBkg": "#F6F8FA",
        "actorBorder": "#C9D1D9",
        "actorTextColor": "#1F2328",
        "actorLineColor": "#C9D1D9",
        "signalColor": "#57606A",
        "signalTextColor": "#1F2328",
        "labelBoxBkgColor": "#F6F8FA",
        "labelBoxBorderColor": "#C9D1D9",
        "labelTextColor": "#1F2328",
        "loopTextColor": "#1F2328",
        "activationBorderColor": "#C9D1D9",
        "activationBkgColor": "#EEF2F7",
    },
    "dark": {
        "fontSize": "14px",
        "primaryColor": "#21262D",
        "primaryBorderColor": "#3D444D",
        "primaryTextColor": "#E6EDF3",
        "secondaryColor": "#30363D",
        "tertiaryColor": "#161B22",
        "lineColor": "#8B949E",
        "textColor": "#E6EDF3",
        "edgeLabelBackground": "#161B22",
        "clusterBkg": "#161B22",
        "clusterBorder": "#30363D",
        "titleColor": "#E6EDF3",
        "noteBkgColor": "#3B2E00",
        "noteTextColor": "#E6EDF3",
        "noteBorderColor": "#9E6A03",
        "actorBkg": "#21262D",
        "actorBorder": "#3D444D",
        "actorTextColor": "#E6EDF3",
        "actorLineColor": "#3D444D",
        "signalColor": "#8B949E",
        "signalTextColor": "#E6EDF3",
        "labelBoxBkgColor": "#21262D",
        "labelBoxBorderColor": "#3D444D",
        "labelTextColor": "#E6EDF3",
        "loopTextColor": "#E6EDF3",
        "activationBorderColor": "#3D444D",
        "activationBkgColor": "#30363D",
    },
}

#: 布局美化参数（曲线走向与间距）
_FLOWCHART_CONFIG = {
    "curve": "basis",
    "nodeSpacing": 40,
    "rankSpacing": 50,
    "padding": 10,
}
_SEQUENCE_CONFIG = {
    "mirrorActors": False,
    "actorMargin": 60,
    "messageMargin": 32,
    "boxMargin": 8,
}

#: 缓存条数上限
_CACHE_CAP = 32
#: 失败哨兵（缓存失败结果，避免流式重渲染反复触发）
_FAILED = object()

#: mermaidx 可用性探测缓存（进程级）
_AVAILABLE: Optional[bool] = None
#: mermaidx 导入失败原因（可用时为 None）
_AVAILABLE_ERROR: Optional[str] = None


def _build_config(theme: str, theme_variables: Optional[dict] = None) -> dict:
    """构造 mermaid 初始化配置（base 主题 + 自定义 themeVariables + 布局）。"""
    variables = dict(
        MERMAID_THEME_VARIABLES.get(theme, MERMAID_THEME_VARIABLES["light"])
    )
    if theme_variables:
        variables.update(theme_variables)
    return {
        "theme": _MERMAID_BASE_THEME,
        "themeVariables": variables,
        "flowchart": dict(_FLOWCHART_CONFIG),
        "sequence": dict(_SEQUENCE_CONFIG),
    }


def mermaidx_available() -> bool:
    """探测可选依赖 mermaidx 是否可用（结果缓存）。"""
    global _AVAILABLE, _AVAILABLE_ERROR
    if _AVAILABLE is None:
        try:
            import mermaidx  # noqa: F401
        except Exception as exc:
            _AVAILABLE = False
            _AVAILABLE_ERROR = f"{type(exc).__name__}: {exc}"
        else:
            _AVAILABLE = True
            _AVAILABLE_ERROR = None
    return _AVAILABLE


def mermaidx_error() -> Optional[str]:
    """mermaidx 不可用时的导入错误信息（可用时为 ``None``）。"""
    mermaidx_available()
    return _AVAILABLE_ERROR


def _render_with_mermaidx(
    code: str, theme: str, theme_variables: Optional[dict] = None
) -> Optional[QImage]:
    """用 mermaidx 渲染 Mermaid 源码为 QImage（2x 超采样）。

    采用 mermaid ``base`` 主题 + :data:`MERMAID_THEME_VARIABLES` 美化配色
    （可经 ``theme_variables`` 覆盖）；mermaidx 自带 PNG 管线会强制使用
    内置 DejaVu 字体（不含 CJK，中文变方块），因此优先取 SVG 后用
    ``resvg_py`` 光栅化（默认加载系统字体，可回退中文字体）；直调失败时
    退回 mermaidx 的 PNG 输出。两者都失败时抛出异常（由调用方记录到
    :meth:`ElaMermaidRenderer.last_error`，便于排查）。
    """
    import mermaidx

    diagram = mermaidx.render(
        code,
        theme=_MERMAID_BASE_THEME,
        config=_build_config(theme, theme_variables),
    )
    svg = diagram.svg()
    try:
        import resvg_py

        data = resvg_py.svg_to_bytes(
            svg_string=svg,
            zoom=2,
            sans_serif_family="Microsoft YaHei",
        )
    except Exception as exc:
        first_error = f"{type(exc).__name__}: {exc}"
        try:
            data = diagram.png(scale=2.0)
        except Exception:
            raise RuntimeError(
                f"Mermaid 渲染失败（resvg 直调与 mermaidx PNG 均不可用）：{first_error}"
            ) from exc
    image = QImage.fromData(bytes(data), "PNG")
    if image.isNull():
        raise RuntimeError("Mermaid 渲染输出无法解码为图片")
    return image


class _RenderTask(QRunnable):
    """后台渲染任务（在 QThreadPool 线程中执行）。"""

    def __init__(self, renderer: "ElaMermaidRenderer", code: str, theme: str):
        super().__init__()
        self._renderer = renderer
        self._code = code
        self._theme = theme

    def run(self) -> None:  # pragma: no cover - 线程内执行
        error = None
        image = None
        try:
            render = self._renderer._render_function()
            if render is not None:
                image = render(self._code, self._theme)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        self._renderer._notify(self._code, self._theme, image, error)


class ElaMermaidRenderer(QObject):
    """Mermaid 异步渲染器（可选依赖 mermaidx，支持自定义渲染函数）。

    :param cache_cap: 缓存条数上限（<=0 表示不缓存）
    :param parent: 父对象
    """

    #: 渲染完成（参数：源码、主题、``QImage`` 或 ``None`` 表示失败、失败原因）
    rendered = pyqtSignal(str, str, object, str)

    def __init__(
        self,
        cache_cap: int = _CACHE_CAP,
        theme_variables: Optional[dict] = None,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self._cache: "OrderedDict[tuple, object]" = OrderedDict()
        self._cache_cap = max(0, int(cache_cap))
        self._inflight: set = set()
        self._callbacks: dict = {}
        self._override: Optional[Callable] = None
        self._last_error: Optional[str] = None
        self._logged_errors: set = set()
        #: 每套主题的 mermaid themeVariables（默认内置美化配色，可覆盖）
        self._theme_variables = {
            name: dict(values) for name, values in MERMAID_THEME_VARIABLES.items()
        }
        if theme_variables:
            for name, values in theme_variables.items():
                self._theme_variables.setdefault(name, {}).update(values)
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(2)
        self.rendered.connect(self._on_rendered)

    # -- 主题 --------------------------------------------------------------

    def set_theme_variables(self, theme: str, variables: Optional[dict] = None) -> None:
        """覆盖指定主题的 mermaid ``themeVariables``（``None`` 恢复内置美化配色）。

        :param theme: 主题键（``"light"`` / ``"dark"``）
        :param variables: 变量字典（如 ``{"primaryColor": "#F6F8FA"}``）
        """
        if variables is None:
            self._theme_variables[theme] = dict(
                MERMAID_THEME_VARIABLES.get(theme, MERMAID_THEME_VARIABLES["light"])
            )
        else:
            self._theme_variables.setdefault(theme, {}).update(variables)
        self.clear_cache()

    def theme_variables(self, theme: str) -> dict:
        """获取指定主题当前生效的 themeVariables 副本。"""
        return dict(self._theme_variables.get(theme, {}))

    # -- 配置 --------------------------------------------------------------

    def set_renderer(self, renderer: Optional[Callable]) -> None:
        """设置自定义渲染函数 ``(code, theme) -> QImage | None``。

        :param renderer: 渲染函数；``None`` 表示使用内置 mermaidx 后端
        """
        self._override = renderer
        self.clear_cache()

    def renderer(self) -> Optional[Callable]:
        """获取自定义渲染函数（未设置返回 ``None``）。"""
        return self._override

    def available(self) -> bool:
        """当前是否有可用的渲染后端（不可用时可在 :meth:`last_error` 查看原因）。"""
        render = self._render_function()
        if render is None and self._last_error is None:
            self._last_error = (
                mermaidx_error() or "未安装可用的 Mermaid 渲染依赖（mermaidx）"
            )
        return render is not None

    def last_error(self) -> Optional[str]:
        """最近一次渲染失败原因（成功或尚未渲染时为 ``None``）。"""
        return self._last_error

    def _render_function(self) -> Optional[Callable]:
        if self._override is not None:
            return self._override
        if mermaidx_available():
            variables = self._theme_variables
            return lambda code, theme: _render_with_mermaidx(
                code, theme, variables.get(theme)
            )
        return None

    # -- 缓存 / 请求 --------------------------------------------------------

    def lookup(self, code: str, theme: str):
        """查询缓存。

        :returns: ``(known, image)``；``known=True, image=None`` 表示此前渲染失败
        """
        key = (code, theme)
        if key not in self._cache:
            return False, None
        value = self._cache[key]
        self._cache.move_to_end(key)
        return (True, None) if value is _FAILED else (True, value)

    def request(
        self, code: str, theme: str, callback: Optional[Callable] = None
    ) -> None:
        """请求渲染（命中缓存时同步回调；否则后台执行并去重）。"""
        key = (code, theme)
        known, image = self.lookup(code, theme)
        if known:
            if callback is not None:
                callback(image)
            return
        render = self._render_function()
        if render is None:
            if callback is not None:
                callback(None)
            return
        if callback is not None:
            self._callbacks.setdefault(key, []).append(callback)
        if key in self._inflight:
            return
        self._inflight.add(key)
        self._pool.start(_RenderTask(self, code, theme))

    def clear_cache(self) -> None:
        """清空渲染缓存与待回调。"""
        self._cache.clear()
        self._callbacks.clear()

    # -- 内部 --------------------------------------------------------------

    def _notify(
        self, code: str, theme: str, image, error: Optional[str] = None
    ) -> None:  # 工作线程
        self.rendered.emit(code, theme, image, error or "")

    def _on_rendered(
        self, code: str, theme: str, image, error: str = ""
    ) -> None:  # GUI 线程
        key = (code, theme)
        self._inflight.discard(key)
        self._last_error = error or None
        if error and error not in self._logged_errors:
            self._logged_errors.add(error)
            print(
                f"[ElaMermaidRenderer] Mermaid 渲染失败：{error}",
                file=sys.stderr,
                flush=True,
            )
        if self._cache_cap > 0:
            self._cache[key] = image if image is not None else _FAILED
            while len(self._cache) > self._cache_cap:
                self._cache.popitem(last=False)
        for callback in self._callbacks.pop(key, []):
            try:
                callback(image)
            except Exception:
                pass
