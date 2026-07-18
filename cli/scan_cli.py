"""
SpySentinel CLI scanner.

Usage:
    python -m cli.scan_cli --file path/to/app.apk

Runs the same static + ML analysis as the /scan API endpoint, but as a
standalone command-line tool — no server needed. Useful for quick local
checks or for the packaged .exe (see P6-SRE10).
"""

import logging
logging.getLogger("androguard").setLevel(logging.ERROR)

try:
    from loguru import logger as _loguru_logger
    _loguru_logger.remove()
    _loguru_logger.add(lambda msg: None)
except ImportError:
    pass

import argparse
import json
import sys
from pathlib import Path

from core.static_analysis.static_engine import StaticAnalysisEngine
from api.services.indicator_adapter import flatten_static_result
from ml.predict_risk import predict_risk

SEVERITY_WEIGHTS = {
    "critical": 1.0,
    "high": 0.7,
    "medium": 0.4,
    "low": 0.1,
}


def scan(file_path: str) -> dict:
    """Run static + ML analysis on a file and return a result dict."""
    engine = StaticAnalysisEngine()

    try:
        raw_result = engine.analyze(file_path)
    except NotImplementedError as e:
        return {
            "error": "unsupported_file_type",
            "message": str(e),
            "filename": Path(file_path).name,
        }
    except FileNotFoundError:
        return {
            "error": "file_not_found",
            "message": f"File does not exist: {file_path}",
        }

    indicator_dicts = flatten_static_result(raw_result)

    if indicator_dicts:
        static_score = max(
            SEVERITY_WEIGHTS.get(ind["severity"], 0.0) for ind in indicator_dicts
        )
    else:
        static_score = 0.0

    ml_score = predict_risk(raw_result)
    final_score = 0.5 * static_score + 0.5 * ml_score

    return {
        "filename": Path(file_path).name,
        "file_type": raw_result.get("file_type", "unknown"),
        "static_score": static_score,
        "ml_score": ml_score,
        "final_score": final_score,
        "indicators": indicator_dicts,
    }


def print_human_readable(result: dict) -> None:
    """Print the scan result in a readable format for terminal use."""
    if "error" in result:
        print(f"\n⚠️  {result['message']}\n")
        return

    risk_pct = round(result["final_score"] * 100)
    print(f"\n{'='*50}")
    print(f"  SpySentinel Scan Report")
    print(f"{'='*50}")
    print(f"  File:        {result['filename']}")
    print(f"  Type:        {result['file_type']}")
    print(f"  Risk Score:  {risk_pct}%")
    print(f"{'='*50}")

    if not result["indicators"]:
        print("  No indicators flagged.\n")
    else:
        print(f"  Indicators ({len(result['indicators'])}):\n")
        for ind in result["indicators"]:
            print(f"   [{ind['severity'].upper():8}] ({ind['source']}) {ind['description']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="spysentinel",
        description="SpySentinel — spyware/stalkerware detection scanner",
    )
    parser.add_argument("--file", required=True, help="Path to the file to scan (.apk)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of readable text")

    args = parser.parse_args()

    result = scan(args.file)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human_readable(result)

    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()