# Power BI model definition

## Recommended star schema

```text
dim_customers  1 ─── *  fct_orders  1 ─── *  fct_order_items  * ─── 1 dim_products
                              |
                              *
                         dim_date

fct_order_items  * ─── 1 dim_sellers
```

## Why two facts

`fct_orders` is the order-grain fact for customer, payment, review, and fulfillment measures. `fct_order_items` is the item-grain fact for category, seller, merchandise, and freight analysis.

Keeping these facts separate prevents order-level measures from being duplicated when an order contains multiple items.

## Report pages

### Executive overview

- KPI cards: Merchandise Revenue, Orders, Customers, Average Order Value, On-Time Delivery Rate.
- Line chart: monthly merchandise revenue and order count.
- Slicers: purchase month, customer state, order status.

### Commercial performance

- Bar chart: top product categories by merchandise revenue.
- Matrix: category revenue, orders, AOV, review score.
- Small multiples: seller state contribution.

### Customer experience

- Delivery delay distribution.
- On-time delivery by customer state.
- Average review score by order status and month.

## UX and governance notes

- Use measure names that match the semantic metric catalog.
- Hide technical surrogate keys from report consumers.
- Format revenue as BRL and rates as percentages.
- Add a visible “Data as of” value based on the maximum purchase date.
- Keep raw Portuguese category names available only for audit, not as the primary report label.
