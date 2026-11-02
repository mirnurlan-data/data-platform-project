"""Illustrative Airflow 2.x DAG. Requires operator-managed Airflow installation.

Not executed in CI: use a separately managed scheduler/worker environment.
AIRFLOW_HOME, Python module installation, S3_BUCKET, AWS credentials and PG_DSN
must be configured outside this repository.
"""
from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="synthetic_sales_s3_postgres_dbt",
    schedule="0 3 * * *",
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["portfolio", "synthetic", "data-quality"],
) as dag:
    land_and_load = BashOperator(
        task_id="s3_publish_verify_pg_load",
        bash_command=(
            "set -euo pipefail; "
            "python -m cloud.cloud_pipeline.cli run "
            "--file data/synthetic_sales.csv --bucket \"$S3_BUCKET\""
        ),
    )
    build_marts = BashOperator(
        task_id="dbt_build_and_test",
        bash_command=(
            "set -euo pipefail; "
            "dbt build --project-dir cloud/dbt --profiles-dir cloud/dbt --target ci"
        ),
    )
    land_and_load >> build_marts
