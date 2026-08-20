{{ config(materialized='view') }}

select
    cast(geolocation_zip_code_prefix as string) as geolocation_zip_code_prefix,
    cast(geolocation_lat as double) as geolocation_lat,
    cast(geolocation_lng as double) as geolocation_lng,
    cast(geolocation_city as string) as geolocation_city,
    cast(geolocation_state as string) as geolocation_state
from {{ source('olist_raw', 'geolocation') }}
