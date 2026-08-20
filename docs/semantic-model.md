# Semantic model

## Metric contract

| Metric | Grain | Definition | Main use |
| --- | --- | --- | --- |
| Merchandise Revenue | order item | `SUM(item_price)` | Commercial performance |
| Freight Revenue | order item | `SUM(freight_value)` | Fulfillment economics |
| Orders | order | `COUNT(DISTINCT order_id)` | Volume |
| Customers | order | `COUNT(DISTINCT customer_unique_id)` | Customer reach |
| Average Order Value | order | Merchandise Revenue / Orders | Basket value |
| Average Review Score | order with review | `AVG(average_review_score)` | Customer experience |
| On-Time Delivery Rate | delivered order | Average of `on_time_delivery_flag` | Fulfillment reliability |

## Dimensions

- time: `purchase_date`, `purchase_month`;
- order: `order_status`;
- customer: `customer_state`, `customer_city`, `customer_unique_id`;
- product: `product_category_name_english`, physical attributes;
- seller: `seller_state`, `seller_city`;
- payment: `payment_types`, `max_payment_installments`.

## Metric safety rules

1. Use `semantic_order_metrics` for orders, customers, delivery, and reviews.
2. Use `semantic_product_metrics` for product category, seller, item price, and freight.
3. Do not sum order-level revenue after joining to `fct_order_items` unless the measure is explicitly defined at item grain.
4. Treat missing delivery dates as not evaluable, not automatically late.
5. Treat `customer_unique_id` as the customer identity for repeat behavior; `customer_id` is the order-specific source key.
