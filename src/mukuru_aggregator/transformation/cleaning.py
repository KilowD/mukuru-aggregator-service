import json
import pandas as pd
import logging


logger = logging.getLogger(__name__)


# Extract the amount and currency from one PAY_IN_AMOUNT JSON value.
def parse_amount(value: str | None,) -> tuple[int | float | str | None, str | None]:
    if not isinstance(value, str) or not value.strip():
        return None, None

    try:
        payload = json.loads(value)
    except json.JSONDecodeError:
        return None, None

    # JSON can be valid while still having the wrong shape, such as a list,
    # scalar, or object with missing or malformed fields.
    if not isinstance(payload, dict):
        return None, None

    amount = payload.get("value")
    currency = payload.get("currency")
    if isinstance(amount, bool) or not isinstance(amount, (int, float, str)):
        amount = None
    if not isinstance(currency, str):
        currency = None

    return amount, currency


def transform_pay_in_amount(transactions: pd.DataFrame) -> pd.DataFrame:
    if "PAY_IN_AMOUNT" not in transactions.columns:
        raise KeyError("Missing required column: PAY_IN_AMOUNT")

    transformed = transactions.copy()
    parsed_amounts = transformed["PAY_IN_AMOUNT"].map(parse_amount).tolist()
    parsed_columns = pd.DataFrame(
        parsed_amounts,
        index=transformed.index,
        columns=["PAY_IN_AMOUNT_VALUE", "PAY_IN_AMOUNT_CURRENCY"],
    )

    transformed[parsed_columns.columns] = parsed_columns
    transformed["PAY_IN_AMOUNT_VALUE"] = pd.to_numeric(
        transformed["PAY_IN_AMOUNT_VALUE"],
        errors="coerce",
    )

    logger.info(
        "PAY_IN_AMOUNT transformed: %s records",
        len(transformed),
    )

    return transformed



def _parse_json(value) -> dict | None:
    if not isinstance(value, str):
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def parse_provider_calculation(values: pd.Series) -> pd.Series:
    return values.map(_parse_json)


def normalize_provider_calculation(provider_calculations: pd.Series) -> pd.DataFrame:

    # NORMALIZE THE NESTED DICTIONARIES
    normalized = pd.json_normalize(provider_calculations.dropna())

    # Keep the original transaction index
    normalized.index = provider_calculations.dropna().index

    # Rename useful columns
    normalized = normalized.rename(
        columns={
            "rate.rate": "RATE",
            "rate.inverted": "RATE_INVERTED",
            "rate.payOutCurrency": "PAYOUT_CURRENCY",
            "rate.settlementCurrency": "SETTLEMENT_CURRENCY",
            "payoutAmount.value": "PAYOUT_AMOUNT_VALUE",
            "payoutAmount.currency": "PAYOUT_AMOUNT_CURRENCY",
            "settlementAmount.value": "SETTLEMENT_AMOUNT_VALUE",
            "settlementAmount.currency": "SETTLEMENT_AMOUNT_CURRENCY",
        }
    )

    return normalized


def extract_transaction_fee(normalized: pd.DataFrame) -> pd.DataFrame:

    # EXTRACT THE SINGLE TRANSACTION FEE
    # take the first element if x is an instance of type list and > 0
    fees = normalized["fees"].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
    )

    # Normalize the fees JSON data into a flat table and reset the index back to the original
    fee_normalized = pd.json_normalize(fees)

    fee_normalized.index = normalized.index

    normalized["TRANSACTION_FEE_VALUE"] = fee_normalized["value"]
    normalized["TRANSACTION_FEE_CURRENCY"] = fee_normalized["currency"]

    return normalized



def transform_provider_calculation(transformed: pd.DataFrame) -> pd.DataFrame:

    provider_calculations = parse_provider_calculation(transformed["PROVIDER_CALCULATION"])

    # NORMALIZE THE NESTED DICTIONARIES AND RENAME the selected columns
    normalized = normalize_provider_calculation(provider_calculations)

    # EXTRACT THE SINGLE TRANSACTION FEE
    normalized  = extract_transaction_fee(normalized)

    # Return only the columns we need
    return normalized [
        [
            "PAYOUT_AMOUNT_VALUE",
            "PAYOUT_AMOUNT_CURRENCY",
            "SETTLEMENT_AMOUNT_VALUE",
            "SETTLEMENT_AMOUNT_CURRENCY",
            "RATE",
            "RATE_INVERTED",
            "PAYOUT_CURRENCY",
            "SETTLEMENT_CURRENCY",
            "TRANSACTION_FEE_VALUE",
            "TRANSACTION_FEE_CURRENCY",
        ]
    ]



def transform_provider_data(transactions: pd.DataFrame) -> pd.DataFrame:

    provider_data = transform_provider_calculation(transactions)

    transformed = transactions.join(provider_data)

    transformed["RATE_INVERTED"] = (
        transformed["RATE_INVERTED"].astype("boolean")
    )

    logger.info(
        "PROVIDER_CALCULATION transformed: %s records, %s columns added",
        len(transformed),
        len(provider_data.columns),
    )

    return transformed



def transform_dates(transactions: pd.DataFrame) -> pd.DataFrame:

    transformed = transactions

    transformed["CREATED_DATE"] = pd.to_datetime(
        transformed["CREATED_DATE"],
        errors="coerce",
    )

    return transformed


def transform_transactions( transactions: pd.DataFrame) -> pd.DataFrame:

    logger.info(
        "Starting transaction transformation: %s records",
        len(transactions),
    )

    transformed = transactions.copy()

    transformed = transform_pay_in_amount(transformed)

    transformed = transform_provider_data(transformed)

    transformed = transform_dates(transformed)

    logger.info(
        "Transaction transformation completed: %s records, %s columns",
        len(transformed),
        len(transformed.columns),
    )

    return transformed
