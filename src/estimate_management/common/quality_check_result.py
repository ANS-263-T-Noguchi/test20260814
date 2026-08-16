"""品管テスト判定結果。"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class QualityCheckResult:
    """品管テストの要否と、判定時に発生した警告を保持します。"""

    required: bool
    warnings: tuple[str, ...] = ()
