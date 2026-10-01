"""charts 大数组的紧凑存储与零拷贝摄入口径。

用途：把调用方传入的**大数值数组**按引用持有为紧凑缓冲区，避免
``setOption`` 的 ``copy.deepcopy`` 与 ``updateOption`` 的合并路径对百万级
数组逐元素复制。实测代价（本机，100 万点 float list）：``deepcopy`` 一次
约 60~95 ms；数据每次更新都付这个成本时，无论渲染多快都不可能实时。

对外可见语义（必须与既有行为完全一致）：

- ``ElaNumericBuffer`` 是 ``collections.abc.Sequence``，``len()`` / 下标 /
  切片 / ``iter()`` 行为与 ``list`` 一致；``==`` 支持与普通 list 比较
  （绘图与测试都依赖数据可比较）。
- 元素一律为原生 Python ``float``，不使用 numpy 标量 —— 后者与 ``int``
  的 ``==`` 虽然成立，但 ``repr`` 与类型断言会露出差异。
- ``getOption()`` / ``SeriesRenderer.data()`` 对外仍返回 **list**，调用方
  观察不到缓冲区的存在（见 ``core`` 中对 ``unwrapData`` 的使用）。

摄入口径（``toBuffer``）：

- ``ndarray`` / 缓冲协议对象：**按引用持有**（真正零拷贝）；
- 普通 list：转 ``numpy.float64`` 连续数组（O(n) 一次性），且仅在元素数量
  达到 ``_BUFFER_MIN_LEN`` 时才包装 —— 小数组直接深拷贝更省事，也不必为
  演示页的十来点数据平白增加包装对象。

**含 None 的间隙数据**：list 里的 ``None`` 在转数组时写成 ``NaN``，与既有
``LineSeriesRenderer._y_at`` 的 ``math.isfinite`` 判空口径一致，断点语义不变。

依赖说明：numpy / tsdownsample 是本模块的可选依赖（见 ``charts._downsample``），
未安装时全部降级为 ``array('d')`` 承载，语义一致。
"""

from __future__ import annotations

from array import array as _array
from collections.abc import Sequence

from . import _downsample as _ds

__all__ = [
    "numpyAvailable",
    "ElaNumericBuffer",
    "toBuffer",
    "unwrapData",
    "normalizeOptionData",
    "isBufferLike",
]

#: 小于该长度的数据不做缓冲包装（小数组直接深拷贝更省事）。
_BUFFER_MIN_LEN = 256

_np = _ds.np


def numpyAvailable() -> bool:
    """当前环境是否可用 numpy（向量化采样与范围统计的加速前提）。"""
    return _np is not None


def isBufferLike(obj) -> bool:
    """是否为可按引用持有的紧凑存储（``ElaNumericBuffer`` / ndarray / array）。

    供上游判断「这个值能否直接当数值序列用」。合并逻辑曾只认
    ``list`` / ``tuple``，于是 numpy 数组既不匹配 list 分支、也不是缓冲区，
    落到兜底的「数据缺失」分支之后被当作空数据 —— 表现为
    **入图后曲线一个点都不画**。

    注意 ``list`` / ``tuple`` **不算**：它们仍需一次 O(n) 转换，那由
    ``toBuffer`` 负责，不属于「已经可以按引用拿着」。
    """
    if isinstance(obj, ElaNumericBuffer):
        return True
    if _np is not None and isinstance(obj, _np.ndarray):
        return True
    if isinstance(obj, _array):
        return True
    return hasattr(obj, "__array_interface__")


