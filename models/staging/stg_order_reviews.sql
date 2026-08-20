{{ config(materialized='view') }}

select
    cast(review_id as string) as review_id,
    cast(order_id as string) as order_id,
    cast(review_score as int) as review_score,
    cast(review_comment_title as string) as review_comment_title,
    cast(review_comment_message as string) as review_comment_message,
    to_timestamp(review_creation_date) as review_creation_timestamp,
    to_timestamp(review_answer_timestamp) as review_answer_timestamp
from {{ source('olist_raw', 'order_reviews') }}
