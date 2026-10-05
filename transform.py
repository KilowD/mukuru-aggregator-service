import json
import pandas as pd


# Take one PAY_IN_AMOUNT value and extract the amount and currency
def parse_amount(value):

    try:
        amount = json.loads(value) # convert JSON string → Python dictionary.

        return amount["value"], amount["currency"]

    except (json.JSONDecodeError, TypeError, KeyError):

        return None, None


def transform_pay_in_amount(transactions):

    parsed_amounts = (
        transactions["PAY_IN_AMOUNT"]
        .apply(parse_amount)
        .to_list()
    )
    # TWO NEW COLUMNS
    transactions[["PAY_IN_AMOUNT_VALUE", "PAY_IN_AMOUNT_CURRENCY"]] = parsed_amounts

    # convert object PAY_IN_AMOUNT_VALUE to NUMERIC
    transactions["PAY_IN_AMOUNT_VALUE"] = pd.to_numeric(
        transactions["PAY_IN_AMOUNT_VALUE"],
        errors="coerce"
    )

    # convert str DATE to DATETIME
    transactions["CREATED_DATE"] = pd.to_datetime(
        transactions["CREATED_DATE"],
        errors="coerce"
    )

    # PROVIDER_CALCULATION
    provider_data = transform_provider_calculation(transactions)

    transactions = transactions.join(provider_data)

    transactions["RATE_INVERTED"] = (transactions["RATE_INVERTED"].astype("boolean"))

    return transactions



# Take the PROVIDER_CALCULATION column and turn the nested JSON into normal columns.
def transform_provider_calculation(transactions):

    provider_calculations = (
        transactions["PROVIDER_CALCULATION"]
        .apply(
            lambda x: json.loads(x) if pd.notna(x) else None
        )
    )

    # NORMALIZE THE NESTED DICTIONARIES
    normalized = pd.json_normalize(
        provider_calculations.dropna()
    )

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

    # EXTRACT THE SINGLE TRANSACTION FEE
    fees = normalized["fees"].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
    )

    fee_normalized = pd.json_normalize(fees)

    fee_normalized.index = normalized.index

    normalized["TRANSACTION_FEE_VALUE"] = fee_normalized["value"]
    normalized["TRANSACTION_FEE_CURRENCY"] = fee_normalized["currency"]

    # Return only the columns we need
    return normalized[
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

if __name__ == "__main__":

    from mukuru_aggregator.extraction.excel import extract_data

    data = extract_data()

    transactions = data["TRANSACTIONS"]

    transformed = transform_pay_in_amount(transactions)

    print(transformed["PAY_IN_AMOUNT_VALUE"].dtype)