select
    *,
    cast(order_purchase_timestamp as date) as order_date,
    extract(year from order_purchase_timestamp) as order_year,
    extract(month from order_purchase_timestamp) as order_month,
    strftime(order_purchase_timestamp, '%Y-%m') as purchase_cohort_month,
    price + freight_value as total_item_value,
    datediff('day', order_purchase_timestamp, order_delivered_customer_date) as delivery_time_days,
    datediff('day', order_estimated_delivery_date, order_delivered_customer_date) as estimated_delay_days,
    case
        when order_delivered_customer_date is not null
         and order_estimated_delivery_date is not null
         and order_delivered_customer_date > order_estimated_delivery_date
        then true else false
    end as is_delayed
from {{ ref('int_orders__base_join') }}
