from fastapi import APIRouter
from app.services.semantic_layer import METRICS

router = APIRouter(prefix="/api/v1/meta", tags=["meta"])

@router.get("/metrics")
async def metrics():
    return [
        {"code": metric.code, "name": metric.name, "unit": metric.unit, "dimensions": metric.allowed_dimensions}
        for metric in METRICS.values()
    ]
