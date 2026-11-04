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


# Read every worksheet into memory.
# Returns sheet name -> DataFrame. The caller (see __main__) passes the path.
#
# pd.ExcelFile opens the workbook once. pd.read_excel then reads one sheet
# from that open workbook, so the file is not reopened for every sheet.
def extract_data(file_path: Path) -> dict[str, pd.DataFrame]:

    _validate_file(file_path)

    workbook = pd.ExcelFile(file_path)

    logger.info(
        "Workbook sheet_names: %s",
        workbook.sheet_names,
    )

    # Key is the sheet name. Value is that sheet's rows.
    data: dict[str, pd.DataFrame] = {}

    for sheet in workbook.sheet_names:
        # A single sheet_name always returns one DataFrame. cast tells the
        # type checker that, because read_excel's declared return type also
        # covers the case where several sheets are requested at once.
        data[sheet] = cast(
            pd.DataFrame,
            pd.read_excel(workbook, sheet_name=sheet)
        )
    return data


# Log one line per sheet: name and row count. Does not change the data.
# The caller passes the dict returned by extract_data.
def log_extraction_summary(extracted_data: dict[str, pd.DataFrame]) -> None:
    for sheet_name, df in extracted_data.items():
        logger.info(
            "Worksheet extracted successfully: %s, %s records",
            sheet_name,
            len(df),
        )
