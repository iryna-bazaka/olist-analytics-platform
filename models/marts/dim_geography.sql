{{ config(materialized='table') }}

select
    geolocation_zip_code_prefix,
    avg(geolocation_lat) as latitude,
    avg(geolocation_lng) as longitude,
    min(geolocation_city) as representative_city,
    min(geolocation_state) as representative_state,
    count(*) as source_observation_count
from {{ ref('stg_geolocation') }}
group by geolocation_zip_code_prefix
