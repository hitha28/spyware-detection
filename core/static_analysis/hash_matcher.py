import csv
import hashlib
from pathlib import Path


SIGNATURE_DB = (
    Path(__file__).resolve().parent.parent
    / "signatures"
    / "known_bad_hashes.csv"
)


def calculate_sha256(file_path: str) -> str:
    """
    Calculate SHA-256 hash of a file.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(4096):
            sha256.update(chunk)

    return sha256.hexdigest()


def load_hash_database():
    """
    Load known bad hashes from CSV.
    """

    hashes = {}

    with open(SIGNATURE_DB, newline="", encoding="utf-8") as csvfile:

        reader = csv.DictReader(csvfile)

        for row in reader:

            hashes[row["sha256"]] = {
                "family": row["family"],
                "source": row["source"],
            }

    return hashes


def check_hash(file_path: str):
    """
    Compare a file hash against the signature database.
    """

    file_hash = calculate_sha256(file_path)

    database = load_hash_database()

    if file_hash in database:

        return {
            "status": "malicious",
            "sha256": file_hash,
            "family": database[file_hash]["family"],
            "source": database[file_hash]["source"],
        }

    return {
        "status": "clean",
        "sha256": file_hash,
        "family": None,
        "source": None,
    }
