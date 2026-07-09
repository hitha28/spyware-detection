"""
TEMPORARY placeholder for Shreya's ML pipeline (Phase 2).

This exists to unblock Phase 3 (API integration/testing) while the real
ML model is still in progress. It is NOT a trained classifier — just
simple rule-based logic so predict_risk() has something real to call.

Replace this with the real model from ml/training/train_model.py once
it's ready. Function signature should stay the same so nothing else
needs to change.
"""


def predict_risk(features: dict) -> float:
    """
    Fake risk scorer — NOT a trained model.

    Args:
        features: dict of extracted signals, e.g.
            {
                "requests_sms_permission": bool,
                "requests_camera_permission": bool,
                "requests_audio_permission": bool,
                "suspicious_network_activity": bool,
            }

    Returns:
        A float between 0.0 and 1.0 representing estimated risk.
    """
    score = 0.3  # baseline

    if features.get("requests_sms_permission"):
        score += 0.2
    if features.get("requests_camera_permission"):
        score += 0.15
    if features.get("requests_audio_permission"):
        score += 0.15
    if features.get("suspicious_network_activity"):
        score += 0.25

    return min(score, 1.0)