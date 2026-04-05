select
    order_id,
    count(*) as review_count,
    avg(review_score) as review_score_mean,
    max(review_creation_date) as latest_review_creation_date,
    max(review_answer_timestamp) as latest_review_answer_timestamp
from {{ ref('stg_olist__reviews') }}
group by 1
