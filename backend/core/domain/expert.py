"""
Expert Domain Entity
Representa um expert especializado (MoE routing)
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass(frozen=True)
class ExpertDecision:
    """Decisão de roteamento para um expert"""
    
    expert_id: str
    lora_adapter: Optional[str] = None
    rag_domains: List[str] = None
    reason: str = ""
    expert_config: Dict[str, Any] = None
    
    def __post_init__(self):
        """Garantir que rag_domains e expert_config têm valores padrão"""
        if self.rag_domains is None:
            object.__setattr__(self, "rag_domains", [])
        if self.expert_config is None:
            object.__setattr__(self, "expert_config", {})


@dataclass(frozen=True)
class ExpertConfig:
    """Configuração de um expert"""
    
    expert_id: str
    human_label: str
    lora_adapter: Optional[str]
    rag_domains: List[str]
    keywords: List[str]
    persona: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dict"""
        return {
            "expert_id": self.expert_id,
            "human_label": self.human_label,
            "lora_adapter": self.lora_adapter,
            "rag_domains": self.rag_domains,
            "keywords": self.keywords,
            "persona": self.persona
        }

