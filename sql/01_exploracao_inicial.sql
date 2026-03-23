SELECT
    order_status,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(*) AS total_items,
    ROUND(SUM(total_item_value), 2) AS total_revenue,
    ROUND(AVG(total_item_value), 2) AS avg_item_value
FROM fact_orders_enriched
GROUP BY 1
ORDER BY total_revenue DESC, total_orders DESC;
