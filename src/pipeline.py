"""Small, dependency-free batch pipeline for the starter project."""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample"
BRONZE = ROOT / "data" / "bronze"
SILVER = ROOT / "data" / "silver"
GOLD = ROOT / "data" / "gold"
REJECTS = ROOT / "data" / "rejects"
RUNS = ROOT / "data" / "observability"


def _read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)

    if fields is None:
        fields = list(rows[0]) if rows else []

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def _read_jsonl(path):
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


def _stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _is_valid_timestamp(value):
    """Return True if the timestamp can be parsed."""
    if not value:
        return False

    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def run_pipeline():
    """Ingest source data, create Bronze/Silver/Gold outputs, and report quality."""

    run_started = _stamp()

    for folder in (BRONZE, SILVER, GOLD, REJECTS, RUNS):
        folder.mkdir(parents=True, exist_ok=True)

    customers = _read_csv(SAMPLE / "customers.csv")
    products = _read_csv(SAMPLE / "products.csv")
    orders = _read_csv(SAMPLE / "orders.csv")
    events = _read_jsonl(SAMPLE / "order_events.jsonl")

    # BRONZE: preserve source records and add ingestion lineage.
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

        _write_csv(BRONZE / f"{name}.csv", bronze_rows)

    bronze_events = [
        {
            **row,
            "_source_file": "data/sample/order_events.jsonl",
            "_ingested_at": run_started,
        }
        for row in events
    ]
    _write_jsonl(BRONZE / "order_events.jsonl", bronze_events)

    # SILVER orders: validate required fields and timestamps.
    customer_ids = {row["customer_id"] for row in customers}
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

    # SILVER events: reject malformed JSON, missing IDs, and duplicate IDs.
    seen_event_ids = set()
    clean_events = []
    rejected_events = []

    for row in events:
        if "_parse_error" in row:
            rejected_events.append({
                **row,
                "_reject_reason": "invalid_json",
            })
            continue

        event_id = row.get("event_id")

        if not event_id:
            rejected_events.append({
                **row,
                "_reject_reason": "missing_event_id",
            })
        elif event_id in seen_event_ids:
            rejected_events.append({
                **row,
                "_reject_reason": "duplicate_event_id",
            })
        else:
            seen_event_ids.add(event_id)
            clean_events.append(row)

    # Write Silver and quarantine outputs.
    _write_csv(SILVER / "orders.csv", clean_orders)
    _write_jsonl(SILVER / "order_events.jsonl", clean_events)

    _write_csv(REJECTS / "orders.csv", rejected_orders)
    _write_jsonl(REJECTS / "order_events.jsonl", rejected_events)

    # GOLD: count valid orders by date and status.
    # Revenue is not calculated because sample orders have no amount field.
    metrics = {}

    for row in clean_orders:
        day = datetime.fromisoformat(
            row["order_ts"].replace("Z", "+00:00")
        ).date().isoformat()

        key = (day, row["order_status"])
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
        GOLD / "daily_order_counts.csv",
        gold_rows,
        ["order_date", "order_status", "order_count"],
    )

    # Observability summary for this run.
    summary = {
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

    (RUNS / "latest_run.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    return summary