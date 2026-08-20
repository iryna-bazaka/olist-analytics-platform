-- Databricks SQL extension point.
-- This file describes the production-style landing path for the same Olist model.
-- Replace the volume and catalog names with the workspace-specific values.

create schema if not exists main.olist_bronze;
create schema if not exists main.olist_silver;
create schema if not exists main.olist_gold;

-- Bronze: preserve source shape and add ingestion metadata.
create table if not exists main.olist_bronze.orders
using delta
as
select *, current_timestamp() as _ingested_at
from read_files('/Volumes/main/olist_raw/orders/*.csv', format => 'csv', header => true);

-- Silver and gold are intentionally implemented in dbt models under models/.
-- The table names below are the contracts consumed by Power BI.
--
-- main.olist_silver.stg_orders
-- main.olist_silver.stg_order_items
-- main.olist_gold.dim_customers
-- main.olist_gold.dim_products
-- main.olist_gold.dim_sellers
-- main.olist_gold.fct_orders
-- main.olist_gold.fct_order_items

-- Optional Delta quality expectation examples:
-- constraint valid_order_id check (order_id is not null) enforced;
-- constraint non_negative_price check (item_price >= 0) enforced;

-- Governance questions to answer in a real deployment:
-- 1. Which fields require masking or row-level restrictions?
-- 2. Which service principal owns the Power BI refresh?
-- 3. Which freshness and completeness thresholds page the data owner?
