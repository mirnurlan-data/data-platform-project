PRAGMA foreign_keys = ON;
CREATE TABLE dim_store (
    store_id TEXT PRIMARY KEY
);
CREATE TABLE dim_product (
    product_id TEXT PRIMARY KEY
);
CREATE TABLE fact_sales (
    transaction_id TEXT PRIMARY KEY,
    sold_date TEXT NOT NULL,
    store_id TEXT NOT NULL REFERENCES dim_store(store_id),
    product_id TEXT NOT NULL REFERENCES dim_product(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0)
);
CREATE INDEX idx_fact_sales_date_store ON fact_sales (sold_date, store_id);
