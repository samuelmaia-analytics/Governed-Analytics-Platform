-- Agrega avaliações por pedido. Um pedido pode ter múltiplas revisões
-- (ex: cliente reabriu chamado), portanto consolidamos antes do join.
with reviews as (
    select * from {{ ref('stg_olist__reviews') }}
)

select
    order_id,
    count(review_id)                                    as review_count,
    avg(review_score)                                   as review_score_mean,
    max(review_score)                                   as review_score_max,
    min(review_score)                                   as review_score_min,
    max(review_creation_date)                           as latest_review_creation_date,
    max(review_answer_timestamp)                        as latest_review_answer_timestamp,
    -- 1 se ao menos uma avaliação possui comentário não vazio
    max(case when trim(coalesce(review_comment_message, '')) <> '' then 1 else 0 end)
        as has_review_comment
from reviews
group by order_id
