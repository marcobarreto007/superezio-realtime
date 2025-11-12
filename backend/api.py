# -*- coding: utf-8 -*-
"""
FastAPI Backend para SuperEzio
API REST para inferência com Qwen2.5-7B-Instruct (100% local)
"""
import os
import sys
import time
import uuid
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
import json
import torch
from inference import chat_completion, load_model, LOCAL_MODEL_DIR, DEVICE
from tools_config import AVAILABLE_TOOLS

# REM: garantir console UTF-8 no Windows
# Comentado - causa problemas com type checkers e venv
# if hasattr(sys.stdout, 'reconfigure'):
#     try:
#         sys.stdout.reconfigure(encoding="utf-8")
#     except Exception:
#         pass

# Models Pydantic
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "Qwen2.5-7B-Instruct"
    temperature: float = 0.7  # Mais criativo e natural
    max_tokens: int = 512  # Reduzido para respostas mais rápidas
    tools: Optional[List[Dict[str, Any]]] = None
    stream: bool = False


def resolve_tools(custom_tools: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Retorna a lista de ferramentas que será enviada ao modelo.
    Se o cliente não enviar nada, usamos o catálogo interno (não exposto ao usuário).
    """
    if custom_tools and len(custom_tools) > 0:
        return custom_tools
    return AVAILABLE_TOOLS

def torch_gc():
    """Limpar cache da GPU"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

# Carregar modelo no startup (usando lifespan para evitar deprecation warning)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    import json
    import time
    from pathlib import Path
    
    STATUS_FILE = Path(__file__).parent / "model_status.json"
    
    print("=" * 60)
    print("🚀 Inicializando SuperEzio Python Backend")
    print("=" * 60)
    print(f"📊 Dispositivo: {DEVICE}")
    print(f"🤖 Modelo: {LOCAL_MODEL_DIR}")
    print(f"📁 Verificando se modelo existe...")
    
    if not LOCAL_MODEL_DIR.exists():
        raise Exception(f"❌ ERRO: Modelo não encontrado em {LOCAL_MODEL_DIR}")
    else:
        print(f"✅ Modelo encontrado!")

    # OTIMIZAÇÃO: Model Loader separado removido - carregamos direto aqui
    # Economia de VRAM: ~4-5 GB (50%)
    print(f"⏳ Carregando modelo... (isso pode levar 90-120 segundos na primeira vez)")
    print(f"   Com quantização 4-bit: ~4-5 GB VRAM")
    try:
        load_model()
        print(f"✅ Modelo carregado com sucesso!")
        if DEVICE == "cuda":
            print(f"💾 Memória GPU usada: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
    except Exception as e:
        print(f"❌ ERRO ao carregar modelo: {e}")
        raise
    
    if DEVICE == "cuda":
        print(f"💾 Memória GPU usada: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
    print("=" * 60)
    
    yield
    
    # Shutdown (opcional)
    print("\n🛑 Encerrando servidor...")

# Criar app FastAPI com lifespan
app = FastAPI(
    title="SuperEzio Python Backend",
    version="1.0.0",
    description="Backend Python com Qwen2.5-7B-Instruct para SuperEzio (100% local)",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raiz - informações do servidor"""
    return {
        "status": "online",
        "model": "Qwen2.5-7B-Instruct",
        "model_path": str(LOCAL_MODEL_DIR),
        "device": DEVICE,
        "gpu_memory_used_gb": torch.cuda.memory_allocated(0) / 1024**3 if torch.cuda.is_available() else 0,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Endpoint de saúde - verificar status"""
    return {
        "status": "healthy",
        "gpu_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "gpu_memory_total_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3 if torch.cuda.is_available() else 0,
        "gpu_memory_used_gb": torch.cuda.memory_allocated(0) / 1024**3 if torch.cuda.is_available() else 0,
        "model_loaded": LOCAL_MODEL_DIR.exists()
    }

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    SSE streaming endpoint - tokens em tempo real.
    """
    req_id = str(uuid.uuid4())[:8]
    
    print(f"\n{'='*60}")
    print(f"🔵 [REQ #{req_id}] STREAM request")
    print(f"📊 max_tokens: {req.max_tokens} | temp: {req.temperature}")
    print(f"📝 {len(req.messages)} mensagens")
    
    tools_payload = resolve_tools(req.tools)

    async def event_generator():
        try:
            chunk_count = 0
            messages_dict = [msg.dict() for msg in req.messages]
            
            for chunk in chat_completion(
                messages=messages_dict,
                max_tokens=req.max_tokens,
                temperature=req.temperature,
                tools=tools_payload,
                stream=True
            ):
                chunk_count += 1
                data = json.dumps({"content": chunk, "done": False})
                yield f"data: {data}\n\n"
            
            # Final event
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

@app.post("/chat")
def chat(req: ChatRequest):
    """
    Endpoint principal de chat
    Loga pergunta/resposta claramente e retorna JSON consistente
    """
    request_id = str(uuid.uuid4())[:8]
    start = time.time()
    
    # REM: guarda última pergunta (se existir)
    user_text = ""
    if req.messages:
        user_text = req.messages[-1].content
    
    print("\n" + "="*60)
    print(f"🔵 [REQ #{request_id}] Nova requisição")
    print(f"📊 Max tokens: {req.max_tokens} | Temp: {req.temperature}")
    print(f"📝 Mensagens: {len(req.messages)} | Última: {user_text[:120]}")
    
    torch_gc()
    
    try:
        # Validação
        if not req.messages:
            print(f"❌ [REQ #{request_id}] Erro: Campo 'messages' vazio")
            return JSONResponse(
                content={"error": "Campo 'messages' é obrigatório"},
                status_code=400,
                media_type="application/json; charset=utf-8"
            )
        
        # Converter Pydantic models para dict
        messages = [msg.dict() for msg in req.messages]
        tools_payload = resolve_tools(req.tools)

        # LIMITE PADRONIZADO: 512 tokens (balanceado entre qualidade e velocidade)
        # - 512 tokens ≈ 15-30 segundos de geração (depende do prompt)
        # - Evita timeouts em prompts complexos
        # - Respostas completas e concisas
        max_new = min(req.max_tokens or 256, 512)
        temp = req.temperature if req.temperature is not None else 0.2
        
        print(f"⏳ [REQ #{request_id}] Iniciando inferência...")
        t0 = time.time()
        
        # Chamar função de inferência (stream=False para modo síncrono)
        result = chat_completion(
            messages=messages,
            tools=tools_payload,
            temperature=temp,
            max_tokens=max_new,
            stream=False,  # IMPORTANTE: modo síncrono retorna Dict
        )
        
        infer_time = time.time() - t0
        
        # Type guard: garantir que result é Dict
        if not isinstance(result, dict):
            print(f"❌ [REQ #{request_id}] Erro: result não é dict (tipo: {type(result)})")
            return JSONResponse(
                content={"error": "Erro interno: tipo de resposta inválido"},
                status_code=500,
                media_type="application/json; charset=utf-8"
            )
        
        # Extrair conteúdo da resposta
        if "error" in result:
            print(f"❌ [REQ #{request_id}] Erro na inferência: {result['error']}")
            return JSONResponse(
                content={"error": result["error"]},
                status_code=500,
                media_type="application/json; charset=utf-8"
            )
        
        content = (result.get("content") or "").strip()
        
        # ===== LOG VISÍVEL PERGUNTA + RESPOSTA =====
        print(f"🧩 [REQ #{request_id}] PERGUNTA:\n{user_text}\n" + "-"*60)
        print(f"🟢 [REQ #{request_id}] RESPOSTA ({len(content)} chars):\n{content}\n" + "-"*60)
        
        total = time.time() - start
        cps = (len(content) / infer_time) if infer_time > 0 else 0.0
        print(f"✅ [REQ #{request_id}] OK | inferência: {infer_time:.2f}s | chars/s: {cps:.1f} | total: {total:.2f}s")
        print("="*60)
        
        # REM: resposta JSON explícita em UTF-8 com "content"
        return JSONResponse(
            content={"content": content},
            media_type="application/json; charset=utf-8"
        )
        
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ [REQ #{request_id}] Erro no chat após {elapsed:.2f}s: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"error": str(e)},
            status_code=500,
            media_type="application/json; charset=utf-8"
        )

if __name__ == "__main__":
    import uvicorn
    print(f"\n🌐 Servidor rodando em http://localhost:8000")
    print(f"📖 Documentação em http://localhost:8000/docs")
    print(f"💡 Teste de saúde em http://localhost:8000/health")
    print(f"\n✅ Pronto para receber requisições!\n")
    
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)

