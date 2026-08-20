{{ config(materialized='table') }}

select
    i.order_id,
    i.order_item_id,
    i.product_id,
    i.seller_id,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.purchase_date,
    o.purchase_month,
    p.product_category_name_english,
    s.seller_state,
    i.item_price,
    i.freight_value,
    i.item_price + i.freight_value as item_total_value,
    i.shipping_limit_date
from {{ ref('stg_order_items') }} i
left join {{ ref('stg_orders') }} o on i.order_id = o.order_id
left join {{ ref('dim_products') }} p on i.product_id = p.product_id
left join {{ ref('dim_sellers') }} s on i.seller_id = s.seller_id
