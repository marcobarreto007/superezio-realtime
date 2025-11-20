"""
Tool Executor Protocol (Interface)
Define contrato para executores de ferramentas
"""
from typing import Protocol, List
from core.domain.tool import ToolCall, ToolResult


class ToolExecutor(Protocol):
    """Protocolo para executores de ferramentas"""
    
    async def execute(self, tool_call: ToolCall) -> ToolResult:
        """
        Executa uma ferramenta.
        
        Args:
            tool_call: Chamada de ferramenta
            
        Returns:
            Resultado da execução
        """
        ...
    
    async def execute_batch(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """
        Executa múltiplas ferramentas.
        
        Args:
            tool_calls: Lista de chamadas de ferramentas
            
        Returns:
            Lista de resultados
        """
        ...

