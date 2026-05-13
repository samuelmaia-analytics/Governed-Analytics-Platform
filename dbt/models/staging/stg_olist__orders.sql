with source as (
    select * from {{ source('olist_raw', 'orders') }}
),

cleaned as (
    select
        order_id,
        customer_id,
        order_status,
        cast(order_purchase_timestamp  as timestamp) as order_purchase_timestamp,
        cast(order_approved_at         as timestamp) as order_approved_at,
        cast(order_delivered_carrier_date   as timestamp) as order_delivered_carrier_date,
        cast(order_delivered_customer_date  as timestamp) as order_delivered_customer_date,
        cast(order_estimated_delivery_date  as timestamp) as order_estimated_delivery_date
    from source
    where order_id    is not null
      and customer_id is not null
    qualify row_number() over (partition by order_id order by order_purchase_timestamp) = 1
)

select * from cleaned
