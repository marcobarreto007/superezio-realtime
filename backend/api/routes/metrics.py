"""
Metrics Routes
GET /metrics endpoint
"""
from fastapi import APIRouter
from api.schemas.responses import MetricsResponse
from infrastructure.observability.metrics import metrics


router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Endpoint de métricas do sistema"""
    stats = metrics.get_stats()
    return MetricsResponse(
        counters=stats.get("counters", {}),
        histograms=stats.get("histograms", {})
    )

