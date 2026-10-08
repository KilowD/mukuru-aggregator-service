import logging

from mukuru_aggregator.config import FILE_PATH
from mukuru_aggregator.extraction import (
    extract_data,
    log_extraction_summary,
)
from mukuru_aggregator.transformation.cleaning import (
    transform_transactions,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> None:
    extracted_data = extract_data(FILE_PATH)

    log_extraction_summary(extracted_data)

    transactions = extracted_data["TRANSACTIONS"]

    transformed = transform_transactions(transactions)

    logger.info(
        "Transactions transformed successfully: %s records",
        len(transformed),
    )


if __name__ == "__main__":
    main()