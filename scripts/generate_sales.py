"""Generate reproducible fake sales data. No third-party dependencies."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def generate(path: Path, count: int = 500):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["transaction_id", "sold_date", "store_id", "product_id", "quantity", "unit_price_cents"])
        for i in range(1, count + 1):
            writer.writerow([f"T{i:06d}", f"2026-01-{(i % 28) + 1:02d}",
                             f"S{i % 5 + 1}", f"P{i % 20 + 1}",
                             i % 4 + 1, (i % 50 + 1) * 125])
    return count


if __name__ == "__main__":
    path = ROOT / "data" / "synthetic_sales.csv"
    n = generate(path)
    print(f"Generated {n} synthetic rows at {path}")
