"""
模型定价与花费换算（``pyqt5_ela_pro.chat`` 内部模块）。

**为什么定价不烤进库里**：模型价格会变，还分「上下文长度阶梯」（超过 200k
后单 token 变贵），任何写死的表过期后只会给出**看起来对但错的金额** ——
比没有金额更糟。所以这里只提供**换算规则**（纯函数，可单测），价格表由宿主
持有并随时传入。

两条并行的用法：

.. code-block:: python

    # 用法 A：库内换算（宿主喂定价表）
    from pyqt5_ela_pro.chat import ModelPricing, stats_cost
    price = ModelPricing(input_per_m=3.0, output_per_m=15.0,
                         cache_read_per_m=0.3, tiers=(
                             # 超过 200k 词元的部分按贵价计
                             (200_000, ModelPricing(input_per_m=6.0,
                                                    output_per_m=22.5)),
                         ))
    usd = stats_cost(binder_last_stats, price)

    # 用法 B：宿主自己算，只把结果塞进来（库不参与计算）
    binder.stats(replace(stats, cost_usd=my_own_estimate))

阶梯语义对齐 opencode ``packages/core/src/session/usage.ts:calculateCost``：

- ``output`` 与 ``reasoning`` **同价**计费；
- 阶梯按「输入侧总量」（``prompt + cache_read + cache_write``）选择，
  取**最大的满足档**（超过 200k 就用 200k 那一档的价，而不是基础档）；
- 价格是**每百万词元**，最后统一除以 1_000_000；
- 空定价表 / 缺字段一律按 0 计（不抛异常 —— 缺价格不该让聊天界面崩）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

__all__ = [
    "ModelPricing",
    "formatCost",
    "selectPricing",
    "stats_cost",
]


def _finite(value, default: float = 0.0) -> float:
    """容错取有限浮点数（NaN / inf / 非法值一律归 ``default``）。"""
    if value is None or isinstance(value, bool):
        return default
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    if out != out or out in (float("inf"), float("-inf")):
        return default
    return max(0.0, out)


@dataclass(frozen=True)
class ModelPricing:
    """单个模型的每百万词元价格（美元）。

    缺省项按 0 计 —— 多数模型不单独收「缓存写」费用，缺失比报错合理。
    """

    #: 输入（未命中缓存）
    input_per_m: float = 0.0
    #: 输出（**含 reasoning**，两者同价）
    output_per_m: float = 0.0
    #: 缓存读命中
    cache_read_per_m: float = 0.0
    #: 缓存写
    cache_write_per_m: float = 0.0
    #: 上下文长度阶梯 ``((阈值词元数, 该档价格), ...)``，按阈值升序
    tiers: Tuple[Tuple[int, "ModelPricing"], ...] = field(default_factory=tuple)

    def isFree(self) -> bool:
        """是否全零（无定价 / 本地模型）。"""
        return not (
            self.input_per_m
            or self.output_per_m
            or self.cache_read_per_m
            or self.cache_write_per_m
        )


def _normalize_tiers(tiers) -> tuple:
    """容错整理阶梯：丢弃非法项并按阈值升序排列。"""
    items = []
    try:
        source = tiers or ()
    except TypeError:
        return ()
    for item in source:
        if not isinstance(item, (tuple, list)) or len(item) < 2:
            continue
        threshold, price = item[0], item[1]
        if not isinstance(price, ModelPricing):
            continue
        try:
            threshold = int(threshold)
        except (TypeError, ValueError):
            continue
        if threshold > 0:
            items.append((threshold, price))
    items.sort(key=lambda pair: pair[0])
    return tuple(items)


def selectPricing(
    promptTokens: int, pricing: Optional[ModelPricing]
) -> Optional[ModelPricing]:
    """按输入侧总量选定价档（取**最大的满足档**）。

    ``tiers`` 自身不再参与选档（避免递归），只用它的最外层阈值 —— 阶梯内
    继续套阶梯没有实际意义，opencode 也是同样处理。

    :param promptTokens: 输入侧总量（已含缓存读写）
    :param pricing: 基础定价；``None`` / 全零返回 ``None``
    """
    if pricing is None:
        return None
    try:
        used = int(promptTokens)
    except (TypeError, ValueError):
        used = 0
    if used < 0:
        used = 0
    selected = pricing
    for threshold, price in _normalize_tiers(pricing.tiers):
        if used > threshold:
            selected = price
        else:
            break
    return None if selected.isFree() else selected


def stats_cost(stats, pricing: Optional[ModelPricing] = None) -> float:
    """把 :class:`~pyqt5_ela_pro.chat.message.ElaChatStats` 换算成美元花费。

    计费口径（对齐 opencode）：

    - 输入侧总量 ``prompt + cached`` 决定**阶梯档位**（``cached`` 含缓存读写，
      两者都按输入侧算）；
    - 实际计费按四路分别乘单价：``prompt × input`` +
      ``completion × output``（**已含 reasoning**，上游 provider 的 usage 里
      reasoning 通常是 completion 的子集，不重复加）+ 缓存读写各自单价；
    - 统一除以 1_000_000。

    ``ElaChatStats`` 本身**不区分**缓存读写（只有一个 ``cached_tokens``），
    因此这里把 ``cached_tokens`` 全部按**缓存读**计价 —— 与
    :attr:`ElaChatStats.cached_tokens` 的语义（缓存**命中**）一致。宿主若有
    更细的拆分，请走 :func:`cost_from_parts` 或自己填 ``cost_usd``。

    :param stats: 用量快照；``None`` 返回 0.0
    :param pricing: 定价；``None`` 返回 0.0
    """
    if stats is None or pricing is None:
        return 0.0
    prompt = _finite(getattr(stats, "prompt_tokens", 0))
    completion = _finite(getattr(stats, "completion_tokens", 0))
    cached = _finite(getattr(stats, "cached_tokens", 0))
    return cost_from_parts(
        prompt,
        completion,
        cacheRead=cached,
        pricing=pricing,
    )


def cost_from_parts(
    promptTokens,
    completionTokens,
    cacheRead=0,
    cacheWrite=0,
    pricing: Optional[ModelPricing] = None,
) -> float:
    """按四路词元明细换算花费（``stats_cost`` 的低层入口）。

    需要区分缓存读 / 写、或需要额外传入 reasoning 的宿主直接用这个。
    ``reasoning`` 不单独计价（已含在 ``completionTokens`` 里，与 opencode 的
    ``output + reasoning`` 同价口径一致）。
    """
    if pricing is None:
        return 0.0
    prompt = _finite(promptTokens)
    completion = _finite(completionTokens)
    cacheRead = _finite(cacheRead)
    cacheWrite = _finite(cacheWrite)
    tier = selectPricing(prompt + cacheRead + cacheWrite, pricing)
    if tier is None:
        return 0.0
    total = (
        prompt * _finite(tier.input_per_m)
        + completion * _finite(tier.output_per_m)
        + cacheRead * _finite(tier.cache_read_per_m)
        + cacheWrite * _finite(tier.cache_write_per_m)
    )
    return total / 1_000_000.0


def formatCost(usd) -> str:
    """美元金额格式化（自适应精度）。

    - ``$0.0142`` —— 1 美元以下给 4 位小数（便宜模型一轮也就几分钱，
      两位小数会全显示成 ``$0.01``，看着像 bug）；
    - ``$1.23`` / ``$12.40`` —— 常规两位小数（补零，避免 ``$12.4`` 像笔误）；
    - ``$1234`` —— 破千不写分隔符（tooltip 空间有限）。

    非法值（``None`` / NaN / 负数）一律回 ``"$0.00"``。
    """
    value = _finite(usd)
    if value <= 0:
        return "$0.00"
    if value < 1:
        return f"${value:.4f}"
    if value < 1000:
        return f"${value:.2f}"
    return f"${value:.0f}"
