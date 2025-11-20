"""
Circuit Breaker Pattern
Protege contra falhas em cascata e serviços instáveis
Moved from backend/utils/circuit_breaker.py to infrastructure/observability/
"""
import time
from enum import Enum
from typing import Callable, Any, Optional
from dataclasses import dataclass, field


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreaker:
    """Circuit breaker para proteger chamadas a serviços"""
    
    failure_threshold: int = 5  # Abrir após N falhas
    success_threshold: int = 2  # Fechar após N sucessos
    timeout: float = 60.0  # Tempo para tentar fechar novamente (segundos)
    
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _success_count: int = field(default=0, init=False)
    _last_failure_time: Optional[float] = field(default=None, init=False)
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Executa função com proteção de circuit breaker"""
        if self._state == CircuitState.OPEN:
            if time.time() - (self._last_failure_time or 0) < self.timeout:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
            # Timeout expirado, tentar half-open
            self._state = CircuitState.HALF_OPEN
            self._success_count = 0
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Callback em caso de sucesso"""
        self._failure_count = 0
        
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                self._state = CircuitState.CLOSED
                self._success_count = 0
    
    def _on_failure(self):
        """Callback em caso de falha"""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
    
    @property
    def state(self) -> CircuitState:
        """Estado atual do circuit breaker"""
        return self._state
    
    def reset(self):
        """Reset manual do circuit breaker"""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None


class CircuitBreakerOpenError(Exception):
    """Exceção quando circuit breaker está aberto"""
    pass


# Instâncias globais
_rag_circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30.0)
_tool_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60.0)
_model_circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=120.0)

