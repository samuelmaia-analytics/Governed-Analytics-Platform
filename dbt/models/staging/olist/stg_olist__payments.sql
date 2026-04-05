select
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    cast(payment_value as double) as payment_value
from read_parquet('{{ var("standardized_olist_path") }}/olist_order_payments_dataset.parquet')
