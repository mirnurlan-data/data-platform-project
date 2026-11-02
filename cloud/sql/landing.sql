-- This local demo user must have CREATE privilege in its own test database.
-- Migrations and permissions must be managed separately in production.
CREATE SCHEMA IF NOT EXISTS landing;
CREATE TABLE IF NOT EXISTS landing.sales_events (
    transaction_id TEXT PRIMARY KEY,
    sold_date DATE NOT NULL,
    store_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity BIGINT NOT NULL CHECK (quantity > 0),
    unit_price_cents BIGINT NOT NULL CHECK (unit_price_cents >= 0),
    source_sha256 CHAR(64) NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_sales_events_sold_date
    ON landing.sales_events (sold_date);
