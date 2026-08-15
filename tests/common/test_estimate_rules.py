from decimal import InvalidOperation
from pathlib import Path

import pytest

from estimate_management.common import (
    Discount,
    Money,
    load_estimate_rules,
    requires_quality_test,
)


@pytest.mark.parametrize(
    ("amount", "discount_rate", "expected"),
    [
        pytest.param(999_999, 19, False, id="below-amount_below-discount"),
        pytest.param(999_999, 20, True, id="below-amount_at-discount"),
        pytest.param(999_999, 21, True, id="below-amount_above-discount"),
        pytest.param(999_999, None, None, id="below-amount_unset-discount"),
        pytest.param(1_000_000, 19, True, id="at-amount_below-discount"),
        pytest.param(1_000_000, 20, True, id="at-amount_at-discount"),
        pytest.param(1_000_000, 21, True, id="at-amount_above-discount"),
        pytest.param(1_000_000, None, True, id="at-amount_unset-discount"),
        pytest.param(1_000_001, 19, True, id="above-amount_below-discount"),
        pytest.param(1_000_001, 20, True, id="above-amount_at-discount"),
        pytest.param(1_000_001, 21, True, id="above-amount_above-discount"),
        pytest.param(1_000_001, None, True, id="above-amount_unset-discount"),
    ],
)
def test_judges_quality_test_from_amount_and_discount(
    amount: int,
    discount_rate: int | None,
    expected: bool | None,
) -> None:
    discount = None if discount_rate is None else Discount.discount(discount_rate)

    if expected is None:
        with pytest.raises(ValueError, match="値引率が未設定"):
            requires_quality_test(Money.yen(amount), discount=discount)
        return

    assert requires_quality_test(Money.yen(amount), discount=discount) is expected


def test_uses_threshold_from_config_file(tmp_path: Path) -> None:
    config_path = tmp_path / "estimate_rules.toml"
    config_path.write_text(
        "[quality_test]\nminimum_amount = 500000\nminimum_discount = 20\n",
        encoding="utf-8",
    )

    assert (
        requires_quality_test(
            Money.yen(499_999),
            discount=Discount.discount(0),
            config_path=config_path,
        )
        is False
    )

    assert (
        requires_quality_test(
            Money.yen(500_000), discount=Discount.discount(0), config_path=config_path
        )
        is True
    )


def test_can_reuse_loaded_rules(tmp_path: Path) -> None:
    config_path = tmp_path / "estimate_rules.toml"
    config_path.write_text(
        "[quality_test]\nminimum_amount = 2000000\nminimum_discount = 20\n",
        encoding="utf-8",
    )
    rules = load_estimate_rules(config_path)

    assert (
        requires_quality_test(
            Money.yen(1_500_000),
            rules,
            discount=Discount.discount(0),
        )
        is False
    )


def test_uses_discount_threshold_from_config_file(tmp_path: Path) -> None:
    config_path = tmp_path / "estimate_rules.toml"
    config_path.write_text(
        "[quality_test]\nminimum_amount = 1000000\nminimum_discount = 30\n",
        encoding="utf-8",
    )

    assert (
        requires_quality_test(
            Money.yen(999_999),
            discount=Discount.discount(29),
            config_path=config_path,
        )
        is False
    )
    assert (
        requires_quality_test(
            Money.yen(999_999),
            discount=Discount.discount(30),
            config_path=config_path,
        )
        is True
    )


def test_rejects_config_without_quality_test_threshold(tmp_path: Path) -> None:
    config_path = tmp_path / "estimate_rules.toml"
    config_path.write_text("[quality_test]\n", encoding="utf-8")

    with pytest.raises(ValueError, match="quality_test.minimum_amount"):
        load_estimate_rules(config_path)


def test_rejects_config_without_discount_threshold(tmp_path: Path) -> None:
    config_path = tmp_path / "estimate_rules.toml"
    config_path.write_text(
        "[quality_test]\nminimum_amount = 1000000\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="quality_test.minimum_discount"):
        load_estimate_rules(config_path)


@pytest.mark.parametrize("amount", [None, ""])
def test_rejects_unset_estimate_amount(amount: object) -> None:
    with pytest.raises((TypeError, ValueError, InvalidOperation)):
        Money.yen(amount)


@pytest.mark.parametrize("discount", [None, ""])
def test_rejects_unset_discount(discount: object) -> None:
    with pytest.raises((TypeError, ValueError, InvalidOperation)):
        Discount.discount(discount)
