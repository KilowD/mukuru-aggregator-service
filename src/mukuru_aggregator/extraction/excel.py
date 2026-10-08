import logging
from pathlib import Path
from typing import cast

import pandas as pd


logger = logging.getLogger(__name__)

# Check whether the file exists
def _validate_file(file_path: Path) -> None:
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Excel file not found: {file_path}"
        )

# EXTRACT
# pd.ExcelFile() → opens/prepares the workbook for access
# pd.read_excel() → reads a specific sheet into a DataFrame

# This function returns a dictionary where the keys are strings and the values are Pandas DataFrames
# FILE_PATH is passed by __main__
def extract_data(file_path: Path) -> dict[str, pd.DataFrame]:

    _validate_file(file_path)

    workbook = pd.ExcelFile(file_path)

    logger.info(
        "Workbook sheet_names: %s",
        workbook.sheet_names,
    )

    # Create an empty dictionary where:
    # key = sheet name (str)
    # value = DataFrame
    data: dict[str, pd.DataFrame] = {}

    # Read each sheet and store the DataFrame in the dictionary.
    # Sheet name = key, DataFrame = value.
    # cast signals to typechecker that this is a DataFrame in this case
    for sheet in workbook.sheet_names:

        data[sheet] = cast(
            pd.DataFrame,
            pd.read_excel(workbook,sheet_name=sheet)
        )
    return data

# extracted_data is passed by __main__
def log_extraction_summary(extracted_data: dict[str, pd.DataFrame]) -> None:
    for sheet_name, df in extracted_data.items():
        logger.info(
            "Worksheet extracted successfully: %s, %s records",
            sheet_name,
            len(df),
        )

