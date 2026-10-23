
import hashlib
from pathlib import Path

CSV_PATH = Path("data/processed/retail_deduplicated.csv")
CHUNK_SIZE = 1024 * 1024  # Read 1 MB at a time


def calculate_sha256(file_path: Path) -> str:
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        while chunk := file.read(CHUNK_SIZE):
            digest.update(chunk)

    return digest.hexdigest()


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {CSV_PATH}")

    fingerprint = calculate_sha256(CSV_PATH)

    print("Dataset:", CSV_PATH)
    print("File size (bytes):", CSV_PATH.stat().st_size)
    print("SHA-256:", fingerprint)


if __name__ == "__main__":
    main()
