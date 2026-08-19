"""Customer code and important-customer rules."""

from __future__ import annotations

import re
from dataclasses import dataclass

_CUSTOMER_CODE_PATTERN = re.compile(r"^[0-9]{20}$")
_IMPORTANT_CUSTOMER_CODES = frozenset({"00000000000000000001"})


@dataclass(frozen=True, slots=True)
class CustomerCode:
    """A customer code represented by exactly 20 decimal digits."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("customer code must be a string")
        if not _CUSTOMER_CODE_PATTERN.fullmatch(self.value):
            raise ValueError("customer code must contain exactly 20 digits")


def is_important_customer(customer_code: CustomerCode) -> bool:
    """Return whether the supplied code belongs to an important customer."""

    return customer_code.value in _IMPORTANT_CUSTOMER_CODES
