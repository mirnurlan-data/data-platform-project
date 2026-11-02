"""Explicit CLI: cloud operations require user-provided AWS/PG configuration."""
import argparse
import json
import os
from pathlib import Path

from .contracts import ContractError, parse_csv, sha256
from .warehouse import load_rows, verify_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic cloud data platform demo")
    parser.add_argument("command", choices=("validate", "load", "verify", "upload", "run"))
    parser.add_argument("--file", required=True, type=Path, help="Synthetic CSV source file")
    parser.add_argument("--bucket", default=os.getenv("S3_BUCKET"))
    args = parser.parse_args()
    data = args.file.read_bytes()
    rows = parse_csv(data)
    result = {"source_sha256": sha256(data), "source_records": len(rows)}
    if args.command in ("upload", "run"):
        if not args.bucket:
            parser.error("--bucket or S3_BUCKET is required")
        import boto3
        from .s3_store import publish, fetch_verified
        client = boto3.client(
            "s3", region_name=os.getenv("AWS_REGION", "us-east-1"),
            endpoint_url=os.getenv("S3_ENDPOINT_URL"),
        )
        key = publish(client, args.bucket, data)
        result["s3_key"] = key
        if args.command == "run":
            downloaded = fetch_verified(client, args.bucket, key)
            rows = parse_csv(downloaded)
    if args.command in ("load", "run"):
        result["inserted"] = load_rows(os.getenv("PG_DSN", ""), rows, sha256(data))
        result["reconciliation"] = verify_rows(os.getenv("PG_DSN", ""), rows)
    if args.command == "verify":
        result["reconciliation"] = verify_rows(os.getenv("PG_DSN", ""), rows)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
