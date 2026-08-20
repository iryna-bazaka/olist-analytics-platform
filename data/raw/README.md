# Raw data setup

Place the nine CSV files from the [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) in this folder, or pass another folder to `scripts/run_pipeline.py --raw-dir`.

Expected files:

```text
olist_customers_dataset.csv
olist_geolocation_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
olist_orders_dataset.csv
olist_products_dataset.csv
olist_sellers_dataset.csv
product_category_name_translation.csv
```

Raw files are excluded from Git by design. This keeps the repository small and leaves dataset redistribution subject to the source's current terms.
