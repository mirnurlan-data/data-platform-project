"""CI-only database smoke: transactions, replay and conflict rollback."""
import os
import unittest

from cloud.cloud_pipeline.contracts import ContractError, parse_csv, sha256
from cloud.cloud_pipeline.warehouse import load_rows, verify_rows

CSV = (b"transaction_id,sold_date,store_id,product_id,quantity,unit_price_cents\n"
       b"CLOUD-CI-T1,2026-01-02,S1,P1,2,125\n"
       b"CLOUD-CI-T2,2026-01-03,S1,P2,1,200\n")


@unittest.skipUnless(os.getenv("PG_DSN"), "Requires an explicitly configured CI PostgreSQL DSN")
class PostgresTests(unittest.TestCase):
    def test_replay_conflict_and_transaction_rollback(self):
        dsn = os.environ["PG_DSN"]
        rows = parse_csv(CSV)
        first = load_rows(dsn, rows, sha256(CSV))
        self.assertIn(first, (0, 2))  # Support re-running against a disposable CI DB.
        self.assertEqual(load_rows(dsn, rows, sha256(CSV)), 0)
        self.assertEqual(verify_rows(dsn, rows)["matching"], 2)

        # Attempt to write one new transaction followed by a conflicting existing one.
        # PostgreSQL must roll back the entire two-row batch.
        changed = [("CLOUD-CI-ROLLBACK", "2026-01-05", "S2", "P3", 1, 500),
                   ("CLOUD-CI-T1", "2026-01-02", "S1", "P1", 2, 999)]
        with self.assertRaises(ContractError):
            load_rows(dsn, changed, "0" * 64)
        self.assertEqual(verify_rows(dsn, rows)["matching"], 2)
        # If the transaction rolled back, retrying this single new record inserts it.
        self.assertEqual(load_rows(dsn, [changed[0]], "1" * 64), 1)


if __name__ == "__main__":
    unittest.main()
