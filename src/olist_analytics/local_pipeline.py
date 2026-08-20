from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Dict

import pandas as pd

from .validation import run_quality_checks


RAW_FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)


def load_raw(raw_dir: str | Path) -> Dict[str, pd.DataFrame]:
    raw_dir = Path(raw_dir)
    missing = [name for name in RAW_FILES.values() if not (raw_dir / name).exists()]
    if missing:
        raise FileNotFoundError(
            "Missing Olist files: " + ", ".join(missing) +
            ". See data/raw/README.md for setup instructions."
        )
    return {key: _read_csv(raw_dir / filename) for key, filename in RAW_FILES.items()}


def _timestamps(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    result = df.copy()
    for column in columns:
        result[column] = pd.to_datetime(result[column], errors="coerce")
    return result


def _write(conn: sqlite3.Connection, name: str, df: pd.DataFrame) -> None:
    df.to_sql(name, conn, if_exists="replace", index=False, chunksize=5000)


def build_local_warehouse(raw_dir: str | Path, db_path: str | Path) -> dict:
    raw = load_raw(raw_dir)
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)

    try:
        for name, frame in raw.items():
            _write(conn, f"raw_{name}", frame)

        orders = _timestamps(
            raw["orders"],
            [
                "order_purchase_timestamp",
                "order_approved_at",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
            ],
        )
        orders["purchase_date"] = orders["order_purchase_timestamp"].dt.date.astype("string")
        orders["purchase_month"] = orders["order_purchase_timestamp"].dt.to_period("M").astype("string")

        order_items = _timestamps(raw["order_items"], ["shipping_limit_date"])
        order_items = order_items.rename(
            columns={"price": "item_price", "freight_value": "freight_value"}
        )
        order_items["item_price"] = pd.to_numeric(order_items["item_price"], errors="coerce")
        order_items["freight_value"] = pd.to_numeric(order_items["freight_value"], errors="coerce")

        payments = raw["order_payments"].copy()
        payments["payment_value"] = pd.to_numeric(payments["payment_value"], errors="coerce")
        payments["payment_installments"] = pd.to_numeric(payments["payment_installments"], errors="coerce")

        reviews = raw["order_reviews"].copy()
        reviews["review_score"] = pd.to_numeric(reviews["review_score"], errors="coerce")
        reviews = _timestamps(reviews, ["review_creation_date", "review_answer_timestamp"])

        customers = raw["customers"].copy()
        products = raw["products"].copy()
        products = products.rename(
            columns={
                "product_name_lenght": "product_name_length",
                "product_description_lenght": "product_description_length",
            }
        )
        translations = raw["category_translation"].copy()
        translations.columns = [str(column).lstrip("\ufeff") for column in translations.columns]
        products = products.merge(translations, on="product_category_name", how="left")
        products["product_category_name_english"] = products["product_category_name_english"].fillna("unknown")
        sellers = raw["sellers"].copy()

        staging = {
            "stg_orders": orders,
            "stg_order_items": order_items,
            "stg_order_payments": payments,
            "stg_order_reviews": reviews,
            "stg_customers": customers,
            "stg_products": products,
            "stg_sellers": sellers,
            "stg_category_translation": translations,
        }
        for name, frame in staging.items():
            _write(conn, name, frame)

        dim_customers = customers[
            [
                "customer_id",
                "customer_unique_id",
                "customer_zip_code_prefix",
                "customer_city",
                "customer_state",
            ]
        ].copy()
        dim_products = products.copy()
        dim_sellers = sellers.copy()
        geo = raw["geolocation"].copy()
        geo["geolocation_zip_code_prefix"] = geo["geolocation_zip_code_prefix"].astype("string")
        dim_geography = (
            geo.groupby("geolocation_zip_code_prefix", dropna=False)
            .agg(
                latitude=("geolocation_lat", "mean"),
                longitude=("geolocation_lng", "mean"),
                representative_city=("geolocation_city", "first"),
                representative_state=("geolocation_state", "first"),
                source_observation_count=("geolocation_zip_code_prefix", "size"),
            )
            .reset_index()
        )
        for name, frame in {
            "dim_customers": dim_customers,
            "dim_products": dim_products,
            "dim_sellers": dim_sellers,
            "dim_geography": dim_geography,
        }.items():
            _write(conn, name, frame)

        item_enriched = (
            order_items.merge(
                orders[
                    [
                        "order_id",
                        "customer_id",
                        "order_status",
                        "order_purchase_timestamp",
                        "purchase_date",
                        "purchase_month",
                    ]
                ],
                on="order_id",
                how="left",
                validate="many_to_one",
            )
            .merge(
                dim_products[["product_id", "product_category_name_english"]],
                on="product_id",
                how="left",
                validate="many_to_one",
            )
            .merge(
                dim_sellers[["seller_id", "seller_state"]],
                on="seller_id",
                how="left",
                validate="many_to_one",
            )
        )
        item_enriched["item_total_value"] = item_enriched["item_price"] + item_enriched["freight_value"]

        item_metrics = (
            order_items.groupby("order_id", as_index=False)
            .agg(
                merchandise_revenue=("item_price", "sum"),
                freight_revenue=("freight_value", "sum"),
                item_count=("order_item_id", "count"),
                distinct_product_count=("product_id", "nunique"),
                distinct_seller_count=("seller_id", "nunique"),
            )
        )
        payment_metrics = payments.groupby("order_id", as_index=False).agg(
            payment_value=("payment_value", "sum"),
            max_payment_installments=("payment_installments", "max"),
        )
        payment_types = (
            payments.groupby("order_id")["payment_type"]
            .agg(lambda values: ", ".join(sorted({str(value) for value in values.dropna()})))
            .rename("payment_types")
            .reset_index()
        )
        payment_metrics = payment_metrics.merge(payment_types, on="order_id", how="left")
        review_metrics = reviews.groupby("order_id", as_index=False).agg(
            average_review_score=("review_score", "mean"),
            review_count=("review_id", "nunique"),
        )

        fct_orders = (
            orders.merge(dim_customers, on="customer_id", how="left", validate="many_to_one")
            .merge(item_metrics, on="order_id", how="left", validate="one_to_one")
            .merge(payment_metrics, on="order_id", how="left", validate="one_to_one")
            .merge(review_metrics, on="order_id", how="left", validate="one_to_one")
        )
        fct_orders["order_total_value"] = fct_orders["merchandise_revenue"] + fct_orders["freight_revenue"]
        fct_orders["delivery_days"] = (
            fct_orders["order_delivered_customer_date"] - fct_orders["order_purchase_timestamp"]
        ).dt.total_seconds().div(86400)
        fct_orders["delivery_delay_days"] = (
            fct_orders["order_delivered_customer_date"] - fct_orders["order_estimated_delivery_date"]
        ).dt.total_seconds().div(86400)
        fct_orders["on_time_delivery_flag"] = pd.NA
        evaluable = (
            fct_orders["order_status"].eq("delivered")
            & fct_orders["order_delivered_customer_date"].notna()
            & fct_orders["order_estimated_delivery_date"].notna()
        )
        fct_orders.loc[evaluable, "on_time_delivery_flag"] = (
            fct_orders.loc[evaluable, "order_delivered_customer_date"]
            <= fct_orders.loc[evaluable, "order_estimated_delivery_date"]
        ).astype(int)

        for name, frame in {
            "fct_order_items": item_enriched,
            "fct_orders": fct_orders,
            "semantic_product_metrics": item_enriched,
            "semantic_order_metrics": fct_orders,
        }.items():
            _write(conn, name, frame)
        conn.commit()

        quality = run_quality_checks(conn)
        report_path = Path("reports/quality_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(quality, indent=2, default=str), encoding="utf-8")

        return {
            "db_path": str(db_path),
            "tables": {
                "fct_orders": int(len(fct_orders)),
                "fct_order_items": int(len(item_enriched)),
                "dim_customers": int(len(dim_customers)),
                "dim_products": int(len(dim_products)),
                "dim_sellers": int(len(dim_sellers)),
                "dim_geography": int(len(dim_geography)),
            },
            "quality": quality,
        }
    finally:
        conn.close()