class ElaNumericBuffer(Sequence):
    """大数值数组的紧凑容器（numpy ndarray 或 ``array('d')`` 承载）。

    **只读语义**：不提供原地修改接口，避免调用方与图表共享可变状态时出现
    难以排查的错位。切片返回 ``list``（与 list 切片语义一致），大范围切片
    请直接用 ``toList()``。
    """

    __slots__ = ("_buf",)

    def __init__(self, buf) -> None:
        self._buf = buf

    # -- Sequence 协议 ---------------------------------------------------
    def __len__(self) -> int:
        return int(len(self._buf))

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self.toList()[index]
        return float(self._buf[index])

    def __iter__(self):
        if _np is not None and isinstance(self._buf, _np.ndarray):
            # tolist() 在 C 层完成 float64 -> Python float 转换，比逐个
            # 下标取值快一个数量级；大数组的迭代是热路径。
            return iter(self._buf.tolist())
        return (float(v) for v in self._buf)

    def __array__(self, dtype=None, copy=None):
        """支持 ``numpy.asarray(buffer)``（numpy 2 会传 ``copy`` 关键字）。"""
        arr = self._buf if _np is not None else _np.frombuffer(self._buf, dtype=float)
        if dtype is not None:
            return arr.astype(dtype, copy=False)
        return arr

    def __repr__(self) -> str:
        return f"ElaNumericBuffer(len={len(self)})"

    # -- 与 list 的可比较性（绘图与测试都直接比较数据） -------------------
    def __eq__(self, other) -> bool:
        if isinstance(other, ElaNumericBuffer):
            other = other.toList()
        if isinstance(other, (list, tuple)):
            if len(other) != len(self):
                return False
            return self.toList() == list(other)
        return NotImplemented

    def __ne__(self, other) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    __hash__ = None  # 可比较但不可哈希（与 list 一致）

    # -- 显式转换 --------------------------------------------------------
    def toList(self) -> list:
        """转为原生 Python float 列表（对外 API 的兼容出口）。"""
        if _np is not None and isinstance(self._buf, _np.ndarray):
            return self._buf.tolist()
        return [float(v) for v in self._buf]

    @property
    def raw(self):
        """底层数组（**只读**使用，供 numpy 向量化路径直接取用）。"""
        return self._buf


def toBuffer(data, minLen: int = _BUFFER_MIN_LEN):
    """把数值序列转为 ``ElaNumericBuffer``；不值得包装时返回 ``None``。

    返回 ``None`` 表示调用方应继续走原有的深拷贝路径（小数组、非数值序列、
    字典项 / ``[x, y]`` 对列表等结构型数据）。判断只看**长度与数值性**，
    不猜测语义。

    仅当序列中每个元素都是 ``int`` / ``float``（非 ``bool``）或 ``None``
    时才包装 —— 含 dict（如 pie 的 ``{"name","value"}``）或含嵌套列表（如
    candlestick 的 ``[o,c,l,h]``、``[x, y]`` 点对）的数据保持原样，交由既有
    渲染路径处理。
    """
    if data is None or isinstance(data, ElaNumericBuffer):
        return None
    if isBufferLike(data):
        try:
            n = len(data)
        except TypeError:
            return None
        return ElaNumericBuffer(data) if n >= minLen else None
    if not isinstance(data, (list, tuple)):
        return None
    n = len(data)
    if n < minLen:
        return None
    # 抽样判别元素类型：只抽样即可，全量扫描会白白增加 O(n) Python 开销。
    # 抽样必须覆盖尾部（见下），否则「前段数值 + 后段结构」的混合数据会被
    # 误判为纯数值，包装后在 asarray 处抛异常。
    step = max(1, n // 64)
    probes = set(range(0, n, step))
    probes.update(range(min(24, n)))
    probes.update(range(max(0, n - 24), n))
    for i in probes:
        v = data[i]
        if v is None:
            continue
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return None
    try:
        if _np is not None:
            buf = _np.asarray(data, dtype=_np.float64)
        else:
            buf = _array(
                "d", [float(v) if v is not None else float("nan") for v in data]
            )
    except (TypeError, ValueError):
        return None
    return ElaNumericBuffer(buf)


def unwrapData(value):
    """把紧凑存储还原为 list；非紧凑存储原样返回（供 ``getOption`` 输出用）。"""
    if isinstance(value, ElaNumericBuffer):
        return value.toList()
    return value


def normalizeOptionData(option: dict, minLen: int = _BUFFER_MIN_LEN) -> dict:
    """就地包装 option 中的大数值数组为紧凑存储，返回同一 dict。

    处理位置：``series`` 列表中每一项的 ``data``。其余顶层键（``xAxis.data``
    等）由各模块按 list 语义直接读取，包装会破坏其语义，故**不处理**。
    """
    if not isinstance(option, dict):
        return option
    series = option.get("series")
    if not isinstance(series, list):
        return option
    for s in series:
        if not isinstance(s, dict):
            continue
        buf = toBuffer(s.get("data"), minLen)
        if buf is not None:
            s["data"] = buf
    return option
