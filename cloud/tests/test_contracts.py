"""Fast, network-free contract and negative-case tests."""
import io
import unittest
from botocore.exceptions import ClientError
from cloud.cloud_pipeline.contracts import parse_csv, ContractError, sha256
from cloud.cloud_pipeline.s3_store import publish, fetch_verified, object_key

HEADER = b"transaction_id,sold_date,store_id,product_id,quantity,unit_price_cents\n"
ROW = b"T1,2026-01-02,S1,P1,2,125\n"


class FakeS3:
    def __init__(self):
        self.objects = {}

    def put_object(self, **kwargs):
        key = kwargs["Key"]
        if key in self.objects:
            raise ClientError(
                {"Error": {"Code": "PreconditionFailed"},
                 "ResponseMetadata": {"HTTPStatusCode": 412}}, "PutObject",
            )
        self.objects[key] = (kwargs["Body"], kwargs["Metadata"])

    def head_object(self, Bucket, Key):
        data, metadata = self.objects[Key]
        return {"ContentLength": len(data), "Metadata": metadata}

    def get_object(self, Bucket, Key):
        data, metadata = self.objects[Key]
        return {"Body": io.BytesIO(data), "Metadata": metadata}


class ContractTests(unittest.TestCase):
    def test_valid_and_deterministic(self):
        self.assertEqual(parse_csv(HEADER + ROW), [("T1", "2026-01-02", "S1", "P1", 2, 125)])
        self.assertEqual(sha256(HEADER + ROW), object_key(HEADER + ROW).split("/")[-1][:-4])

    def test_reject_invalid_inputs(self):
        bad_rows = [
            ROW + ROW, ROW.replace(b",2,125", b",-2,125"),
            ROW.replace(b",2,125", b",2,1.25"),
            ROW.replace(b"2026-01-02", b"2026-02-30"),
            ROW.replace(b"T1,", b" ,"),
            ROW.replace(b",S1,", b", S1,"),
            ROW.replace(b",2,125", b",2,-1"),
        ]
        for value in bad_rows:
            with self.subTest(value=value), self.assertRaises(ContractError):
                parse_csv(HEADER + value)
        with self.assertRaises(ContractError):
            parse_csv(b"")
        with self.assertRaises(ContractError):
            parse_csv(HEADER + ROW + b"x,y\n")

    def test_idempotent_s3_and_tamper_detection(self):
        s3 = FakeS3()
        data = HEADER + ROW
        key = publish(s3, "demo", data)
        self.assertEqual(publish(s3, "demo", data), key)
        self.assertEqual(fetch_verified(s3, "demo", key), data)
        s3.objects[key] = (data + b"tampered", {"sha256": sha256(data)})
        with self.assertRaises(ContractError):
            fetch_verified(s3, "demo", key)

    def test_existing_object_conflicts_fail(self):
        s3 = FakeS3()
        data = HEADER + ROW
        key = publish(s3, "demo", data)
        s3.objects[key] = (b"wrong", {"sha256": sha256(data)})
        with self.assertRaises(ContractError):
            publish(s3, "demo", data)


if __name__ == "__main__":
    unittest.main()
