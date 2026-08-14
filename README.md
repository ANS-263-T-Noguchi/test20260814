# 見積管理システム

GitHub Actionsを試しながら開発する、Python製のシンプルな見積管理システムです。

## 開発環境

- Python 3.11以上
- `src`レイアウト
- pytest（テスト）
- Ruff（静的解析・フォーマット確認）

## セットアップ

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## 確認コマンド

```powershell
ruff check .
ruff format --check .
pytest
```

`main`ブランチへのpushとpull requestで、同じ確認をGitHub Actionsが実行します。

## 端数処理

金額の生成や計算では、保持する小数桁数と端数処理方式を指定できます。

```python
from decimal import Decimal

from estimate_management.common import Money, RoundingMode, RoundingPolicy

policy = RoundingPolicy(decimal_places=2, mode=RoundingMode.DOWN)
amount = Money.yen("123.456", policy)  # 123.45
tax = amount.calculate_tax(Decimal("0.10"), policy)
```

指定できる方式は`DOWN`（切り捨て）、`UP`（切り上げ）、`HALF_UP`（四捨五入）です。
設定を省略した場合は、従来どおり小数0桁で四捨五入します。

## 品管テスト判定

`config/estimate_rules.toml`の`quality_test.minimum_amount`以上の見積金額は、
品管テストが必要と判定されます。初期値は1,000,000円です。

```python
from estimate_management.common import Money, requires_quality_test

requires_quality_test(Money.yen(999_999))  # False
requires_quality_test(Money.yen(1_000_000))  # True
```

複数の見積りをまとめて判定する場合は、`load_estimate_rules()`で設定を一度だけ
読み込み、`requires_quality_test()`の第2引数へ渡せます。

## ディレクトリ構成

```text
.
├── .github/workflows/ci.yml
├── config/estimate_rules.toml
├── src/estimate_management/
│   └── common/
├── tests/common/
└── pyproject.toml
```
