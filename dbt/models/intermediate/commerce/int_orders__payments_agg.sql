select
    order_id,
    count(*) as payment_count,
    sum(payment_value) as total_payment_value,
    max(payment_installments) as max_payment_installments,
    any_value(payment_type) as payment_type_mode
from {{ ref('stg_olist__payments') }}
group by 1
