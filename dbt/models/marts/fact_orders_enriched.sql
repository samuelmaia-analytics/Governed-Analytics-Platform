-- Tabela analítica principal com granularidade por item de pedido.
-- Equivalente à camada curated gerada por src/build_analytics.py.
-- Mantém colunas sensíveis (customer_id, seller_id, geolocalização detalhada)
-- para uso interno — não publicar diretamente para consumo externo.
with order_items as (
    select * from {{ ref('stg_olist__order_items') }}
),

orders as (
    select * from {{ ref('stg_olist__orders') }}
),

customers as (
    select * from {{ ref('stg_olist__customers') }}
),

products as (
    select * from {{ ref('stg_olist__products') }}
),

sellers as (
    select * from {{ ref('stg_olist__sellers') }}
),

payments as (
    select * from {{ ref('int_payments_aggregated') }}
),

reviews as (
    select * from {{ ref('int_reviews_aggregated') }}
),

category_translation as (
    select * from {{ ref('stg_olist__category_translation') }}
),

seller_metrics as (
    select * from {{ ref('int_seller_metrics') }}
),

cohort as (
    select * from {{ ref('int_customer_cohort') }}
),

joined as (
    select
        -- Chaves
        oi.order_id,
        oi.order_item_id,
        o.customer_id,
        c.customer_unique_id,
        oi.product_id,
        oi.seller_id,

        -- Status e timestamps do pedido
        o.order_status,
        o.order_purchase_timestamp,
        o.order_approved_at,
        oi.shipping_limit_date,
        o.order_delivered_carrier_date,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,

        -- Derivações temporais
        cast(o.order_purchase_timestamp as date) as order_date,
        year(o.order_purchase_timestamp)          as order_year,
        month(o.order_purchase_timestamp)         as order_month,
        strftime(o.order_purchase_timestamp, '%Y-%m') as purchase_cohort_month,

        -- Cohort e recorrência
        co.customer_first_purchase_timestamp,
        co.cohort_order_month_number,
        co.customer_order_sequence,
        co.is_first_order,

        -- Logística
        datediff('day', o.order_purchase_timestamp, o.order_delivered_customer_date)
            as delivery_time_days,
        datediff('day', o.order_approved_at, o.order_delivered_carrier_date)
            as seller_dispatch_time_days,
        datediff('day', o.order_delivered_carrier_date, o.order_delivered_customer_date)
            as carrier_delivery_time_days,
        datediff('day', o.order_estimated_delivery_date, o.order_delivered_customer_date)
            as estimated_delay_days,
        case
            when o.order_delivered_customer_date is not null
             and o.order_estimated_delivery_date is not null
             and o.order_delivered_customer_date > o.order_estimated_delivery_date
            then true else false
        end as is_delayed,

        -- Financeiro
        oi.price,
        oi.freight_value,
        case when oi.price > 0
            then oi.freight_value / oi.price
            else null
        end as freight_to_price_ratio,
        oi.price + oi.freight_value as total_item_value,

        -- Pagamentos (agregados ao nível do pedido)
        pay.payment_count,
        pay.total_payment_value,
        pay.max_payment_installments,
        pay.payment_type_mode,

        -- Avaliações (agregadas ao nível do pedido)
        rev.review_count,
        rev.review_score_mean,
        rev.review_score_max,
        rev.review_score_min,
        rev.has_review_comment,
        rev.latest_review_creation_date,
        rev.latest_review_answer_timestamp,

        -- Produto e categoria
        p.product_category_name,
        ct.product_category_name_english,
        p.product_name_lenght,
        p.product_description_lenght,
        p.product_photos_qty,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm,

        -- Cliente (sensível — uso interno)
        c.customer_zip_code_prefix,
        c.customer_city,
        c.customer_state,

        -- Seller (sensível — uso interno)
        s.seller_zip_code_prefix,
        s.seller_city,
        s.seller_state,
        sm.seller_order_count,
        sm.seller_avg_delivery_days,
        sm.seller_delay_rate,
        sm.seller_volume_tier

    from order_items oi
    left join orders           o  using (order_id)
    left join customers        c  using (customer_id)
    left join products         p  using (product_id)
    left join sellers          s  using (seller_id)
    left join payments         pay using (order_id)
    left join reviews          rev using (order_id)
    left join category_translation ct using (product_category_name)
    left join seller_metrics   sm using (seller_id)
    left join cohort            co using (order_id)
),

filtered as (
    select *
    from joined
    where order_purchase_timestamp is not null
      and price          >= 0
      and freight_value  >= 0
      and (delivery_time_days is null or delivery_time_days >= 0)
)

select * from filtered
