"""
Configuração centralizada do sistema.
Valida variáveis de ambiente e fornece acesso tipado via Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List, Optional


class Settings(BaseSettings):
    """Configurações do sistema validadas via Pydantic"""
    
    # Modelo
    model_path: Path = Path("models/qwen2.5-7b-instruct")
    device: str = "cuda"  # cuda ou cpu
    
    # LoRA Adapters
    lora_familia_path: Path = Path("models/lora_familia_hardcore_v1")
    lora_accounting_path: Path = Path("models/lora_accounting")
    lora_legacy_path: Path = Path("models/lora_superezio")
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # Rate Limiting
    rate_limit_chat: int = 30  # req/min
    rate_limit_stream: int = 10  # req/min
    rate_limit_tools: int = 100  # req/min
    
    # RAG
    rag_top_k: int = 6
    rag_use_enhanced: bool = True
    
    # Tools
    express_api_url: str = "http://localhost:8080"
    tool_timeout: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_dir: Path = Path("logs")
    
    # HuggingFace (opcional)
    hf_token: Optional[str] = None
    
    # Inference
    max_tokens_default: int = 512
    temperature_default: float = 0.7
    max_tokens_max: int = 2048
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_prefix = ""  # Sem prefixo nas env vars
        extra = 'ignore'


# Instância global (singleton)
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Retorna instância singleton de Settings"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Alias para facilitar imports
settings = get_settings()

