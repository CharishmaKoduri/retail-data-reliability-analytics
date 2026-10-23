
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "Online Retail.xlsx"
REPORT_FILE = PROJECT_ROOT / "data_quality_report.csv"


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    df = pd.read_excel(DATA_FILE)

    # Normalize column names for reliable access.
    df.columns = df.columns.str.strip()

    required_columns = {
        "InvoiceNo",
        "StockCode",
        "Quantity",
        "InvoiceDate",
        "UnitPrice",
        "CustomerID",
    }

    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Expected columns are missing: {sorted(missing_columns)}"
        )

    checks = {
        "total_rows": len(df),
        "exact_duplicate_rows": int(df.duplicated().sum()),
        "missing_invoice_numbers": int(df["InvoiceNo"].isna().sum()),
        "missing_product_codes": int(df["StockCode"].isna().sum()),
        "missing_transaction_dates": int(df["InvoiceDate"].isna().sum()),
        "missing_customer_ids": int(df["CustomerID"].isna().sum()),
        "missing_unit_prices": int(df["UnitPrice"].isna().sum()),
        "missing_quantities": int(df["Quantity"].isna().sum()),
        "negative_quantities": int((df["Quantity"] < 0).sum()),
        "zero_quantities": int((df["Quantity"] == 0).sum()),
        "zero_prices": int((df["UnitPrice"] == 0).sum()),
        "negative_prices": int((df["UnitPrice"] < 0).sum()),
        "cancellation_invoice_rows": int(
            df["InvoiceNo"]
            .astype("string")
            .str.startswith("C", na=False)
            .sum()
        ),
    }

    report = pd.DataFrame(
        checks.items(),
        columns=["quality_check", "count"],
    )

    report["percentage_of_rows"] = (
        report["count"] / len(df) * 100
        if len(df) > 0
        else 0
    )

    report.to_csv(REPORT_FILE, index=False)

    print("\n--- DATA QUALITY AUDIT ---")
    print(report.to_string(index=False))
    print(f"\nReport saved to: {REPORT_FILE}")
    print("\nOriginal dataset was not modified.")


if __name__ == "__main__":
    main()
