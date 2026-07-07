"""
Converts StaticAnalysisEngine.analyze() output into a flat list of
{source, description, severity} dicts, ready for Indicator rows.
"""

# Permissions considered risky enough to flag, with an assigned severity.
# Extend this table as the team identifies more indicators worth flagging.
RISKY_PERMISSIONS = {
    "android.permission.READ_SMS": "high",
    "android.permission.SEND_SMS": "high",
    "android.permission.RECEIVE_SMS": "high",
    "android.permission.RECORD_AUDIO": "high",
    "android.permission.CAMERA": "medium",
    "android.permission.ACCESS_FINE_LOCATION": "medium",
    "android.permission.ACCESS_COARSE_LOCATION": "medium",
    "android.permission.READ_CONTACTS": "medium",
    "android.permission.READ_CALL_LOG": "high",
    "android.permission.SYSTEM_ALERT_WINDOW": "medium",
}


def flatten_static_result(raw: dict) -> list[dict]:
    """Take StaticAnalysisEngine.analyze() output and return a flat list
    of indicator dicts: {source, description, severity}."""

    indicators = []
    indicators.extend(_hash_indicators(raw.get("hash_matcher")))
    indicators.extend(_yara_indicators(raw.get("yara")))
    indicators.extend(_apk_indicators(raw.get("analysis"), raw.get("file_type")))
    return indicators


def _hash_indicators(hash_result: dict | None) -> list[dict]:
    """Turn check_hash() output into an indicator, if the file matched."""
    if not hash_result or hash_result.get("status") != "malicious":
        return []

    family = hash_result.get("family") or "unknown family"
    reported_by = hash_result.get("source") or "unknown source"
    return [{
        "source": "hash",
        "description": f"Known-bad hash match: {family} (reported by {reported_by})",
        "severity": "critical",
    }]


def _yara_indicators(yara_result: dict | None) -> list[dict]:
    """Turn YaraScanner.scan() matches into one indicator per matched rule."""
    if not yara_result or yara_result.get("status") != "matched":
        return []

    results = []
    for match in yara_result.get("matches", []):
        rule_name = match.get("rule", "unknown_rule")
        meta = match.get("meta", {})
        # Rule authors can set meta["severity"] in the .yar file itself;
        # fall back to "high" if a rule doesn't define one.
        severity = meta.get("severity", "high")
        description = meta.get("description", f"Matched YARA rule: {rule_name}")
        results.append({
            "source": "yara",
            "description": description,
            "severity": severity,
        })
    return results


def _apk_indicators(analysis: dict | None, file_type: str | None) -> list[dict]:
    """Turn APKAnalyzer.analyze() output into indicators: risky permissions
    and exported components."""
    if not analysis or file_type != "apk" or analysis.get("status") != "analyzed":
        return []

    results = []

    for permission in analysis.get("permissions", []):
        severity = RISKY_PERMISSIONS.get(permission)
        if severity:
            results.append({
                "source": "apk",
                "description": f"Requests risky permission: {permission}",
                "severity": severity,
            })

    for component in analysis.get("exported_components", []):
        results.append({
            "source": "apk",
            "description": f"Exported {component['type']}: {component['name']}",
            "severity": "low",
        })

    return results