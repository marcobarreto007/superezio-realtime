"""
Compatibilidade com código legado
Reexports novos módulos com nomes antigos para manter compatibilidade
"""
# Reexports para compatibilidade
from infrastructure.models.registry import (
    get_model_and_tokenizer,
    get_available_modes,
    LOCAL_MODEL_DIR,
    DEVICE,
    LORA_ADAPTERS
)
from infrastructure.observability.logger import (
    app_logger,
    rag_logger,
    tool_logger,
    model_logger
)
from infrastructure.observability.metrics import metrics
from infrastructure.observability.circuit_breaker import CircuitBreakerOpenError
from infrastructure.observability.rate_limiter import rate_limiter
from infrastructure.observability.health import health_checker

# Reexport para compatibilidade com imports diretos
__all__ = [
    "get_model_and_tokenizer",
    "get_available_modes",
    "LOCAL_MODEL_DIR",
    "DEVICE",
    "LORA_ADAPTERS",
    "app_logger",
    "rag_logger",
    "tool_logger",
    "model_logger",
    "metrics",
    "CircuitBreakerOpenError",
    "rate_limiter",
    "health_checker",
]

