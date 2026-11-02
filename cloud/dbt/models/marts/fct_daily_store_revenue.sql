select
    sold_date,
    store_id,
    count(*) as transactions,
    sum(quantity) as units,
    sum(revenue_cents) as revenue_cents
from {{ ref('stg_sales') }}
group by sold_date, store_id
