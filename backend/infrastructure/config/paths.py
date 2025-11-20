"""
Paths centralizados do sistema.
Resolve caminhos relativos ao projeto de forma consistente.
"""
from pathlib import Path
from infrastructure.config.settings import get_settings


# Diretório raiz do backend
BACKEND_DIR = Path(__file__).parent.parent.parent.resolve()

# Diretório raiz do projeto (um nível acima do backend)
PROJECT_ROOT = BACKEND_DIR.parent.resolve()

# Paths de modelos (usando settings)
settings = get_settings()


def get_model_path() -> Path:
    """Retorna path do modelo base"""
    path = settings.model_path
    if not path.is_absolute():
        return PROJECT_ROOT / path
    return path


def get_lora_path(mode: str) -> Path:
    """Retorna path do LoRA para o modo especificado"""
    path_map = {
        "familia": settings.lora_familia_path,
        "accounting": settings.lora_accounting_path,
        "legacy": settings.lora_legacy_path,
    }
    
    if mode not in path_map:
        raise ValueError(f"LoRA mode '{mode}' não encontrado")
    
    path = path_map[mode]
    if not path.is_absolute():
        return PROJECT_ROOT / path
    return path


def get_data_path() -> Path:
    """Retorna path do diretório de dados"""
    return PROJECT_ROOT / "data"


def get_logs_path() -> Path:
    """Retorna path do diretório de logs"""
    path = settings.log_dir
    if not path.is_absolute():
        return PROJECT_ROOT / path
    return path

