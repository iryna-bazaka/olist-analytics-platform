{{ config(severity='warn') }}
-- Warn (not fail) when what the customer paid differs from items + freight by more than 1 BRL.
-- Known causes in Olist: installment interest, vouchers, orders without items.
select order_id, order_status, order_total_value, payment_value,
       payment_value - order_total_value as payment_gap
from {{ ref('fct_orders') }}
where has_items
  and payment_value is not null
  and abs(payment_value - order_total_value) > 1
