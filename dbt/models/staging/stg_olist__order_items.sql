with source as (
    select * from {{ source('olist_raw', 'order_items') }}
),

cleaned as (
    select
        order_id,
        cast(order_item_id as integer)  as order_item_id,
        product_id,
        seller_id,
        cast(shipping_limit_date as timestamp) as shipping_limit_date,
        cast(price         as double) as price,
        cast(freight_value as double) as freight_value
    from source
    where order_id   is not null
      and product_id is not null
      and seller_id  is not null
      and cast(price         as double) >= 0
      and cast(freight_value as double) >= 0
    qualify row_number() over (
        partition by order_id, order_item_id, product_id, seller_id
        order by shipping_limit_date
    ) = 1
)

select * from cleaned
