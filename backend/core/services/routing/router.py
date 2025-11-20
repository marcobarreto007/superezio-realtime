"""
Router Protocol (Interface)
Define contrato para routers de experts
"""
from typing import Protocol, List, Dict, Optional
from core.domain.expert import ExpertDecision


class Router(Protocol):
    """Protocolo para routers de experts"""
    
    def route(
        self,
        messages: List[Dict[str, str]],
        explicit_mode: Optional[str] = None
    ) -> ExpertDecision:
        """
        Roteia mensagens para um expert apropriado.
        
        Args:
            messages: Lista de mensagens da conversa
            explicit_mode: Modo explícito (override)
            
        Returns:
            ExpertDecision com expert_id, lora_adapter, rag_domains
        """
        ...

