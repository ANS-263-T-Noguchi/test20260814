import logging
from decimal import InvalidOperation
from pathlib import Path

import pytest

from estimate_management.common import (
    Discount,
    Money,
    QualityCheckResult,
    load_estimate_rules,
    requires_quality_test,
)


@pytest.mark.parametrize(
    ("amount", "discount_rate", "important_customer", "expected"),
    [
        pytest.param(999_999, 19, True, True, id="TC-01-important-both-below"),
        pytest.param(999_999, 20, True, True, id="TC-02-important-discount-at-threshold"),
        pytest.param(999_999, 21, True, True, id="TC-03-important-discount-above"),
        pytest.param(999_999, None, True, True, id="TC-04-important-discount-unset"),
        pytest.param(1_000_000, 19, True, True, id="TC-05-important-amount-at-threshold"),
        pytest.param(1_000_000, 20, True, True, id="TC-06-important-both-at-threshold"),
        pytest.param(1_000_000, 21, True, True, id="TC-07-important-discount-above-at-amount"),
        pytest.param(1_000_000, None, True, True, id="TC-08-important-unset-at-amount"),
        pytest.param(1_000_001, 19, True, True, id="TC-09-important-amount-above"),
        pytest.param(1_000_001, 20, True, True, id="TC-10-important-amount-above-discount-at"),
        pytest.param(1_000_001, 21, True, True, id="TC-11-important-both-above"),
        pytest.param(1_000_001, None, True, True, id="TC-12-important-unset-above-amount"),
        pytest.param(999_999, 19, False, False, id="TC-13-regular-both-below"),
        pytest.param(999_999, 20, False, False, id="TC-14-regular-discount-at-threshold"),
        pytest.param(999_999, 21, False, True, id="TC-15-regular-discount-above"),
        pytest.param(999_999, None, False, False, id="TC-16-regular-discount-unset"),
        pytest.param(1_000_000, 19, False, True, id="TC-17-regular-amount-at-threshold"),
        pytest.param(1_000_000, 20, False, True, id="TC-18-regular-both-at-threshold"),
        pytest.param(1_000_000, 21, False, True, id="TC-19-regular-discount-above-at-amount"),
        pytest.param(1_000_000, None, False, True, id="TC-20-regular-unset-at-amount"),
        pytest.param(1_000_001, 19, False, True, id="TC-21-regular-amount-above"),
        pytest.param(1_000_001, 20, False, True, id="TC-22-regular-amount-above-discount-at"),
        pytest.param(1_000_001, 21, False, True, id="TC-23-regular-both-above"),
        pytest.param(1_000_001, None, False, True, id="TC-24-regular-unset-above-amount"),
    ],
)
def test_judges_quality_test_from_amount_and_discount(
    amount: int,
    discount_rate: int | None,
    important_customer: bool,
    expected: bool,
    caplog: pytest.LogCaptureFixture,
) -> None:
    discount = None if discount_rate is None else Discount.discount(discount_rate)

    with caplog.at_level(logging.WARNING, logger="estimate_management.common.estimate_rules"):
        result = requires_quality_test(
            Money.yen(amount),
            discount=discount,
            important_customer=important_customer,
        )

    assert isinstance(result, QualityCheckResult)
    assert result.required is expected
    if discount_rate is None:
        assert len(result.warnings) == 1
        assert "値引率が未設定です" in result.warnings[0]
        assert f"estimate_amount={amount}" in result.warnings[0]
        assert f"requires_quality_test={expected}" in result.warnings[0]
        assert "値引率が未設定です" in caplog.text
        assert f"estimate_amount={amount}" in caplog.text
        assert f"requires_quality_test={expected}" in caplog.text
    else:
        assert result.warnings == ()
        assert "値引率が未設定です" not in caplog.text


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
        ).required
        is False
    )

    assert (
        requires_quality_test(
            Money.yen(500_000),
            discount=Discount.discount(0),
            config_path=config_path,
        ).required
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
        ).required
        is False
    )


@pytest.mark.parametrize(
    ("discount_rate", "expected"),
    [
        pytest.param(29, False, id="below-configured-discount-threshold"),
        pytest.param(30, False, id="at-configured-discount-threshold"),
        pytest.param(31, True, id="above-configured-discount-threshold"),
    ],
)
def test_uses_discount_threshold_from_config_file(
    tmp_path: Path,
    discount_rate: int,
    expected: bool,
) -> None:
    config_path = tmp_path / "estimate_rules.toml"
    config_path.write_text(
        "[quality_test]\nminimum_amount = 1000000\nminimum_discount = 30\n",
        encoding="utf-8",
    )

    result = requires_quality_test(
        Money.yen(999_999),
        discount=Discount.discount(discount_rate),
        config_path=config_path,
    )

    assert result.required is expected
    assert result.warnings == ()


def test_does_not_require_quality_test_when_minimum_amount_is_unset(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    config_path = tmp_path / "estimate_rules.toml"
    config_path.write_text(
        "[quality_test]\nminimum_discount = 20\n",
        encoding="utf-8",
    )

    with caplog.at_level(logging.WARNING, logger="estimate_management.common.estimate_rules"):
        result = requires_quality_test(
            Money.yen(1_000_001),
            discount=Discount.discount(21),
            config_path=config_path,
        )

    assert result.required is False
    assert result.warnings == ("quality_test.minimum_amountが未設定のため品管テスト対象外です",)
    assert "quality_test.minimum_amountが未設定のため品管テスト対象外です" in caplog.text


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
