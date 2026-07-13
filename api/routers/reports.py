"""
GET /reports and GET /reports/:id — retrieve past scan results.

Complements /scan (creates a new scan) and /monitor (creates a live
system snapshot) by letting past results actually be viewed back,
rather than only ever creating new ones.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.db.models import Scan, Indicator

router = APIRouter()


@router.get("/reports")
def list_reports(db: Session = Depends(get_db)):
    """Return a summary list of all past scans, most recent first."""
    scans = db.query(Scan).order_by(Scan.created_at.desc()).all()

    return [
        {
            "scan_id": scan.id,
            "filename": scan.filename,
            "file_type": scan.file_type,
            "status": scan.status,
            "final_score": scan.final_score,
            "created_at": scan.created_at,
        }
        for scan in scans
    ]


@router.get("/reports/{scan_id}")
def get_report(scan_id: int, db: Session = Depends(get_db)):
    """Return full details for one specific scan, including its indicators."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()

    if scan is None:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")

    indicators = db.query(Indicator).filter(Indicator.scan_id == scan_id).all()

    return {
        "scan_id": scan.id,
        "filename": scan.filename,
        "file_type": scan.file_type,
        "status": scan.status,
        "static_score": scan.static_score,
        "ml_score": scan.ml_score,
        "final_score": scan.final_score,
        "created_at": scan.created_at,
        "indicators": [
            {
                "source": ind.source,
                "description": ind.description,
                "severity": ind.severity,
            }
            for ind in indicators
        ],
    }