"""
KV Cache Optimization
Otimização de cache de chaves-valores para inferência mais rápida

Baseado em papers sobre attention caching e KV cache optimization
"""
import torch
from typing import Optional, Dict, Any
from transformers import PreTrainedModel


class KVCacheManager:
    """
    Gerenciador de KV cache para otimizar inferência
    Reutiliza cache entre requisições similares
    """
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_hits = 0
        self._cache_misses = 0
    
    def get_cache_key(self, prompt_prefix: str, max_length: int = 50) -> str:
        """Gera chave de cache baseada no prefixo do prompt"""
        # Usar primeiros N tokens como chave
        prefix = prompt_prefix[:max_length].strip()
        return f"kv_{hash(prefix)}"
    
    def get_cache(
        self, 
        model: PreTrainedModel,
        input_ids: torch.Tensor,
        cache_key: Optional[str] = None
    ) -> Optional[Dict[str, torch.Tensor]]:
        """
        Recupera KV cache se disponível
        """
        if cache_key and cache_key in self._cache:
            self._cache_hits += 1
            return self._cache[cache_key]
        
        self._cache_misses += 1
        return None
    
    def save_cache(
        self,
        cache_key: str,
        past_key_values: Any,
        max_cache_size: int = 10
    ):
        """
        Salva KV cache para reutilização
        """
        if len(self._cache) >= max_cache_size:
            # Remover entrada mais antiga (FIFO)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[cache_key] = past_key_values
    
    def clear_cache(self):
        """Limpa todo o cache"""
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0
        
        return {
            "cache_size": len(self._cache),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": round(hit_rate, 2)
        }


# Instância global
kv_cache_manager = KVCacheManager()

