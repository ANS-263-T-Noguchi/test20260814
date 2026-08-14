"""金額を安全に扱うための値オブジェクト。"""

from __future__ import annotations

from dataclasses import InitVar, dataclass
from decimal import Decimal
from typing import Self

from estimate_management.common.rounding import DEFAULT_ROUNDING_POLICY, RoundingPolicy


@dataclass(frozen=True, slots=True)
class Money:
    """円建ての金額。

    浮動小数点数による丸め誤差を避けるため、内部ではDecimalを利用します。
    端数処理の設定は金額そのものには保持せず、生成・計算時に適用します。
    """

    amount: Decimal
    rounding_policy: InitVar[RoundingPolicy] = DEFAULT_ROUNDING_POLICY

    def __post_init__(self, rounding_policy: RoundingPolicy) -> None:
        normalized = rounding_policy.apply(Decimal(str(self.amount)))
        if normalized < 0:
            raise ValueError("金額は0円以上で指定してください")
        object.__setattr__(self, "amount", normalized)

    @classmethod
    def yen(
        cls,
        amount: int | str | Decimal,
        rounding_policy: RoundingPolicy = DEFAULT_ROUNDING_POLICY,
    ) -> Self:
        """円の金額を生成します。"""

        return cls(Decimal(str(amount)), rounding_policy)

    def add(
        self,
        other: Money,
        rounding_policy: RoundingPolicy = DEFAULT_ROUNDING_POLICY,
    ) -> Self:
        """同じ通貨の金額を加算します。"""

        return type(self)(self.amount + other.amount, rounding_policy)

    def calculate_tax(
        self,
        rate: Decimal = Decimal("0.10"),
        rounding_policy: RoundingPolicy = DEFAULT_ROUNDING_POLICY,
    ) -> Self:
        """指定税率と端数処理設定で消費税額を計算します。"""

        if rate < 0:
            raise ValueError("税率は0以上で指定してください")
        return type(self)(self.amount * rate, rounding_policy)
