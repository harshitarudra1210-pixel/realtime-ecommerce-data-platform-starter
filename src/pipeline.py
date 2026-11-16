
"""Small, dependency-free batch pipeline for the starter project."""

import csv
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

SAMPLE = ROOT / "data" / "sample"

BRONZE = ROOT / "data" / "bronze"
SILVER = ROOT / "data" / "silver"
GOLD = ROOT / "data" / "gold"
REJECTS = ROOT / "data" / "rejects"

RUNS = ROOT / "data" / "observability"


# --------------------------------------------------
# 2. CSV AND JSONL HELPER FUNCTIONS
# --------------------------------------------------

def _read_csv(path):
    """Read CSV records and return them as dictionaries."""

    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_csv(path, rows, fields=None):
    """Write dictionary records into a CSV file."""

    path.parent.mkdir(parents=True, exist_ok=True)

    if fields is None:
        fields = list(rows[0]) if rows else []

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _write_jsonl(path, rows):
    """Write records into a JSON Lines file."""

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def _read_jsonl(path):
    """Read JSON Lines and identify malformed JSON records."""

    rows = []

    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):

            if line.strip():
                try:
                    rows.append(json.loads(line))

                except json.JSONDecodeError as exc:
                    rows.append({
                        "_parse_error": str(exc),
                        "_line": line_no,
                        "_raw": line.rstrip()
                    })

    return rows


# --------------------------------------------------
# 3. TIMESTAMP HELPER FUNCTIONS
# --------------------------------------------------

def _stamp():
    """Return the current UTC timestamp."""

    return datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )


def _is_valid_timestamp(value):
    """Return True if the timestamp can be parsed."""

    if not value:
        return False

    try:
        datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
        return True

    except ValueError:
        return False


# --------------------------------------------------
# 4. MAIN PIPELINE
# --------------------------------------------------

