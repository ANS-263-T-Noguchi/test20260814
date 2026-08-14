"""端数処理の共通設定。"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_DOWN, ROUND_HALF_UP, ROUND_UP, Decimal
from enum import StrEnum


class RoundingMode(StrEnum):
    DOWN = "down"
    UP = "up"
    HALF_UP = "half_up"


_DECIMAL_ROUNDING_MODES = {
    RoundingMode.DOWN: ROUND_DOWN,
    RoundingMode.UP: ROUND_UP,
    RoundingMode.HALF_UP: ROUND_HALF_UP,
}


@dataclass(frozen=True, slots=True)
class RoundingPolicy:
    """保持する小数桁数と端数処理方式を表す設定。"""

    decimal_places: int = 0
    mode: RoundingMode = RoundingMode.HALF_UP

    def __post_init__(self) -> None:
        if isinstance(self.decimal_places, bool) or not isinstance(self.decimal_places, int):
            raise TypeError("小数桁数は整数で指定してください")
        if self.decimal_places < 0:
            raise ValueError("小数桁数は0以上で指定してください")
        if not isinstance(self.mode, RoundingMode):
            raise TypeError("丸め方式はRoundingModeで指定してください")

    def apply(self, value: Decimal) -> Decimal:
        """設定した桁数と方式でDecimalを丸めます。"""

        quantizer = Decimal(1).scaleb(-self.decimal_places)
        return value.quantize(quantizer, rounding=_DECIMAL_ROUNDING_MODES[self.mode])


DEFAULT_ROUNDING_POLICY = RoundingPolicy()
