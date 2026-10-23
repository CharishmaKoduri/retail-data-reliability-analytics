
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "Online Retail.xlsx"


def main():
    df = pd.read_excel(DATA_FILE)

    # Compare rows using all original source columns.
    duplicate_mask = df.duplicated(keep="first")
    duplicates = df.loc[duplicate_mask].copy()

    df["LineValue"] = df["Quantity"] * df["UnitPrice"]
    duplicates["LineValue"] = (
        duplicates["Quantity"] * duplicates["UnitPrice"]
    )

    print(f"Original rows: {len(df):,}")
    print(f"Extra exact duplicate rows: {len(duplicates):,}")
    print(
        "Rows remaining after hypothetical exact deduplication: "
        f"{len(df) - len(duplicates):,}"
    )

    print("\n--- Duplicate rows by transaction type ---")

    invoice = duplicates["InvoiceNo"].astype("string").str.strip()
    is_cancellation = invoice.str.startswith("C", na=False)

    print(f"Cancellation invoice rows: {int(is_cancellation.sum()):,}")
    print(
        "Negative-quantity rows: "
        f"{int((duplicates['Quantity'] < 0).sum()):,}"
    )
    print(
        "Positive-quantity rows: "
        f"{int((duplicates['Quantity'] > 0).sum()):,}"
    )

    print("\n--- Financial impact of duplicate rows ---")
    print(
        f"Signed line value: {duplicates['LineValue'].sum():,.2f}"
    )
    print(
        "Positive-quantity line value: "
        f"{duplicates.loc[duplicates['Quantity'] > 0, 'LineValue'].sum():,.2f}"
    )
    print(
        "Negative-quantity line value: "
        f"{duplicates.loc[duplicates['Quantity'] < 0, 'LineValue'].sum():,.2f}"
    )

    print("\nNo records were removed or modified.")


if __name__ == "__main__":
    main()
