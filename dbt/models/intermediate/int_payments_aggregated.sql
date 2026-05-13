-- Agrega pagamentos por pedido eliminando a cardinalidade múltipla
-- antes do join com order_items (padrão: many-to-one).
with payments as (
    select * from {{ ref('stg_olist__payments') }}
)

select
    order_id,
    count(payment_sequential)           as payment_count,
    sum(payment_value)                  as total_payment_value,
    max(payment_installments)           as max_payment_installments,
    -- Modo: tipo de pagamento mais frequente no pedido
    mode() within group (order by payment_type) as payment_type_mode
from payments
group by order_id
