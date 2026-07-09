"""
TEMPORARY (Phase 2 fallback): extracts a numeric feature vector from
Shivanshi's static analysis output, for use by the temporary ML stub.

Real Phase 2 (Shreya) may extract richer/different features — this is
a simplified, honest stand-in so the pipeline can be trained and tested
end-to-end in the meantime.
"""

# Permissions considered risky enough to count as features.
# Mirrors api/services/indicator_adapter.py's RISKY_PERMISSIONS list,
# kept separate here since ML features and DB indicators serve different
# purposes even though they overlap conceptually.
RISKY_PERMISSIONS = [
    "android.permission.READ_SMS",
    "android.permission.SEND_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.RECORD_AUDIO",
    "android.permission.CAMERA",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.READ_CONTACTS",
    "android.permission.READ_CALL_LOG",
    "android.permission.SYSTEM_ALERT_WINDOW",
]

# Must match the column order used in ml/training/datasets/synthetic_features.csv
# (excluding the "label" column) — the model expects features in this exact order.
FEATURE_NAMES = [
    "hash_matched",
    "yara_match_count",
    "num_exported_components",
    "num_embedded_urls",
    "perm_read_sms",
    "perm_send_sms",
    "perm_receive_sms",
    "perm_record_audio",
    "perm_camera",
    "perm_access_fine_location",
    "perm_access_coarse_location",
    "perm_read_contacts",
    "perm_read_call_log",
    "perm_system_alert_window",
]
def extract_features(raw_static_result: dict) -> dict:
    """
    Convert StaticAnalysisEngine.analyze() output into a flat numeric
    feature dict, suitable for a simple ML model.

    Args:
        raw_static_result: the dict returned by StaticAnalysisEngine.analyze()

    Returns:
        A dict of numeric/boolean features.
    """
    hash_result = raw_static_result.get("hash_matcher") or {}
    yara_result = raw_static_result.get("yara") or {}
    analysis = raw_static_result.get("analysis") or {}

    permissions = set(analysis.get("permissions", []))

    features = {
        "hash_matched": 1 if hash_result.get("status") == "malicious" else 0,
        "yara_match_count": yara_result.get("match_count", 0),
        "num_exported_components": len(analysis.get("exported_components", [])),
        "num_embedded_urls": len(analysis.get("embedded_urls", [])),
    }

    # One feature per risky permission: 1 if requested, else 0
    for permission in RISKY_PERMISSIONS:
        short_name = permission.split(".")[-1].lower()
        features[f"perm_{short_name}"] = 1 if permission in permissions else 0

    return features