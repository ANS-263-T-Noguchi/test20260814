"""pytestの共通設定。"""

import re

import pytest

CASE_ID_PATTERN = re.compile(r"\[(TC-\d{2})(?:-[^]]*)?]$")


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_table_header(cells: list[str]) -> None:
    """HTMLレポートへテストケースID列を追加します。"""
    cells.insert(
        1,
        '<th class="sortable" data-column-type="caseId">ケースID</th>',
    )


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_table_row(report: pytest.TestReport, cells: list[str]) -> None:
    """パラメータIDからTC番号を取り出して表示します。"""
    match = CASE_ID_PATTERN.search(report.nodeid)
    case_id = match.group(1) if match else "—"
    cells.insert(1, f'<td class="col-caseId">{case_id}</td>')
