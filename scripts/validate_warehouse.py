"""Reconcile synthetic source rows with the local warehouse; emit evidence."""
import csv
from pathlib import Path
import sqlite3
import json

ROOT = Path(__file__).resolve().parents[1]


def validate(csv_path: Path, db_path: Path) -> dict:
    with csv_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    expected_count = len(rows)
    expected_cents = sum(int(r["quantity"]) * int(r["unit_price_cents"]) for r in rows)
    with sqlite3.connect(db_path) as conn:
        count, revenue, missing_store, missing_product, bad_amount = conn.execute(
            (ROOT / "sql" / "data_quality.sql").read_text(encoding="utf-8")
        ).fetchone()
    report = {
        "expected_source_records": expected_count,
        "warehouse_records": count,
        "expected_revenue_cents": expected_cents,
        "warehouse_revenue_cents": revenue,
        "missing_store": missing_store,
        "missing_product": missing_product,
        "invalid_amounts": bad_amount,
    }
    path = ROOT / "output" / "quality_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if (count != expected_count or revenue != expected_cents or
            missing_store != 0 or missing_product != 0 or bad_amount != 0):
        raise AssertionError(f"Warehouse data quality failed: {report}")
    return report


if __name__ == "__main__":
    print(json.dumps(validate(ROOT / "data" / "synthetic_sales.csv",
                              ROOT / "output" / "warehouse.sqlite3"), indent=2))
