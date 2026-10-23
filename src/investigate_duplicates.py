
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "Online Retail.xlsx"


def main():
    df = pd.read_excel(DATA_FILE)
    df.columns = df.columns.str.strip()

    duplicate_mask = df.duplicated(keep=False)
    duplicates = df.loc[duplicate_mask].sort_values(
        by=["InvoiceNo", "StockCode", "InvoiceDate"]
    )

    print(f"Total source rows: {len(df):,}")
    print(f"Rows belonging to duplicate groups: {len(duplicates):,}")
    print(f"Extra duplicate rows: {df.duplicated().sum():,}")

    print("\n--- Example duplicate groups ---")
    print(duplicates.head(20).to_string(index=False))

    print("\n--- Duplicate counts by invoice ---")
    print(
        duplicates.groupby("InvoiceNo")
        .size()
        .sort_values(ascending=False)
        .head(10)
    )

    print("\nNo records were changed.")


if __name__ == "__main__":
    main()
