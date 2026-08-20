from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from olist_analytics.local_pipeline import RAW_FILES, build_local_warehouse
from olist_analytics.metrics import kpis


class LocalPipelineTests(unittest.TestCase):
    def write_fixture(self, raw_dir: Path) -> None:
        frames = {
            "customers": pd.DataFrame([
                {"customer_id": "c1", "customer_unique_id": "u1", "customer_zip_code_prefix": "10000", "customer_city": "sao paulo", "customer_state": "SP"},
            ]),
            "geolocation": pd.DataFrame([
                {"geolocation_zip_code_prefix": "10000", "geolocation_lat": -23.5, "geolocation_lng": -46.6, "geolocation_city": "sao paulo", "geolocation_state": "SP"},
            ]),
            "order_items": pd.DataFrame([
                {"order_id": "o1", "order_item_id": 1, "product_id": "p1", "seller_id": "s1", "shipping_limit_date": "2017-01-02 00:00:00", "price": 100.0, "freight_value": 10.0},
                {"order_id": "o1", "order_item_id": 2, "product_id": "p2", "seller_id": "s2", "shipping_limit_date": "2017-01-02 00:00:00", "price": 20.0, "freight_value": 5.0},
            ]),
            "order_payments": pd.DataFrame([
                {"order_id": "o1", "payment_sequential": 1, "payment_type": "credit_card", "payment_installments": 2, "payment_value": 135.0},
            ]),
            "order_reviews": pd.DataFrame([
                {"review_id": "r1", "order_id": "o1", "review_score": 5, "review_comment_title": "good", "review_comment_message": "fast", "review_creation_date": "2017-01-06 00:00:00", "review_answer_timestamp": "2017-01-07 00:00:00"},
            ]),
            "orders": pd.DataFrame([
                {"order_id": "o1", "customer_id": "c1", "order_status": "delivered", "order_purchase_timestamp": "2017-01-01 00:00:00", "order_approved_at": "2017-01-01 01:00:00", "order_delivered_carrier_date": "2017-01-02 00:00:00", "order_delivered_customer_date": "2017-01-04 00:00:00", "order_estimated_delivery_date": "2017-01-05 00:00:00"},
            ]),
            "products": pd.DataFrame([
                {"product_id": "p1", "product_category_name": "beleza_saude", "product_name_lenght": 10, "product_description_lenght": 20, "product_photos_qty": 1, "product_weight_g": 100, "product_length_cm": 10, "product_height_cm": 10, "product_width_cm": 10},
                {"product_id": "p2", "product_category_name": "informatica_acessorios", "product_name_lenght": 12, "product_description_lenght": 24, "product_photos_qty": 2, "product_weight_g": 200, "product_length_cm": 20, "product_height_cm": 10, "product_width_cm": 10},
            ]),
            "sellers": pd.DataFrame([
                {"seller_id": "s1", "seller_zip_code_prefix": "10000", "seller_city": "sao paulo", "seller_state": "SP"},
                {"seller_id": "s2", "seller_zip_code_prefix": "10000", "seller_city": "sao paulo", "seller_state": "SP"},
            ]),
            "category_translation": pd.DataFrame([
                {"product_category_name": "beleza_saude", "product_category_name_english": "health_beauty"},
                {"product_category_name": "informatica_acessorios", "product_category_name_english": "computers_accessories"},
            ]),
        }
        for key, filename in RAW_FILES.items():
            frames[key].to_csv(raw_dir / filename, index=False)

    def test_pipeline_reconciles_order_and_item_revenue(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw_dir = Path(tmp) / "raw"
            raw_dir.mkdir()
            db_path = Path(tmp) / "olist.sqlite"
            self.write_fixture(raw_dir)
            result = build_local_warehouse(raw_dir, db_path)
            self.assertTrue(result["quality"]["passed"])
            self.assertEqual(result["tables"]["fct_orders"], 1)
            self.assertEqual(result["tables"]["fct_order_items"], 2)

            import sqlite3
            conn = sqlite3.connect(db_path)
            try:
                values = kpis(conn)
            finally:
                conn.close()
            self.assertEqual(values["merchandise_revenue"], 120.0)
            self.assertEqual(values["orders"], 1)
            self.assertEqual(values["average_order_value"], 120.0)
            self.assertEqual(values["on_time_delivery_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
