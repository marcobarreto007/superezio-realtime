"""
Dependencies for FastAPI endpoints
Dependency injection para use cases e serviços
"""
from fastapi import Depends, HTTPException, Request
from core.use_cases.chat_completion import ChatCompletionUseCase
from core.use_cases.stream_completion import StreamCompletionUseCase
from core.services.routing.router import Router
from core.services.rag.retriever import Retriever
from core.services.inference.generator import Generator
from core.services.tools.executor import ToolExecutor

# Factories
from core.services.routing.expert_router_impl import create_router
from core.services.rag.rag_retriever_impl import create_rag_retriever
from core.services.inference.generator_impl import create_generator
from core.services.tools.tool_executor_impl import create_tool_executor

# Rate limiting
from infrastructure.observability.rate_limiter import rate_limiter


# Cache de instâncias (singletons)
_router: Router | None = None
_rag_retriever: Retriever | None = None
_generator: Generator | None = None
_tool_executor: ToolExecutor | None = None
_chat_use_case: ChatCompletionUseCase | None = None
_stream_use_case: StreamCompletionUseCase | None = None


def get_router() -> Router:
    """Retorna instância do router"""
    global _router
    if _router is None:
        _router = create_router()
    return _router


def get_rag_retriever() -> Retriever:
    """Retorna instância do RAG retriever"""
    global _rag_retriever
    if _rag_retriever is None:
        _rag_retriever = create_rag_retriever(use_enhanced=True)
    return _rag_retriever


def get_generator() -> Generator:
    """Retorna instância do generator"""
    global _generator
    if _generator is None:
        _generator = create_generator()
    return _generator


def get_tool_executor() -> ToolExecutor:
    """Retorna instância do tool executor"""
    global _tool_executor
    if _tool_executor is None:
        _tool_executor = create_tool_executor()
    return _tool_executor


def get_chat_use_case() -> ChatCompletionUseCase:
    """Retorna instância do ChatCompletionUseCase"""
    global _chat_use_case
    if _chat_use_case is None:
        _chat_use_case = ChatCompletionUseCase(
            router=get_router(),
            rag_retriever=get_rag_retriever(),
            generator=get_generator(),
            tool_executor=get_tool_executor()
        )
    return _chat_use_case


def get_stream_use_case() -> StreamCompletionUseCase:
    """Retorna instância do StreamCompletionUseCase"""
    global _stream_use_case
    if _stream_use_case is None:
        _stream_use_case = StreamCompletionUseCase(
            router=get_router(),
            rag_retriever=get_rag_retriever(),
            generator=get_generator()
        )
    return _stream_use_case


def check_rate_limit(request: Request, endpoint: str = "chat"):
    """Dependency para verificar rate limit"""
    from fastapi import HTTPException
    
    client_id = request.client.host if request.client else "unknown"
    allowed, retry_after = rate_limiter.check(endpoint)
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Retry after {retry_after} seconds",
            headers={"Retry-After": str(retry_after)}
        )
    
    return True

