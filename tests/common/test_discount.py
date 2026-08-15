from decimal import Decimal

import pytest

from estimate_management.common import Discount, Money


def test_calculates_discount_amount() -> None:
    discount = Discount.discount(20)

    assert discount.calculate_discount(Money.yen(1_000)) == Money.yen(200)


@pytest.mark.parametrize("rate", [0, 100])
def test_accepts_discount_rate_boundaries(rate: int) -> None:
    assert Discount.discount(rate).amount == Decimal(rate)


@pytest.mark.parametrize(
    "rate",
    [
        pytest.param(-1, id="below-minimum"),
        pytest.param(101, id="above-maximum"),
        pytest.param("20.5", id="not-integer"),
        pytest.param(None, id="none"),
        pytest.param("", id="empty"),
    ],
)
def test_rejects_invalid_discount_rate(rate: object) -> None:
    with pytest.raises(ValueError):
        Discount.discount(rate)


def test_direct_creation_also_rejects_fractional_rate() -> None:
    with pytest.raises(ValueError, match="整数"):
        Discount(Decimal("20.5"))
