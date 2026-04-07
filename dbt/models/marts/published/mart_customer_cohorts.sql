select
    purchase_cohort_month,
    cohort_order_month_number,
    count(distinct customer_unique_id) as customers,
    count(distinct order_id) as orders,
    count(*) as items,
    sum(total_item_value) as revenue_gross,
    avg(total_item_value) as avg_ticket,
    avg(case when is_delayed then 1.0 else 0.0 end) as delay_rate
from {{ ref('fct_orders_dashboard') }}
group by 1, 2
