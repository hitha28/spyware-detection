import joblib
import pandas as pd
from pathlib import Path

from ml.training.feature_extraction.feature_extractor import (
    extract_static_features,
    FEATURES
)

# -----------------------------
# Load model and feature names
# -----------------------------

MODEL_DIR = Path("ml/models")

model = joblib.load(MODEL_DIR / "spyware_classifier.joblib")
feature_names = joblib.load(MODEL_DIR / "feature_names.joblib")


def predict_risk(indicators):
    """
    Predict whether an APK is spyware.
    """

    # 16-feature vector from extractor
    extracted = extract_static_features(indicators)

    extracted_dict = dict(zip(FEATURES, extracted))

    # Create all 215 features as zero
    sample = {}

    for feature in feature_names:
        sample[feature] = 0

    # Fill only the features we know
    for feature in FEATURES:
        if feature in sample:
            sample[feature] = extracted_dict[feature]

    X = pd.DataFrame([sample])

    prediction = model.predict(X)[0]

    probability = model.predict_proba(X)[0][1]

    return {
        "prediction": int(prediction),
        "risk_score": float(probability)
    }