# End-to-End Data Platform — Synthetic Sales Analytics

[![Data Platform CI](https://github.com/mirnurlan-data/data-platform-project/actions/workflows/ci.yml/badge.svg)](https://github.com/mirnurlan-data/data-platform-project/actions/workflows/ci.yml)

An educational batch ETL / dimensional warehouse example using Python standard libraries and SQLite. All transactions are **synthetic**, not client data.

## Architecture

```text
Synthetic CSV → strict validation → dim_store + dim_product + fact_sales → SQL reports
                                                              ↳ quality reconciliation
```

Read [system architecture and production trade-offs](docs/architecture.md).

## Quick start

Requirements: Python 3.10+ (no external packages).

```bash
python scripts/generate_sales.py
python scripts/run_etl.py
python scripts/validate_warehouse.py
python -m unittest discover -s tests -v
```

Generates 500 synthetic sales rows, populates a local demo warehouse, and reconciles count, revenue and referential integrity. The checker writes `output/quality_report.json`; GitHub Actions retains that evidence as an artifact.

## Data and correctness

- ISO date validation; all required fields checked
- Nonnegative integer cents to prevent floating-point currency drift
- Positive quantity, duplicate transaction ID detection
- Dimension foreign keys and duplicate-safe demo rebuild
- Reconciliation of **independently calculated** source record count and total revenue
- Repeatable CI unit tests and data-quality gate

## File guide

- `scripts/generate_sales.py`: deterministic synthetic generator
- `scripts/run_etl.py`: validated CSV batch load
- `scripts/validate_warehouse.py`: source-to-target reconciliation
- `sql/schema.sql`: fact and dimension schema
- `sql/daily_revenue.sql`: analytical aggregates
- `sql/data_quality.sql`: integrity check
- `docs/architecture.md`: architecture and production considerations
- `tests/`: correctness tests

**Limitations:** SQLite is deliberately used for local reproducibility; this project does not claim a production streaming system, high availability, or benchmarked throughput. The CLI recreates only the disposable `output/warehouse.sqlite3` file; don't store user data there.
