"""金額を安全に扱うための値オブジェクト。"""

from __future__ import annotations

from dataclasses import InitVar, dataclass
from decimal import Decimal, InvalidOperation
from typing import Self

from estimate_management.common.money import Money
from estimate_management.common.rounding import DEFAULT_ROUNDING_POLICY, RoundingPolicy


@dataclass(frozen=True, slots=True)
class Discount:
    """値引き割合。

    整数で利用
    """

    amount: Decimal
    rounding_policy: InitVar[RoundingPolicy] = DEFAULT_ROUNDING_POLICY

    def __post_init__(self, rounding_policy: RoundingPolicy) -> None:
        try:
            value = Decimal(str(self.amount))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("値引率を数値で指定してください") from None

        if value != value.to_integral_value():
            raise ValueError("値引率は整数で指定してください")

        if not Decimal("0") <= value <= Decimal("100"):
            raise ValueError("値引率は0%以上100%以下で指定してください")

        normalized = rounding_policy.apply(value)
        object.__setattr__(self, "amount", normalized)

    @classmethod
    def discount(
        cls,
        amount: int | str | Decimal,
        rounding_policy: RoundingPolicy = DEFAULT_ROUNDING_POLICY,
    ) -> Self:
        """値引きを生成します。"""
        try:
            value = Decimal(str(amount))

        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("値引率を数値で指定してください") from None

        return cls(value, rounding_policy)

    def add(
        self,
        other: Discount,
        rounding_policy: RoundingPolicy = DEFAULT_ROUNDING_POLICY,
    ) -> Self:
        """同じ値引きを加算します。"""

        return type(self)(self.amount + other.amount, rounding_policy)

    def calculate_discount(
        self,
        amount: Money,
        rounding_policy: RoundingPolicy = DEFAULT_ROUNDING_POLICY,
    ) -> Money:
        """金額と値引率で値引きを計算します。"""

        discount_amount = amount.amount * self.amount / Decimal("100")
        return Money.yen(discount_amount, rounding_policy)
