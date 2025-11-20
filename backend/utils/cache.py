"""
Sistema de Cache Inteligente
Cache em memória com TTL e invalidação automática
"""
import time
from typing import Any, Optional, Dict
from functools import wraps
import hashlib
import json


class TTLCache:
    """Cache com Time-To-Live"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutos padrão
        self._cache: Dict[str, tuple[Any, float]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera valor do cache se ainda válido"""
        if key not in self._cache:
            return None
        
        value, expiry = self._cache[key]
        if time.time() > expiry:
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Armazena valor no cache com TTL"""
        ttl = ttl or self.default_ttl
        expiry = time.time() + ttl
        self._cache[key] = (value, expiry)
    
    def clear(self) -> None:
        """Limpa todo o cache"""
        self._cache.clear()
    
    def cleanup(self) -> int:
        """Remove entradas expiradas, retorna número removido"""
        now = time.time()
        expired = [k for k, (_, expiry) in self._cache.items() if now > expiry]
        for k in expired:
            del self._cache[k]
        return len(expired)
    
    def size(self) -> int:
        """Retorna número de entradas no cache"""
        return len(self._cache)


# Instâncias globais
_model_cache = TTLCache(default_ttl=3600)  # 1 hora para modelos
_response_cache = TTLCache(default_ttl=300)  # 5 minutos para respostas
_rag_cache = TTLCache(default_ttl=600)  # 10 minutos para RAG


def cache_key(*args, **kwargs) -> str:
    """Gera chave de cache a partir de argumentos"""
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    key_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(ttl: int = 300, cache_instance: Optional[TTLCache] = None):
    """Decorator para cachear resultados de funções"""
    cache = cache_instance or TTLCache(default_ttl=ttl)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value
            
            result = func(*args, **kwargs)
            cache.set(key, result, ttl=ttl)
            return result
        
        wrapper.cache = cache
        return wrapper
    return decorator

