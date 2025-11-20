"""
Stream Routes
POST /chat/stream endpoint
"""
import json
import uuid
import textwrap
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from api.schemas.requests import ChatRequest
from api.dependencies import get_stream_use_case, check_rate_limit
from core.domain.message import Message
from core.use_cases.stream_completion import StreamCompletionUseCase


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    request: Request,
    use_case: StreamCompletionUseCase = Depends(get_stream_use_case)
):
    """
    SSE streaming endpoint - tokens em tempo real.
    """
    # Rate limiting
    check_rate_limit(request, "chat_stream")
    
    req_id = str(uuid.uuid4())[:8]
    
    print(f"\n{'='*60}")
    print(f"🔵 [REQ #{req_id}] STREAM request")
    print(f"📊 max_tokens: {req.max_tokens} | temp: {req.temperature}")
    print(f"📝 {len(req.messages)} mensagens")
    
    async def event_generator():
        try:
            chunk_count = 0
            
            # Converter request para domain entities
            messages = [Message.from_dict(m.model_dump()) for m in req.messages]
            
            # Executar use case (streaming)
            async for token in use_case.execute(
                messages=messages,
                temperature=req.temperature,
                max_tokens=req.max_tokens,
                mode=req.mode
            ):
                # Enviar token diretamente
                chunk_count += 1
                data = json.dumps({"content": token, "done": False})
                yield f"data: {data}\n\n"
            
            # Enviar final
            final_data = json.dumps({"content": "", "done": True})
            yield f"data: {final_data}\n\n"
            
            print(f"✅ [REQ #{req_id}] Stream OK: {chunk_count} chunks")
            
        except Exception as e:
            print(f"❌ [REQ #{req_id}] Erro: {e}")
            import traceback
            traceback.print_exc()
            error_data = json.dumps({"error": str(e), "done": True})
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

