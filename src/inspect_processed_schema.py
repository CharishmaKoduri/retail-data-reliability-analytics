
from pathlib import Path

import pandas as pd

file_path = Path("data/processed/retail_deduplicated.csv")

df = pd.read_csv(file_path, nrows=5)

print("CSV columns:")
for column in df.columns:
    print(f"- {column}: {df[column].dtype}")

print("\nSample records:")
print(df.to_string(index=False))
