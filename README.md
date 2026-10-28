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

I've spent 9+ years building data platforms for enterprise clients, most recently as a team lead.
Much of that work was semantic modelling: running definition sessions with the business on what an "order",
a "customer" or "revenue" means, designing the architecture and semantic models (I draw them in draw.io
or Excalidraw), and implementing them on Databricks and Power BI.

My way of working has always been incremental. I build on a small dataset first and let the business test it.
Then I add more history and test again. Every red flag or warning I find, I confirm with the business owner
the same day instead of guessing. Most of the trust in a number comes from that loop, not from the SQL.

That experience also taught me where things break: definitions, grain, and the edge cases nobody mentions
until two reports show different numbers. In client work, that reasoning lives in workshops, diagrams and
private repositories. Here I wanted it to be visible.

I chose dbt because it turns those decisions into code. Each model has one grain, each metric is defined once,
and every assumption I make about the data is a test that runs on every build. I hadn't used dbt in production
before, so this project is also where I learned it properly, on real, messy data rather than a tutorial.

A few choices here reflect how I work on client projects:

- **Two fact tables at two grains.** Mixing order-level and item-level measures in one table is a classic way
  to double-count revenue.
- **Warnings, not silent filters.** When 772 paid orders have no items, I'd rather surface it and ask the
  business than quietly drop them.
- **A hypothesis is labelled as one.** Installment interest fits the payment gaps, but Olist can't prove it,
  so I don't claim it.
- **Small data first, then full history.** CI builds on small fixture files with the edge cases built in;
  the same tests then run on all 99,441 orders.
