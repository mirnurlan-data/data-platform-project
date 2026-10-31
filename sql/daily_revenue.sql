SELECT sold_date,
       store_id,
       COUNT(*) AS transaction_count,
       SUM(quantity) AS units_sold,
       SUM(quantity * unit_price_cents) AS revenue_cents
FROM fact_sales
GROUP BY sold_date, store_id
ORDER BY sold_date, store_id;
