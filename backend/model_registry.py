"""
Registry de Modelos para SuperEzio com Llama.cpp Engine.
"""
import os
from pathlib import Path
from typing import Optional, Tuple
from transformers import AutoTokenizer, PreTrainedTokenizer
from llama_cpp import Llama

# Configuração
BACKEND_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = BACKEND_DIR.parent.resolve()
# Aponta para o novo modelo GGUF que baixamos
LOCAL_MODEL_PATH = PROJECT_ROOT / "models" / "Qwen2.5-7B-Instruct-Q4_K_M.gguf"

DEVICE = "cuda" if "CUDA_PATH" in os.environ else "cpu"

# Cache Singleton para o motor Llama.cpp e tokenizer
_llama_engine: Optional[Llama] = None
_base_tokenizer: Optional[PreTrainedTokenizer] = None

def load_llama_cpp_model() -> Tuple[Llama, PreTrainedTokenizer]:
    """
    Carrega o motor Llama.cpp e o tokenizer.
    Usa cache global para garantir uma única instância (Singleton).
    """
    global _llama_engine, _base_tokenizer

    if _llama_engine is not None and _base_tokenizer is not None:
        return _llama_engine, _base_tokenizer

    print(f"📂 Carregando modelo GGUF de {LOCAL_MODEL_PATH} com Llama.cpp...")

    if not LOCAL_MODEL_PATH.exists():
        print(f"❌ ERROR: Model file does not exist at the specified path.")
        models_dir = LOCAL_MODEL_PATH.parent
        print(f"Contents of '{models_dir}':")
        try:
            for item in os.listdir(models_dir):
                print(f"  - {item}")
        except Exception as e:
            print(f"    Could not list directory contents: {e}")

        raise FileNotFoundError(
            f"❌ Modelo GGUF não encontrado em {LOCAL_MODEL_PATH}\n"
            f"📥 Execute primeiro: python scripts/download_gguf_model.py"
        )
    
    # O tokenizer pode ser carregado do diretório original do modelo Hugging Face
    tokenizer_path = PROJECT_ROOT / "models" / "qwen2.5-7b-instruct"
    print(f"📂 Carregando tokenizer de {tokenizer_path}...")
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path))

    # Carregar modelo com Llama.cpp
    # n_gpu_layers=-1 significa descarregar todas as camadas possíveis para a GPU
    print("🚀 Inicializando motor Llama.cpp...")
    llm = Llama(
        model_path=str(LOCAL_MODEL_PATH),
        n_ctx=4096,
        n_gpu_layers=-1,
        verbose=True
    )

    _llama_engine = llm
    _base_tokenizer = tokenizer
    
    print(f"✅ Motor Llama.cpp carregado!")

    return llm, tokenizer

def get_model_and_tokenizer() -> Tuple[Llama, PreTrainedTokenizer]:
    """
    Retorna a instância do motor Llama.cpp e o tokenizer.
    """
    return load_llama_cpp_model()

# Funções relacionadas a LoRA e experts são simplificadas ou removidas
# por enquanto, para focar no funcionamento do modelo base com Llama.cpp.
def get_model_for_expert(expert_id: str) -> Tuple[Llama, PreTrainedTokenizer]:
    """Retorna o modelo base para qualquer expert."""
    print(f"[Llama.cpp] Usando modelo base para expert={expert_id}")
    return get_model_and_tokenizer()

def clear_cache():
    """Limpa o cache do motor Llama.cpp."""
    global _llama_engine, _base_tokenizer
    _llama_engine = None
    _base_tokenizer = None

def get_available_modes() -> list[str]:
    """Retorna lista vazia, pois LoRAs não são carregados dinamicamente com Llama.cpp nesta configuração."""
    return []


