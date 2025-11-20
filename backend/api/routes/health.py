"""
Health Routes
GET /health endpoints
"""
import torch
from fastapi import APIRouter
from api.schemas.responses import HealthResponse
from infrastructure.observability.health import health_checker
from infrastructure.models.registry import LOCAL_MODEL_DIR, DEVICE


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint básico"""
    return {
        "status": "healthy",
        "gpu_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "gpu_memory_total_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3 if torch.cuda.is_available() else 0,
        "gpu_memory_used_gb": torch.cuda.memory_allocated(0) / 1024**3 if torch.cuda.is_available() else 0,
        "model_loaded": LOCAL_MODEL_DIR.exists()
    }


@router.get("/health/detailed")
async def health_detailed():
    """Health check detalhado de todos os componentes"""
    return health_checker.check_all()

