
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = ROOT / "data" / "Online Retail.xlsx"
OUTPUT_DIR = ROOT / "data" / "processed"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(RAW_FILE)
    df.columns = df.columns.str.strip()

    # Retain the original Excel row number for traceability.
    df.insert(0, "SourceRowNumber", range(2, len(df) + 2))

    # Compare all original business columns, excluding row number.
    business_columns = [
        column for column in df.columns
        if column != "SourceRowNumber"
    ]

    duplicate_mask = df.duplicated(
        subset=business_columns,
        keep="first",
    )

    duplicate_review = df.loc[duplicate_mask].copy()
    deduplicated = df.loc[~duplicate_mask].copy()

    duplicate_review["ReviewReason"] = (
        "Exact match to an earlier source row; "
        "review before treating as an erroneous duplicate."
    )

    deduplicated.to_csv(
        OUTPUT_DIR / "retail_deduplicated.csv",
        index=False,
    )

    duplicate_review.to_csv(
        OUTPUT_DIR / "duplicate_review.csv",
        index=False,
    )

    assert len(deduplicated) + len(duplicate_review) == len(df)
    assert not deduplicated.duplicated(
        subset=business_columns
    ).any()

    print("\n--- DEDUPLICATION SUMMARY ---")
    print(f"Source rows: {len(df):,}")
    print(f"Deduplicated output rows: {len(deduplicated):,}")
    print(f"Rows sent for duplicate review: {len(duplicate_review):,}")
    print("Row-count reconciliation passed.")
    print("Raw source workbook was not modified.")


if __name__ == "__main__":
    main()
