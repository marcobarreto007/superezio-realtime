"""
Chat Routes
POST /chat endpoint
"""
import time
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from api.schemas.requests import ChatRequest
from api.schemas.responses import ChatResponse
from api.dependencies import get_chat_use_case, check_rate_limit
from core.domain.message import Message
from core.use_cases.chat_completion import ChatCompletionUseCase
from infrastructure.observability.logger import app_logger
from infrastructure.observability.metrics import metrics
from infrastructure.observability.circuit_breaker import CircuitBreakerOpenError
from middleware.error_handler import ErrorHandler
import torch


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    request: Request,
    use_case: ChatCompletionUseCase = Depends(get_chat_use_case)
):
    """
    Endpoint principal de chat completion.
    Valida entrada e delega para use case.
    """
    # Rate limiting
    check_rate_limit(request, "chat")
    
    request_id = str(uuid.uuid4())[:8]
    start = time.time()
    
    # Métricas
    metrics.increment("requests.total")
    
    # Validação
    if not req.messages:
        return JSONResponse(
            content={"error": "Campo 'messages' é obrigatório"},
            status_code=400,
            media_type="application/json; charset=utf-8"
        )
    
    # Converter request para domain entities
    messages = [Message.from_dict(m.model_dump()) for m in req.messages]
    
    # Log
    user_text = messages[-1].content if messages else ""
    app_logger.info(
        "Chat request received",
        request_id=request_id,
        message_count=len(messages),
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        user_message_preview=user_text[:120]
    )
    
    # Limpar cache GPU
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    try:
        # Limitar max_tokens
        max_new = min(req.max_tokens or 256, 512)
        temp = req.temperature if req.temperature is not None else 0.2
        
        print(f"⏳ [REQ #{request_id}] Iniciando inferência...")
        t0 = time.time()
        
        # Executar use case
        result = await use_case.execute(
            messages=messages,
            temperature=temp,
            max_tokens=max_new,
            mode=req.mode
        )
        
        infer_time = time.time() - t0
        
        # Métricas
        metrics.histogram("chat.inference_time", infer_time)
        metrics.increment("requests.success")
        
        # Log resposta
        print(f"🧩 [REQ #{request_id}] PERGUNTA:\n{user_text}\n" + "-"*60)
        print(f"🟢 [REQ #{request_id}] RESPOSTA ({len(result.content)} chars):\n{result.content}\n" + "-"*60)
        
        total_time = time.time() - start
        metrics.histogram("chat.total_time", total_time)
        
        app_logger.info(
            "Chat request completed",
            request_id=request_id,
            total_time=round(total_time, 2),
            inference_time=round(infer_time, 2),
            response_length=len(result.content)
        )
        
        # Converter result para response
        response_data = result.to_dict()
        response_data.update({
            "id": f"chatcmpl-{request_id}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": req.model or "Qwen2.5-7B-Instruct",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result.content
                },
                "finish_reason": "stop"
            }]
        })
        
        return JSONResponse(
            content=response_data,
            media_type="application/json; charset=utf-8"
        )
        
    except HTTPException:
        raise
    except CircuitBreakerOpenError as exc:
        app_logger.warning(
            "Circuit breaker open",
            request_id=request_id,
            error=str(exc)
        )
        metrics.increment("errors.circuit_breaker")
        return JSONResponse(
            content={
                "error": "Service temporarily unavailable",
                "message": "The service is currently overloaded. Please try again in a moment.",
                "retryable": True
            },
            status_code=503,
            media_type="application/json; charset=utf-8"
        )
    except Exception as exc:
        elapsed = time.time() - start
        app_logger.error(
            "Chat request failed",
            request_id=request_id,
            error_type=type(exc).__name__,
            error_message=str(exc),
            elapsed_time=round(elapsed, 2)
        )
        metrics.increment("errors.total", tags={"type": type(exc).__name__})
        
        error_response = ErrorHandler.handle_model_error(exc, {"request_id": request_id})
        
        return JSONResponse(
            content=error_response,
            status_code=500,
            media_type="application/json; charset=utf-8"
        )

