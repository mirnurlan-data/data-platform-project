# End-to-End Data Platform — Synthetic Sales Analytics

[![Data Platform CI](https://github.com/mirnurlan-data/data-platform-project/actions/workflows/ci.yml/badge.svg)](https://github.com/mirnurlan-data/data-platform-project/actions/workflows/ci.yml)

An educational Python + SQLite dimensional warehouse with reproducible synthetic sales, strict batch validation, SQL reporting and **source-to-target reconciliation**.

## Architecture
```text
Synthetic CSV → strict validation → dimension tables + fact_sales → revenue analytics
                                                        ↳ integrity and revenue quality gates
```

[Architecture](docs/architecture.md) · [Operations and reliability](docs/OPERATIONS.md) · [Continuous integration](https://github.com/mirnurlan-data/data-platform-project/actions/workflows/ci.yml)

## Run locally

Python 3.10+; all code uses the Python standard library.

```bash
python scripts/generate_sales.py
python scripts/run_etl.py
python scripts/validate_warehouse.py
python -m unittest discover -s tests -v
```

The quality report is written to `output/quality_report.json` (and published as a CI artifact). Automated tests also **inject a corrupted monetary value** into the disposable warehouse and assert that reconciliation rejects it.

## What is actually implemented
- Deterministic generation of 500 synthetic sales
- CSV schema, date, integer and quantity validation; duplicate transaction rejection
- Dimension tables, referential integrity, and star-like sales fact table
- Revenue calculations using integer cents instead of floating point currency
- Source-to-target row counts, revenue totals, missing dimension and bad amount checks
- Negative unit tests verifying bad data is detected
- Rebuildable local run plus GitHub Actions validation

## Limitations
This is a **disposable single-node learning project**, not evidence of actual enterprise-scale production reliability, Airflow scheduling, incremental ingestion, or cloud deployment. The example CLI deletes only the generated `output/warehouse.sqlite3` file and recreates it. Do not put real user data in that path.
