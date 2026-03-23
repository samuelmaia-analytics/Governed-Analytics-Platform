SELECT
    MAKE_DATE(order_year, order_month, 1) AS order_month_date,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(total_item_value), 2) AS total_revenue,
    ROUND(AVG(delivery_time_days), 2) AS avg_delivery_time_days,
    ROUND(AVG(CASE WHEN is_delayed THEN 1 ELSE 0 END) * 100, 2) AS delayed_items_pct
FROM fact_orders_enriched
GROUP BY 1
ORDER BY order_month_date;
