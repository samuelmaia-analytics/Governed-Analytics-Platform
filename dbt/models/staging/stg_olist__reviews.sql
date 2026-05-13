with source as (
    select * from {{ source('olist_raw', 'reviews') }}
),

cleaned as (
    select
        review_id,
        order_id,
        cast(review_score as integer)           as review_score,
        review_comment_message,
        cast(review_creation_date  as timestamp) as review_creation_date,
        cast(review_answer_timestamp as timestamp) as review_answer_timestamp
    from source
    where order_id is not null
    qualify row_number() over (partition by review_id order by review_creation_date) = 1
)

select * from cleaned
