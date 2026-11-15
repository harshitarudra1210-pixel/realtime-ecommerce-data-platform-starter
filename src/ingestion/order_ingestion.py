
import csv
import logging
from pathlib import Path
from typing import Iterator

# Configure module logger
logger = logging.getLogger(__name__)

# Find project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def read_orders(file_path: Path) -> Iterator[dict]:
    """
    Read e-commerce order data from a CSV file.

    Args:
        file_path: Path to the orders CSV file.

    Yields:
        Each order as a dictionary.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"Orders file not found: {file_path}"
        )

    logger.info("Starting order data ingestion")

    with file_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV file is empty or has no headers")

        for row in reader:
            yield row

    logger.info("Order data ingestion completed")


def main():
    """Run order ingestion."""

    orders_file = PROJECT_ROOT / "data" / "raw" / "orders.csv"

    try:
        for order in read_orders(orders_file):
            print(order)

    except (FileNotFoundError, ValueError) as error:
        logger.error("Ingestion failed: %s", error)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
