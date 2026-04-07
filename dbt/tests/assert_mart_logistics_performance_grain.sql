select
    order_year,
    order_month,
    customer_state,
    seller_state,
    count(*) as row_count
from {{ ref('mart_logistics_performance') }}
group by 1, 2, 3, 4
having count(*) > 1
