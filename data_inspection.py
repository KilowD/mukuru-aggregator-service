import pandas as pd
import logging

from src.mukuru_aggregator.config import FILE_PATH



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

    # # PROFILE EACH DATAFRAME
    for sheet_name, df in extracted_data.items():

        print(f"\n-----{sheet_name}-----")
        df.info()
        print(f"\n-----{sheet_name}-----STRUCTURE")
        print(df.shape)

    # Profile the transaction statuses
    transactions = extracted_data["TRANSACTIONS"]

    for x in ["SOURCE_OF_FUNDS","ORDER_PURPOSE","STATUS"]:
        print("\n\n---profile the categorical columns---")
        print(f"\n---{x}---")
        print(transactions[x].value_counts(dropna=False))
        print()

    # NULL PROFILING
    print("\n\n ---check nulls across the transaction columns---")
    print(transactions.isna().sum())

    print("\n\n ---null_percentage across the transaction columns---")
    null_percentage = (
            transactions.isna().sum()
            / len(transactions)
            * 100
    )

    print(null_percentage)

    print("\n\n ---CREATED DATE PROFILING---")
    print(transactions["CREATED_DATE"].dtype)
    print("\n\n ---ACTUAL DATE VALUES---")
    print(transactions["CREATED_DATE"].head())

    created_dates = pd.to_datetime(
        transactions["CREATED_DATE"],
        errors="coerce"
    )

    print("\n\n ---DATE RANGE---")
    print("Earliest transaction:", created_dates.min())
    print("Latest transaction:", created_dates.max())
    print("Invalid dates:", created_dates.isna().sum())

    print("\n\n ---TRANSACTION AMOUNT PROFILING---")
    print(transactions["PAY_IN_AMOUNT"].dtype)
    print("\n\n ---ACTUAL PAY_IN_AMOUNT VALUES---")
    print(
        transactions["PAY_IN_AMOUNT"].iloc[0]
    )

    print()
    print(transactions["STATUS"].unique())

    print()
    print(transactions["COLLECTION_INSTRUCTIONS"].iloc[0])
    print(type(transactions["COLLECTION_INSTRUCTIONS"].iloc[0]))

    print()
    # print(transactions["PROVIDER_CALCULATION"].iloc[0])
    # print(type(transactions["PROVIDER_CALCULATION"].iloc[0]))

    import json

    provider_calculation = json.loads(
        transactions["PROVIDER_CALCULATION"].iloc[0]
    )

    print(provider_calculation.keys())
    print(type(provider_calculation["fees"]))
    print(type(provider_calculation["rate"]))
    print(type(provider_calculation["payoutAmount"]))
    print(type(provider_calculation["settlementAmount"]))

    print()
    print(
        transactions["PROVIDER_CALCULATION"]
        .dropna()
        .apply(json.loads)
        .apply(lambda x: len(x["fees"]))
        .value_counts()
    )
    print()
    print(
        transactions["PROVIDER_CALCULATION"]
        .dropna()
        .apply(json.loads)
        .apply(lambda x: x["fees"][0])
        .value_counts()
    )
    print()
    print(
        transactions["PROVIDER_CALCULATION"]
        .dropna()
        .apply(json.loads)
        .apply(lambda x: x["fees"][0]["name"])
        .value_counts()
    )

    provider_calculations = (
        transactions["PROVIDER_CALCULATION"]
        .dropna()
        .apply(json.loads)
    )

    normalized = pd.json_normalize(provider_calculations)

    print(normalized.columns.tolist())
    print(normalized.head(1).T)






