
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "Online Retail.xlsx"


def main():
    df = pd.read_excel(DATA_FILE)
    df.columns = df.columns.str.strip()

    # Normalize invoice numbers only for identifying cancellations.
    invoice = df["InvoiceNo"].astype("string").str.strip()
    is_cancellation = invoice.str.startswith("C", na=False)

    checks = {
        "Exact duplicate rows": df.duplicated(),
        "Negative quantities": df["Quantity"] < 0,
        "Zero unit prices": df["UnitPrice"] == 0,
        "Negative unit prices": df["UnitPrice"] < 0,
        "Cancellation invoices": is_cancellation,
        "Cancellation and negative quantity": (
            is_cancellation & (df["Quantity"] < 0)
        ),
        "Negative quantity without cancellation invoice": (
            ~is_cancellation & (df["Quantity"] < 0)
        ),
    }

    for label, mask in checks.items():
        print(f"\n--- {label}: {int(mask.sum()):,} rows ---")

        if mask.any():
            print(
                df.loc[mask].head(10).to_string(index=False)
            )
        else:
            print("No matching records.")

    print("\n--- Missing customer ID examples ---")
    print(
        df.loc[df["CustomerID"].isna()]
        .head(10)
        .to_string(index=False)
    )

    print("\nInvestigation complete. No records were changed.")


if __name__ == "__main__":
    main()
