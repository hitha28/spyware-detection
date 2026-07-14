"""
TEMPORARY (Phase 2 fallback): loads a RandomForestClassifier trained on
SYNTHETIC data (see ml/training/train_model.py) to unblock Phase 3
integration/testing while Shreya's real ML pipeline is in progress.

Trained only on synthetic, made-up feature patterns — NOT real malware
data. Replace with the real trained model once available, keeping this
same function signature so nothing downstream needs to change.
"""

from pathlib import Path

import joblib
import pandas as pd

from ml.features.extract_static_features import extract_features, FEATURE_NAMES

MODEL_PATH = Path(__file__).resolve().parent / "models" / "spyware_classifier.joblib"

_model = None  # loaded lazily, once, on first use


def _get_model():
    """Load the trained model from disk, caching it after the first load."""
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_risk(raw_static_result: dict) -> float:
    """
    Predict a risk score using the (temporary, synthetic-trained) model.

    Args:
        raw_static_result: the dict returned by StaticAnalysisEngine.analyze()

    Returns:
        A float between 0.0 and 1.0 representing estimated risk.
    """
    features = extract_features(raw_static_result)

    # Ensure feature order matches training data exactly
    ordered_values = pd.DataFrame(
        [[features.get(name, 0) for name in FEATURE_NAMES]],
        columns=FEATURE_NAMES,
    )

    model = _get_model()
    probability_malicious = model.predict_proba(ordered_values)[0][1]

    return float(probability_malicious)