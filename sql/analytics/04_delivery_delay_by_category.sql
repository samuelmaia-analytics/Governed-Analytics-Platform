SELECT
    COALESCE(product_category_name_english, product_category_name, 'unknown') AS category,
    COUNT(*) AS total_items,
    ROUND(AVG(delivery_time_days), 2) AS avg_delivery_time_days,
    ROUND(AVG(estimated_delay_days), 2) AS avg_estimated_delay_days,
    ROUND(AVG(CASE WHEN is_delayed THEN 1 ELSE 0 END) * 100, 2) AS delayed_items_pct,
    ROUND(SUM(CASE WHEN is_delayed THEN total_item_value ELSE 0 END), 2) AS delayed_revenue
FROM fact_orders_enriched
GROUP BY 1
HAVING COUNT(*) >= 100
ORDER BY delayed_items_pct DESC, avg_estimated_delay_days DESC, total_items DESC;
