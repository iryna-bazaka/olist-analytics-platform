-- fct_order_items must have exactly one row per order_id + order_item_id.
select order_id, order_item_id, count(*) as row_count
from {{ ref('fct_order_items') }}
group by order_id, order_item_id
having count(*) > 1
