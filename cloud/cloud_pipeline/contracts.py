"""Strict input contract for a bounded, deterministic synthetic sales batch."""
import csv
from datetime import date
import hashlib
import io
import re

FIELDS = ("transaction_id", "sold_date", "store_id", "product_id", "quantity", "unit_price_cents")
MAX_BYTES = 10 * 1024 * 1024
INTEGER = re.compile(r"(0|[1-9][0-9]*)\Z")


class ContractError(ValueError):
    """An input, object or warehouse invariant failed."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_csv(data: bytes) -> list[tuple]:
    if not data or len(data) > MAX_BYTES:
        raise ContractError("Input must be nonempty and at most 10 MiB")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ContractError("Input must be UTF-8 CSV") from exc
    if "\x00" in text:
        raise ContractError("NUL byte in CSV")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if tuple(reader.fieldnames or ()) != FIELDS:
        raise ContractError(f"Unexpected CSV header: {reader.fieldnames!r}")
    records, ids = [], set()
    for line, record in enumerate(reader, start=2):
        if None in record or any(record.get(f) is None for f in FIELDS):
            raise ContractError(f"Malformed row at line {line}")
        values = [record[f] for f in FIELDS]
        if any(not v or v.strip() != v or len(v) > 128 for v in values):
            raise ContractError(f"Blank, padded or oversized field at line {line}")
        tx, day, store, product, quantity, cents = values
        if tx in ids:
            raise ContractError(f"Duplicate transaction_id at line {line}")
        ids.add(tx)
        try:
            date.fromisoformat(day)
        except ValueError as exc:
            raise ContractError(f"Invalid calendar date at line {line}") from exc
        if not INTEGER.fullmatch(quantity) or not INTEGER.fullmatch(cents):
            raise ContractError(f"Invalid integer at line {line}")
        q, p = int(quantity), int(cents)
        if q == 0 or q > 1_000_000 or p > 1_000_000_000:
            raise ContractError(f"Quantity or price outside contract at line {line}")
        records.append((tx, day, store, product, q, p))
    if not records:
        raise ContractError("CSV must contain data rows")
    return records
