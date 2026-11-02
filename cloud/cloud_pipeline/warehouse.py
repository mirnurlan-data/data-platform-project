"""Transaction-safe, replayable PostgreSQL landing for bounded demo batches."""
from collections import Counter
from pathlib import Path

import psycopg
from .contracts import ContractError

SCHEMA = Path(__file__).resolve().parents[1] / "sql" / "landing.sql"
COLUMNS = "transaction_id, sold_date::text, store_id, product_id, quantity, unit_price_cents"


def load_rows(dsn: str, rows: list[tuple], source_digest: str) -> int:
    """Identical transactions are replay-safe; conflicting updates fail and roll back."""
    if not dsn:
        raise ContractError("PG_DSN must be supplied explicitly")
    inserted = 0
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA.read_text(encoding="utf-8"))
            for record in rows:
                cur.execute(
                    """INSERT INTO landing.sales_events
                       (transaction_id, sold_date, store_id, product_id, quantity,
                        unit_price_cents, source_sha256)
                       VALUES (%s,%s,%s,%s,%s,%s,%s)
                       ON CONFLICT (transaction_id) DO NOTHING
                       RETURNING transaction_id""",
                    (*record, source_digest),
                )
                inserted += int(cur.fetchone() is not None)
                cur.execute(
                    f"SELECT {COLUMNS} FROM landing.sales_events WHERE transaction_id = %s",
                    (record[0],),
                )
                if tuple(cur.fetchone()) != record:
                    raise ContractError(f"Existing transaction conflicts: {record[0]}")
    return inserted


def verify_rows(dsn: str, rows: list[tuple]) -> dict:
    """Check every input key; unrelated historical transactions may also exist."""
    if not dsn:
        raise ContractError("PG_DSN must be supplied explicitly")
    expected = Counter(rows)
    observed = Counter()
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            for record in rows:
                cur.execute(
                    f"SELECT {COLUMNS} FROM landing.sales_events WHERE transaction_id = %s",
                    (record[0],),
                )
                found = cur.fetchone()
                if found:
                    observed[tuple(found)] += 1
    missing = sum((expected - observed).values())
    changed = sum((observed - expected).values())
    result = {
        "expected": len(rows), "matching": len(rows) - missing,
        "missing_or_changed": missing, "unexpected_values": changed,
        "expected_revenue_cents": sum(row[4] * row[5] for row in rows),
    }
    if missing or changed:
        raise ContractError(f"Source-to-warehouse reconciliation failed: {result}")
    return result
