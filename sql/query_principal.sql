-- query_principal.sql
-- Base SQL consolidada para sustentar os principais indicadores e analises
-- do dashboard final do case Olist.
--
-- Fonte:
--   fact_orders_enriched
--
-- Uso recomendado:
-- Executar os blocos de forma independente para validacao dos resultados,
-- evidencias do case e rastreabilidade dos KPIs.

-- =========================================================
-- 1. KPIs EXECUTIVOS
-- Receita Total
-- Total de Pedidos
-- Ticket Medio
-- Review Medio
-- % Pedidos em Atraso
-- =========================================================
WITH base AS (
    SELECT
        order_id,
        total_item_value,
        review_score_mean,
        is_delayed
    FROM fact_orders_enriched
)
SELECT
    ROUND(SUM(total_item_value), 2) AS receita_total,
    COUNT(DISTINCT order_id) AS total_pedidos,
    ROUND(SUM(total_item_value) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS ticket_medio,
    ROUND(AVG(review_score_mean), 2) AS review_medio,
    ROUND(AVG(CASE WHEN is_delayed THEN 1 ELSE 0 END) * 100, 2) AS percentual_pedidos_em_atraso
FROM base;


-- =========================================================
-- 2. EVOLUCAO DA RECEITA NO TEMPO
-- =========================================================
WITH base AS (
    SELECT
        CAST(order_date AS DATE) AS order_date,
        order_id,
        total_item_value
    FROM fact_orders_enriched
    WHERE order_date IS NOT NULL
)
SELECT
    DATE_TRUNC('month', order_date) AS mes_referencia,
    COUNT(DISTINCT order_id) AS total_pedidos,
    ROUND(SUM(total_item_value), 2) AS receita_total,
    ROUND(AVG(total_item_value), 2) AS receita_media_por_item
FROM base
GROUP BY 1
ORDER BY 1;


-- =========================================================
-- 3. TOP 10 CATEGORIAS POR RECEITA
-- =========================================================
WITH base AS (
    SELECT
        COALESCE(product_category_name_english, product_category_name, 'unknown') AS categoria,
        order_id,
        total_item_value,
        freight_value,
        is_delayed
    FROM fact_orders_enriched
)
SELECT
    categoria,
    COUNT(DISTINCT order_id) AS total_pedidos,
    ROUND(SUM(total_item_value), 2) AS receita_total,
    ROUND(AVG(total_item_value), 2) AS ticket_medio_item,
    ROUND(AVG(freight_value), 2) AS frete_medio,
    ROUND(AVG(CASE WHEN is_delayed THEN 1 ELSE 0 END) * 100, 2) AS percentual_atraso
FROM base
GROUP BY 1
ORDER BY receita_total DESC, total_pedidos DESC
LIMIT 10;


-- =========================================================
-- 4. DISTRIBUICAO DOS PEDIDOS POR STATUS
-- =========================================================
WITH base AS (
    SELECT
        order_status,
        order_id,
        total_item_value
    FROM fact_orders_enriched
)
SELECT
    order_status,
    COUNT(DISTINCT order_id) AS total_pedidos,
    ROUND(SUM(total_item_value), 2) AS receita_total,
    ROUND(AVG(total_item_value), 2) AS ticket_medio_item
FROM base
GROUP BY 1
ORDER BY receita_total DESC, total_pedidos DESC;


-- =========================================================
-- 5. ESTADOS COM MAIOR PERCENTUAL DE ATRASO
-- =========================================================
WITH base AS (
    SELECT
        customer_state,
        order_id,
        total_item_value,
        is_delayed
    FROM fact_orders_enriched
    WHERE customer_state IS NOT NULL
)
SELECT
    customer_state,
    COUNT(DISTINCT order_id) AS total_pedidos,
    ROUND(SUM(total_item_value), 2) AS receita_total,
    ROUND(AVG(total_item_value), 2) AS ticket_medio_item,
    ROUND(AVG(CASE WHEN is_delayed THEN 1 ELSE 0 END) * 100, 2) AS percentual_atraso
FROM base
GROUP BY 1
ORDER BY percentual_atraso DESC, total_pedidos DESC;


-- =========================================================
-- 6. TOP 10 CATEGORIAS POR FRETE MEDIO
-- =========================================================
WITH base AS (
    SELECT
        COALESCE(product_category_name_english, product_category_name, 'unknown') AS categoria,
        order_id,
        freight_value,
        total_item_value
    FROM fact_orders_enriched
)
SELECT
    categoria,
    COUNT(DISTINCT order_id) AS total_pedidos,
    ROUND(AVG(freight_value), 2) AS frete_medio,
    ROUND(SUM(total_item_value), 2) AS receita_total
FROM base
GROUP BY 1
HAVING COUNT(DISTINCT order_id) >= 30
ORDER BY frete_medio DESC, receita_total DESC
LIMIT 10;


-- =========================================================
-- 7. DETALHAMENTO POR CATEGORIA
-- =========================================================
WITH base AS (
    SELECT
        COALESCE(product_category_name_english, product_category_name, 'unknown') AS categoria,
        order_id,
        total_item_value,
        freight_value,
        review_score_mean,
        delivery_time_days,
        estimated_delay_days,
        is_delayed
    FROM fact_orders_enriched
)
SELECT
    categoria,
    COUNT(DISTINCT order_id) AS total_pedidos,
    ROUND(SUM(total_item_value), 2) AS receita_total,
    ROUND(AVG(total_item_value), 2) AS ticket_medio_item,
    ROUND(AVG(freight_value), 2) AS frete_medio,
    ROUND(AVG(review_score_mean), 2) AS review_medio,
    ROUND(AVG(delivery_time_days), 2) AS prazo_medio_entrega_dias,
    ROUND(AVG(estimated_delay_days), 2) AS atraso_estimado_medio_dias,
    ROUND(AVG(CASE WHEN is_delayed THEN 1 ELSE 0 END) * 100, 2) AS percentual_atraso
FROM base
GROUP BY 1
ORDER BY receita_total DESC, total_pedidos DESC;
