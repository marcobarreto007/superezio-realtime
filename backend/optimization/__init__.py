"""
Optimization Module
Otimizações avançadas baseadas em papers recentes
"""
from .kv_cache import KVCacheManager, kv_cache_manager
from .prompt_cache import PromptCache, prompt_cache

__all__ = [
    'KVCacheManager', 'kv_cache_manager',
    'PromptCache', 'prompt_cache',
]

