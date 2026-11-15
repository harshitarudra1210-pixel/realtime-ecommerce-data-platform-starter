
import csv
import logging
from pathlib import Path

from src.ingestion.order_ingestion import read_orders
from src.validation.order_validation import validate_order

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Original source file
ORDERS_FILE = PROJECT_ROOT / "data" / "raw" / "orders.csv"

# Rejected records output file
REJECTED_FILE = (
    PROJECT_ROOT / "data" / "rejects" / "rejected_orders.csv"
)


def run_pipeline():

    valid_count = 0
    rejected_orders = []

    logger.info("Order pipeline started")

    for order in read_orders(ORDERS_FILE):

        errors = validate_order(order)

        if errors:
            rejected_order = order.copy()
            rejected_order["_reject_reason"] = "; ".join(errors)

            rejected_orders.append(rejected_order)

            logger.warning(
                "Rejected order %s: %s",
                order.get("order_id", "UNKNOWN"),
                "; ".join(errors)
            )

        else:
            valid_count += 1

            logger.info(
                "Order %s passed validation",
                order["order_id"]
            )

    # Create rejects directory if required
    REJECTED_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Save rejected records
    fieldnames = [
        "order_id",
        "customer_id",
        "product_id",
        "quantity",
        "unit_price",
        "order_date",
        "status",
        "_reject_reason"
    ]

    with REJECTED_FILE.open(
        mode="w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rejected_orders)

    # Pipeline summary
    summary = {
        "source_file": str(ORDERS_FILE),
        "total_orders": valid_count + len(rejected_orders),
        "valid_orders": valid_count,
        "rejected_orders": len(rejected_orders),
        "rejected_file": str(REJECTED_FILE),
        "pipeline_status": "completed"
    }

    logger.info("Pipeline execution completed")
    logger.info("Pipeline summary: %s", summary)

    return summary


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s"
    )

    run_pipeline()
