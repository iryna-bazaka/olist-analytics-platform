# Architecture and design decisions

## Design goal

Create one trusted analytical contract that can be consumed by dbt, Databricks SQL, Power BI, or a lightweight local preview without redefining business logic in every surface.

## Layering

| Layer | Responsibility | Example objects |
| --- | --- | --- |
| Bronze | Preserve source shape, ingestion metadata, and source auditability | `olist_bronze.orders` |
| Staging / silver | Standardize names, types, timestamps, and source-level semantics | `stg_orders`, `stg_order_items` |
| Gold | Apply business joins and establish dimensional grains | `fct_orders`, `fct_order_items`, `dim_products` |
| Semantic | Publish reusable measures and dimensions | `semantic_order_metrics`, `metrics.yml` |
| Consumption | Make insights usable by business and technical audiences | Power BI model, Streamlit preview |

## Grain decisions

- `fct_orders`: one row per `order_id`.
- `fct_order_items`: one row per `order_id` + `order_item_id`.
- `dim_customers`: one row per source `customer_id`; use `customer_unique_id` for repeat-customer analysis.
- `dim_products`: one row per `product_id`.
- `dim_sellers`: one row per `seller_id`.
- `dim_geography`: one row per ZIP-code prefix after aggregating geolocation observations.

## Why order and item facts are separate

An order can contain multiple products, sellers, payments, and review records. If order-level measures are joined directly to item-level rows, revenue, review, and delivery measures can be multiplied. The semantic layer therefore exposes order-level and item-level measures separately and documents the safe aggregation path.

## Portability

The dbt models use Databricks SQL as the primary production dialect. The local preview uses SQLite and a small Python adapter to validate data contracts without a cloud account. Differences are documented rather than hidden.

## Future production controls

- Unity Catalog ownership and lineage;
- Delta table constraints and expectation monitoring;
- incremental loads keyed by source update timestamps;
- freshness and volume anomaly alerts;
- Power BI refresh ownership and service-principal access;
- row-level security if the dataset becomes multi-tenant;
- Snowflake adapter if the target platform changes.
