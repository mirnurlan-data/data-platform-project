"""Batch ETL contract and failure-safety tests."""
import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = load("sales_gen", "scripts/generate_sales.py")
pipeline = load("sales_pipeline", "scripts/run_etl.py")


class PipelineTests(unittest.TestCase):
    def test_valid_synthetic_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            csv_path = root / "sales.csv"
            generator.generate(csv_path, 25)
            n, report = pipeline.run(csv_path, root / "warehouse.sqlite3")
            self.assertEqual(n, 25)
            self.assertEqual(sum(row[2] for row in report), 25)

    def test_reject_negative_quantity(self):
        row = dict(zip(pipeline.FIELDS, ["a", "2026-01-01", "S1", "P1", "-1", "100"]))
        with self.assertRaises(ValueError):
            pipeline.parse_row(row)

    def test_reject_blank_ids(self):
        row = dict(zip(pipeline.FIELDS, [" ", "2026-01-01", "S1", "P1", "1", "100"]))
        with self.assertRaises(ValueError):
            pipeline.parse_row(row)

    def test_reject_invalid_date(self):
        row = dict(zip(pipeline.FIELDS, ["a", "2026-02-31", "S1", "P1", "1", "100"]))
        with self.assertRaises(ValueError):
            pipeline.parse_row(row)

    def test_existing_db_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            csv_path = root / "sales.csv"
            generator.generate(csv_path, 2)
            db = root / "warehouse.sqlite3"
            db.write_bytes(b"important existing data")
            with self.assertRaises(FileExistsError):
                pipeline.run(csv_path, db)
            self.assertEqual(db.read_bytes(), b"important existing data")

    def test_reject_duplicate_transaction_ids_before_creating_db(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            csv_path = root / "sales.csv"
            generator.generate(csv_path, 2)
            with csv_path.open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            rows[1]["transaction_id"] = rows[0]["transaction_id"]
            with csv_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=pipeline.FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            db = root / "warehouse.sqlite3"
            with self.assertRaises(ValueError):
                pipeline.run(csv_path, db)
            self.assertFalse(db.exists())


if __name__ == "__main__":
    unittest.main()
