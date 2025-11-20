"""
Rate Limiting
Proteção contra abuso e sobrecarga
Moved from backend/utils/rate_limiter.py to infrastructure/observability/
"""
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from infrastructure.config.settings import get_settings


settings = get_settings()


@dataclass
class RateLimit:
    """Configuração de rate limit"""
    max_requests: int
    window_seconds: int


class RateLimiter:
    """Rate limiter simples baseado em sliding window"""
    
    def __init__(self):
        self._requests: Dict[str, list[float]] = defaultdict(list)
        self._limits: Dict[str, RateLimit] = {}
    
    def add_limit(self, key: str, max_requests: int, window_seconds: int):
        """Adiciona limite para uma chave"""
        self._limits[key] = RateLimit(max_requests, window_seconds)
    
    def check(self, key: str) -> tuple[bool, Optional[int]]:
        """
        Verifica se requisição está dentro do limite
        
        Returns:
            (allowed, retry_after_seconds)
        """
        if key not in self._limits:
            return True, None
        
        limit = self._limits[key]
        now = time.time()
        
        # Limpar requisições antigas
        cutoff = now - limit.window_seconds
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]
        
        # Verificar limite
        if len(self._requests[key]) >= limit.max_requests:
            oldest = min(self._requests[key])
            retry_after = int(oldest + limit.window_seconds - now) + 1
            return False, retry_after
        
        # Registrar requisição
        self._requests[key].append(now)
        return True, None
    
    def reset(self, key: Optional[str] = None):
        """Reset contadores"""
        if key:
            self._requests[key].clear()
        else:
            self._requests.clear()


# Instância global
rate_limiter = RateLimiter()

# Limites padrão (usando settings)
rate_limiter.add_limit("chat", max_requests=settings.rate_limit_chat, window_seconds=60)
rate_limiter.add_limit("chat_stream", max_requests=settings.rate_limit_stream, window_seconds=60)
rate_limiter.add_limit("tools", max_requests=settings.rate_limit_tools, window_seconds=60)

