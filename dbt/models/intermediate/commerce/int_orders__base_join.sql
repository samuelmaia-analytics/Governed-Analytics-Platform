select
    items.order_id,
    items.order_item_id,
    orders.customer_id,
    customers.customer_unique_id,
    items.product_id,
    items.seller_id,
    orders.order_status,
    orders.order_purchase_timestamp,
    orders.order_approved_at,
    items.shipping_limit_date,
    orders.order_delivered_carrier_date,
    orders.order_delivered_customer_date,
    orders.order_estimated_delivery_date,
    items.price,
    items.freight_value,
    payments.payment_count,
    payments.total_payment_value,
    payments.max_payment_installments,
    payments.payment_type_mode,
    reviews.review_count,
    reviews.review_score_mean,
    reviews.latest_review_creation_date,
    reviews.latest_review_answer_timestamp,
    products.product_category_name,
    translation.product_category_name_english,
    customers.customer_state,
    sellers.seller_state
from {{ ref('stg_olist__order_items') }} as items
left join {{ ref('stg_olist__orders') }} as orders using (order_id)
left join {{ ref('stg_olist__customers') }} as customers using (customer_id)
left join {{ ref('stg_olist__products') }} as products using (product_id)
left join {{ ref('stg_olist__sellers') }} as sellers using (seller_id)
left join {{ ref('int_orders__payments_agg') }} as payments using (order_id)
left join {{ ref('int_orders__reviews_agg') }} as reviews using (order_id)
left join {{ ref('stg_olist__translation') }} as translation using (product_category_name)
