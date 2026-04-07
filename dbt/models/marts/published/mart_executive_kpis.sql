with order_level as (
    select *
    from {{ ref('int_revenue__order_level_dashboard') }}
),
delivered as (
    select *
    from order_level
    where order_delivered_customer_date is not null
)
select 'revenue_gross' as metric_id, 'Receita Total' as metric_label, 'commercial' as metric_group, sum(total_item_value) as metric_value, 'currency' as metric_unit
from {{ ref('fct_orders_dashboard') }}
union all
select 'orders', 'Total de Pedidos', 'commercial', count(distinct order_id), 'count'
from order_level
union all
select 'customers', 'Total de Clientes', 'commercial', count(distinct customer_unique_id), 'count'
from order_level
union all
select 'avg_ticket', 'Ticket Médio', 'commercial', sum(total_item_value) / nullif(count(distinct order_id), 0), 'currency'
from {{ ref('fct_orders_dashboard') }}
union all
select 'avg_delivery_time_days', 'Prazo Médio', 'operations', avg(delivery_time_days), 'days'
from delivered
union all
select 'delay_rate', 'Taxa de Atraso', 'operations', avg(case when is_delayed then 1.0 else 0.0 end), 'ratio'
from delivered
union all
select 'avg_review_score', 'Nota Média', 'experience', avg(review_score_mean), 'score'
from order_level
union all
select 'avg_freight_per_item', 'Frete Médio por Item', 'operations', avg(freight_value), 'currency'
from {{ ref('fct_orders_dashboard') }}
