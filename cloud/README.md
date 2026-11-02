# AWS-oriented Data Platform — S3 → PostgreSQL → dbt (Airflow blueprint)

[![Cloud Data Platform CI](https://github.com/mirnurlan-data/data-platform-project/actions/workflows/cloud-ci.yml/badge.svg)](https://github.com/mirnurlan-data/data-platform-project/actions/workflows/cloud-ci.yml)

**Status: production-inspired reference implementation, not a production deployment.** All data are synthetic. CI exercises PostgreSQL and dbt locally without AWS credentials; it tests S3 integrity/conditional-write behavior using a deterministic in-memory fake. The Terraform and Airflow examples are **not deployed or end-to-end tested in a real AWS account**.

## Architecture and trust boundaries

```mermaid
flowchart LR
  A[Synthetic CSV] --> B[Strict schema, uniqueness and bounds validation]
  B --> C[S3 raw immutable SHA-256 key, SSE-S3]
  C --> D[Checksum verification on read]
  D --> E[PostgreSQL landing - atomic idempotent insert]
  E --> F[dbt staging model]
  F --> G[dbt daily store mart]
  G --> H[dbt tests and reconciliation]
  I[Airflow scheduled example] -. orchestrates .-> B
  I -. orchestrates .-> F
```

The S3 operations are optional for the local CI: the same CSV bytes are validated and loaded directly into a disposable PostgreSQL service. AWS deployment must supply networking, identity, PostgreSQL hosting, secret management and scheduler operations separately.

## What is actually tested

- UTF-8 CSV with an exact six-column contract; real dates; nonempty, trimmed IDs; bounded positive quantities; integer cents and unique transaction IDs.
- SHA-256 content-addressed S3 object names, conditional `PutObject` and integrity checks on reads (via an isolated fake S3 client in CI).
- PostgreSQL transaction rollback on conflicting replay, same-input idempotence and full-record input-key reconciliation (via real PostgreSQL 16 in CI).
- dbt staging + daily store revenue mart; uniqueness, nonnull and a cross-layer revenue reconciliation test.
- GitHub Actions produces reproducible validation evidence (no actual throughput, latency or availability SLO claim).

## Local reproduce without cloud spending

Requires Python 3.11, an isolated PostgreSQL 16 database, and the two commands already in the repository for generating synthetic data. The disposable CI database uses example credentials: **never reuse those on a reachable server**.

```bash
python -m pip install -r cloud/requirements-ci.txt
python scripts/generate_sales.py
export PG_DSN='postgresql://portfolio:portfolio@127.0.0.1:5432/portfolio'
export DBT_PG_USER=portfolio DBT_PG_PASSWORD=portfolio DBT_PG_DB=portfolio
python -m unittest discover -s cloud/tests -v
python -m cloud.cloud_pipeline.cli validate --file data/synthetic_sales.csv
python -m cloud.cloud_pipeline.cli load --file data/synthetic_sales.csv
python -m cloud.cloud_pipeline.cli load --file data/synthetic_sales.csv
dbt build --project-dir cloud/dbt --profiles-dir cloud/dbt --target ci
python -m cloud.cloud_pipeline.cli verify --file data/synthetic_sales.csv
```

`load` returns `inserted: 0` on an identical replay. A conflicting transaction aborts and rolls back the whole batch. The `verify` operation inspects the submitted transaction IDs and allows unrelated historic rows in the same landing table.

## AWS optional path — deliberately not executed by CI

1. Review `infra/*.tf` and use your own AWS account, budget alarm, remote encrypted Terraform state and approved IAM role. **No `terraform apply` runs automatically.**
2. The Terraform plan provisions one private versioned SSE-S3 bucket, denies HTTP, and creates an **unattached** prefix-scoped IAM policy. It does not provision VPC, RDS, Airflow, an IAM role, secrets, alarms or production backup systems.
3. Provide least-privilege short-lived AWS credentials through a workload identity; set `S3_BUCKET`, `AWS_REGION`, `PG_DSN` and dbt environment variables securely, outside Git.
4. On an approved isolated synthetic environment, run:
   `python -m cloud.cloud_pipeline.cli run --file data/synthetic_sales.csv --bucket "$S3_BUCKET"`.
   The `run` command writes only the raw content-addressed object, reads it back and verifies SHA-256 before the PostgreSQL load.
5. The Airflow DAG under `dags/` illustrates retry and scheduling boundaries. It is **not** bundled in GitHub Actions or shipped as a deployable Airflow environment.

## Failure modes, privacy and operating limits

- No real customer or pharmacy data: generate synthetic input only. Do not upload sensitive data or secrets.
- S3 `IfNoneMatch="*"` prevents overwriting an existing object; conflicting content is rejected. Storage versioning can still grow cost over time.
- The small demo uses in-memory batch parsing, row-by-row PostgreSQL inserts and verification; it is intentionally bounded to 10 MiB. It is **not** optimized for scale.
- dbt materializations operate in one local/Postgres database; no cross-system distributed transaction between S3 and PostgreSQL. Failed loads can leave an immutable raw object; rerunning is safe for identical data.
- This blueprint lacks production-grade KMS rotation, VPC endpoints, RDS HA, backups, remote state, secrets manager, schema evolution, data lineage, centralized monitoring, alerts, SLA enforcement, privacy classification and cost monitoring.
- For real production, introduce managed deployment, IAM role assumption, CloudWatch/OTel observability, secret rotation, streaming/batch partitioning, proper schema migration tooling, recovery drills, data retention decisions and threat-model review.

## Recruiter-ready evidence

[Cloud CI](https://github.com/mirnurlan-data/data-platform-project/actions/workflows/cloud-ci.yml) · [Data contracts](cloud_pipeline/contracts.py) · [S3 checksum + idempotency](cloud_pipeline/s3_store.py) · [PostgreSQL transaction safety](cloud_pipeline/warehouse.py) · [dbt models](dbt/models) · [Terraform baseline](infra) · [Airflow orchestration example](dags/sales_pipeline.py)

No live AWS deployment, real-world throughput or production operational claims are implied.
