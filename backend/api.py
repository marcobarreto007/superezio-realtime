# -*- coding: utf-8 -*-
import os
import sys
import time
import uuid
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
import json
import traceback
import torch
import tempfile

from inference import chat_completion
from model_registry import get_available_modes, LOCAL_MODEL_PATH as LOCAL_MODEL_DIR, DEVICE
from tools_config import AVAILABLE_TOOLS
from mode_router import auto_route_mode

# Utils imports
from utils.rate_limiter import rate_limiter
from utils.logger import app_logger
from utils.metrics import metrics
from utils.circuit_breaker import CircuitBreakerOpenError
from middleware.error_handler import ErrorHandler
from middleware.health_check import health_checker


# Models Pydantic
class Message(BaseModel):
    role: str
    content: str
    rag_context: Optional[Union[str, List[str]]] = Field(default=None, alias="ragContext")
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "Qwen2.5-7B-Instruct"
    temperature: float = 0.7
    max_tokens: int = 512
    tools: Optional[List[Dict[str, Any]]] = None
    stream: bool = False
    mode: Optional[str] = None

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("Starting SuperEzio Backend with Llama.cpp Engine", version="4.0.0")
    print("=" * 60)
    print("🚀 Inicializando SuperEzio Python Backend v4.0.0 (Motor Llama.cpp)")
    print("=" * 60)
    # A inicialização do modelo agora é feita no 'inference.py'
    yield
    app_logger.info("Shutting down SuperEzio Backend")
    print("\n🛑 Encerrando servidor...")

# Criar app FastAPI com lifespan
app = FastAPI(
    title="SuperEzio Python Backend",
    version="4.0.0",
    description="Backend com Llama.cpp para SuperEzio",
    lifespan=lifespan
)

def resolve_tools(custom_tools: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    return AVAILABLE_TOOLS

@app.post("/chat/vision")
async def chat_vision(request: str = Form(...), image: UploadFile = File(...)):
    req_id = str(uuid.uuid4())[:8]
    print(f"\n{'='*60}\n🖼️  [REQ #{req_id}] VISION request")
    try:
        chat_request = ChatRequest.model_validate_json(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request format: {e}")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(await image.read())
            image_path = tmp.name
        print(f"   Image saved to: {image_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {e}")

    async def event_generator():
        try:
            messages_dict = [msg.model_dump(by_alias=True) for msg in chat_request.messages]
            result_stream = chat_completion(
                messages=messages_dict,
                max_tokens=chat_request.max_tokens,
                temperature=chat_request.temperature,
                stream=True,
                image_path=image_path
            )
            for chunk in result_stream:
                yield f"data: {json.dumps(chunk)}\n\n"
        finally:
            if os.path.exists(image_path):
                os.remove(image_path)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Add o resto dos seus endpoints aqui (chat, health, etc.)
@app.get("/")
async def root():
    return {"status": "online"}

@app.post("/chat")
def chat(req: ChatRequest):
     return chat_completion(
        messages=[msg.model_dump() for msg in req.messages],
        tools=resolve_tools(req.tools),
        temperature=req.temperature,
        max_tokens=req.max_tokens,
        stream=False
    )