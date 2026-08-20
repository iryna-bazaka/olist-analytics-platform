{{ config(materialized='view') }}

select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    purchase_date,
    purchase_month,
    product_category_name_english,
    seller_state,
    item_price,
    freight_value,
    item_total_value
from {{ ref('fct_order_items') }}
