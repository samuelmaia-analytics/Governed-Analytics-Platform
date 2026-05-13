with source as (
    select * from {{ source('olist_raw', 'category_translation') }}
),

cleaned as (
    select
        product_category_name,
        product_category_name_english
    from source
    where product_category_name is not null
    qualify row_number() over (partition by product_category_name order by product_category_name_english) = 1
)

select * from cleaned
