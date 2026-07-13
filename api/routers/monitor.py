"""
GET /monitor — inspects currently running processes on this machine and
flags ones showing suspicious behavioral signals (high connection counts,
low IP diversity, unusually high thread counts, etc.)

Unlike /scan (which analyzes an uploaded FILE), this endpoint analyzes
LIVE SYSTEM BEHAVIOR right now — the "process/network monitoring" side
of Phase 2's original scope.

Note: true beaconing detection (see ml/netwrok/dns_analyzer.py) requires
timestamps sampled over time, which a single live snapshot can't provide.
This endpoint reports point-in-time behavioral signals only; continuous
monitoring (e.g. a scheduled background job) would be needed to apply
real beaconing detection in practice.
"""

from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends

from api.db.database import get_db
from api.db.models import Scan, Indicator
from ml.features.extract_process_features import extract_features_for_all_processes
from ml.features.extract_network_features import extract_network_features_for_all_processes

router = APIRouter()


@router.get("/monitor")
def monitor_system(db: Session = Depends(get_db)):
    """Inspect currently running processes and flag suspicious behavior."""

    process_data = {p["pid"]: p for p in extract_features_for_all_processes()}
    network_data = {n["pid"]: n for n in extract_network_features_for_all_processes()}

    indicators = []
    for pid, proc in process_data.items():
        net = network_data.get(pid, {})

        if proc.get("high_connection_count") and not proc.get("is_common_safe_process"):
            indicators.append({
                "source": "process",
                "description": f"{proc['name']} (pid {pid}) has an unusually high number of open connections",
                "severity": "medium",
            })

        if net.get("low_ip_diversity"):
            indicators.append({
                "source": "network",
                "description": f"{proc['name']} (pid {pid}) repeatedly contacts a very small set of destinations",
                "severity": "medium",
            })

        if proc.get("high_thread_count") and not proc.get("is_common_safe_process"):
            indicators.append({
                "source": "process",
                "description": f"{proc['name']} (pid {pid}) has an unusually high thread count",
                "severity": "low",
            })

    # Save as a Scan row with file_type="system" so it's visible in scan history
    scan = Scan(
        filename="live-system-monitor",
        file_type="system",
        status="done",
        static_score=0.0,
        ml_score=0.0,
        final_score=min(len(indicators) * 0.1, 1.0),
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    for ind in indicators:
        db.add(Indicator(scan_id=scan.id, **ind))
    db.commit()

    return {
        "scan_id": scan.id,
        "processes_inspected": len(process_data),
        "indicators": indicators,
    }