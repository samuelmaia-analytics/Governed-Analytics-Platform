select *
from {{ ref('stg_platform__fact_orders_enriched') }}
