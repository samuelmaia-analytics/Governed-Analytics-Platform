select
    order_year,
    order_month,
    customer_state,
    count(*) as row_count
from {{ ref('mart_state_performance') }}
group by 1, 2, 3
having count(*) > 1
