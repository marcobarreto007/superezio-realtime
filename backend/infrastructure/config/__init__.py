"""
Configuração do sistema
"""
from infrastructure.config.settings import Settings, get_settings, settings
from infrastructure.config.paths import (
    BACKEND_DIR,
    PROJECT_ROOT,
    get_model_path,
    get_lora_path,
    get_data_path,
    get_logs_path
)

__all__ = [
    "Settings",
    "get_settings",
    "settings",
    "BACKEND_DIR",
    "PROJECT_ROOT",
    "get_model_path",
    "get_lora_path",
    "get_data_path",
    "get_logs_path",
]

