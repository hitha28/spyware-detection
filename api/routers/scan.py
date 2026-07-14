"""
POST /scan — the main integration endpoint.

Runs Shivanshi's StaticAnalysisEngine, converts results through
indicator_adapter, gets a risk score from predict_risk() (currently the
TEMPORARY synthetic/real-Drebin-trained stub — see ml/predict_risk.py),
combines both into a final_score, and persists everything to the database.
"""

import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.db.models import Scan, Indicator
from api.services.indicator_adapter import flatten_static_result
from core.static_analysis.static_engine import StaticAnalysisEngine
from ml.predict_risk import predict_risk

router = APIRouter()

_engine = StaticAnalysisEngine()

# Maps severity strings to numeric scores for computing static_score.
SEVERITY_WEIGHTS = {
    "critical": 1.0,
    "high": 0.7,
    "medium": 0.4,
    "low": 0.1,
}


@router.post("/scan")
async def scan_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Accept a file upload, run static + ML analysis, save and return results."""

    # Save the uploaded file to a temporary location on disk
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # Run Shivanshi's static engine
        try:
            raw_result = _engine.analyze(tmp_path)
        except NotImplementedError as e:
            # PE (.exe) analysis isn't built yet — respond gracefully
            # instead of crashing with a 500 error.
            return {
                "error": "unsupported_file_type",
                "message": str(e),
                "filename": file.filename,
            }

        # Convert to flat indicator list
        indicator_dicts = flatten_static_result(raw_result)

        # Compute static_score: highest severity found, mapped to a number
        if indicator_dicts:
            static_score = max(
                SEVERITY_WEIGHTS.get(ind["severity"], 0.0) for ind in indicator_dicts
            )
        else:
            static_score = 0.0

        # Get ML risk score (currently the temporary synthetic/real-Drebin-trained stub)
        ml_score = predict_risk(raw_result)

        final_score = 0.5 * static_score + 0.5 * ml_score

        # Save to database
        scan = Scan(
            filename=file.filename,
            file_type=raw_result.get("file_type", "unknown"),
            status="done",
            static_score=static_score,
            ml_score=ml_score,
            final_score=final_score,
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)

        for ind in indicator_dicts:
            db.add(Indicator(scan_id=scan.id, **ind))
        db.commit()

        return {
            "scan_id": scan.id,
            "filename": scan.filename,
            "file_type": scan.file_type,
            "static_score": static_score,
            "ml_score": ml_score,
            "final_score": final_score,
            "indicators": indicator_dicts,
        }

    finally:
        Path(tmp_path).unlink(missing_ok=True)