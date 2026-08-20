{{ config(materialized='table') }}

with item_metrics as (
    select
        order_id,
        sum(item_price) as merchandise_revenue,
        sum(freight_value) as freight_revenue,
        count(*) as item_count,
        count(distinct product_id) as distinct_product_count,
        count(distinct seller_id) as distinct_seller_count
    from {{ ref('stg_order_items') }}
    group by order_id
),
payment_metrics as (
    select
        order_id,
        sum(payment_value) as payment_value,
        max(payment_installments) as max_payment_installments,
        concat_ws(', ', sort_array(collect_set(payment_type))) as payment_types
    from {{ ref('stg_order_payments') }}
    group by order_id
),
review_metrics as (
    select
        order_id,
        avg(review_score) as average_review_score,
        count(distinct review_id) as review_count
    from {{ ref('stg_order_reviews') }}
    group by order_id
)
select
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_state,
    c.customer_city,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    o.purchase_date,
    o.purchase_month,
    i.merchandise_revenue,
    i.freight_revenue,
    i.merchandise_revenue + i.freight_revenue as order_total_value,
    i.item_count,
    i.distinct_product_count,
    i.distinct_seller_count,
    p.payment_value,
    p.max_payment_installments,
    p.payment_types,
    r.average_review_score,
    r.review_count,
    case
        when o.order_delivered_customer_date is not null
         and o.order_purchase_timestamp is not null
        then datediff(o.order_delivered_customer_date, o.order_purchase_timestamp)
    end as delivery_days,
    case
        when o.order_delivered_customer_date is not null
         and o.order_estimated_delivery_date is not null
        then datediff(o.order_delivered_customer_date, o.order_estimated_delivery_date)
    end as delivery_delay_days,
    case
        when o.order_status = 'delivered'
         and o.order_delivered_customer_date is not null
         and o.order_estimated_delivery_date is not null
        then case when o.order_delivered_customer_date <= o.order_estimated_delivery_date then 1 else 0 end
    end as on_time_delivery_flag
from {{ ref('stg_orders') }} o
left join {{ ref('dim_customers') }} c on o.customer_id = c.customer_id
left join item_metrics i on o.order_id = i.order_id
left join payment_metrics p on o.order_id = p.order_id
left join review_metrics r on o.order_id = r.order_id
