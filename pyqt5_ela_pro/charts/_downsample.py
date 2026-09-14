"""
charts 折线降采样适配层（tsdownsample，可选依赖）。

- ``available()``：tsdownsample / numpy 是否可用；
- ``is_sorted(x)``：x 是否单调不减（tsdownsample 算法要求有序 x，
  非单调时返回空结果，调用方须退化为不采样）；
- ``downsample_indices(x, y, n_out, algorithm)``：按算法返回采样点下标
  （uint64 ndarray），失败 / 不可用返回 None。

算法名对齐 tsdownsample：minmax / m4 / lttb / minmaxLTTB。
未安装 tsdownsample 时本模块全部降级（渲染走原始全量路径，不崩溃）。
"""

from __future__ import annotations

try:
    import numpy as np

    from tsdownsample import (
        LTTBDownsampler,
        M4Downsampler,
        MinMaxDownsampler,
        MinMaxLTTBDownsampler,
    )

    _ALGORITHMS = {
        "minmax": MinMaxDownsampler,
        "m4": M4Downsampler,
        "lttb": LTTBDownsampler,
        "minmaxLTTB": MinMaxLTTBDownsampler,
    }
    _AVAILABLE = True
except ImportError:  # 可选依赖：未安装时降级
    np = None
    LTTBDownsampler = M4Downsampler = MinMaxDownsampler = MinMaxLTTBDownsampler = None
    _ALGORITHMS = {}
    _AVAILABLE = False

__all__ = ["available", "is_sorted", "downsample_indices", "ALGORITHMS", "np"]

ALGORITHMS = _ALGORITHMS


def available() -> bool:
    """tsdownsample 与 numpy 是否可用。"""
    return _AVAILABLE


def is_sorted(x) -> bool:
    """x（np 数组）是否单调不减（NaN 视为非法，返回 False）。"""
    if not _AVAILABLE:
        return False
    if x.size < 2:
        return True
    if not np.all(np.isfinite(x)):
        return False
    return bool(np.all(np.diff(x) >= 0))


def downsample_indices(
    x, y, n_out: int, algorithm: str = "minmax", parallel: bool = False
):
    """按算法对 (x, y) 降采样，返回采样点下标 ndarray；失败返回 None。

    要求 x 单调不减（非单调由调用方先 ``is_sorted`` 判定，此处不兜底）；
    n_out 小于数据量时直接返回全量下标（np.arange）。
    """
    if not _AVAILABLE or x is None or y is None:
        return None
    n = len(x)
    if n == 0:
        return None
    n_out = max(2, int(n_out))
    if n_out >= n:
        return np.arange(n, dtype=np.uint64)
    cls = _ALGORITHMS.get(str(algorithm))
    if cls is None:
        return None
    try:
        return cls().downsample(x, y, n_out=n_out, parallel=parallel)
    except Exception:
        return None
