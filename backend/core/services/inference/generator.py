"""
Generator Protocol (Interface)
Define contrato para geradores de texto
"""
from typing import Protocol, List, Dict, Optional, AsyncGenerator
from core.domain.message import Message
from core.domain.completion import CompletionResult


class Generator(Protocol):
    """Protocolo para geradores de texto"""
    
    async def generate(
        self,
        messages: List[Message],
        rag_context: Optional[str] = None,
        expert_id: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
        tools: Optional[List[Dict]] = None
    ) -> CompletionResult:
        """
        Gera completion de chat.
        
        Args:
            messages: Lista de mensagens
            rag_context: Contexto RAG (opcional)
            expert_id: ID do expert (opcional)
            temperature: Temperatura de geração
            max_tokens: Máximo de tokens
            tools: Ferramentas disponíveis (opcional)
            
        Returns:
            CompletionResult
        """
        ...
    
    async def generate_stream(
        self,
        messages: List[Message],
        rag_context: Optional[str] = None,
        expert_id: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
        tools: Optional[List[Dict]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Gera completion com streaming.
        
        Args:
            messages: Lista de mensagens
            rag_context: Contexto RAG (opcional)
            expert_id: ID do expert (opcional)
            temperature: Temperatura de geração
            max_tokens: Máximo de tokens
            tools: Ferramentas disponíveis (opcional)
            
        Yields:
            Tokens de texto
        """
        ...

