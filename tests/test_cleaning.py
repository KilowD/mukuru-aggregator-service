import pandas as pd
import pytest
from mukuru_aggregator.transformation.cleaning import (
    extract_transaction_fee,
    normalize_provider_calculation,
    parse_amount,
    parse_provider_calculation,
    transform_pay_in_amount,
)


def test_parse_amount():
    value = '{"value": 80.0, "currency": "ZAR"}'

    result = parse_amount(value)

    assert result == (80.0, "ZAR")


def test_transform_pay_in_amount_with_valid_data():
    transactions = pd.DataFrame(
        {
            "PAY_IN_AMOUNT": [
                '{"value": 100.5, "currency": "USD"}',
                '{"value": 200, "currency": "EUR"}',
            ]
        }
    )

    result = transform_pay_in_amount(transactions)

    expected_values = [100.5, 200.0]
    expected_currencies = ["USD", "EUR"]

    assert result["PAY_IN_AMOUNT_VALUE"].tolist() == expected_values
    assert result["PAY_IN_AMOUNT_CURRENCY"].tolist() == expected_currencies


def test_transform_pay_in_amount_with_invalid_json():
    transactions = pd.DataFrame(
        {
            "PAY_IN_AMOUNT": [
                '{"value": "invalid_value", "currency": "USD"}',
                None,
                "{invalid_json}",
            ]
        }
    )

    result = transform_pay_in_amount(transactions)

    assert result["PAY_IN_AMOUNT_VALUE"].isna().tolist() == [True, True, True]
    assert result["PAY_IN_AMOUNT_CURRENCY"].isna().tolist() == [False, True, True]
    assert result["PAY_IN_AMOUNT_CURRENCY"].iloc[0] == "USD"


def test_transform_pay_in_amount_with_missing_columns():
    transactions = pd.DataFrame({"OTHER_COLUMN": [1, 2, 3]})

    with pytest.raises(KeyError, match="Missing required column"):
        transform_pay_in_amount(transactions)


def test_transform_pay_in_amount_with_empty_dataframe():
    transactions = pd.DataFrame(columns=["PAY_IN_AMOUNT"])

    result = transform_pay_in_amount(transactions)

    assert result.empty
    assert "PAY_IN_AMOUNT_VALUE" in result.columns
    assert "PAY_IN_AMOUNT_CURRENCY" in result.columns


def test_transform_pay_in_amount_with_mixed_data_types():
    transactions = pd.DataFrame(
        {
            "PAY_IN_AMOUNT": [
                '{"value": 50, "currency": "GBP"}',
                1234,
                None,
                '{"value": 75.5, "currency": "USD"}',
            ]
        }
    )

    result = transform_pay_in_amount(transactions)


    assert result["PAY_IN_AMOUNT_VALUE"].isna().tolist() == [False, True, True,False]
    assert result["PAY_IN_AMOUNT_VALUE"].dropna().tolist() == [50.0, 75.5]
    assert result["PAY_IN_AMOUNT_CURRENCY"].isna().tolist() == [False, True, True, False]
    assert result["PAY_IN_AMOUNT_CURRENCY"].dropna().tolist() == ["GBP", "USD"]

# Does parse_provider_calculation() correctly convert each JSON string into a Python dictionary?
def test_parse_provider_calculation():
    values = pd.Series(
        [
            '{"rate": {"rate": 17.5}}',
            '{"rate": {"rate": 18.2}}',
        ]
    )

    result = parse_provider_calculation(values)

    assert result.iloc[0] == {"rate": {"rate": 17.5}}
    assert result.iloc[1] == {"rate": {"rate": 18.2}}


def test_parse_provider_calculation_with_invalid_data():

    values = pd.Series(
        [
            "{invalid_json}",
            None,
            12345,
        ]
    )

    result = parse_provider_calculation(values)

    assert result.iloc[0] is None
    assert result.iloc[1] is None
    assert result.iloc[2] is None


def test_normalize_provider_calculation():

    provider_calculations = pd.Series(
        {
            10: {
                "rate": {
                    "rate": 17.5,
                    "inverted": False,
                    "payOutCurrency": "ZAR",
                    "settlementCurrency": "USD",
                },
                "payoutAmount": {
                    "value": 1750.0,
                    "currency": "ZAR",
                },
                "settlementAmount": {
                    "value": 100.0,
                    "currency": "USD",
                },
                "fees": [
                    {
                        "value": 5.00,
                        "currency": "ZAR",
                    }
                ],
            }
        }
    )

    result = normalize_provider_calculation(provider_calculations)

    assert result.loc[10, "RATE"] == 17.5
    assert result.loc[10, "RATE_INVERTED"] == False
    assert result.loc[10, "PAYOUT_CURRENCY"] == "ZAR"
    assert result.loc[10, "SETTLEMENT_CURRENCY"] == "USD"
    assert result.loc[10, "PAYOUT_AMOUNT_VALUE"] == 1750.0
    assert result.loc[10, "PAYOUT_AMOUNT_CURRENCY"] == "ZAR"
    assert result.loc[10, "SETTLEMENT_AMOUNT_VALUE"] == 100.0
    assert result.loc[10, "SETTLEMENT_AMOUNT_CURRENCY"] == "USD"
    assert isinstance(result.loc[10, "fees"], list)

    assert result.loc[10, "fees"] == [
        {
            "value": 5.00,
            "currency": "ZAR",
        }
    ]

    assert result.index.tolist() == [10]


def test_extract_transaction_fee():

    normalized = pd.DataFrame(
        {
            "fees": [
                [
                    {
                        "value": 5.00,
                        "currency": "ZAR",
                    }
                ]
            ]
        },
        index=[10],
    )

    result = extract_transaction_fee(normalized)

    assert result.loc[10, "TRANSACTION_FEE_VALUE"] == 5.00
    assert result.loc[10, "TRANSACTION_FEE_CURRENCY"] == "ZAR"

    assert result.index.tolist() == [10]


def test_extract_transaction_fee_with_empty_fees():

    normalized = pd.DataFrame(
        {
            "fees": [
                []
            ]
        },
        index=[10],
    )

    result = extract_transaction_fee(normalized)

    assert pd.isna(result.loc[10, "TRANSACTION_FEE_VALUE"])
    assert pd.isna(result.loc[10, "TRANSACTION_FEE_CURRENCY"])


def test_extract_transaction_fee_uses_first_fee():

    normalized = pd.DataFrame(
        {
            "fees": [
                [
                    {
                        "value": 5.00,
                        "currency": "ZAR",
                    },
                    {
                        "value": 2.00,
                        "currency": "USD",
                    },
                ]
            ]
        },
        index=[10],
    )

    result = extract_transaction_fee(normalized)

    assert result.loc[10, "TRANSACTION_FEE_VALUE"] == 5.00
    assert result.loc[10, "TRANSACTION_FEE_CURRENCY"] == "ZAR"