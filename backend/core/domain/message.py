"""
Message Domain Entity
Representa uma mensagem na conversa (user ou assistant)
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass(frozen=True)
class Message:
    """Entidade de mensagem - imutável"""
    
    role: str  # "user", "assistant", "system"
    content: str
    rag_context: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dict (formato OpenAI)"""
        result: Dict[str, Any] = {
            "role": self.role,
            "content": self.content
        }
        if self.rag_context:
            result["ragContext"] = self.rag_context
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Cria Message a partir de dict"""
        return cls(
            role=data["role"],
            content=data["content"],
            rag_context=data.get("ragContext") or data.get("rag_context")
        )
    
    def __str__(self) -> str:
        return f"{self.role}: {self.content[:50]}..."

