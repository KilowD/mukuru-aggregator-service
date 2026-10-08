# File: tests/test_cleaning.py
from json.decoder import NaN

import pandas as pd
import pytest
from src.mukuru_aggregator.transformation.cleaning import transform_pay_in_amount


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