"""Validate synthetic CSV and build a disposable analytical SQLite database."""
import csv
from datetime import date
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["transaction_id", "sold_date", "store_id", "product_id", "quantity", "unit_price_cents"]


def parse_row(row):
    if set(row) != set(FIELDS) or any(row[k] in (None, "") for k in FIELDS):
        raise ValueError("Missing, unexpected or empty CSV field")
    try:
        date.fromisoformat(row["sold_date"])
        quantity = int(row["quantity"])
        cents = int(row["unit_price_cents"])
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid date or integer") from exc
    if quantity <= 0 or cents < 0:
        raise ValueError("Invalid quantity or price")
    return (row["transaction_id"], row["sold_date"], row["store_id"], row["product_id"], quantity, cents)


def run(csv_path: Path, db_path: Path):
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise ValueError(f"Expected header: {FIELDS}")
        rows = [parse_row(row) for row in reader]
    if len({row[0] for row in rows}) != len(rows):
        raise ValueError("Duplicate transaction_id in source")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # Rebuild a disposable demo DB; do not point this at existing user data.
    if db_path.exists():
        raise FileExistsError("Refusing to overwrite an existing database. Delete the disposable output file explicitly.")
    with sqlite3.connect(db_path) as conn:
        conn.executescript((ROOT / "sql" / "schema.sql").read_text(encoding="utf-8"))
        conn.executemany("INSERT INTO dim_store VALUES (?)", sorted({(r[2],) for r in rows}))
        conn.executemany("INSERT INTO dim_product VALUES (?)", sorted({(r[3],) for r in rows}))
        conn.executemany("INSERT INTO fact_sales VALUES (?, ?, ?, ?, ?, ?)", rows)
        revenue = conn.execute((ROOT / "sql" / "daily_revenue.sql").read_text(encoding="utf-8")).fetchall()
    return len(rows), revenue


if __name__ == "__main__":
    csv_path = ROOT / "data" / "synthetic_sales.csv"
    db_path = ROOT / "output" / "warehouse.sqlite3"
    if not csv_path.exists():
        raise SystemExit("Run python scripts/generate_sales.py first")
    if db_path.exists():
        db_path.unlink()  # Known disposable file in output/ only.
    count, report = run(csv_path, db_path)
    print(f"Loaded {count} synthetic transactions into {db_path}")
    print("date,store,transactions,units,revenue_cents")
    for line in report[:10]:
        print(",".join(map(str, line)))
