select
    order_id,
    order_item_id,
    seller_key,
    count(*) as row_count
from {{ ref('fct_orders_dashboard') }}
group by 1, 2, 3
having count(*) > 1
