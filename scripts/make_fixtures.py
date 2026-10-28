"""Write a tiny Olist-shaped sample to tests/fixtures/ for CI.

Includes edge cases on purpose:
- o2: canceled order with a payment but no items
- o3: paid more than items + freight (10 installments with interest) and delivered late
- c1/c2: same person (u1) under two order-level customer_ids
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures"
OUT.mkdir(parents=True, exist_ok=True)


def write(name, header, rows):
    with open(OUT / name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


write("olist_customers_dataset.csv",
      ["customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"],
      [["c1", "u1", "01000", "sao paulo", "SP"],
       ["c2", "u1", "01000", "sao paulo", "SP"],
       ["c3", "u3", "20000", "rio de janeiro", "RJ"]])
write("olist_geolocation_dataset.csv",
      ["geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng", "geolocation_city", "geolocation_state"],
      [["01000", -23.55, -46.63, "sao paulo", "SP"],
       ["01000", -23.56, -46.64, "sao paulo", "SP"],
       ["20000", -22.90, -43.20, "rio de janeiro", "RJ"]])
write("olist_orders_dataset.csv",
      ["order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_approved_at",
       "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"],
      [["o1", "c1", "delivered", "2017-01-01 10:00:00", "2017-01-01 11:00:00", "2017-01-02 09:00:00", "2017-01-04 15:00:00", "2017-01-10 00:00:00"],
       ["o2", "c2", "canceled", "2017-02-03 12:00:00", "", "", "", "2017-02-20 00:00:00"],
       ["o3", "c3", "delivered", "2017-03-05 08:00:00", "2017-03-05 09:00:00", "2017-03-06 10:00:00", "2017-03-25 10:00:00", "2017-03-20 00:00:00"]])
write("olist_order_items_dataset.csv",
      ["order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", "price", "freight_value"],
      [["o1", 1, "p1", "s1", "2017-01-03 00:00:00", 100.00, 10.00],
       ["o1", 2, "p2", "s2", "2017-01-03 00:00:00", 20.00, 5.00],
       ["o3", 1, "p1", "s1", "2017-03-07 00:00:00", 200.00, 15.00]])
write("olist_order_payments_dataset.csv",
      ["order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"],
      [["o1", 1, "credit_card", 2, 135.00],
       ["o2", 1, "boleto", 1, 49.90],
       ["o3", 1, "credit_card", 10, 226.30],
       ["o3", 2, "voucher", 1, 0.00]])
write("olist_order_reviews_dataset.csv",
      ["review_id", "order_id", "review_score", "review_comment_title", "review_comment_message",
       "review_creation_date", "review_answer_timestamp"],
      [["r1", "o1", 5, "", "chegou rapido", "2017-01-05 00:00:00", "2017-01-06 10:00:00"],
       ["r3", "o3", 2, "", "atrasou", "2017-03-26 00:00:00", "2017-03-27 10:00:00"]])
write("olist_products_dataset.csv",
      ["product_id", "product_category_name", "product_name_lenght", "product_description_lenght",
       "product_photos_qty", "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"],
      [["p1", "beleza_saude", 40, 300, 1, 500, 20, 10, 15],
       ["p2", "informatica_acessorios", 35, 250, 2, 200, 15, 5, 10]])
write("olist_sellers_dataset.csv",
      ["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"],
      [["s1", "01000", "sao paulo", "SP"], ["s2", "20000", "rio de janeiro", "RJ"]])
write("product_category_name_translation.csv",
      ["product_category_name", "product_category_name_english"],
      [["beleza_saude", "health_beauty"], ["informatica_acessorios", "computers_accessories"]])
print(f"Wrote fixtures to {OUT}")
