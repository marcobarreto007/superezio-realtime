"""
FastAPI Main Application
App FastAPI + lifespan + middleware
Refactored from backend/api.py to api/main.py
"""
import os
import sys
import time
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import torch

# Infrastructure imports
from infrastructure.config.settings import get_settings
from infrastructure.models.registry import (
    get_model_and_tokenizer,
    get_available_modes,
    LOCAL_MODEL_DIR,
    DEVICE
)
from infrastructure.observability.logger import app_logger
from infrastructure.observability.metrics import metrics
from infrastructure.observability.health import health_checker

# Middleware
from middleware.error_handler import ErrorHandler

# Routes
from api.routes import chat, stream, health, metrics as metrics_route

# Import legacy para compatibilidade durante migração
from inference import load_model


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events: startup e shutdown"""
    # Startup
    app_logger.info("Starting SuperEzio Backend", version="2.0.0")
    
    print("=" * 60)
    print("🚀 Inicializando SuperEzio Python Backend v2.0.0")
    print("=" * 60)
    print(f"📊 Dispositivo: {DEVICE}")
    print(f"🤖 Modelo: {LOCAL_MODEL_DIR}")
    print(f"📁 Verificando se modelo existe...")
    
    if not LOCAL_MODEL_DIR.exists():
        app_logger.error("Model not found", path=str(LOCAL_MODEL_DIR))
        raise Exception(f"❌ ERRO: Modelo não encontrado em {LOCAL_MODEL_DIR}")
    else:
        print(f"✅ Modelo encontrado!")
        app_logger.info("Model found", path=str(LOCAL_MODEL_DIR))
    
    print(f"⏳ Carregando modelo base... (isso pode levar 90-120 segundos na primeira vez)")
    print(f"   Com quantização 4-bit: ~4-5 GB VRAM")
    print(f"   LoRAs serão carregados sob demanda quando mode for especificado")
    
    try:
        with metrics.timer("startup.model_load"):
            load_model(mode=None)  # Carregar apenas modelo base
        print(f"✅ Modelo base carregado com sucesso!")
        app_logger.info("Model loaded", mode="base")
        
        available_modes = get_available_modes()
        if available_modes:
            print(f"📦 LoRAs disponíveis: {', '.join(available_modes)}")
        else:
            print(f"📦 Nenhum LoRA disponível (usando apenas modelo base)")
        app_logger.info("Available LoRAs", modes=available_modes)
        
        if DEVICE == "cuda":
            print(f"💾 Memória GPU usada: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
        
        # Health check inicial
        health_status = health_checker.check_all()
        app_logger.info("Initial health check", status=health_status["status"])
        
        # Inicializar Graph RAG
        print(f"🔷 Inicializando Graph RAG...")
        try:
            from rag.graph_rag_initializer import initialize_graph_rag
            initialize_graph_rag()
            print(f"✅ Graph RAG inicializado")
            app_logger.info("Graph RAG initialized")
        except Exception as e:
            print(f"⚠️  Erro ao inicializar Graph RAG: {e}")
            app_logger.warning("Graph RAG initialization failed", error=str(e))
    except Exception as e:
        app_logger.error("Model load failed", error=str(e))
        print(f"❌ ERRO ao carregar modelo: {e}")
        raise
    
    if DEVICE == "cuda":
        print(f"💾 Memória GPU usada: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
    print("=" * 60)
    
    yield
    
    # Shutdown
    app_logger.info("Shutting down SuperEzio Backend")
    print("\n🛑 Encerrando servidor...")


# Criar app FastAPI
app = FastAPI(
    title="SuperEzio Python Backend",
    version="2.0.0",
    description="Backend Python com Qwen2.5-7B-Instruct para SuperEzio (100% local) - Enhanced Edition",
    lifespan=lifespan
)

# Error handler global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global de exceções"""
    return await ErrorHandler.handle_exception(request, exc)

# Configurar CORS (usando settings)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Endpoint raiz - informações do servidor"""
    from datetime import datetime
    return {
        "status": "online",
        "model": "Qwen2.5-7B-Instruct",
        "model_path": str(LOCAL_MODEL_DIR),
        "device": DEVICE,
        "gpu_memory_used_gb": torch.cuda.memory_allocated(0) / 1024**3 if torch.cuda.is_available() else 0,
        "available_modes": get_available_modes(),
        "timestamp": datetime.now().isoformat()
    }

# Registrar rotas
app.include_router(chat.router)
app.include_router(stream.router)
app.include_router(health.router)
app.include_router(metrics_route.router)


if __name__ == "__main__":
    import uvicorn
    print(f"\n🌐 Servidor rodando em http://localhost:{settings.api_port}")
    print(f"📖 Documentação em http://localhost:{settings.api_port}/docs")
    print(f"💡 Teste de saúde em http://localhost:{settings.api_port}/health")
    print(f"\n✅ Pronto para receber requisições!\n")
    
    uvicorn.run("api.main:app", host=settings.api_host, port=settings.api_port, reload=False)

