import pytest

import estimate_management.common as common
from estimate_management.common import Discount, Money, requires_quality_test

IMPORTANT_CUSTOMER_CODE = "00000000000000000001"
REGULAR_CUSTOMER_CODE = "00000000000000000002"


@pytest.mark.parametrize(
    ("customer_code", "expected"),
    [
        pytest.param(
            IMPORTANT_CUSTOMER_CODE,
            IMPORTANT_CUSTOMER_CODE,
            id="TC-25-20文字の顧客コードを受理",
        ),
        pytest.param(
            "ABC12345678901234567",
            "ABC12345678901234567",
            id="TC-26-英数字の顧客コードを受理",
        ),
        pytest.param(
            12_345_678_901_234_567_890,
            "12345678901234567890",
            id="TC-29-文字列以外の顧客コードを文字列として受理",
        ),
    ],
)
def test_accepts_20_character_customer_code(customer_code: object, expected: str) -> None:
    code = common.CustomerCode(customer_code)

    assert code.value == expected


@pytest.mark.parametrize(
    "customer_code",
    [
        pytest.param("0" * 19, id="TC-27-19文字の顧客コードを拒否"),
        pytest.param("0" * 21, id="TC-28-21文字の顧客コードを拒否"),
    ],
)
def test_rejects_customer_code_other_than_20_character_string(customer_code: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        common.CustomerCode(customer_code)


@pytest.mark.parametrize(
    ("customer_code", "expected"),
    [
        pytest.param(IMPORTANT_CUSTOMER_CODE, True, id="TC-30-重要顧客を判定"),
        pytest.param(REGULAR_CUSTOMER_CODE, False, id="TC-31-通常顧客を判定"),
    ],
)
def test_identifies_important_customer(customer_code: str, expected: bool) -> None:
    result = common.is_important_customer(common.CustomerCode(customer_code))

    assert result is expected


@pytest.mark.parametrize(
    "expected",
    [pytest.param(False, id="TC-32-重要顧客フラグ未設定を通常顧客として処理")],
)
def test_treats_unset_important_customer_flag_as_regular(expected: bool) -> None:
    result = requires_quality_test(
        Money.yen(999_999),
        discount=Discount.discount(20),
    )

    assert result.required is expected
