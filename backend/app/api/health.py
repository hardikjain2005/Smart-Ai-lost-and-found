from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    try:
        db.execute(text("SELECT 1"))
        db_status, status, code = "up", "ok", 200
    except Exception:
        db_status, status, code = "down", "degraded", 503
    body = HealthResponse(
        status=status, app=settings.app_name, environment=settings.environment, database=db_status
    )
    return JSONResponse(body.model_dump(), status_code=code)
