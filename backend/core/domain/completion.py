"""
Completion Domain Entity
Representa resultado de uma completion de chat
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from core.domain.tool import ToolCall, ToolResult


@dataclass(frozen=True)
class CompletionResult:
    """Resultado de completion de chat"""
    
    content: str
    expert: Optional[str] = None
    lora_adapter: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_results: Optional[List[ToolResult]] = None
    usage: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dict (formato API)"""
        result: Dict[str, Any] = {
            "content": self.content
        }
        
        if self.expert:
            result["expert"] = self.expert
        if self.lora_adapter:
            result["lora_adapter"] = self.lora_adapter
        if self.tool_calls:
            result["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        if self.tool_results:
            result["tool_results"] = [tr.to_dict() for tr in self.tool_results]
        if self.usage:
            result["usage"] = self.usage
        if self.metadata:
            result.update(self.metadata)
        
        return result

