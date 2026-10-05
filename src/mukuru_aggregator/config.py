import os

from dotenv import load_dotenv
from sqlalchemy import create_engine


# LOAD CONFIGURATION
# Values from .env are loaded into the environment.
# If a value is not defined, use the default below.
load_dotenv()


# CONFIGURATION
FILE_PATH = os.getenv(
    "FILE_PATH",
    r"C:\Users\sinyo\Downloads\Aggregator Service STAGE Data.xlsx",
)

DB_SERVER = os.getenv(
    "DB_SERVER",
    "localhost",
)

DB_NAME = os.getenv(
    "DB_NAME",
    "Mukuru_db",
)

DB_DRIVER = os.getenv(
    "DB_DRIVER",
    "ODBC Driver 18 for SQL Server",
)


# DATABASE ENGINE CREATION
engine = create_engine(
    f"mssql+pyodbc://{DB_SERVER}/{DB_NAME}"
    f"?driver={DB_DRIVER.replace(' ', '+')}"
    "&trusted_connection=yes"
    "&TrustServerCertificate=yes"
)