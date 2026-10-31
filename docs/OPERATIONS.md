# Local operations and reliability runbook

This repository is a **synthetic batch ETL lab**. It does not implement a production control plane, remote deployment, secrets manager, or scheduler.

## Replay and overwrite safety
The ETL function exclusively creates its SQLite output and **refuses to overwrite an existing file**. Repeat a full demo only after deliberately deleting the disposable `output/warehouse.sqlite3` file yourself. The CLI will not silently delete it. Deterministic transaction IDs and a `PRIMARY KEY` prevent duplicate facts within a batch. This is **not** an incremental upsert system. Never store personal or client data in the disposable output folder.

## Quality gate
`python scripts/validate_warehouse.py` reconciles row counts, revenue in integer cents, dimension foreign keys, and invalid monetary values. The CLI emits `output/quality_report.json`. CI tests rejection of bad dates, blank identifiers, duplicate transaction IDs, accidental overwrites and intentional corruption of an existing warehouse.

## Security
Only synthetic data; no secrets or outbound connections. Production would require restricted database roles, secret rotation, encrypted transport, audit records, backup validation, retention policies and an incident response plan.

## Observability and future production design
A production workflow should emit structured logs, batch/job IDs, source row counts, failed row counts, freshness age, job duration and reconciliation status. Set alerts for missing data, ingestion lag and reconciliation failures. Add retry/backoff, quarantine, durable staging, lineage, and rollback plans. These are proposed controls, **not** implemented production features.

## Release checklist
1. Confirm CI on the exact commit is green.
2. Run the synthetic demo and inspect the JSON quality report.
3. Check fact/dimension foreign keys and source schema.
4. Ensure no real data is written to the demo output.
5. Document schema migrations and rollback for any future production work.
