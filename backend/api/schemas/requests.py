"""
Request Schemas (DTOs)
Pydantic models para validação de entrada
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any, Union


class Message(BaseModel):
    """Mensagem de chat"""
    role: str
    content: str
    rag_context: Optional[Union[str, List[str]]] = Field(default=None, alias="ragContext")
    
    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class ChatRequest(BaseModel):
    """Request para completion de chat"""
    messages: List[Message]
    model: Optional[str] = "Qwen2.5-7B-Instruct"
    temperature: float = 0.7
    max_tokens: int = 512
    tools: Optional[List[Dict[str, Any]]] = None
    stream: bool = False
    mode: Optional[str] = None  # Modo/perfil LoRA

