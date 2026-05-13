with source as (
    select * from {{ source('olist_raw', 'customers') }}
),

cleaned as (
    select
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state
    from source
    where customer_id is not null
    qualify row_number() over (partition by customer_id order by customer_unique_id) = 1
)

select * from cleaned
