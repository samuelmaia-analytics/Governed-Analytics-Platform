with source as (
    select * from {{ source('olist_raw', 'payments') }}
),

cleaned as (
    select
        order_id,
        cast(payment_sequential    as integer) as payment_sequential,
        payment_type,
        cast(payment_installments  as integer) as payment_installments,
        cast(payment_value         as double)  as payment_value
    from source
    where order_id is not null
)

select * from cleaned
