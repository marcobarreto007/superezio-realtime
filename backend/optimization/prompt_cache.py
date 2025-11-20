"""
Prompt Caching Optimization
Cache de prompts formatados para reduzir latência

Baseado em papers sobre prompt optimization e caching
"""
import hashlib
import json
from typing import Optional, Dict, Any, List
from utils.cache import TTLCache


class PromptCache:
    """
    Cache de prompts formatados
    Reduz tempo de formatação em requisições similares
    """
    
    def __init__(self, ttl: int = 3600):  # 1 hora
        self._cache = TTLCache(default_ttl=ttl)
        self._hits = 0
        self._misses = 0
    
    def get_cache_key(
        self, 
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """Gera chave de cache baseada nas mensagens"""
        # Criar hash das mensagens
        cache_data = {
            "messages": messages,
            "system": system_prompt
        }
        cache_str = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def get(self, cache_key: str) -> Optional[str]:
        """Recupera prompt do cache"""
        cached = self._cache.get(cache_key)
        if cached:
            self._hits += 1
            return cached
        
        self._misses += 1
        return None
    
    def set(self, cache_key: str, prompt: str):
        """Armazena prompt no cache"""
        self._cache.set(cache_key, prompt)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        
        return {
            "cache_size": self._cache.size(),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2)
        }


# Instância global
prompt_cache = PromptCache()

