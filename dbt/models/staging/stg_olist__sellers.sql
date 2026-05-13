with source as (
    select * from {{ source('olist_raw', 'sellers') }}
),

cleaned as (
    select
        seller_id,
        seller_zip_code_prefix,
        seller_city,
        seller_state
    from source
    where seller_id is not null
    qualify row_number() over (partition by seller_id order by seller_state) = 1
)

select * from cleaned
