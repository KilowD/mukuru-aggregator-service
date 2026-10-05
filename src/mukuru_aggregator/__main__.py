import logging

from mukuru_aggregator.config import FILE_PATH
from mukuru_aggregator.extraction.excel import (
    extract_data,
    log_extraction_summary,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> None:
    extracted_data = extract_data(FILE_PATH)

    log_extraction_summary(extracted_data)


if __name__ == "__main__":
    main()