select
    product_category_name,
    product_category_name_english
from read_parquet('{{ var("standardized_olist_path") }}/product_category_name_translation.parquet')
