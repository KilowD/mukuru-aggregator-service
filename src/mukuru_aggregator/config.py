import os
from pathlib import Path

from dotenv import load_dotenv


# LOAD CONFIGURATION
# Values from .env are loaded into the environment.
# If a value is not defined in .env, use the default below.
load_dotenv()


PROJECT_ROOT = Path(__file__).resolve().parents[2]


FILE_PATH = PROJECT_ROOT / os.getenv(
    "FILE_PATH",
    "data/raw/Aggregator Service STAGE Data.xlsx",
)


DB_SERVER = os.getenv("DB_SERVER","localhost",)
DB_NAME = os.getenv("DB_NAME", "Mukuru_db",)
DB_DRIVER = os.getenv("DB_DRIVER","ODBC Driver 18 for SQL Server",)
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "yes")
DB_ENCRYPT = os.getenv("DB_ENCRYPT", "yes")
DB_TRUST_SERVER_CERTIFICATE = os.getenv(
    "DB_TRUST_SERVER_CERTIFICATE",
    "yes",
)