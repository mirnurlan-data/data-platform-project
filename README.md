# End-to-End Data Platform — Synthetic Sales Analytics

[![Data Platform CI](https://github.com/mirnurlan-data/data-platform-project/actions/workflows/ci.yml/badge.svg)](https://github.com/mirnurlan-data/data-platform-project/actions/workflows/ci.yml)

A portable, educational Python + SQLite data warehouse with synthetic sales, strict validation, dimensional models, SQL reporting and source-to-target quality reconciliation.

## Architecture

```text
Synthetic CSV → validation → dim_store / dim_product / fact_sales → daily revenue
                                                            ↳ integrity checks
```

[System design](docs/architecture.md) · [Operations and reliability](docs/OPERATIONS.md) · [CI results](https://github.com/mirnurlan-data/data-platform-project/actions)

## Run from a clean checkout

Python 3.10+; no external Python packages.

```bash
python scripts/generate_sales.py
python scripts/run_etl.py
python scripts/validate_warehouse.py
python -m unittest discover -s tests -v
```

The pipeline generates 500 **synthetic** sales and writes to `output/warehouse.sqlite3`. The data-quality gate compares independently calculated counts and monetary totals, checks foreign keys, and emits `output/quality_report.json`.

**Important:** the loader deliberately refuses to overwrite existing database files. To rerun, explicitly delete only the disposable `output/warehouse.sqlite3` created by the demo, after verifying it does not contain your data. Do not use this repo as a production migration tool.

## Test coverage
- Invalid dates, blank identifiers, negative quantities, duplicate transaction IDs
- Existing database preserved byte-for-byte; no implicit overwrite
- Dimension keys and source-to-target count / revenue reconciliation
- Synthetic corruption detection: a modified fact amount must fail reconciliation
- GitHub Actions publishes a validation report as an artifact

## Limitations
Single-node SQLite and 500-row generated input are intentionally small for reproducibility. No claims of cloud production deployment, scheduler orchestration, concurrency capacity, throughput SLOs, or client systems.
