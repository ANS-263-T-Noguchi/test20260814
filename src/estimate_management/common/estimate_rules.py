"""見積金額に応じた作業判定ルール。"""

from __future__ import annotations

import logging
import tomllib
from dataclasses import dataclass
from pathlib import Path

from estimate_management.common.discount import Discount
from estimate_management.common.money import Money
from estimate_management.common.quality_check_result import QualityCheckResult

DEFAULT_RULES_PATH = Path(__file__).resolve().parents[3] / "config" / "estimate_rules.toml"
logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class EstimateRules:
    """設定ファイルから読み込んだ見積判定ルール。"""

    quality_test_minimum_amount: Money | None
    quality_test_minimum_discount: Discount


def load_estimate_rules(config_path: str | Path = DEFAULT_RULES_PATH) -> EstimateRules:
    """TOML設定ファイルから見積判定ルールを読み込みます。"""
    path = Path(config_path)
    try:
        with path.open("rb") as config_file:
            config = tomllib.load(config_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"見積判定設定ファイルが見つかりません: {path}") from None

    """minimum_amountのチェック"""
    try:
        minimum_amount = config["quality_test"]["minimum_amount"]
    except (KeyError, TypeError):
        threshold = None
    else:
        if isinstance(minimum_amount, bool) or not isinstance(minimum_amount, (int, str)):
            raise ValueError("quality_test.minimum_amountは円単位の整数で指定してください")

        try:
            threshold = Money.yen(minimum_amount)
        except (ValueError, ArithmeticError):
            raise ValueError(
                "quality_test.minimum_amountは0以上の円単位の整数で指定してください"
            ) from None

    """minimum_discountのチェック"""
    try:
        minimum_discount = config["quality_test"]["minimum_discount"]
    except (KeyError, TypeError):
        raise ValueError("設定ファイルにquality_test.minimum_discountを指定してください") from None

    if isinstance(minimum_discount, bool) or not isinstance(minimum_discount, (int, str)):
        raise ValueError("quality_test.minimum_discountは整数で指定してください")

    try:
        threshold_discount = Discount.discount(minimum_discount)
    except (ValueError, ArithmeticError):
        raise ValueError(
            "quality_test.minimum_discountは0以上100以下の整数で指定してください"
        ) from None

    return EstimateRules(
        quality_test_minimum_amount=threshold, quality_test_minimum_discount=threshold_discount
    )


def requires_quality_test(
    estimate_amount: Money,
    rules: EstimateRules | None = None,
    *,
    discount: Discount | None,
    config_path: str | Path = DEFAULT_RULES_PATH,
) -> QualityCheckResult:
    """見積金額または値引率による品管テスト判定結果を返します。

    大量の見積りを判定する場合は、load_estimate_rulesで一度だけ読み込んだ
    rulesを渡すことで、設定ファイルの繰り返し読み込みを避けられます。

    minimum_amountが未設定の場合は警告を記録し、品管テスト不要と判定します。
    値引率が未設定の場合は警告を記録し、金額条件だけで判定します。
    """

    active_rules = rules if rules is not None else load_estimate_rules(config_path)
    if active_rules.quality_test_minimum_amount is None:
        warning = "quality_test.minimum_amountが未設定のため品管テスト対象外です"
        logger.warning("%s", warning)
        return QualityCheckResult(required=False, warnings=(warning,))

    amount_requires_quality_test = (
        estimate_amount.amount >= active_rules.quality_test_minimum_amount.amount
    )

    if discount is None:
        warning = (
            "値引率が未設定です。金額条件による判定結果を採用します: "
            f"estimate_amount={estimate_amount.amount}, "
            f"requires_quality_test={amount_requires_quality_test}"
        )
        logger.warning("%s", warning)
        return QualityCheckResult(
            required=amount_requires_quality_test,
            warnings=(warning,),
        )

    if amount_requires_quality_test:
        return QualityCheckResult(required=True)

    return QualityCheckResult(
        required=discount.amount > active_rules.quality_test_minimum_discount.amount
    )
