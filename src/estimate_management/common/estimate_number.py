"""見積番号を扱うための値オブジェクト。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Self

_ESTIMATE_NUMBER_PATTERN = re.compile(r"^EST-\d{8}-\d{4}$")


@dataclass(frozen=True, slots=True)
class EstimateNumber:
    """`EST-YYYYMMDD-NNNN`形式の見積番号。"""

    value: str

    def __post_init__(self) -> None:
        if not _ESTIMATE_NUMBER_PATTERN.fullmatch(self.value):
            raise ValueError("見積番号はEST-YYYYMMDD-NNNN形式で指定してください")

    @classmethod
    def issue(cls, issued_on: date, sequence: int) -> Self:
        """発行日と日次連番から見積番号を生成します。"""

        if not 1 <= sequence <= 9999:
            raise ValueError("連番は1から9999の範囲で指定してください")
        return cls(f"EST-{issued_on:%Y%m%d}-{sequence:04d}")

