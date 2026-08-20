from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from olist_analytics.metrics import delivery_distribution, kpis, monthly_sales, state_performance, top_categories


DB_PATH = os.getenv("OLIST_DB_PATH", str(ROOT / "data" / "warehouse" / "olist.sqlite"))


def money(value: float | None) -> str:
    return "-" if value is None else f"R$ {float(value):,.0f}"


def main() -> None:
    st.set_page_config(page_title="Olist Analytics Platform", page_icon="📊", layout="wide")
    st.title("Olist Analytics Platform")
    st.caption("SQL-first semantic analytics for commerce performance and customer experience")

    if not Path(DB_PATH).exists():
        st.error("Warehouse not found. Run: python scripts/run_pipeline.py --raw-dir /path/to/olist_csvs")
        st.stop()

    conn = sqlite3.connect(DB_PATH)
    try:
        kpi = kpis(conn)
        monthly = monthly_sales(conn)
        categories = top_categories(conn)
        states = state_performance(conn)
        delivery = delivery_distribution(conn)
    finally:
        conn.close()

    columns = st.columns(6)
    columns[0].metric("Merchandise revenue", money(kpi["merchandise_revenue"]))
    columns[1].metric("Orders", f"{int(kpi['orders']):,}")
    columns[2].metric("Customers", f"{int(kpi['customers']):,}")
    columns[3].metric("Average order value", money(kpi["average_order_value"]))
    columns[4].metric("On-time delivery", f"{float(kpi['on_time_delivery_rate']) * 100:.1f}%")
    columns[5].metric("Average review", f"{float(kpi['average_review_score']):.2f} / 5")

    left, right = st.columns(2)
    with left:
        st.subheader("Monthly merchandise revenue")
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(monthly["purchase_month"], monthly["merchandise_revenue"], color="#1d6f8c", marker="o")
        ax.tick_params(axis="x", rotation=45)
        ax.set_ylabel("BRL")
        ax.grid(axis="y", alpha=0.25)
        st.pyplot(fig, clear_figure=True)
    with right:
        st.subheader("Top categories")
        fig, ax = plt.subplots(figsize=(9, 4))
        view = categories.sort_values("merchandise_revenue")
        ax.barh(view["category"], view["merchandise_revenue"], color="#e28d4f")
        ax.set_xlabel("BRL")
        ax.grid(axis="x", alpha=0.25)
        st.pyplot(fig, clear_figure=True)

    st.subheader("Customer-state performance")
    st.dataframe(states.style.format({"merchandise_revenue": "R$ {:,.0f}", "on_time_delivery_rate": "{:.1%}", "average_review_score": "{:.2f}"}), use_container_width=True)
    st.subheader("Delivery outcome")
    st.dataframe(delivery, use_container_width=True)


if __name__ == "__main__":
    main()
