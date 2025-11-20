"""
Response Schemas (DTOs)
Pydantic models para respostas da API
"""
from pydantic import BaseModel
from typing import List, Dict, Optional, Any


class ChatMessage(BaseModel):
    """Mensagem na resposta"""
    role: str
    content: str


class ChatChoice(BaseModel):
    """Choice na resposta"""
    index: int
    message: ChatMessage
    finish_reason: str


class ChatResponse(BaseModel):
    """Response de chat completion"""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    expert: Optional[str] = None
    lora_adapter: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    usage: Optional[Dict[str, int]] = None


class HealthResponse(BaseModel):
    """Response de health check"""
    status: str
    gpu_available: bool
    gpu_name: Optional[str] = None
    gpu_memory_total_gb: float = 0.0
    gpu_memory_used_gb: float = 0.0
    model_loaded: bool


class MetricsResponse(BaseModel):
    """Response de métricas"""
    counters: Dict[str, int]
    histograms: Dict[str, Dict[str, Any]]

