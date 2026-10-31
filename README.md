# End-to-End Data Platform — Synthetic Sales Analytics

An **educational Python + SQLite ETL and dimensional-modeling example**, designed to show how raw sales records become validated, analytics-ready fact and dimension tables.

## Architecture

```text
Synthetic CSV → validation → SQLite staging → dimension tables → fact_sales → daily revenue SQL
```

No external infrastructure is required for the baseline workflow. This repository is not a claim of production deployment, distributed orchestration, or cloud-scale throughput.

## Quick start

Python 3.10+ (standard library only):

```bash
python scripts/generate_sales.py
python scripts/run_etl.py
python -m unittest discover -s tests -v
```

This generates 500 synthetic sales records, imports them into a disposable `output/warehouse.sqlite3`, builds dimensions and a sales fact table, and prints store-level revenue. Re-running the script **rebuilds** the disposable demo warehouse from the CSV; it does not append duplicate facts.

## Repository map

- [scripts/generate_sales.py](scripts/generate_sales.py): deterministic synthetic sales
- [scripts/run_etl.py](scripts/run_etl.py): validated CSV-to-SQLite batch ingest
- [sql/schema.sql](sql/schema.sql): dimension and fact schema
- [sql/daily_revenue.sql](sql/daily_revenue.sql): analytics query
- [tests/test_pipeline.py](tests/test_pipeline.py): checks reproducibility, validation, and correctness

## Design decisions

- This demonstration uses SQLite for portability, not as a substitute for PostgreSQL or a distributed warehouse.
- Fact table stores integer cents to avoid floating-point errors in currency aggregation.
- Primary and foreign key constraints enforce key integrity.
- Rows are validated before insertion. Invalid input aborts the demo instead of silently dropping records.
- Separate synthetic test data only. No real business or client data.
- A production implementation would add orchestration, metrics, incremental loads, secrets management, and automated data-quality checks.

**Measurement policy:** No fabricated performance, accuracy, latency, or business-impact percentages.
