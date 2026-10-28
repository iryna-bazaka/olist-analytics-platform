-- Total merchandise revenue must be identical at item grain and at order grain.
-- If this returns a row, a join has duplicated or dropped items.
with items as (select sum(item_price) as revenue from {{ ref('fct_order_items') }}),
     orders as (select sum(merchandise_revenue) as revenue from {{ ref('fct_orders') }})
select items.revenue as item_revenue, orders.revenue as order_revenue
from items cross join orders
where abs(items.revenue - orders.revenue) > 0.01
