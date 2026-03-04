from fastapi import APIRouter
from ..deps import get_db_session
from app.ml.model_loader import get_ml_service

router = APIRouter(prefix="/api/ml", tags=["ML"])


@router.get("/status")
def ml_status():
    svc = get_ml_service()
    try:
        path = str(svc.models_path.resolve())
    except Exception:
        path = str(svc.models_path)
    return {
        "models": list(svc.models.keys()),
        "scalers": {k: (v is not None) for k, v in svc.scalers.items()},
        "models_path": path,
        "egfr_fallback_available": egfr_fallback is not None,
    }
