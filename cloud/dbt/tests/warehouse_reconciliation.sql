-- A singular dbt test fails when transformed revenue differs from landing.
with raw_total as (
    select coalesce(sum(cast(quantity as numeric) * unit_price_cents), 0) as amount
    from {{ source('landing', 'sales_events') }}
),
mart_total as (
    select coalesce(sum(revenue_cents), 0) as amount
    from {{ ref('fct_daily_store_revenue') }}
)
select raw_total.amount as raw_amount, mart_total.amount as mart_amount
from raw_total cross join mart_total
where raw_total.amount <> mart_total.amount
