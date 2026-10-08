from pathlib import Path

import pandas as pd
import pytest
import logging

from mukuru_aggregator.extraction.excel import (
    _validate_file,
    extract_data,
    log_extraction_summary,
)


def test_validate_file_exists(tmp_path: Path) -> None:
    test_file = tmp_path / "test.xlsx"  # this creates a path to the folder where file will be stored

    test_file.touch()  #Create an empty file here

    _validate_file(test_file)


def test_validate_file_missing(tmp_path: Path) -> None:
    test_file = tmp_path / "missing.xlsx"

    with pytest.raises(FileNotFoundError):
        _validate_file(test_file)


def test_extract_data(tmp_path: Path) -> None:
    test_file = tmp_path / "test.xlsx"

    customers = pd.DataFrame(
        {
            "name": ["Admire", "John"],
            "amount": [500, 300],
        }
    )

    products = pd.DataFrame(
        {
            "product": ["A", "B"],
        }
    )

    with pd.ExcelWriter(test_file) as writer:
        customers.to_excel(
            writer,
            sheet_name="CUSTOMERS",
            index=False,
        )

        products.to_excel(
            writer,
            sheet_name="PRODUCTS",
            index=False,
        )

    result = extract_data(test_file)

    # Is this object an instance of this type?
    # Is result a dictionary?
    assert isinstance(result, dict)  # assert means I expect result to be a dictionary."

    # Did I get a dictionary containing the two sheets?"
    assert "CUSTOMERS" in result
    assert "PRODUCTS" in result

    # Are the values inside that dictionary actually DataFrames
    assert isinstance(result["CUSTOMERS"], pd.DataFrame)
    assert isinstance(result["PRODUCTS"], pd.DataFrame)

    # Test the number of rows
    assert len(result["CUSTOMERS"]) == 2
    assert len(result["PRODUCTS"]) == 2

    # Test the actual values
    # I expect the DataFrame returned by extract_data() to be exactly equal to the DataFrame I originally created.
    pd.testing.assert_frame_equal(
        result["CUSTOMERS"],
        customers,
    )

    pd.testing.assert_frame_equal(
        result["PRODUCTS"],
        products,
    )


def test_extract_data_file_missing(tmp_path: Path) -> None:
    test_file = tmp_path / "missing.xlsx"

    with pytest.raises(FileNotFoundError):
        extract_data(test_file)


def test_log_extraction_summary(caplog) -> None:

    caplog.set_level(logging.INFO)
    data = {
        "CUSTOMERS": pd.DataFrame(
            {
                "name": ["Admire", "John"],
            }
        ),
        "PRODUCTS": pd.DataFrame(
            {
                "product": ["A", "B", "C"],
            }
        ),
    }

    log_extraction_summary(data)

    assert "Worksheet extracted successfully: CUSTOMERS, 2 records" in caplog.text
    assert "Worksheet extracted successfully: PRODUCTS, 3 records" in caplog.text