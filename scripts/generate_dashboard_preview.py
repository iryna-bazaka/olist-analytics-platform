from __future__ import annotations

import argparse
import html
import json
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from olist_analytics.metrics import delivery_distribution, kpis, monthly_sales, state_performance, top_categories


def money(value) -> str:
    if value is None:
        return "-"
    return f"R$ {float(value):,.0f}"


def pct(value) -> str:
    if value is None:
        return "-"
    return f"{float(value) * 100:.1f}%"


def bar_rows(frame, label_col, value_col, format_value=money, limit=10):
    rows = []
    frame = frame.head(limit)
    maximum = max(frame[value_col].max(), 1) if len(frame) else 1
    for _, row in frame.iterrows():
        label = html.escape(str(row[label_col]))
        value = float(row[value_col])
        width = max(2, round(value / maximum * 100))
        rows.append(
            f'<div class="bar-row"><div class="bar-label">{label}</div><div class="bar-track"><div class="bar-fill" style="width:{width}%"></div></div><div class="bar-value">{format_value(value)}</div></div>'
        )
    return "\n".join(rows)


def table_html(frame, columns, headers):
    head = "".join(f"<th>{html.escape(header)}</th>" for header in headers)
    body = []
    for _, row in frame.iterrows():
        cells = []
        for column in columns:
            value = row[column]
            if column.endswith("rate"):
                display = pct(value)
            elif column.endswith("revenue"):
                display = money(value)
            else:
                display = f"{value:,.0f}" if isinstance(value, (int, float)) else str(value)
            cells.append(f"<td>{html.escape(display)}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def render(db_path: str | Path, output: str | Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        kpi = kpis(conn)
        monthly = monthly_sales(conn)
        categories = top_categories(conn)
        states = state_performance(conn).head(8)
        delivery = delivery_distribution(conn)
    finally:
        conn.close()

    snapshot = {
        "kpis": kpi,
        "monthly_sales": monthly.to_dict(orient="records"),
        "top_categories": categories.to_dict(orient="records"),
        "state_performance": states.to_dict(orient="records"),
        "delivery_distribution": delivery.to_dict(orient="records"),
    }
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "metric_snapshot.json").write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")
    (reports / "metric_snapshot.md").write_text(
        "# Local metric snapshot\n\nGenerated from the attached Olist CSVs by the local preview adapter.\n\n"
        + "\n".join(f"- **{key}:** {value}" for key, value in kpi.items()),
        encoding="utf-8",
    )

    cards = [
        ("Merchandise revenue", money(kpi.get("merchandise_revenue"))),
        ("Orders", f"{int(kpi.get('orders', 0)):,}"),
        ("Customers", f"{int(kpi.get('customers', 0)):,}"),
        ("Average order value", money(kpi.get("average_order_value"))),
        ("On-time delivery", pct(kpi.get("on_time_delivery_rate"))),
        ("Average review", f"{float(kpi.get('average_review_score', 0)):.2f} / 5"),
    ]
    card_html = "".join(f'<div class="card"><div class="label">{label}</div><div class="value">{value}</div></div>' for label, value in cards)
    category_html = bar_rows(categories, "category", "merchandise_revenue")
    state_html = table_html(states, ["state", "merchandise_revenue", "orders", "on_time_delivery_rate"], ["State", "Revenue", "Orders", "On-time"])
    delivery_html = table_html(delivery, ["delivery_bucket", "orders"], ["Delivery bucket", "Orders"])
    month_labels = ",".join(json.dumps(str(value)) for value in monthly["purchase_month"].tolist())
    month_values = ",".join(str(round(float(value), 2)) for value in monthly["merchandise_revenue"].tolist())

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Olist Analytics Platform</title>
<style>
:root {{ --ink:#14212b; --muted:#687782; --line:#d8e1e7; --surface:#f6f8fa; --accent:#1d6f8c; --accent2:#e28d4f; }}
* {{ box-sizing:border-box; }} body {{ margin:0; font-family:Inter,Arial,sans-serif; color:var(--ink); background:white; }}
.wrap {{ max-width:1180px; margin:0 auto; padding:40px 24px 64px; }}
.eyebrow {{ color:var(--accent); font-weight:700; letter-spacing:.12em; text-transform:uppercase; font-size:12px; }}
h1 {{ font-size:38px; line-height:1.08; margin:10px 0 10px; }} h2 {{ font-size:20px; margin:34px 0 12px; }}
.sub {{ color:var(--muted); max-width:760px; line-height:1.55; }} .cards {{ display:grid; grid-template-columns:repeat(6,1fr); gap:12px; margin:28px 0; }}
.card {{ background:var(--surface); border:1px solid var(--line); padding:18px; min-height:96px; }} .label {{ color:var(--muted); font-size:12px; }} .value {{ font-size:22px; font-weight:750; margin-top:9px; }}
.grid {{ display:grid; grid-template-columns:1.25fr 1fr; gap:22px; }} .panel {{ border-top:3px solid var(--accent); padding-top:12px; }}
.bar-row {{ display:grid; grid-template-columns:190px 1fr 100px; gap:10px; align-items:center; margin:10px 0; font-size:13px; }} .bar-label {{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }} .bar-track {{ height:10px; background:#e9eff2; }} .bar-fill {{ height:100%; background:var(--accent2); }} .bar-value {{ text-align:right; color:var(--muted); }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }} th,td {{ padding:10px 8px; border-bottom:1px solid var(--line); text-align:left; }} th {{ color:var(--muted); font-weight:600; }}
.footer {{ margin-top:40px; color:var(--muted); font-size:12px; }}
@media(max-width:900px) {{ .cards {{ grid-template-columns:repeat(3,1fr); }} .grid {{ grid-template-columns:1fr; }} }}
@media(max-width:560px) {{ .cards {{ grid-template-columns:repeat(2,1fr); }} .bar-row {{ grid-template-columns:120px 1fr 80px; }} }}
</style></head><body><main class="wrap">
<div class="eyebrow">Olist Analytics Platform</div><h1>Commerce performance, fulfillment reliability, and customer experience</h1>
<p class="sub">A semantic, dbt-style analytics layer built for Databricks and Power BI, with a local preview adapter for reproducible review.</p>
<section class="cards">{card_html}</section>
<section class="grid"><div class="panel"><h2>Top categories by merchandise revenue</h2>{category_html}</div>
<div class="panel"><h2>Delivery outcome</h2>{delivery_html}</div></section>
<section class="panel"><h2>Customer-state performance</h2>{state_html}</section>
<div class="footer">Source: Olist Brazilian E-Commerce Public Dataset. Metrics are defined in models/semantic/metrics.yml. Local preview generated from the attached CSV files.</div>
</main></body></html>"""
    Path(output).write_text(page, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", default=str(ROOT / "data" / "warehouse" / "olist.sqlite"))
    parser.add_argument("--output", default=str(ROOT / "reports" / "dashboard.html"))
    args = parser.parse_args()
    render(args.db_path, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
