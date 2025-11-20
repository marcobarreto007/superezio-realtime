"""
Script para baixar modelo do Hugging Face UMA VEZ
Depois disso, modelo fica 100% local e funciona offline
"""
import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForCausalLM

# Fix encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuração
HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", None)  # ⚠️ Configure via env var
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"

# Localização do modelo
# Opção 1: Mesmo disco do projeto (C:) - RECOMENDADO
LOCAL_MODEL_DIR = Path("./models/qwen2.5-7b-instruct").resolve()
# Resultado: C:\Users\marco\Superezio Realtime\models\qwen2.5-7b-instruct\

# Opção 2: Disco D: (descomente se preferir)
# LOCAL_MODEL_DIR = Path("D:/models/qwen2.5-7b-instruct")
# ou
# LOCAL_MODEL_DIR = Path("D:/SuperEzio/models/qwen2.5-7b-instruct")

def download_model():
    """Baixa modelo do HF e salva localmente (UMA VEZ)"""
    print("=" * 60)
    print("📥 DOWNLOAD DE MODELO - HUGGING FACE")
    print("=" * 60)
    print(f"🎯 Modelo: {MODEL_NAME}")
    print(f"💾 Destino: {LOCAL_MODEL_DIR}")
    print(f"📊 Tamanho estimado: ~5-7 GB")
    print()
    print("⚠️  Este download acontece UMA VEZ.")
    print("✅ Depois disso, o modelo funciona 100% offline!")
    print()
    
    # Criar diretório se não existir
    LOCAL_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        print("🔄 Baixando modelo...")
        print("   (Isso pode levar 10-30 minutos dependendo da internet)")
        print()
        
        # Baixar modelo completo do Hugging Face
        snapshot_download(
            repo_id=MODEL_NAME,
            token=HF_TOKEN,
            local_dir=str(LOCAL_MODEL_DIR),
            local_dir_use_symlinks=False,  # Copiar arquivos, não symlinks
        )
        
        # Verificar se baixou corretamente
        if not (LOCAL_MODEL_DIR / "config.json").exists():
            raise FileNotFoundError("Modelo não foi baixado corretamente")
        
        print()
        print("=" * 60)
        print("✅ DOWNLOAD CONCLUÍDO!")
        print("=" * 60)
        print(f"📍 Localização: {LOCAL_MODEL_DIR}")
        print(f"💾 Tamanho: ~{get_dir_size(LOCAL_MODEL_DIR) / 1024**3:.2f} GB")
        print()
        print("🚀 Agora você pode usar o modelo 100% OFFLINE!")
        print("   Execute: python server/hf_inference.py")
        print()
        print("🌐 Você pode desconectar a internet agora.")
        print("   O modelo não precisa mais do Hugging Face!")
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERRO NO DOWNLOAD")
        print("=" * 60)
        print(f"Erro: {e}")
        print()
        print("💡 Verifique:")
        print("   1. Token do Hugging Face está correto?")
        print("   2. Você tem espaço em disco? (~7GB)")
        print("   3. Conexão com internet está funcionando?")
        sys.exit(1)

def get_dir_size(path: Path) -> int:
    """Calcula tamanho do diretório"""
    total = 0
    for entry in path.rglob("*"):
        if entry.is_file():
            total += entry.stat().st_size
    return total

if __name__ == "__main__":
    download_model()

