"""Additional ETL invariants: money, integrity and destructive-operation prevention."""
import csv
import importlib.util
from pathlib import Path
import sqlite3
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

gen = load("gen_edges", "scripts/generate_sales.py")
etl = load("etl_edges", "scripts/run_etl.py")


class EdgeCaseTests(unittest.TestCase):
    def test_zero_price_allowed_and_exact_cents(self):
        r = dict(zip(etl.FIELDS, ["T0001", "2026-01-02", "S1", "P1", "3", "0"]))
        self.assertEqual(etl.parse_row(r)[-2:], (3, 0))

    def test_rejects_unexpected_csv_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "data.csv"
            with source.open("w", newline="") as f:
                w = csv.writer(f)
                w.writerow(etl.FIELDS + ["unknown"])
                w.writerow(["T0001","2026-01-02","S1","P1","2","100","unexpected"])
            out = Path(tmp) / "db.sqlite3"
            with self.assertRaises(ValueError):
                etl.run(source, out)
            self.assertFalse(out.exists())

    def test_foreign_keys_enabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.csv"
            gen.generate(source, 5)
            db = root / "warehouse.sqlite3"
            etl.run(source, db)
            with sqlite3.connect(db) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        "INSERT INTO fact_sales VALUES ('bad-id','2026-01-01','missing-store','P1',1,100)"
                    )

    def test_rejects_partial_empty_fields(self):
        bad = dict(zip(etl.FIELDS, ["T0001", "2026-01-02", "", "P1", "2", "100"]))
        with self.assertRaises(ValueError):
            etl.parse_row(bad)


if __name__ == "__main__":
    unittest.main()
