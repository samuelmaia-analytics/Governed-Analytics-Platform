SELECT
    COALESCE(product_category_name_english, product_category_name, 'unknown') AS category,
    COUNT(*) AS total_items,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(total_item_value), 2) AS total_revenue,
    ROUND(AVG(total_item_value), 2) AS avg_item_value,
    ROUND(AVG(CASE WHEN is_delayed THEN 1 ELSE 0 END) * 100, 2) AS delayed_items_pct
FROM fact_orders_enriched
GROUP BY 1
ORDER BY total_revenue DESC, total_orders DESC
LIMIT 20;
