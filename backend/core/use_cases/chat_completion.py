"""
Chat Completion Use Case
Orquestra routing, RAG, inference e tools para completar chat
"""
from typing import List, Optional
from core.domain.message import Message
from core.domain.completion import CompletionResult
from core.services.routing.router import Router
from core.services.rag.retriever import Retriever
from core.services.inference.generator import Generator
from core.services.tools.executor import ToolExecutor


class ChatCompletionUseCase:
    """Use case para completar chat"""
    
    def __init__(
        self,
        router: Router,
        rag_retriever: Retriever,
        generator: Generator,
        tool_executor: ToolExecutor
    ):
        self.router = router
        self.rag_retriever = rag_retriever
        self.generator = generator
        self.tool_executor = tool_executor
    
    async def execute(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 512,
        mode: Optional[str] = None
    ) -> CompletionResult:
        """
        Executa completion de chat.
        
        Fluxo:
        1. Route para expert
        2. Query RAG
        3. Generate
        4. Execute tools (se necessário)
        5. Return result
        """
        # 1. Route
        messages_dict = [m.to_dict() for m in messages]
        decision = self.router.route(messages_dict, explicit_mode=mode)
        
        # 2. RAG
        user_query = messages[-1].content if messages else ""
        rag_context = None
        if decision.rag_domains:
            rag_context = self.rag_retriever.retrieve(
                domains=decision.rag_domains,
                query=user_query,
                top_k=6
            )
        
        # 3. Generate
        result = await self.generator.generate(
            messages=messages,
            rag_context=rag_context,
            expert_id=decision.expert_id,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 4. Tools (se necessário)
        if result.tool_calls:
            # tool_calls já são ToolCall objects
            tool_results = await self.tool_executor.execute_batch(result.tool_calls)
            
            # Atualizar result com tool_results
            from dataclasses import replace
            result = replace(result, tool_results=tool_results)
        
        return result

