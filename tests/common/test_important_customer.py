import pytest

import estimate_management.common as common
from estimate_management.common import Discount, Money, requires_quality_test

IMPORTANT_CUSTOMER_CODE = "00000000000000000001"
REGULAR_CUSTOMER_CODE = "00000000000000000002"


@pytest.mark.parametrize(
    "customer_code",
    [pytest.param(IMPORTANT_CUSTOMER_CODE, id="TC-25-accepts-20-digit-customer-code")],
)
def test_accepts_20_digit_customer_code(customer_code: str) -> None:
    code = common.CustomerCode(customer_code)

    assert code.value == customer_code


@pytest.mark.parametrize(
    "customer_code",
    [
        pytest.param("0" * 19, id="TC-26-rejects-19-digit-customer-code"),
        pytest.param("0" * 21, id="TC-27-rejects-21-digit-customer-code"),
        pytest.param("0" * 19 + "A", id="TC-28-rejects-non-digit-customer-code"),
        pytest.param(12_345_678_901_234_567_890, id="TC-29-rejects-non-string-customer-code"),
    ],
)
def test_rejects_customer_code_other_than_20_digit_string(customer_code: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        common.CustomerCode(customer_code)


@pytest.mark.parametrize(
    ("customer_code", "expected"),
    [
        pytest.param(IMPORTANT_CUSTOMER_CODE, True, id="TC-30-identifies-important-customer"),
        pytest.param(REGULAR_CUSTOMER_CODE, False, id="TC-31-identifies-regular-customer"),
    ],
)
def test_identifies_important_customer(customer_code: str, expected: bool) -> None:
    result = common.is_important_customer(common.CustomerCode(customer_code))

    assert result is expected


@pytest.mark.parametrize(
    "expected",
    [pytest.param(False, id="TC-32-treats-unset-important-customer-as-regular")],
)
def test_treats_unset_important_customer_flag_as_regular(expected: bool) -> None:
    result = requires_quality_test(
        Money.yen(999_999),
        discount=Discount.discount(20),
    )

    assert result.required is expected
