"""
POST /scan — the main integration endpoint.

Returns scan_id immediately (status: pending) and runs the actual
static + ML analysis in the background, updating the same Scan row
once complete — per P3-SRE4's acceptance criteria.
"""

import os
import shutil
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from api.db.database import get_db, SessionLocal
from api.db.models import Scan, Indicator
from api.services.indicator_adapter import flatten_static_result
from core.static_analysis.static_engine import StaticAnalysisEngine
from ml.predict_risk import predict_risk

load_dotenv()

router = APIRouter()

_engine = StaticAnalysisEngine()

SEVERITY_WEIGHTS = {
    "critical": 1.0,
    "high": 0.7,
    "medium": 0.4,
    "low": 0.1,
}

STATIC_WEIGHT = float(os.getenv("STATIC_WEIGHT", 0.5))
ML_WEIGHT = float(os.getenv("ML_WEIGHT", 0.5))


def run_analysis(scan_id: int, tmp_path: str):
    """
    Runs the actual static + ML analysis in the background, then updates
    the existing Scan row with real results once finished.
    """
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()

        try:
            raw_result = _engine.analyze(tmp_path)
        except NotImplementedError as e:
            scan.status = "failed"
            scan.file_type = "unsupported"
            db.commit()
            return

        indicator_dicts = flatten_static_result(raw_result)

        if indicator_dicts:
            static_score = max(
                SEVERITY_WEIGHTS.get(ind["severity"], 0.0) for ind in indicator_dicts
            )
        else:
            static_score = 0.0

        ml_score = predict_risk(raw_result)
        final_score = STATIC_WEIGHT * static_score + ML_WEIGHT * ml_score

        scan.file_type = raw_result.get("file_type", "unknown")
        scan.status = "done"
        scan.static_score = static_score
        scan.ml_score = ml_score
        scan.final_score = final_score
        db.commit()

        for ind in indicator_dicts:
            db.add(Indicator(scan_id=scan.id, **ind))
        db.commit()

    finally:
        db.close()
        Path(tmp_path).unlink(missing_ok=True)


@router.post("/scan")
async def scan_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Accept a file upload, immediately return scan_id, analyze in background."""

    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # Create the Scan row immediately, with pending status
    scan = Scan(
        filename=file.filename,
        file_type="pending",
        status="pending",
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    # Queue the real work to happen after the response is sent
    background_tasks.add_task(run_analysis, scan.id, tmp_path)

    return {
        "scan_id": scan.id,
        "filename": scan.filename,
        "status": "pending",
        "message": "Analysis started. Check GET /reports/{scan_id} for results.",
    }