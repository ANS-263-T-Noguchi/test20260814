from decimal import Decimal

import pytest

from estimate_management.common import Money, RoundingMode, RoundingPolicy


def test_adds_money() -> None:
    assert Money.yen(1_000).add(Money.yen(500)) == Money.yen(1_500)


def test_rounds_fractional_yen_half_up() -> None:
    assert Money.yen("100.5") == Money.yen(101)


def test_calculates_tax() -> None:
    assert Money.yen(1_005).calculate_tax(Decimal("0.10")) == Money.yen(101)


def test_rejects_negative_amount() -> None:
    with pytest.raises(ValueError, match="0円以上"):
        Money.yen(-1)


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        (RoundingMode.DOWN, "123.45"),
        (RoundingMode.UP, "123.46"),
        (RoundingMode.HALF_UP, "123.46"),
    ],
)
def test_applies_selected_rounding_mode(mode: RoundingMode, expected: str) -> None:
    policy = RoundingPolicy(decimal_places=2, mode=mode)

    assert Money.yen("123.456", policy).amount == Decimal(expected)


def test_keeps_selected_number_of_decimal_places() -> None:
    policy = RoundingPolicy(decimal_places=3)

    assert Money.yen("10.5", policy).amount == Decimal("10.500")


def test_applies_rounding_policy_to_tax_calculation() -> None:
    two_decimal_places = RoundingPolicy(decimal_places=2, mode=RoundingMode.DOWN)
    amount = Money.yen("100.55", two_decimal_places)

    assert amount.calculate_tax(Decimal("0.10"), two_decimal_places).amount == Decimal("10.05")


def test_rejects_negative_decimal_places() -> None:
    with pytest.raises(ValueError, match="0以上"):
        RoundingPolicy(decimal_places=-1)
