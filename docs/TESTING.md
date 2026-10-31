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
- Database foreign-key violations fail

All tests use synthetic data and temporary SQLite files. This is deterministic correctness evidence, **not** a performance or scale claim.

## Production gaps
Incremental ingestion, orchestration, dead-letter handling, monitoring and cloud IAM are intentionally not implemented. These would require a new integration test environment and documented operational SLOs.
