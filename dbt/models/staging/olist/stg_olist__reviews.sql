select
    review_id,
    order_id,
    cast(review_score as double) as review_score,
    cast(review_creation_date as timestamp) as review_creation_date,
    cast(review_answer_timestamp as timestamp) as review_answer_timestamp
from read_parquet('{{ var("standardized_olist_path") }}/olist_order_reviews_dataset.parquet')
