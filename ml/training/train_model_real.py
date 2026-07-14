"""
Trains a RandomForestClassifier on the REAL Drebin-115 permission dataset
(ml/training/datasets/real_drebin/real_permission_features.csv).

This replaces the synthetic-data model (see train_model.py) with one
trained on genuine, labeled malware/benign Android app data from the
Drebin project (15,036 real apps: 5,560 malware, 9,476 benign).
"""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

DATASET_FILE = Path(__file__).resolve().parent / "datasets" / "real_drebin" / "real_permission_features.csv"
MODEL_OUTPUT = Path(__file__).resolve().parent.parent / "models" / "spyware_classifier.joblib"


def load_dataset() -> tuple:
    """Load the real dataset and split into features (X) and labels (y)."""
    df = pd.read_csv(DATASET_FILE)
    X = df.drop(columns=["label"])
    y = df["label"]
    return X, y


def train_model(X, y) -> RandomForestClassifier:
    """Train a RandomForestClassifier and print a real evaluation."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    print(f"Accuracy on held-out REAL test set: {accuracy_score(y_test, predictions):.4f}")
    print(classification_report(y_test, predictions, target_names=["benign", "malware"]))

    # Show which permissions mattered most — genuinely informative with real data
    importances = pd.Series(model.feature_importances_, index=X.columns)
    print("\nTop 10 most important permissions:")
    print(importances.sort_values(ascending=False).head(10))

    return model


def save_model(model) -> None:
    """Save the trained model to disk with joblib."""
    MODEL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_OUTPUT)
    print(f"\nModel saved to {MODEL_OUTPUT}")


def main():
    X, y = load_dataset()
    model = train_model(X, y)
    save_model(model)


if __name__ == "__main__":
    main()