# Test strategy and evidence

GitHub Actions runs the Python standard-library unit test suite, generates deterministic synthetic sales, builds a disposable SQLite warehouse, and reconciles source records and monetary totals.

## Positive cases
- CSV import builds dimension and fact tables and returns expected counts
- Currency uses integer cents; zero-price rows are legal and exactly represented
- Foreign-key checks maintain relationships among dimensions and fact records

## Negative cases
- Invalid calendar dates and missing IDs
- Negative quantities, unexpected CSV columns and duplicate transaction IDs
- Existing destination database is never silently overwritten
- Deliberately changed warehouse money value is detected by source-to-target reconciliation
- Offset-price corruption that preserves row counts and aggregate revenue is detected by full-record multiset reconciliation
- Database foreign-key violations fail

All tests use synthetic data and temporary SQLite files. This is deterministic correctness evidence, **not** a performance or scale claim.

## Production gaps
Incremental ingestion, orchestration, dead-letter handling, monitoring and cloud IAM are intentionally not implemented. These would require a new integration test environment and documented operational SLOs.

## Reconciliation scope

The quality gate compares complete source and warehouse records (including multiplicity), not only row counts and revenue totals. It emits `source_records_missing_in_warehouse` and `unexpected_warehouse_records` in the JSON artifact. This implementation materializes records in memory and is intentionally limited to the small synthetic teaching dataset; production-scale pipelines should use partitioned reconciliation, keyed checks or streaming checks with measured resource limits.
