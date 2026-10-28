{{ config(severity='warn') }}
-- Warn when a customer paid for an order that has no items.
-- In Olist these are mostly 'unavailable' and 'canceled' orders (likely refunds),
-- but a few are 'shipped' or 'invoiced', which needs an explanation from the business.
select order_id, order_status, payment_value
from {{ ref('fct_orders') }}
where not has_items
  and payment_value > 0
