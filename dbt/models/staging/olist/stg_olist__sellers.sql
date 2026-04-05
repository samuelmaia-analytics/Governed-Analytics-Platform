select
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
from read_parquet('{{ var("standardized_olist_path") }}/olist_sellers_dataset.parquet')
