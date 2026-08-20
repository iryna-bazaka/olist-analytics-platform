{{ config(materialized='view') }}

select
    cast(product_category_name as string) as product_category_name,
    cast(product_category_name_english as string) as product_category_name_english
from {{ source('olist_raw', 'category_translation') }}
