from fastapi import APIRouter, HTTPException
from app.database import SessionLocal
from app.models.scan_log import ScanLog

router = APIRouter()

@router.get("/logs")
def recent_logs(limit: int = 20):
    """Most recent logged requests, newest first (max 100)."""
    limit = max(1, min(limit, 100))
    try:
        with SessionLocal() as session:
            rows = session.query(ScanLog).order_by(ScanLog.id.desc()).limit(limit).all()
            return [
                {
                    "id": r.id,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "input_type": r.input_type,
                    "query_text": r.query_text,
                    "product_name": r.product_name,
                    "health_score": r.health_score,
                }
                for r in rows
            ]
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")
