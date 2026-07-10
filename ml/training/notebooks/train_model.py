import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    ConfusionMatrixDisplay
)

import matplotlib.pyplot as plt

# ==============================
# Load Dataset
# ==============================

DATASET_PATH = "ml/training/notebooks/datasets/processed/cleaned_dataset.csv"

df = pd.read_csv(DATASET_PATH, low_memory=False)
df.replace("?", 0, inplace=True)
print(df.head())
print(df.columns.tolist())
print(df["class"].head(10))

# ==============================
# Features and Labels
# ==============================

# ==============================
# Features and Labels
# ==============================

X = df.drop("class", axis=1)

X = X.apply(pd.to_numeric, errors="coerce")

X = X.fillna(0)
y = df["class"]

print(df["class"].unique())

# ==============================
# Split Dataset
# ==============================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ==============================
# Train Model
# ==============================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# ==============================
# Predictions
# ==============================

predictions = model.predict(X_test)

# ==============================
# Evaluation
# ==============================

accuracy = accuracy_score(y_test, predictions)
precision = precision_score(y_test, predictions)
recall = recall_score(y_test, predictions)
f1 = f1_score(y_test, predictions)

print("\n========== MODEL RESULTS ==========")
print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")

# ==============================
# Confusion Matrix
# ==============================

cm = confusion_matrix(y_test, predictions)

disp = ConfusionMatrixDisplay(confusion_matrix=cm)

disp.plot()

plt.savefig("confusion_matrix.png")

print("\nConfusion matrix saved!")

# ==============================
# Save Model
# ==============================

from pathlib import Path

MODEL_DIR = Path("ml/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

joblib.dump(model, MODEL_DIR / "spyware_classifier.joblib")

print("Model saved successfully!")

print("Model saved successfully!")