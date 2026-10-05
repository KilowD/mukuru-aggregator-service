import pandas as pd
import logging
import json

from config import FILE_PATH


# CONFIGURE LOGGING
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# EXTRACT
# pd.ExcelFile() → opens/prepares the workbook for access
# pd.read_excel() → reads a specific sheet into a DataFrame

def extract_data():

    workbook = pd.ExcelFile(FILE_PATH)

    logging.info(
        "Workbook sheet_names: %s",
        workbook.sheet_names,
    )

    # create an empty dictionary called data
    data = {}

    # Read each sheet and store the DataFrame in the dictionary.
    # Sheet name = key, DataFrame = value.
    for sheet in workbook.sheet_names:

        data[sheet] = pd.read_excel(
            workbook,
            sheet_name=sheet,
        )

    return data


# RUN EXTRACTION FILE : Only execute the code below if this file is being run directly
if __name__ == "__main__":

    extracted_data = extract_data()

    for sheet_name, df in extracted_data.items():

        logging.info(
            "Worksheet extracted successfully: %s, %s records",
            sheet_name,
            len(df),
        )


