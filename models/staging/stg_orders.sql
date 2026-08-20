{{ config(materialized='view') }}

select
    cast(order_id as string) as order_id,
    cast(customer_id as string) as customer_id,
    cast(order_status as string) as order_status,
    to_timestamp(order_purchase_timestamp) as order_purchase_timestamp,
    to_timestamp(order_approved_at) as order_approved_at,
    to_timestamp(order_delivered_carrier_date) as order_delivered_carrier_date,
    to_timestamp(order_delivered_customer_date) as order_delivered_customer_date,
    to_timestamp(order_estimated_delivery_date) as order_estimated_delivery_date,
    cast(date(to_timestamp(order_purchase_timestamp)) as date) as purchase_date,
    cast(date_trunc('month', to_timestamp(order_purchase_timestamp)) as date) as purchase_month
from {{ source('olist_raw', 'orders') }}
