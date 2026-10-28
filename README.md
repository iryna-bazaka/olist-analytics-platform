# Olist analytics in dbt

A dbt project on the public [Olist Brazilian e-commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
(99,441 orders, 2016–2018). It turns nine raw CSV files into tested facts, dimensions and a small semantic layer,
and runs locally on DuckDB with no cloud account.

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DBT_PROFILES_DIR=.
# download the Kaggle dataset and unzip the CSVs into data/raw/
dbt build
```

Expected result: `PASS=41 WARN=2 ERROR=0`. The two warnings are real data issues, explained below.

## What's inside

| Layer | Models | Materialized as |
|---|---|---|
| Staging (`models/staging`) | 9 models, one per source file: types, timestamps, renaming | views |
| Marts (`models/marts`) | `fct_orders`, `fct_order_items`, `dim_customers`, `dim_products`, `dim_sellers`, `dim_geography` | tables |
| Semantic (`models/semantic`) | 2 semantic models, 12 metrics, time spine | views |

Two facts on purpose: `fct_orders` is one row per order (payments, delivery, reviews),
`fct_order_items` is one row per item (category, seller, price). Keeping them apart stops
order-level numbers from being counted once per item.

Metrics are defined once in `semantic_models.yml`: merchandise revenue, orders, customers,
average order value, on-time delivery rate, average review score and item revenue by category.
CI checks they parse; I haven't queried them through MetricFlow yet.

## How it's tested

25 data tests run on every `dbt build`:

- **Keys and grain:** unique and not-null keys, one row per order item, relationships between facts and dimensions.
- **Accepted values:** order status, review score 1–5.
- **Reconciliation:** item revenue in `fct_order_items` adds up to `fct_orders`.
- **Data quality warnings** (warn, not fail): payments that don't match items + freight, and paid orders with no items.

CI (`.github/workflows/ci.yml`) runs `dbt parse` and `dbt build` on small fixture files in `tests/fixtures/`,
which include the edge cases on purpose: a canceled order with a payment and no items, and an order paid in
10 installments with a voucher. Regenerate them with `python scripts/make_fixtures.py`.

## What I found in the data

- **772 orders were paid but have no items**, most of them `unavailable` or `canceled`. Average order value
  therefore divides by orders with items only.
- **249 orders don't match items + freight.** The gap rate jumps for 11–12 installments (~12% vs ~0.4% for 2–10),
  which fits installment interest, but some gaps go the other way and can't be explained that way.
- My first test reported these as one number (1,021). Splitting it by cause made both warnings actionable.

Details and open questions: [docs/data-findings.md](docs/data-findings.md).

## Limitations

- Static historical data, so no incremental models or source freshness checks.
- No refund or interest data in Olist; two findings above stay hypotheses.
- Runs on DuckDB only. The SQL uses dbt cross-database macros where dialects differ.

## Why I built this

I've designed semantic models for enterprise clients and implemented them on Databricks and Power BI.
This is the same approach in dbt with the tests and the messy parts visible.
