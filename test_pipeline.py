
import os

import psycopg
import pytest
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "retail_analytics"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}


@pytest.fixture(scope="module")
def connection():
    """Provide a PostgreSQL connection for the test module."""
    with psycopg.connect(**DB_CONFIG) as conn:
        yield conn


# ==================================================
# 1. Original pipeline tests
# ==================================================

def test_raw_table_has_expected_row_count(connection):
    with connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM raw_retail_transactions")
        assert cur.fetchone()[0] == 536641


def test_source_row_numbers_are_unique(connection):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*), COUNT(DISTINCT source_row_number)
            FROM raw_retail_transactions
        """)
        total_rows, unique_rows = cur.fetchone()
        assert total_rows == unique_rows


def test_analytics_view_matches_raw_table(connection):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT
                (SELECT COUNT(*) FROM raw_retail_transactions),
                (SELECT COUNT(*) FROM retail_transaction_analytics)
        """)
        raw_count, view_count = cur.fetchone()
        assert raw_count == view_count


def test_missing_customer_ids_are_preserved(connection):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM raw_retail_transactions
            WHERE customer_id IS NULL
        """)
        assert cur.fetchone()[0] == 135037


def test_successful_load_has_valid_fingerprint(connection):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT rows_loaded, load_status, file_sha256
            FROM pipeline_loads
            WHERE load_name = 'retail_deduplicated_v1'
        """)
        result = cur.fetchone()

        assert result is not None
        rows_loaded, load_status, file_sha256 = result

        assert rows_loaded == 536641
        assert load_status == "SUCCESS"
        assert file_sha256 is not None

        fingerprint = file_sha256.strip()
        assert len(fingerprint) == 64
        assert all(
            character in "0123456789abcdefABCDEF"
            for character in fingerprint
        )


# ==================================================
# 2. Warehouse tests
# ==================================================

def test_fact_table_has_expected_row_count(connection):
    with connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM fact_retail_transactions")
        assert cur.fetchone()[0] == 536641


def test_fact_table_source_rows_are_unique(connection):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*), COUNT(DISTINCT source_row_number)
            FROM fact_retail_transactions
        """)
        total_rows, unique_sources = cur.fetchone()
        assert total_rows == unique_sources


def test_fact_table_has_no_orphaned_dimension_keys(connection):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM fact_retail_transactions f
            LEFT JOIN dim_product p
                ON f.product_key = p.product_key
            LEFT JOIN dim_customer c
                ON f.customer_key = c.customer_key
            LEFT JOIN dim_date d
                ON f.date_key = d.date_key
            WHERE p.product_key IS NULL
               OR c.customer_key IS NULL
               OR d.date_key IS NULL
        """)
        assert cur.fetchone()[0] == 0


def test_missing_customers_map_to_unknown_dimension(connection):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM fact_retail_transactions f
            JOIN raw_retail_transactions r
                ON r.source_row_number = f.source_row_number
            JOIN dim_customer c
                ON c.customer_key = f.customer_key
            WHERE r.customer_id IS NULL
              AND c.customer_id IS NOT NULL
        """)
        assert cur.fetchone()[0] == 0


# ==================================================
# 3. Raw-to-fact reconciliation tests
# ==================================================

def test_every_raw_transaction_has_a_fact_row(connection):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM raw_retail_transactions r
            LEFT JOIN fact_retail_transactions f
                ON f.source_row_number = r.source_row_number
            WHERE f.source_row_number IS NULL
        """)
        assert cur.fetchone()[0] == 0


def test_raw_and_fact_transaction_values_match(connection):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM raw_retail_transactions r
            JOIN fact_retail_transactions f
                ON f.source_row_number = r.source_row_number
            WHERE f.invoice_no IS DISTINCT FROM r.invoice_no
               OR f.invoice_date IS DISTINCT FROM r.invoice_date
               OR f.quantity IS DISTINCT FROM r.quantity
               OR f.unit_price IS DISTINCT FROM r.unit_price
               OR f.line_value IS DISTINCT FROM
                  (r.quantity::NUMERIC * r.unit_price)
        """)
        assert cur.fetchone()[0] == 0


# ==================================================
# 4. Monthly analytics test
# ==================================================

def test_monthly_analysis_reconciles_to_fact_table(connection):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT
                (SELECT COUNT(*)
                 FROM fact_retail_transactions),
                (SELECT COALESCE(SUM(monthly_count), 0)
                 FROM (
                     SELECT COUNT(*) AS monthly_count
                     FROM fact_retail_transactions f
                     JOIN dim_date d
                         ON f.date_key = d.date_key
                     GROUP BY d.year, d.month
                 ) AS monthly_totals)
        """)
        fact_count, monthly_count = cur.fetchone()

        assert fact_count == monthly_count
