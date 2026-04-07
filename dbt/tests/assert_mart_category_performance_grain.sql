select
    order_year,
    order_month,
    product_category_name_english,
    payment_type_mode,
    count(*) as row_count
from {{ ref('mart_category_performance') }}
group by 1, 2, 3, 4
having count(*) > 1
