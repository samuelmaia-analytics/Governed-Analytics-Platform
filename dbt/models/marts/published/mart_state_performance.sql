select
    order_year,
    order_month,
    customer_state,
    count(distinct order_id) as orders,
    count(distinct customer_unique_id) as customers,
    sum(total_item_value) as revenue_gross,
    avg(total_item_value) as avg_ticket,
    avg(delivery_time_days) as avg_delivery_time_days,
    avg(case when is_delayed then 1 else 0 end) as delay_rate,
    avg(review_score_mean) as avg_review_score
from {{ ref('fct_orders_dashboard') }}
group by 1, 2, 3
