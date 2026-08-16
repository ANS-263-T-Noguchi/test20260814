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

品管テストは、次のいずれかを満たす場合に必要と判定されます。

- 見積金額が`quality_test.minimum_amount`以上
- 値引率が`quality_test.minimum_discount`を超える

初期設定は、見積金額1,000,000円以上、または値引率20%超です。

```toml
[quality_test]
minimum_amount = 1000000
minimum_discount = 20
```

値引率には0以上100以下の整数を指定します。

```python
from estimate_management.common import Discount, Money, requires_quality_test

result = requires_quality_test(
    Money.yen(999_999),
    discount=Discount.discount(21),
)

assert result.required is True
assert result.warnings == ()
```

判定結果は`QualityCheckResult`で返されます。`required`は品管テストの要否、
`warnings`はログなどへ出力すべき警告のタプルです。値引率が未設定の場合は、
金額条件だけで判定し、その旨を`warnings`へ格納するとともに警告ログを出力します。
`minimum_amount`が未設定の場合は品管テスト不要と判定し、`warnings`への格納と
警告ログの出力を行います。

複数の見積りをまとめて判定する場合は、`load_estimate_rules()`で設定を一度だけ
読み込み、`requires_quality_test()`の第2引数へ渡せます。

```python
from estimate_management.common import Discount, Money, load_estimate_rules
from estimate_management.common import requires_quality_test

rules = load_estimate_rules()

requires_quality_test(
    Money.yen(800_000),
    rules,
    discount=Discount.discount(10),
).required
```

## 値引額計算

`Discount`は値引率を表し、見積金額から値引額を計算できます。

```python
from estimate_management.common import Discount, Money

discount_rate = Discount.discount(20)
discount_amount = discount_rate.calculate_discount(Money.yen(1_000))

assert discount_amount == Money.yen(200)
```

## ディレクトリ構成

```text
.
├── .github/workflows/ci.yml
├── config/estimate_rules.toml
├── src/estimate_management/
│   └── common/
│       ├── discount.py
│       ├── estimate_number.py
│       ├── estimate_rules.py
│       ├── money.py
│       ├── quality_check_result.py
│       └── rounding.py
├── tests/common/
└── pyproject.toml
```
