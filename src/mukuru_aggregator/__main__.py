import logging

from mukuru_aggregator.config import FILE_PATH
from mukuru_aggregator.loading import (
    create_engine_connection,
    drop_staging_tables,
    create_staging_tables,
    load_staging_data,
)
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
    # 1. Extract the original source data.
    extracted_data = extract_data(FILE_PATH)

    log_extraction_summary(extracted_data)

    # 2. Create the database connection.
    engine = create_engine_connection()

    try:
        # 3. Recreate staging tables.
        drop_staging_tables(engine)
        create_staging_tables(engine)

        # 4. Load the original source data into staging.
        load_staging_data(
            dataframes=extracted_data,
            engine=engine,
        )

        logger.info(
            "All source data loaded into staging successfully"
        )

        # 5. Transform transactions for the data warehouse.
        transformed_transactions = transform_transactions(
            extracted_data["TRANSACTIONS"]
        )

        logger.info(
            "Transactions transformed successfully: %s records, %s columns",
            len(transformed_transactions),
            len(transformed_transactions.columns),
        )

        logger.info(
            "Transformed transaction columns: %s",
            transformed_transactions.columns.tolist(),
        )

        # DW loading will be implemented next.

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()