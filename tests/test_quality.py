"""Data quality contract and corruption detection tests."""
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
generator = load("gen", "scripts/generate_sales.py")
pipeline = load("pipeline", "scripts/run_etl.py")
quality = load("quality", "scripts/validate_warehouse.py")


class QualityTests(unittest.TestCase):
    def test_reconciles_actual_generated_data(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            source, db = p / "sales.csv", p / "store.sqlite3"
            generator.generate(source, 25)
            pipeline.run(source, db)
            report = quality.validate(source, db)
            self.assertEqual(report["warehouse_records"], 25)
            self.assertEqual(report["missing_store"], 0)
            self.assertEqual(report["warehouse_revenue_cents"], report["expected_revenue_cents"])

    def test_detects_corrupted_warehouse(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            source, db = p / "sales.csv", p / "store.sqlite3"
            generator.generate(source, 25)
            pipeline.run(source, db)
            with sqlite3.connect(db) as conn:
                conn.execute("UPDATE fact_sales SET unit_price_cents = unit_price_cents + 1 WHERE transaction_id = 'T000001'")
            with self.assertRaises(AssertionError):
                quality.validate(source, db)


if __name__ == "__main__":
    unittest.main()
