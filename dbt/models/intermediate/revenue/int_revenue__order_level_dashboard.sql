with ranked_orders as (
    select
        *,
        row_number() over (
            partition by order_id
            order by order_purchase_timestamp desc, order_item_id desc
        ) as order_row_num
    from {{ ref('stg_platform__fact_orders_dashboard') }}
)

select
    order_id,
    customer_unique_id,
    order_status,
    order_purchase_timestamp,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    order_date,
    order_year,
    order_month,
    purchase_cohort_month,
    cohort_order_month_number,
    customer_order_sequence,
    is_first_order,
    seller_key,
    seller_volume_tier,
    seller_order_count,
    seller_avg_delivery_days,
    seller_delay_rate,
    delivery_time_days,
    seller_dispatch_time_days,
    carrier_delivery_time_days,
    estimated_delay_days,
    is_delayed,
    freight_value,
    review_score_mean
from ranked_orders
where order_row_num = 1
