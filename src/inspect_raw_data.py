
from pathlib import Path

import pandas as pd


# Find the project directory and raw dataset.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "Online Retail.xlsx"


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {DATA_FILE}\n"
            "Download Online Retail.xlsx into the data folder."
        )

    print("Loading raw retail dataset...")
    df = pd.read_excel(DATA_FILE)

    print("\n--- Dataset overview ---")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\n--- Column names ---")
    print(df.columns.tolist())

    print("\n--- Data types ---")
    print(df.dtypes)

    print("\n--- First five records ---")
    print(df.head().to_string(index=False))

    print("\n--- Missing values per column ---")
    print(df.isna().sum())

    print("\n--- Exact duplicate rows ---")
    print(df.duplicated().sum())

    print("\n--- Numeric summary ---")
    print(df[["Quantity", "UnitPrice"]].describe())


if __name__ == "__main__":
    main()
