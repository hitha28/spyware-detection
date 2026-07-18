"""
Converts raw static-analysis output into the shared indicator schema
(source, description, severity) before it's written to the DB.
"""

RISKY_PERMISSIONS = {
    "android.permission.RECORD_AUDIO": "medium",
    "android.permission.CAMERA": "medium",
    "android.permission.READ_SMS": "high",
    "android.permission.ACCESS_FINE_LOCATION": "medium",
    "android.permission.READ_CONTACTS": "medium",
    "android.permission.READ_CALL_LOG": "high",
}


def flatten_static_result(raw: dict) -> list[dict]:
    """Convert StaticAnalysisEngine.analyze() output into a flat list of
    {source, description, severity} indicator dicts."""
    indicators = []
    indicators.extend(_hash_indicators(raw.get("hash_matcher")))
    indicators.extend(_yara_indicators(raw.get("yara")))
    indicators.extend(_apk_indicators(raw.get("analysis"), raw.get("file_type")))
    indicators.extend(_pe_indicators(raw.get("analysis"), raw.get("file_type")))
    return indicators


def _hash_indicators(hash_result: dict | None) -> list[dict]:
    if not hash_result or hash_result.get("status") != "known_bad":
        return []
    return [{
        "source": "hash",
        "description": f"Matches known-bad hash ({hash_result.get('family', 'unknown family')})",
        "severity": "critical",
    }]


def _yara_indicators(yara_result: dict | None) -> list[dict]:
    if not yara_result:
        return []
    results = []
    for match in yara_result.get("matches", []):
        results.append({
            "source": "yara",
            "description": f"Matched YARA rule: {match.get('rule', 'unknown')}",
            "severity": match.get("meta", {}).get("severity", "medium"),
        })
    return results


def _apk_indicators(analysis: dict | None, file_type: str | None) -> list[dict]:
    if not analysis or file_type != "apk":
        return []
    results = []

    for perm in analysis.get("permissions", []):
        if perm in RISKY_PERMISSIONS:
            results.append({
                "source": "apk",
                "description": f"Requests risky permission: {perm}",
                "severity": RISKY_PERMISSIONS[perm],
            })

    for url in analysis.get("embedded_urls", []):
        results.append({
            "source": "apk",
            "description": f"Embedded URL found: {url}",
            "severity": "low",
        })

    for component in analysis.get("exported_components", []):
        results.append({
            "source": "apk",
            "description": f"Exported {component['type']}: {component['name']}",
            "severity": "low",
        })

    return results


def _pe_indicators(analysis: dict | None, file_type: str | None) -> list[dict]:
    """Turn PEAnalyzer.analyze() output into indicators: suspicious imports
    and packer/obfuscation signals."""
    if not analysis or file_type != "pe" or analysis.get("status") != "analyzed":
        return []

    results = []

    for imp in analysis.get("suspicious_imports", []):
        results.append({
            "source": "pe",
            "description": f"Imports {imp['function']} from {imp['dll']} — possible {imp['reason']}",
            "severity": "high",
        })

    if analysis.get("packer_suspected"):
        results.append({
            "source": "pe",
            "description": "Executable shows signs of packing/obfuscation (known packer section or high-entropy code section)",
            "severity": "medium",
        })

    return results