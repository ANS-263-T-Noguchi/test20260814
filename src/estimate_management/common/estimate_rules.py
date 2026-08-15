"""見積金額に応じた作業判定ルール。"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from estimate_management.common.discount import Discount
from estimate_management.common.money import Money

DEFAULT_RULES_PATH = Path(__file__).resolve().parents[3] / "config" / "estimate_rules.toml"


@dataclass(frozen=True, slots=True)
class EstimateRules:
    """設定ファイルから読み込んだ見積判定ルール。"""

    quality_test_minimum_amount: Money
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
        raise ValueError("設定ファイルにquality_test.minimum_amountを指定してください") from None

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
) -> bool:
    """見積金額または値引率が品管テストの対象ならTrueを返します。

    大量の見積りを判定する場合は、load_estimate_rulesで一度だけ読み込んだ
    rulesを渡すことで、設定ファイルの繰り返し読み込みを避けられます。

    金額条件が成立せず、値引率が未設定の場合は判定不能としてValueErrorを送出します。
    """

    active_rules = rules if rules is not None else load_estimate_rules(config_path)
    if estimate_amount.amount >= active_rules.quality_test_minimum_amount.amount:
        return True

    if discount is None:
        raise ValueError("値引率が未設定のため品管テスト対象を判定できません")

    return discount.amount >= active_rules.quality_test_minimum_discount.amount
