"""Content-addressed S3 landing. No deletes, bucket creation or credentials here."""
from botocore.exceptions import ClientError
from .contracts import ContractError, MAX_BYTES, sha256


def object_key(data: bytes) -> str:
    return f"raw/sales/sha256/{sha256(data)}.csv"


def publish(client, bucket: str, data: bytes) -> str:
    """Put only if absent; reject a conflicting object. Concurrent uploads are safe."""
    if not bucket:
        raise ContractError("A bucket is required")
    key, digest = object_key(data), sha256(data)
    try:
        client.put_object(
            Bucket=bucket, Key=key, Body=data, ContentType="text/csv",
            ServerSideEncryption="AES256", Metadata={"sha256": digest},
            IfNoneMatch="*",
        )
    except ClientError as exc:
        status = str(exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode", ""))
        code = exc.response.get("Error", {}).get("Code", "")
        if status != "412" and code not in {"PreconditionFailed", "412"}:
            raise
        head = client.head_object(Bucket=bucket, Key=key)
        if (head.get("Metadata", {}).get("sha256") != digest or
                head.get("ContentLength") != len(data)):
            raise ContractError("Existing S3 object conflicts with source content") from exc
    return key


def fetch_verified(client, bucket: str, key: str) -> bytes:
    if not key.startswith("raw/sales/sha256/") or not key.endswith(".csv"):
        raise ContractError("Unexpected object key")
    expected = key.rsplit("/", 1)[1][:-4]
    if len(expected) != 64 or any(ch not in "0123456789abcdef" for ch in expected):
        raise ContractError("Invalid SHA256 key")
    response = client.get_object(Bucket=bucket, Key=key)
    try:
        data = response["Body"].read(MAX_BYTES + 1)
    finally:
        response["Body"].close()
    if len(data) > MAX_BYTES or sha256(data) != expected:
        raise ContractError("Object too large or SHA256 integrity mismatch")
    if response.get("Metadata", {}).get("sha256") != expected:
        raise ContractError("S3 metadata checksum mismatch")
    return data
