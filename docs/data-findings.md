# What I found in the Olist data

All numbers come from `dbt build` and `dbt show` on the public Olist dataset (99,441 orders).
Two warn-level tests track these issues on every build.

## 1. Paid orders with no items (772 orders)

775 orders have no rows in `order_items`. By status:

| Status | Orders | Paid (BRL) |
|---|---:|---:|
| unavailable | 603 | 124,339.02 |
| canceled | 164 | 37,337.87 |
| created | 5 | 688.10 |
| invoiced | 2 | 149.23 |
| shipped | 1 | 77.73 |

772 of them have a payment. Unavailable and canceled orders are probably refunds, but the dataset
has no refund table, so I can't confirm it. The 3 `invoiced`/`shipped` orders without items are harder
to explain and would need a question to the business.

**What I did:** added `has_items` to `fct_orders`. Average order value divides by orders with items only,
so these orders don't pull it down. Test: `assert_paid_orders_have_items` (warn).

## 2. Payments that don't match items + freight (249 orders)

For orders with items, 98,416 match within 1 BRL (~99.7%). 249 don't.

My first hypothesis was installment interest. The data supports it only partly:

| Installments | Gap rate |
|---|---:|
| 1 | 0.03% |
| 2–10 | ~0.4% |
| 11–12 | ~12% |

The jump after 10 installments fits the common Brazilian practice of interest-free installments
up to about 10, with interest above that. But Olist has no interest column, so this is a hypothesis.
It also doesn't explain 13 gaps on single payments, or orders where the customer paid *less*
(for example, one order paid 51.62 BRL below its total).

**What I did:** `assert_payments_match_order_totals` (warn, not error). Revenue metrics use item prices,
not payments, so these gaps don't change revenue numbers.

## 3. Lesson from building the tests

My first version had one test that reported 1,021 mismatches. It mixed two problems with different
causes. Splitting it into two tests made each warning explainable and actionable.

## Open questions for the business

- Are unavailable/canceled payments refunded, and where is that recorded?
- Why do 3 invoiced/shipped orders have no items?
- Which payments include installment interest, and how are vouchers applied?
- One order has items but no payment record. Is that a data loss?
