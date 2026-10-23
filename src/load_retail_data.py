
import hashlib
import os
from pathlib import Path

import pandas as pd
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

CSV_PATH = Path("data/processed/retail_deduplicated.csv")
LOAD_NAME = "retail_deduplicated_v1"
BATCH_SIZE = 10_000

# All executions of this loader must use the same lock key.
ADVISORY_LOCK_KEY = 20261023

INSERT_SQL = """
    INSERT INTO raw_retail_transactions (
        source_row_number,
        invoice_no,
        stock_code,
        description,
        quantity,
        invoice_date,
        unit_price,
        customer_id,
        country
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def calculate_sha256(file_path: Path) -> str:
    """Calculate a SHA-256 fingerprint using bounded memory."""
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def count_csv_rows(file_path: Path) -> int:
    """Count CSV data rows without loading the entire file into memory."""
    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        return sum(1 for _ in file) - 1


def main():
    if not CSV_PATH.is_file():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    if not DB_CONFIG["password"]:
        raise RuntimeError(
            "DB_PASSWORD is missing. Check the .env file in your project root."
        )

    file_sha256 = calculate_sha256(CSV_PATH)
    expected_rows = count_csv_rows(CSV_PATH)

    if expected_rows <= 0:
        raise ValueError("The CSV contains no data rows.")

    print("Dataset:", CSV_PATH)
    print("Expected rows:", f"{expected_rows:,}")
    print("SHA-256:", file_sha256)

    loaded_rows = 0
    actual_rows = 0

    # The database transaction commits only after all validations and
    # the successful load-history record have completed.
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:

            # Prevent concurrent executions of this loader from passing
            # the load checks simultaneously. Automatically released
            # when this transaction commits or rolls back.
            cur.execute(
                "SELECT pg_advisory_xact_lock(%s)",
                (ADVISORY_LOCK_KEY,),
            )

            # Check whether this dataset has already been loaded.
            cur.execute(
                """
                SELECT rows_loaded, load_status, file_sha256
                FROM pipeline_loads
                WHERE load_name = %s
                """,
                (LOAD_NAME,),
            )
            previous_load = cur.fetchone()

            if previous_load and previous_load[1] == "SUCCESS":
                previous_hash = (
                    previous_load[2].strip()
                    if previous_load[2] is not None
                    else None
                )

                if previous_hash == file_sha256:
                    raise RuntimeError(
                        "This exact dataset has already been loaded "
                        "successfully. No rows were inserted."
                    )

                raise RuntimeError(
                    "A successful load exists, but its fingerprint differs "
                    "from the current file. The file may have changed. "
                    "No rows were inserted; investigate before loading "
                    "a new version."
                )

            # Do not load over existing data without a matching success record.
            cur.execute(
                "SELECT COUNT(*) FROM raw_retail_transactions"
            )
            existing_rows = cur.fetchone()[0]

            if existing_rows:
                raise RuntimeError(
                    f"The target table already contains {existing_rows:,} "
                    "rows, but no matching successful load record was found. "
                    "Stopping for safety."
                )

            # Stream the source file in batches.
            for chunk in pd.read_csv(
                CSV_PATH,
                chunksize=BATCH_SIZE,
                dtype={
                    "InvoiceNo": "string",
                    "StockCode": "string",
                    "Description": "string",
                    "InvoiceDate": "string",
                    "Country": "string",
                },
            ):
                chunk = chunk.astype(object).where(
                    pd.notna(chunk), None
                )

                records = []

                for row in chunk.itertuples(index=False, name=None):
                    (
                        source_row,
                        invoice_no,
                        stock_code,
                        description,
                        quantity,
                        invoice_date,
                        unit_price,
                        customer_id,
                        country,
                    ) = row

                    records.append(
                        (
                            int(source_row),
                            invoice_no,
                            stock_code,
                            description,
                            int(quantity),
                            pd.Timestamp(invoice_date).to_pydatetime(),
                            (
                                str(unit_price)
                                if unit_price is not None
                                else None
                            ),
                            (
                                int(customer_id)
                                if customer_id is not None
                                else None
                            ),
                            country,
                        )
                    )

                cur.executemany(INSERT_SQL, records)
                loaded_rows += len(records)

                print(
                    f"Processed {loaded_rows:,} / {expected_rows:,} rows..."
                )

            # Validate source processing.
            if loaded_rows != expected_rows:
                raise RuntimeError(
                    f"CSV row-count mismatch: expected {expected_rows:,}, "
                    f"processed {loaded_rows:,}."
                )

            # Validate the target table before recording success.
            cur.execute(
                "SELECT COUNT(*) FROM raw_retail_transactions"
            )
            actual_rows = cur.fetchone()[0]

            if actual_rows != expected_rows:
                raise RuntimeError(
                    f"Database row-count mismatch: expected {expected_rows:,}, "
                    f"found {actual_rows:,}."
                )

            # Record success in the same transaction as the inserted rows.
            cur.execute(
                """
                INSERT INTO pipeline_loads (
                    load_name,
                    source_file,
                    rows_loaded,
                    load_status,
                    file_sha256
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    LOAD_NAME,
                    str(CSV_PATH).replace("\\", "/"),
                    loaded_rows,
                    "SUCCESS",
                    file_sha256,
                ),
            )

    print("\nLoad completed successfully!")
    print(f"Rows processed: {loaded_rows:,}")
    print(f"Rows verified in PostgreSQL: {actual_rows:,}")
    print(f"Load name: {LOAD_NAME}")
    print("Load status: SUCCESS")
    print(f"SHA-256: {file_sha256}")


if __name__ == "__main__":
    main()
