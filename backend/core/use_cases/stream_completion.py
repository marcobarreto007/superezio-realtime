"""
Stream Completion Use Case
Orquestra routing, RAG, inference para streaming de tokens
"""
from typing import List, Optional, AsyncGenerator
from core.domain.message import Message
from core.services.routing.router import Router
from core.services.rag.retriever import Retriever
from core.services.inference.generator import Generator


class StreamCompletionUseCase:
    """Use case para streaming de completion"""
    
    def __init__(
        self,
        router: Router,
        rag_retriever: Retriever,
        generator: Generator
    ):
        self.router = router
        self.rag_retriever = rag_retriever
        self.generator = generator
    
    async def execute(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 512,
        mode: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Executa streaming completion de chat.
        
        Fluxo:
        1. Route para expert
        2. Query RAG
        3. Generate stream
        4. Yield tokens
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
        
        # 3. Generate stream
        async for token in self.generator.generate_stream(
            messages=messages,
            rag_context=rag_context,
            expert_id=decision.expert_id,
            temperature=temperature,
            max_tokens=max_tokens
        ):
            yield token

