"""
Tool Domain Entity
Representa uma ferramenta disponível para o modelo
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass(frozen=True)
class ToolCall:
    """Chamada de ferramenta pelo modelo"""
    
    name: str
    parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dict"""
        return {
            "name": self.name,
            "parameters": self.parameters
        }


@dataclass(frozen=True)
class ToolResult:
    """Resultado da execução de uma ferramenta"""
    
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dict"""
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "result": self.result,
            "error": self.error
        }

