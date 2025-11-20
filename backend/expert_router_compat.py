"""
Compatibilidade para expert_router.py
Wrapper que delega para nova implementação mantendo interface antiga
"""
from typing import List, Dict, Optional
from core.services.routing.expert_router_impl import ExpertRouterImpl
from expert_registry import ExpertConfig

# Manter RouterDecision para compatibilidade
from core.domain.expert import ExpertDecision as RouterDecision

# Singleton instance
_router_instance: Optional[ExpertRouterImpl] = None


def get_router() -> ExpertRouterImpl:
    """Get singleton router instance (compatibilidade)"""
    global _router_instance
    if _router_instance is None:
        _router_instance = ExpertRouterImpl()
    return _router_instance