def run_pipeline():
    """
    Ingest source data, create Bronze/Silver/Gold outputs,
    quarantine rejected records, and generate observability.
    """

    # Generate a unique ID for every pipeline execution.
    run_started = _stamp()
    run_id = str(uuid.uuid4())

    # --------------------------------------------------
    # 4.1 CREATE RUN-SPECIFIC OUTPUT PATHS
    # --------------------------------------------------

    bronze_run = BRONZE / run_id
    silver_run = SILVER / run_id
    gold_run = GOLD / run_id
    rejects_run = REJECTS / run_id

    run_history = RUNS / "runs"

    # Create directories for this execution.
    for folder in (
        bronze_run,
        silver_run,
        gold_run,
        rejects_run,
        run_history,
    ):
        folder.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # 4.2 SOURCE DATA INGESTION
    # --------------------------------------------------

    customers = _read_csv(
        SAMPLE / "customers.csv"
    )

    products = _read_csv(
        SAMPLE / "products.csv"
    )

    orders = _read_csv(
        SAMPLE / "orders.csv"
    )

    events = _read_jsonl(
        SAMPLE / "order_events.jsonl"
    )

    # --------------------------------------------------
    # 4.3 BRONZE LAYER
    # --------------------------------------------------
    # Preserve source records and add ingestion metadata.

    for name, rows in (
        ("customers", customers),
        ("products", products),
        ("orders", orders),
    ):

        bronze_rows = [
            {
                **row,
                "_source_file": f"data/sample/{name}.csv",
                "_ingested_at": run_started,
            }
            for row in rows
        ]

        _write_csv(
            bronze_run / f"{name}.csv",
            bronze_rows
        )

    # Preserve order events in Bronze.

    bronze_events = [
        {
            **row,
            "_source_file": "data/sample/order_events.jsonl",
            "_ingested_at": run_started,
        }
        for row in events
    ]

    _write_jsonl(
        bronze_run / "order_events.jsonl",
        bronze_events
    )

    # --------------------------------------------------
    # 4.4 SILVER LAYER - ORDER VALIDATION
    # --------------------------------------------------

    customer_ids = {
        row["customer_id"]
        for row in customers
    }

    clean_orders = []
    rejected_orders = []

    for row in orders:

        reason = ""

        if not row.get("order_id"):
            reason = "missing_order_id"

        elif row.get("customer_id") not in customer_ids:
            reason = "unknown_customer_id"

        elif not row.get("order_ts"):
            reason = "missing_order_timestamp"

        elif not _is_valid_timestamp(row["order_ts"]):
            reason = "invalid_order_timestamp"

        if reason:

            rejected_orders.append({
                **row,
                "_reject_reason": reason,
            })

        else:

            clean_orders.append({
                **row,
                "customer_id": int(row["customer_id"]),
            })

    # --------------------------------------------------
    # 4.5 SILVER LAYER - EVENT VALIDATION
    # --------------------------------------------------

    seen_event_ids = set()

    clean_events = []
    rejected_events = []

    for row in events:

        # Reject malformed JSON.
        if "_parse_error" in row:

            rejected_events.append({
                **row,
                "_reject_reason": "invalid_json",
            })

            continue

        event_id = row.get("event_id")

        # Reject missing event IDs.
        if not event_id:

            rejected_events.append({
                **row,
                "_reject_reason": "missing_event_id",
            })

        # Reject duplicate event IDs.
        elif event_id in seen_event_ids:

            rejected_events.append({
                **row,
                "_reject_reason": "duplicate_event_id",
            })

        else:

            seen_event_ids.add(event_id)
            clean_events.append(row)

    # --------------------------------------------------
    # 4.6 WRITE SILVER OUTPUTS
    # --------------------------------------------------

    _write_csv(
        silver_run / "orders.csv",
        clean_orders
    )

    _write_jsonl(
        silver_run / "order_events.jsonl",
        clean_events
    )

    # --------------------------------------------------
    # 4.7 WRITE REJECTS / QUARANTINE OUTPUTS
    # --------------------------------------------------

    _write_csv(
        rejects_run / "orders.csv",
        rejected_orders
    )

    _write_jsonl(
        rejects_run / "order_events.jsonl",
        rejected_events
    )

    # --------------------------------------------------
    # 4.8 GOLD LAYER - DAILY ORDER METRICS
    # --------------------------------------------------

    metrics = {}

    for row in clean_orders:

        day = datetime.fromisoformat(
            row["order_ts"].replace("Z", "+00:00")
        ).date().isoformat()

        key = (
            day,
            row["order_status"]
        )

        metrics[key] = metrics.get(key, 0) + 1

    gold_rows = [
        {
            "order_date": day,
            "order_status": status,
            "order_count": count,
        }
        for (day, status), count in sorted(metrics.items())
    ]

    _write_csv(
        gold_run / "daily_order_counts.csv",
        gold_rows,
        [
            "order_date",
            "order_status",
            "order_count",
        ],
    )

    # --------------------------------------------------
    # 4.9 OBSERVABILITY SUMMARY
    # --------------------------------------------------

    summary = {

        "run_id": run_id,

        "run_started_at": run_started,

        "run_status": "success",

        "source_counts": {
            "customers": len(customers),
            "products": len(products),
            "orders": len(orders),
            "order_events": len(events),
        },

        "silver_counts": {
            "orders": len(clean_orders),
            "order_events": len(clean_events),
        },

        "reject_counts": {
            "orders": len(rejected_orders),
            "order_events": len(rejected_events),
        },

        "gold_daily_order_groups": len(gold_rows),
    }

    summary_json = json.dumps(
        summary,
        indent=2
    )

    # --------------------------------------------------
    # 4.10 SAVE INDIVIDUAL RUN MANIFEST
    # --------------------------------------------------

    run_manifest = run_history / f"{run_id}.json"

    run_manifest.write_text(
        summary_json + "\n",
        encoding="utf-8",
    )

    # --------------------------------------------------
    # 4.11 UPDATE LATEST RUN MANIFEST
    # --------------------------------------------------

    latest_run = RUNS / "latest_run.json"

    latest_run.write_text(
        summary_json + "\n",
        encoding="utf-8",
    )

    # Return execution summary.
    return summary
