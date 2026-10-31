# Local operations and reliability runbook

This repository is a **synthetic batch ETL lab**. It does not implement a production control plane, remote deployment, secrets manager, or scheduler.

## Replay and idempotency
The command `python scripts/run_etl.py` intentionally recreates only `output/warehouse.sqlite3`, and the import's core `run()` refuses overwriting an existing file. This protects other database files when the Python function is reused. Deterministic transaction IDs and a `PRIMARY KEY` prevent duplicate facts within a batch. This is **not** an incremental upsert system; rerun the entire disposable demonstration after generating the source file.

## Quality gate
`python scripts/validate_warehouse.py` reconciles row counts, revenue in integer cents, dimension foreign keys, and invalid monetary values. The CLI emits `output/quality_report.json`. CI includes a deliberate corruption test verifying that an altered fact is caught. If data quality fails, do not publish reports.

## Security
Use only synthetic data in this repository. No real customer information or credentials. The scripts do not require secrets or outbound connections. For a real service, implement scoped database accounts, secret rotation, encrypted transport, audit records, backup validation, and retention policies.

## Observability and future production design
A production orchestration workflow should emit structured JSON logs, batch/job IDs, source row counts, failed row counts, freshness age, job duration and reconciliation status. Set alerts for missing data, ingestion lag and reconciliation failures. Add retry/backoff with quarantine for invalid rows, durable staging, lineage, and rollback plans. None of those behaviors are claimed to be implemented here.

## Release checklist
1. Confirm tests are green on the exact commit.
2. Run a synthetic sample and read the JSON quality report.
3. Verify CSV schema and fact/dimension foreign keys.
4. Check that reprocessing cannot overwrite non-disposable data.
5. Document any schema migration and rollback before production use.
