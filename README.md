# Mukuru Aggregator Service

A data pipeline that loads Mukuru aggregator source data from an Excel workbook into SQL Server staging tables, then flattens nested transaction fields so they can be loaded into a data warehouse.

Warehouse loading is not implemented yet. After transformation, the pipeline logs the result and stops.

## What it does

Each run follows this sequence:

1. **Extract.** Read every sheet in the source workbook into a pandas DataFrame, keyed by sheet name.
2. **Stage.** Drop and recreate the `stg` tables, then append each sheet into its matching table.
3. **Transform.** Flatten JSON stored on the transactions sheet into typed columns. This result stays in memory and is not written to the database.

Staging is a full reload. Existing rows in the `stg` tables are removed at the start of every run.

```
Excel workbook
    -> extract_data()
    -> stg.* tables (SQL Server)
    -> transform_transactions()   # in memory only
    -> data warehouse             # not implemented
```

## Source sheets

The workbook must contain these sheets. Names are mapped to staging tables as follows.

| Excel sheet | Staging table |
|---|---|
| PARTNER ACCOUNTS | `stg.partner_accounts` |
| PARTNERS | `stg.partners` |
| PAYOUT LOCATIONS | `stg.payout_locations` |
| PAYOUT LOCATIONS PRODUCTS | `stg.payout_locations_products` |
| PRODUCTS | `stg.products` |
| PROVIDERS | `stg.providers` |
| TRANSACTIONS | `stg.transactions` |

The default file is `data/raw/Aggregator Service STAGE Data.xlsx`. That directory is gitignored.

## Transaction transformation

`transform_transactions` copies the transactions DataFrame and adds columns. Original JSON columns are kept.

| Source column | New columns |
|---|---|
| `PAY_IN_AMOUNT` (JSON `{"value", "currency"}`) | `PAY_IN_AMOUNT_VALUE`, `PAY_IN_AMOUNT_CURRENCY` |
| `PROVIDER_CALCULATION` (nested JSON) | `PAYOUT_AMOUNT_VALUE`, `PAYOUT_AMOUNT_CURRENCY`, `SETTLEMENT_AMOUNT_VALUE`, `SETTLEMENT_AMOUNT_CURRENCY`, `RATE`, `RATE_INVERTED`, `PAYOUT_CURRENCY`, `SETTLEMENT_CURRENCY`, `TRANSACTION_FEE_VALUE`, `TRANSACTION_FEE_CURRENCY` |
| `CREATED_DATE` | Parsed to datetime. Invalid values become null. |

Invalid or empty JSON becomes null rather than failing the run. The fee columns use the first item in the `fees` list.

## Project layout

```
src/mukuru_aggregator/
  __main__.py                 Pipeline entry point
  config.py                   Paths and database settings from the environment
  extraction/excel.py         Workbook validation and sheet reads
  loading/warehouse.py        SQL Server connection and staging load
  sql/drop_staging_tables.sql
  sql/create_staging_tables.sql
  transformation/cleaning.py  Transaction JSON flattening
tests/
  test_excel.py
  test_cleaning.py
```

## Configuration

Settings come from a `.env` file in the project root. `python-dotenv` loads it. If a variable is missing, the default in `config.py` is used.

| Variable | Default | Purpose |
|---|---|---|
| `FILE_PATH` | `data/raw/Aggregator Service STAGE Data.xlsx` | Workbook path, relative to the project root |
| `DB_SERVER` | `localhost` | SQL Server host |
| `DB_NAME` | `Mukuru_db` | Database name |
| `DB_DRIVER` | `ODBC Driver 18 for SQL Server` | ODBC driver name |
| `DB_TRUSTED_CONNECTION` | `yes` | Windows authentication |
| `DB_ENCRYPT` | `yes` | Encrypt the connection |
| `DB_TRUST_SERVER_CERTIFICATE` | `yes` | Trust the server certificate |

The database user connects with Windows authentication. The `stg` schema and an empty database must already exist. This project creates and drops tables inside `stg`; it does not create the database or the schema.

## Run

From the project root, using the project virtual environment (the package is installed there in editable mode):

```powershell
.\.venv\Scripts\python -m mukuru_aggregator
```

Logs go to the console at INFO level. A successful run reports sheet names and row counts, each staging table loaded, and the transformed transaction shape.

## Tests

```powershell
.\.venv\Scripts\python -m pytest
```

`tests/test_excel.py` covers workbook extraction and the missing-file error. `tests/test_cleaning.py` covers amount parsing and provider-calculation flattening. Tests do not connect to SQL Server.

## Requirements

- Python 3.14 or newer (`pyproject.toml`)
- pandas, SQLAlchemy, pyodbc, python-dotenv
- ODBC Driver 18 for SQL Server
- A local SQL Server instance with database `Mukuru_db` and schema `stg`
