{{ config(materialized='view') }}

select
    order_id,
    customer_unique_id,
    customer_state,
    order_status,
    purchase_date,
    purchase_month,
    merchandise_revenue,
    freight_revenue,
    order_total_value,
    item_count,
    average_review_score,
    delivery_days,
    delivery_delay_days,
    on_time_delivery_flag
from {{ ref('fct_orders') }}
