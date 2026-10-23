
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = ROOT / "data" / "Online Retail.xlsx"
OUTPUT_DIR = ROOT / "data" / "processed"


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Raw dataset not found: {RAW_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(RAW_FILE)
    df.columns = df.columns.str.strip()

    # Preserve source-row traceability.
    df.insert(0, "SourceRowNumber", range(2, len(df) + 2))

    invoice = df["InvoiceNo"].astype("string").str.strip()
    quantity = df["Quantity"]
    price = df["UnitPrice"]

    # Classify records without discarding business events.
    df["IsCancellationInvoice"] = invoice.str.startswith(
        "C", na=False
    )
    df["IsReturnOrNegativeQuantity"] = quantity < 0
    df["HasMissingCustomerID"] = df["CustomerID"].isna()
    df["HasZeroUnitPrice"] = price == 0
    df["HasNegativeUnitPrice"] = price < 0

    reasons = pd.Series("", index=df.index, dtype="string")

    def add_reason(mask, reason):
        nonlocal reasons
        reasons = reasons.where(~mask, reasons + reason + "; ")

    # These are initial quarantine rules, not universal business rules.
    add_reason(df["InvoiceNo"].isna(), "MISSING_INVOICE")
    add_reason(df["StockCode"].isna(), "MISSING_PRODUCT_CODE")
    add_reason(df["InvoiceDate"].isna(), "MISSING_INVOICE_DATE")
    add_reason(df["Quantity"].isna(), "MISSING_QUANTITY")
    add_reason(df["UnitPrice"].isna(), "MISSING_UNIT_PRICE")
    add_reason(price < 0, "NEGATIVE_UNIT_PRICE")

    # Keep negative quantities and zero prices for investigation.
    # Do not reject a row solely because CustomerID is missing.
    df["QuarantineReason"] = reasons.str.rstrip("; ")
    df["NeedsQuarantine"] = df["QuarantineReason"].ne("")

    quarantined = df[df["NeedsQuarantine"]].copy()
    accepted = df[~df["NeedsQuarantine"]].copy()

    # Save outputs separately from the immutable raw workbook.
    accepted.to_csv(
        OUTPUT_DIR / "retail_cleaned.csv", index=False
    )
    quarantined.to_csv(
        OUTPUT_DIR / "retail_quarantine.csv", index=False
    )

    summary = pd.DataFrame(
        [
            {"metric": "source_rows", "count": len(df)},
            {"metric": "accepted_rows", "count": len(accepted)},
            {"metric": "quarantined_rows", "count": len(quarantined)},
            {
                "metric": "negative_quantity_rows_preserved",
                "count": int((quantity < 0).sum()),
            },
            {
                "metric": "missing_customer_ids_preserved",
                "count": int(df["CustomerID"].isna().sum()),
            },
        ]
    )

    summary.to_csv(OUTPUT_DIR / "cleaning_summary.csv", index=False)

    print("\n--- CLEANING SUMMARY ---")
    print(summary.to_string(index=False))
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("Raw source file was not modified.")


if __name__ == "__main__":
    main()
