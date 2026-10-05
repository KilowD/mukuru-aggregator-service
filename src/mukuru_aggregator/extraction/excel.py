import logging

import pandas as pd


logger = logging.getLogger(__name__)


# EXTRACT
# pd.ExcelFile() → opens/prepares the workbook for access
# pd.read_excel() → reads a specific sheet into a DataFrame

# This function returns a dictionary where the keys are strings and the values are Pandas DataFrames
# FILE_PATH is passed by __main__
def extract_data(file_path: str) -> dict[str, pd.DataFrame]:
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
    for sheet in workbook.sheet_names:

        data[sheet] = pd.read_excel(
            workbook,
            sheet_name=sheet,
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

