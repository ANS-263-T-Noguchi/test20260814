from pathlib import Path

import pytest

from estimate_management.common import (
    Money,
    load_estimate_rules,
    requires_quality_test,
)


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (999_999, False),
        (1_000_000, True),
        (1_000_001, True),
    ],
)
def test_judges_quality_test_with_default_threshold(amount: int, expected: bool) -> None:
    assert requires_quality_test(Money.yen(amount)) is expected


def test_uses_threshold_from_config_file(tmp_path: Path) -> None:
    config_path = tmp_path / "estimate_rules.toml"
    config_path.write_text(
        "[quality_test]\nminimum_amount = 500000\n",
        encoding="utf-8",
    )

    assert requires_quality_test(Money.yen(499_999), config_path=config_path) is False
    assert requires_quality_test(Money.yen(500_000), config_path=config_path) is True


def test_can_reuse_loaded_rules(tmp_path: Path) -> None:
    config_path = tmp_path / "estimate_rules.toml"
    config_path.write_text(
        "[quality_test]\nminimum_amount = 2000000\n",
        encoding="utf-8",
    )
    rules = load_estimate_rules(config_path)

    assert requires_quality_test(Money.yen(1_500_000), rules) is False


def test_rejects_config_without_quality_test_threshold(tmp_path: Path) -> None:
    config_path = tmp_path / "estimate_rules.toml"
    config_path.write_text("[quality_test]\n", encoding="utf-8")

    with pytest.raises(ValueError, match="quality_test.minimum_amount"):
        load_estimate_rules(config_path)

