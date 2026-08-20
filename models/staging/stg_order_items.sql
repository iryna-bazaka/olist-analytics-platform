{{ config(materialized='view') }}

select
    cast(order_id as string) as order_id,
    cast(order_item_id as int) as order_item_id,
    cast(product_id as string) as product_id,
    cast(seller_id as string) as seller_id,
    to_timestamp(shipping_limit_date) as shipping_limit_date,
    cast(price as decimal(18, 2)) as item_price,
    cast(freight_value as decimal(18, 2)) as freight_value
from {{ source('olist_raw', 'order_items') }}
