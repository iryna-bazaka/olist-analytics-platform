# Portfolio story

## The short version

“I built a dbt-style analytics platform for the Olist marketplace dataset. I started by documenting the grain of each source, then created staging models, gold facts and dimensions, and a semantic metric contract. I separated the order and item facts because otherwise revenue and experience metrics are easy to double count. I added data-quality checks for keys, relationships, valid statuses, numeric ranges, timestamps, and financial reconciliation. The final star schema is designed for Power BI and can run on Databricks SQL, while a local SQLite preview makes the work easy to review.”

## Five-minute demo flow

1. Open the dashboard and show monthly revenue, orders, AOV, and on-time rate.
2. Show the semantic model file and explain why `fct_orders` and `fct_order_items` are separate.
3. Open the dbt schema tests and one quality result.
4. Open `powerbi/measures.dax` and explain how the same metric definitions reach business users.
5. Open `databricks/olist_medallion.sql` and explain the bronze/silver/gold deployment path.

## Resume-ready project bullet

Built a dbt-style SQL analytics platform on the Olist e-commerce dataset, modeling order- and item-grain facts, customer/product/seller dimensions, and a reusable semantic metric catalog; added data-quality checks for key integrity, relationships, timestamp logic, and revenue reconciliation, with a Power BI-ready star schema and Databricks deployment path.

## Developer advocacy angle

This repository should be presented as an educational reference implementation, not only an analysis:

- every model has a documented grain;
- metric definitions are centralized;
- quality checks explain why a result is trustworthy;
- the README guides another developer from source files to dashboard;
- the same story can be delivered as a workshop or technical talk.
