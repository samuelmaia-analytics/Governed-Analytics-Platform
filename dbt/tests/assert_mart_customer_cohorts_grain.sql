select
    purchase_cohort_month,
    cohort_order_month_number,
    count(*) as row_count
from {{ ref('mart_customer_cohorts') }}
group by 1, 2
having count(*) > 1
