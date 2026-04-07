select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    count(*) as row_count
from {{ ref('fct_orders_enriched') }}
group by 1, 2, 3, 4
having count(*) > 1
