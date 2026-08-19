"""Customer code and important-customer rules."""

from __future__ import annotations

from dataclasses import dataclass

_IMPORTANT_CUSTOMER_CODES = frozenset({"00000000000000000001"})


@dataclass(frozen=True, slots=True)
class CustomerCode:
    """A customer code represented by exactly 20 characters."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            object.__setattr__(self, "value", str(self.value))
        if len(self.value) != 20:
            raise ValueError("customer code must contain exactly 20 characters")


def is_important_customer(customer_code: CustomerCode) -> bool:
    """Return whether the supplied code belongs to an important customer."""

    return customer_code.value in _IMPORTANT_CUSTOMER_CODES
