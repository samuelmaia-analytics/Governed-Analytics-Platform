SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN price < 0 THEN 1 ELSE 0 END) AS negative_price_rows,
    SUM(CASE WHEN freight_value < 0 THEN 1 ELSE 0 END) AS negative_freight_rows,
    SUM(CASE WHEN order_delivered_customer_date < order_purchase_timestamp THEN 1 ELSE 0 END) AS invalid_delivery_rows,
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS null_order_id_rows
FROM fact_orders_enriched;
