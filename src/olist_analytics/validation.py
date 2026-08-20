from __future__ import annotations

import sqlite3
from typing import Any

import pandas as pd


def _result(name: str, passed: bool, details: str, observed: Any = None, severity: str = "error") -> dict:
    return {"name": name, "passed": bool(passed), "severity": severity, "details": details, "observed": observed}


def _query(conn: sqlite3.Connection, sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn)


def run_quality_checks(conn: sqlite3.Connection) -> dict:
    checks = []

    for table, key in [
        ("fct_orders", "order_id"),
        ("fct_order_items", "order_id || '|' || order_item_id"),
        ("dim_customers", "customer_id"),
        ("dim_products", "product_id"),
        ("dim_sellers", "seller_id"),
    ]:
        counts = _query(conn, f"select count(*) as rows, count({key}) as non_null, count(distinct {key}) as distinct_keys from {table}").iloc[0]
        passed = counts["rows"] == counts["non_null"] == counts["distinct_keys"]
        checks.append(_result(f"unique_{table}_{key}", passed, "No null or duplicate keys", counts.to_dict()))

    for child, parent, key in [
        ("fct_order_items", "fct_orders", "order_id"),
        ("fct_order_items", "dim_products", "product_id"),
        ("fct_order_items", "dim_sellers", "seller_id"),
        ("fct_orders", "dim_customers", "customer_id"),
    ]:
        orphan = _query(
            conn,
            f"select count(*) as orphan_rows from {child} c left join {parent} p on c.{key} = p.{key} where c.{key} is not null and p.{key} is null",
        ).iloc[0]["orphan_rows"]
        checks.append(_result(f"relationship_{child}_{parent}", orphan == 0, "No orphan foreign keys", int(orphan)))

    statuses = _query(conn, "select distinct order_status from fct_orders where order_status is not null")
    allowed = {"delivered", "invoiced", "shipped", "processing", "unavailable", "canceled", "created", "approved"}
    observed_statuses = set(statuses["order_status"].astype(str))
    invalid_statuses = sorted(observed_statuses - allowed)
    checks.append(_result("accepted_order_statuses", not invalid_statuses, "All statuses are in the documented source domain", invalid_statuses))

    negative_values = _query(
        conn,
        "select sum(case when item_price < 0 then 1 else 0 end) as negative_price, sum(case when freight_value < 0 then 1 else 0 end) as negative_freight from fct_order_items",
    ).iloc[0]
    checks.append(_result("non_negative_item_values", negative_values.sum() == 0, "Price and freight values are non-negative", negative_values.to_dict()))

    score_range = _query(
        conn,
        "select sum(case when review_score < 1 or review_score > 5 then 1 else 0 end) as invalid_scores from raw_order_reviews where review_score is not null",
    ).iloc[0]["invalid_scores"]
    checks.append(_result("review_score_range", score_range == 0, "Review scores are between 1 and 5", int(score_range)))

    temporal = _query(
        conn,
        """
        select
          sum(case when order_approved_at < order_purchase_timestamp then 1 else 0 end) as approved_before_purchase,
          sum(case when order_delivered_carrier_date < order_purchase_timestamp then 1 else 0 end) as carrier_before_purchase,
          sum(case when order_delivered_customer_date < order_delivered_carrier_date then 1 else 0 end) as customer_before_carrier
        from fct_orders
        """,
    ).iloc[0]
    checks.append(
        _result(
            "timestamp_ordering",
            temporal.sum() == 0,
            "Source fulfillment timestamp anomalies are surfaced for review",
            temporal.to_dict(),
            severity="warning",
        )
    )

    reconciliation = _query(
        conn,
        """
        select
          (select round(sum(item_price), 2) from fct_order_items) as item_revenue,
          (select round(sum(merchandise_revenue), 2) from fct_orders) as order_revenue
        """,
    ).iloc[0]
    difference = round(float(reconciliation["item_revenue"] - reconciliation["order_revenue"]), 2)
    checks.append(_result("revenue_reconciliation", abs(difference) < 0.01, "Item and order merchandise revenue reconcile", difference))

    return {
        "passed": all(check["passed"] or check["severity"] == "warning" for check in checks),
        "check_count": len(checks),
        "failed_count": sum(not check["passed"] and check["severity"] == "error" for check in checks),
        "warning_count": sum(not check["passed"] and check["severity"] == "warning" for check in checks),
        "checks": checks,
    }
