select
    transaction_id,
    sold_date,
    store_id,
    product_id,
    quantity,
    unit_price_cents,
    cast(quantity as numeric) * unit_price_cents as revenue_cents
from {{ source('landing', 'sales_events') }}
