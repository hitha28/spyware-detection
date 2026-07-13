"""
Feature Extraction Module

Converts static analysis indicators into numerical feature vectors
that can be fed into the ML model.
"""

from typing import List

FEATURES = [
    "SEND_SMS",
    "READ_SMS",
    "RECEIVE_SMS",
    "CAMERA",
    "RECORD_AUDIO",
    "ACCESS_FINE_LOCATION",
    "ACCESS_COARSE_LOCATION",
    "READ_CONTACTS",
    "READ_CALL_LOG",
    "SYSTEM_ALERT_WINDOW",

    "hash_match",
    "yara_match",

    "critical",
    "high",
    "medium",
    "low"
]


def extract_static_features(indicators: List[dict]) -> list:
    """
    Convert indicator list into a numerical feature vector.
    """

    # Initialize all features to 0
    feature_dict = {}

    for feature in FEATURES:
        feature_dict[feature] = 0

    # Process each indicator
    for indicator in indicators:

        source = indicator.get("source", "")
        description = indicator.get("description", "")
        severity = indicator.get("severity", "")

        # Check permissions
        for permission in FEATURES:
            if permission in description:
                feature_dict[permission] = 1

        # Check hash match
        if source == "hash":
            feature_dict["hash_match"] = 1

        # Check YARA match
        if source == "yara":
            feature_dict["yara_match"] = 1

        # Check severity
        if severity in feature_dict:
            feature_dict[severity] = 1

    # Return feature vector
    return [feature_dict[feature] for feature in FEATURES]