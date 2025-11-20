"""
Tool Executor Implementation
Implementa ToolExecutor protocol usando código existente de tool_executor.py
"""
import os
from typing import List
from core.services.tools.executor import ToolExecutor
from core.domain.tool import ToolCall, ToolResult
from infrastructure.config.settings import get_settings

# Importar código existente
from tool_executor import execute_tool


class ToolExecutorImpl:
    """
    Implementação do ToolExecutor protocol.
    Usa código existente de tool_executor.py para executar tools via Express API.
    """
    
    def __init__(self):
        self.settings = get_settings()
    
    async def execute(self, tool_call: ToolCall) -> ToolResult:
        """
        Executa uma ferramenta.
        
        Args:
            tool_call: Chamada de ferramenta
            
        Returns:
            Resultado da execução
        """
        try:
            # Chamar função existente execute_tool
            result = execute_tool(
                tool_name=tool_call.name,
                parameters=tool_call.parameters
            )
            
            if result.get("success"):
                return ToolResult(
                    tool_name=tool_call.name,
                    success=True,
                    result=result.get("result"),
                    error=None
                )
            else:
                return ToolResult(
                    tool_name=tool_call.name,
                    success=False,
                    result=None,
                    error=result.get("error", "Erro desconhecido")
                )
                
        except Exception as e:
            return ToolResult(
                tool_name=tool_call.name,
                success=False,
                result=None,
                error=str(e)
            )
    
    async def execute_batch(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """
        Executa múltiplas ferramentas.
        
        Args:
            tool_calls: Lista de chamadas de ferramentas
            
        Returns:
            Lista de resultados
        """
        results = []
        for tool_call in tool_calls:
            result = await self.execute(tool_call)
            results.append(result)
        return results


# Factory function
def create_tool_executor() -> ToolExecutor:
    """Factory para criar instância do tool executor"""
    return ToolExecutorImpl()
