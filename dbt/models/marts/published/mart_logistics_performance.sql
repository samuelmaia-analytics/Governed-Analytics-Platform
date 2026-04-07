select
    order_year,
    order_month,
    customer_state,
    seller_state,
    count(distinct order_id) as orders,
    count(*) as total_items,
    avg(case when is_delayed then 1.0 else 0.0 end) as delayed_rate,
    avg(delivery_time_days) as avg_delivery_time_days,
    avg(seller_dispatch_time_days) as avg_dispatch_time_days,
    avg(carrier_delivery_time_days) as avg_carrier_time_days,
    avg(freight_to_price_ratio) as avg_freight_to_price_ratio
from {{ ref('fct_orders_dashboard') }}
group by 1, 2, 3, 4
