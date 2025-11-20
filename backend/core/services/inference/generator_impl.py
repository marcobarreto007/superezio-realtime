"""
Generator Implementation
Implementa Generator protocol usando código existente de inference.py
Esta é uma camada de adaptação que mantém compatibilidade com código legado
"""
import os
import json
import time
from typing import List, Dict, Optional, Any, AsyncGenerator
from core.services.inference.generator import Generator
from core.domain.message import Message
from core.domain.completion import CompletionResult
from core.domain.tool import ToolCall
from infrastructure.config.settings import get_settings

# Importar código existente (legado)
# NOTA: Estes imports são do código legado que ainda funciona
# Em produção futura, estes serão substituídos por implementações puras
try:
    from inference import (
        chat_completion as legacy_chat_completion,
        format_messages,
        _inject_rag_context,
        SYSTEM_PROMPT
    )
    from model_registry import get_model_and_tokenizer, get_model_for_expert
    from prompt_builder import build_messages as build_messages_legacy
    from expert_router import get_router
    from rag_client import query_rag, build_rag_system_message
except ImportError as e:
    # Fallback se imports legados não disponíveis
    print(f"⚠️  Warning: Legacy imports not available: {e}")
    legacy_chat_completion = None


class GeneratorImpl:
    """
    Implementação do Generator protocol.
    Adapta código existente de inference.py para a nova interface.
    """
    
    def __init__(self):
        self.settings = get_settings()
    
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
        if legacy_chat_completion is None:
            raise RuntimeError("Legacy chat_completion not available")
        
        # Converter domain entities para formato legado
        messages_dict = [m.to_dict() for m in messages]
        
        # Se expert_id fornecido, usar router para obter decisão completa
        mode = None
        if expert_id:
            router = get_router()
            decision = router.route(messages_dict, explicit_mode=expert_id)
            mode = decision.lora_adapter if decision.lora_adapter else None
        
        # Chamar função legada
        result = legacy_chat_completion(
            messages=messages_dict,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
            mode=mode
        )
        
        # Converter resultado legado para domain entity
        if isinstance(result, dict):
            # Extrair tool_calls se existirem
            tool_calls = None
            if result.get("tool_calls"):
                # tool_calls vem como lista de dicts
                tool_calls_list = result["tool_calls"]
                if tool_calls_list and isinstance(tool_calls_list[0], dict):
                    tool_calls = [
                        ToolCall(name=tc["name"], parameters=tc["parameters"])
                        for tc in tool_calls_list
                    ]
            
            return CompletionResult(
                content=result.get("content", ""),
                expert=result.get("expert") or expert_id,
                lora_adapter=result.get("lora_adapter"),
                tool_calls=tool_calls,
                usage=result.get("usage")
            )
        else:
            # Fallback: converter string para CompletionResult
            return CompletionResult(
                content=str(result),
                expert=expert_id
            )
    
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
        if legacy_chat_completion is None:
            raise RuntimeError("Legacy chat_completion not available")
        
        # Converter domain entities para formato legado
        messages_dict = [m.to_dict() for m in messages]
        
        # Se expert_id fornecido, usar router
        mode = None
        if expert_id:
            router = get_router()
            decision = router.route(messages_dict, explicit_mode=expert_id)
            mode = decision.lora_adapter if decision.lora_adapter else None
        
        # Chamar função legada com stream=True
        result = legacy_chat_completion(
            messages=messages_dict,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            mode=mode
        )
        
        # Yield tokens do generator
        if hasattr(result, '__iter__'):
            for token in result:
                yield token
        else:
            # Fallback: retornar resultado completo como único token
            yield str(result)


# Factory function
def create_generator() -> Generator:
    """Factory para criar instância do generator"""
    return GeneratorImpl()

