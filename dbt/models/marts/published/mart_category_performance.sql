select
    order_year,
    order_month,
    coalesce(product_category_name_english, product_category_name, 'unknown_category') as product_category_name_english,
    payment_type_mode,
    count(distinct order_id) as orders,
    count(*) as items,
    sum(total_item_value) as revenue_gross,
    avg(total_item_value) as avg_ticket,
    avg(review_score_mean) as avg_review_score,
    avg(case when is_delayed then 1.0 else 0.0 end) as delay_rate,
    avg(freight_to_price_ratio) as avg_freight_to_price_ratio
from {{ ref('fct_orders_dashboard') }}
group by 1, 2, 3, 4
