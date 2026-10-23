
import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "retail_analytics"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}

try:
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), version();")
            database_name, version = cur.fetchone()

            print("Database connection successful!")
            print("Database:", database_name)
            print("PostgreSQL:", version.split(",")[0])

except psycopg.OperationalError as error:
    print("Database connection failed.")
    print("Check PostgreSQL status and credentials.")
    print("Error:", error)
