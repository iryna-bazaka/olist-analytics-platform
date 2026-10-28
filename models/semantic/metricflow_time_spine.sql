{{ config(materialized='table') }}
-- One row per day; required by the dbt Semantic Layer to aggregate metrics over time.
select cast(d as date) as date_day
from (
    {{ dbt.date_spine(datepart="day", start_date="cast('2016-01-01' as date)", end_date="cast('2019-01-01' as date)") }}
) as spine(d)
