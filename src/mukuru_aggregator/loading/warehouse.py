import logging
import pandas as pd
import re
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from mukuru_aggregator.config import (
    DB_SERVER,
    DB_NAME,
    DB_DRIVER,
    DB_TRUSTED_CONNECTION,
    DB_ENCRYPT,
    DB_TRUST_SERVER_CERTIFICATE,
)


logger = logging.getLogger(__name__)


def create_engine_connection():
    connection_url = URL.create(
        "mssql+pyodbc",
        query={
            "driver": DB_DRIVER,
            "trusted_connection": DB_TRUSTED_CONNECTION,
            "Encrypt": DB_ENCRYPT,
            "TrustServerCertificate": DB_TRUST_SERVER_CERTIFICATE,
        },
        host=DB_SERVER,
        database=DB_NAME,
    )

    engine = create_engine(connection_url)

    logger.info("SQLAlchemy engine created for database: %s", DB_NAME)

    return engine


# Starting from warehouse.py, Python navigates to the mukuru_aggregator package directory, then into sql, and locates the file.
# This works regardless of which directory you launch the program from.
# parents[0] = loading , parents[1] = warehouse   with reference to starting point  warehouse.py

def drop_staging_tables(engine) -> None:
    sql_file = (
        Path(__file__).resolve().parents[1]
        / "sql"
        / "drop_staging_tables.sql"
    )

    sql_script = sql_file.read_text(encoding="utf-8")

    # Extract table names from DROP TABLE statements
    staging_tables = re.findall(
        r"DROP\s+TABLE\s+IF\s+EXISTS\s+([^\s;]+)",
        sql_script,
        flags=re.IGNORECASE,
    )

    with engine.begin() as connection:
        connection.exec_driver_sql(sql_script)

    logger.info(
        "Staging tables dropped successfully: %s",
        staging_tables,
    )



def create_staging_tables(engine) -> None:
    sql_file = (
        Path(__file__).resolve().parents[1]
        / "sql"
        / "create_staging_tables.sql"
    )

    sql_script = sql_file.read_text(encoding="utf-8")

    # Extract table names from CREATE TABLE statements
    staging_tables = re.findall(
        r"CREATE\s+TABLE\s+([^\s(]+)",
        sql_script,
        flags=re.IGNORECASE,
    )

    with engine.begin() as connection:
        connection.exec_driver_sql(sql_script)

    logger.info(
        "Staging tables created successfully: %s",
                 staging_tables,
    )



def load_dataframe(dataframe: pd.DataFrame, schema: str, table: str,engine,) -> None:

    # the first character must be a letter or underscore.
    # subsequent characters can be letters, digits or underscores.
    # the entire string must match the pattern.
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", schema):
        raise ValueError(f"Invalid schema name: {schema}")

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table):
        raise ValueError(f"Invalid table name: {table}")

    if dataframe.columns.empty:
        raise ValueError(
            f"Cannot load an empty DataFrame structure into {schema}.{table}"
        )

    columns = dataframe.columns.to_list()

    dataframe.to_sql(
        name=table,
        con=engine,
        schema=schema,
        if_exists="append",
        index=False,
        chunksize=1000,
    )

    logger.info(
        "Loaded %s rows into %s.%s with %s columns: %s",
        len(dataframe),
        schema,
        table,
        len(columns),
        columns,
    )


def load_staging_data(dataframes: dict[str, pd.DataFrame], engine,) -> None:
    table_mapping = {
        "PARTNER ACCOUNTS": "partner_accounts",
        "PARTNERS": "partners",
        "PAYOUT LOCATIONS": "payout_locations",
        "PAYOUT LOCATIONS PRODUCTS": "payout_locations_products",
        "PRODUCTS": "products",
        "PROVIDERS": "providers",
        "TRANSACTIONS": "transactions",
    }

    missing_sheets = set(table_mapping) - set(dataframes)

    if missing_sheets:
        raise ValueError(
            f"Missing required DataFrames for sheets: {sorted(missing_sheets)}"
        )

    for sheet_name, table_name in table_mapping.items():
        dataframe = dataframes[sheet_name]

        load_dataframe(
            dataframe=dataframe,
            schema="stg",
            table=table_name,
            engine=engine,
        )

    logger.info("All staging DataFrames loaded successfully")