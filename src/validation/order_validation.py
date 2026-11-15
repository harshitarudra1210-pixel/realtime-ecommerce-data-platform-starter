
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


REQUIRED_FIELDS = [
    "order_id",
    "customer_id",
    "product_id",
    "quantity",
    "unit_price",
    "order_date",
    "status",
]

VALID_STATUSES = {"completed", "pending", "cancelled"}


def validate_order(order: dict) -> list:
    """
    Validate a single e-commerce order.

    Returns:
        A list of validation errors.
        Empty list means the order is valid.
    """

    errors = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        if not order.get(field):
            errors.append(f"Missing required field: {field}")

    if errors:
        return errors

    # Validate order ID
    if not order["order_id"].isdigit():
        errors.append("Invalid order_id")

    # Validate quantity
    try:
        quantity = int(order["quantity"])
        if quantity <= 0:
            errors.append("Quantity must be greater than zero")
    except (ValueError, TypeError):
        errors.append("Quantity must be an integer")

    # Validate unit price
    try:
        unit_price = float(order["unit_price"])
        if unit_price < 0:
            errors.append("Unit price cannot be negative")
    except (ValueError, TypeError):
        errors.append("Unit price must be numeric")

    # Validate order date
    try:
        datetime.strptime(order["order_date"], "%Y-%m-%d")
    except (ValueError, TypeError):
        errors.append("Invalid order date format. Expected YYYY-MM-DD")

    # Validate order status
    if order["status"].lower() not in VALID_STATUSES:
        errors.append("Invalid order status")

    return errors


def main():
    """Test order validation with sample data."""

    sample_order = {
        "order_id": "1001",
        "customer_id": "C001",
        "product_id": "P101",
        "quantity": "2",
        "unit_price": "500",
        "order_date": "2026-10-27",
        "status": "completed",
    }

    errors = validate_order(sample_order)

    if errors:
        logger.error("Order validation failed")
        for error in errors:
            logger.error(error)
    else:
        logger.info("Order %s is valid", sample_order["order_id"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
