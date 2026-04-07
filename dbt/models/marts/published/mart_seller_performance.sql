select
    seller_key,
    seller_state,
    seller_volume_tier,
    max(seller_order_count) as seller_order_count,
    count(distinct order_id) as orders,
    count(*) as total_items,
    sum(total_item_value) as revenue_gross,
    avg(total_item_value) as avg_ticket,
    max(seller_avg_delivery_days) as avg_delivery_time_days,
    max(seller_delay_rate) as delay_rate,
    avg(review_score_mean) as avg_review_score
from {{ ref('fct_orders_dashboard') }}
group by 1, 2, 3
