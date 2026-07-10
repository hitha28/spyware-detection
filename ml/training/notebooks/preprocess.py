import pandas as pd
from pathlib import Path

# ----------------------------
# Project folders
# ----------------------------

BASE_DIR = Path(__file__).resolve().parent

DATASET_DIR = BASE_DIR / "datasets"
RAW_DIR = DATASET_DIR / "raw"
PROCESSED_DIR = DATASET_DIR / "processed"

DATASET_FILE = (
    RAW_DIR
    / "benign"
    / "archive (1)"
    / "drebin-215-dataset-5560malware-9476-benign.csv"
)

print("Dataset location:")
print(DATASET_FILE)

if DATASET_FILE.exists():
    print("\n✅ Dataset found!")
    # Load dataset
    df = pd.read_csv(DATASET_FILE, low_memory=False)
    print("\nRemoving duplicate rows...")
    df = df.drop_duplicates()
    print("Rows after removing duplicates:", df.shape[0])
    print("\nClass distribution:")
    print(df["class"].value_counts())
    print("\nConverting labels...")
    df["class"] = df["class"].map({ "B": 0, "S": 1})
    print(df["class"].value_counts())
    # Create processed folder if it doesn't exist
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE = PROCESSED_DIR / "cleaned_dataset.csv"
    df.to_csv(OUTPUT_FILE, index=False)
    print("\nCleaned dataset saved successfully!")
    print(OUTPUT_FILE)
    print("\nDataset loaded successfully!")
    print("Rows:", df.shape[0])
    print("Columns:", df.shape[1])
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nColumn names:")
    print(df.columns.tolist())
    print("\nMissing values:")
    print(df.isnull().sum().sum())
    print("\nDuplicate rows:")
    print(df.duplicated().sum())
else:
    print("\n❌ Dataset NOT found!")
print(DATASET_FILE)
print("\nFiles inside benign folder:")

benign_folder = RAW_DIR / "benign"

if benign_folder.exists():
    for file in benign_folder.iterdir():
        print(file.name)
else:
    print("❌ Benign folder does not exist!")
