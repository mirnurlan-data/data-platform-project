SELECT
  (SELECT COUNT(*) FROM fact_sales) AS row_count,
  (SELECT COALESCE(SUM(quantity * unit_price_cents), 0) FROM fact_sales) AS revenue_cents,
  (SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_store s ON f.store_id = s.store_id WHERE s.store_id IS NULL) AS missing_store_count,
  (SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_product p ON f.product_id = p.product_id WHERE p.product_id IS NULL) AS missing_product_count,
  (SELECT COUNT(*) FROM fact_sales WHERE quantity <= 0 OR unit_price_cents < 0) AS invalid_amount_count;
