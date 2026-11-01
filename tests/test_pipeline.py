import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import src.pipeline as pipeline


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sample_dir = Path(self.temp_dir.name)

        # Temporary input data for repeatable tests
        self._write_csv(
            "customers.csv",
            ["customer_id", "name"],
            [{"customer_id": "1", "name": "Test Customer"}],
        )
        self._write_csv(
            "products.csv",
            ["product_id", "name"],
            [{"product_id": "10", "name": "Test Product"}],
        )
        self._write_csv(
            "orders.csv",
            ["order_id", "customer_id", "order_ts", "order_status"],
            [
                {
                    "order_id": "O1",
                    "customer_id": "1",
                    "order_ts": "2026-11-01T10:00:00Z",
                    "order_status": "placed",
                },
                {
                    "order_id": "O2",
                    "customer_id": "999",
                    "order_ts": "2026-11-01T11:00:00Z",
                    "order_status": "placed",
                },
                {
                    "order_id": "O3",
                    "customer_id": "1",
                    "order_ts": "not-a-date",
                    "order_status": "cancelled",
                },
                {
                    "order_id": "O4",
                    "customer_id": "1",
                    "order_ts": "",
                    "order_status": "placed",
                },
            ],
        )
        self._write_jsonl(
            "order_events.jsonl",
            [
                {"event_id": "E1", "event_type": "order_created"},
                {"event_id": "E1", "event_type": "order_created"},
                {"event_type": "missing_id"},
            ],
        )

        # Keep generated outputs in the project, but use test-only input files.
        self.sample_patch = patch.object(pipeline, "SAMPLE", self.sample_dir)
        self.sample_patch.start()

        for folder in (
            pipeline.BRONZE,
            pipeline.SILVER,
            pipeline.GOLD,
            pipeline.REJECTS,
            pipeline.RUNS,
        ):
            shutil.rmtree(folder, ignore_errors=True)

    def tearDown(self):
        self.sample_patch.stop()
        self.temp_dir.cleanup()

    def _write_csv(self, filename, fields, rows):
        path = self.sample_dir / filename
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def _write_jsonl(self, filename, rows):
        path = self.sample_dir / filename
        with path.open("w", encoding="utf-8") as file:
            for row in rows:
                file.write(json.dumps(row) + "\n")

    def test_valid_order_passes_to_silver(self):
        run_summary = pipeline.run_pipeline()

        self.assertEqual(run_summary["silver_counts"]["orders"], 1)

        with (pipeline.SILVER / "orders.csv").open(encoding="utf-8") as file:
            silver_orders = list(csv.DictReader(file))

        self.assertEqual(silver_orders[0]["order_id"], "O1")

    def test_unknown_customer_is_rejected(self):
        pipeline.run_pipeline()

        with (pipeline.REJECTS / "orders.csv").open(encoding="utf-8") as file:
            rejected = list(csv.DictReader(file))

        reasons = {row["_reject_reason"] for row in rejected}
        self.assertIn("unknown_customer_id", reasons)

    def test_invalid_and_missing_timestamps_are_rejected(self):
        pipeline.run_pipeline()

        with (pipeline.REJECTS / "orders.csv").open(encoding="utf-8") as file:
            rejected = list(csv.DictReader(file))

        reasons = {row["_reject_reason"] for row in rejected}
        self.assertIn("invalid_order_timestamp", reasons)
        self.assertIn("missing_order_timestamp", reasons)

    def test_duplicate_and_missing_event_ids_are_rejected(self):
        pipeline.run_pipeline()

        with (pipeline.REJECTS / "order_events.jsonl").open(
            encoding="utf-8"
        ) as file:
            rejected = [json.loads(line) for line in file if line.strip()]

        reasons = {row["_reject_reason"] for row in rejected}
        self.assertIn("duplicate_event_id", reasons)
        self.assertIn("missing_event_id", reasons)

    def test_run_summary_is_written(self):
        summary = pipeline.run_pipeline()

        saved_summary = json.loads(
            (pipeline.RUNS / "latest_run.json").read_text(encoding="utf-8")
        )

        self.assertEqual(summary["run_status"], "success")
        self.assertEqual(saved_summary["run_status"], "success")


if __name__ == "__main__":
    unittest.main()