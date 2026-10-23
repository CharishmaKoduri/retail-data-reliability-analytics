
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = ROOT / "data" / "Online Retail.xlsx"
OUTPUT_DIR = ROOT / "data" / "processed"

CLEAN_FILE = OUTPUT_DIR / "retail_cleaned.csv"
QUARANTINE_FILE = OUTPUT_DIR / "retail_quarantine.csv"
SUMMARY_FILE = OUTPUT_DIR / "cleaning_summary.csv"


def main():
    raw_rows = len(pd.read_excel(RAW_FILE))

    clean = pd.read_csv(CLEAN_FILE)
    quarantine = pd.read_csv(QUARANTINE_FILE)
    summary = pd.read_csv(SUMMARY_FILE)

    assert len(clean) + len(quarantine) == raw_rows, (
        "Row-count mismatch: output rows do not reconcile."
    )

    assert clean["SourceRowNumber"].is_unique, (
        "Duplicate source row numbers found in cleaned output."
    )

    assert quarantine["SourceRowNumber"].is_unique, (
        "Duplicate source row numbers found in quarantine."
    )

    overlap = set(clean["SourceRowNumber"]) & set(
        quarantine["SourceRowNumber"]
    )
    assert not overlap, "Some source rows appear in both outputs."

    assert clean["QuarantineReason"].astype("string").fillna("").eq("").all(), (
        "Cleaned output contains quarantine reasons."
    )

    assert quarantine["QuarantineReason"].notna().all(), (
        "Quarantined records are missing reasons."
    )

    assert summary.loc[
        summary["metric"] == "source_rows", "count"
    ].iloc[0] == raw_rows

    print("All output validation checks passed.")
    print(f"Source rows: {raw_rows:,}")
    print(f"Cleaned rows: {len(clean):,}")
    print(f"Quarantined rows: {len(quarantine):,}")
    print("No source-row overlap detected.")


if __name__ == "__main__":
    main()
