from datetime import date

import pytest

from estimate_management.common import EstimateNumber


def test_issues_estimate_number() -> None:
    number = EstimateNumber.issue(date(2026, 8, 14), 12)

    assert number.value == "EST-20260814-0012"


@pytest.mark.parametrize("sequence", [0, 10_000])
def test_rejects_out_of_range_sequence(sequence: int) -> None:
    with pytest.raises(ValueError, match="1から9999"):
        EstimateNumber.issue(date(2026, 8, 14), sequence)


def test_rejects_invalid_format() -> None:
    with pytest.raises(ValueError, match="EST-YYYYMMDD-NNNN"):
        EstimateNumber("invalid")
