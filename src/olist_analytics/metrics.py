from __future__ import annotations

import sqlite3

import pandas as pd


def query(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn, params=params)


def kpis(conn: sqlite3.Connection) -> dict:
    order = query(
        conn,
        """
        select
          round(sum(merchandise_revenue), 2) as merchandise_revenue,
          round(sum(freight_revenue), 2) as freight_revenue,
          count(distinct order_id) as orders,
          count(distinct customer_unique_id) as customers,
          round(avg(average_review_score), 2) as average_review_score,
          round(avg(on_time_delivery_flag), 4) as on_time_delivery_rate
        from semantic_order_metrics
        """,
    ).iloc[0].to_dict()
    order["average_order_value"] = round(order["merchandise_revenue"] / order["orders"], 2) if order["orders"] else None
    return order


def monthly_sales(conn: sqlite3.Connection) -> pd.DataFrame:
    return query(
        conn,
        """
        select purchase_month,
               round(sum(item_price), 2) as merchandise_revenue,
               count(distinct order_id) as orders
        from semantic_product_metrics
        group by purchase_month
        order by purchase_month
        """,
    )


def top_categories(conn: sqlite3.Connection, limit: int = 10) -> pd.DataFrame:
    return query(
        conn,
        """
        select product_category_name_english as category,
               round(sum(item_price), 2) as merchandise_revenue,
               count(distinct order_id) as orders
        from semantic_product_metrics
        group by product_category_name_english
        order by merchandise_revenue desc
        limit ?
        """,
        (limit,),
    )


def state_performance(conn: sqlite3.Connection) -> pd.DataFrame:
    return query(
        conn,
        """
        select customer_state as state,
               round(sum(merchandise_revenue), 2) as merchandise_revenue,
               count(distinct order_id) as orders,
               round(avg(on_time_delivery_flag), 4) as on_time_delivery_rate,
               round(avg(average_review_score), 2) as average_review_score
        from semantic_order_metrics
        group by customer_state
        order by merchandise_revenue desc
        """,
    )


def delivery_distribution(conn: sqlite3.Connection) -> pd.DataFrame:
    return query(
        conn,
        """
        select
          case
            when delivery_delay_days <= -15 then '15+ days early'
            when delivery_delay_days <= -1 then '1-14 days early'
            when delivery_delay_days <= 0 then 'On estimated date'
            when delivery_delay_days <= 7 then '1-7 days late'
            else '8+ days late'
          end as delivery_bucket,
          count(*) as orders
        from semantic_order_metrics
        where order_status = 'delivered' and delivery_delay_days is not null
        group by 1
        order by orders desc
        """,
    )
