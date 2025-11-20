"""
Model Loader - Carrega o modelo e mantém em memória
Processo independente que carrega o modelo ANTES dos outros componentes
"""
import os
import sys
import time
import json
from pathlib import Path
from inference import load_model, LOCAL_MODEL_DIR, DEVICE
import torch

# Arquivo de status para comunicação com outros processos
STATUS_FILE = Path(__file__).parent / "model_status.json"

def save_status(status: str, error: str = None):
    """Salva status do carregamento do modelo"""
    data = {
        "status": status,  # "loading", "ready", "error"
        "error": error,
        "timestamp": time.time(),
        "model_path": str(LOCAL_MODEL_DIR),
        "device": DEVICE,
    }
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    print("=" * 60)
    print("🤖 SuperEzio - Model Loader")
    print("=" * 60)
    print(f"📊 Dispositivo: {DEVICE}")
    print(f"🤖 Modelo: {LOCAL_MODEL_DIR}")
    print()
    
    # Verificar se modelo existe
    if not LOCAL_MODEL_DIR.exists():
        error_msg = f"❌ Modelo não encontrado em {LOCAL_MODEL_DIR}"
        print(error_msg)
        save_status("error", error_msg)
        sys.exit(1)
    
    # Marcar como carregando
    save_status("loading")
    print("⏳ Carregando modelo... (isso pode levar 1-2 minutos)")
    print()
    
    try:
        # Carregar modelo (isso vai preencher as variáveis globais)
        load_model()
        
        # Verificar se carregou corretamente
        from inference import model, tokenizer, generator
        if model is None or tokenizer is None or generator is None:
            raise Exception("Modelo não foi carregado corretamente")
        
        # Marcar como pronto
        vram_used = torch.cuda.memory_allocated(0) / 1024**3 if DEVICE == "cuda" else 0
        save_status("ready")
        
        print("=" * 60)
        print("✅ MODELO CARREGADO COM SUCESSO!")
        print("=" * 60)
        print(f"💾 VRAM usada: {vram_used:.2f} GB")
        print(f"🌐 Status: OFFLINE (sem dependência do Hugging Face)")
        print()
        print("🔄 Modelo está pronto e mantido em memória.")
        print("📝 Outros componentes podem ser iniciados agora.")
        print("⏸️  Pressione Ctrl+C para descarregar o modelo.")
        print("=" * 60)
        print()
        
        # Manter processo vivo (modelo em memória)
        try:
            while True:
                time.sleep(1)
                # Atualizar timestamp do status periodicamente
                save_status("ready")
        except KeyboardInterrupt:
            print("\n🛑 Descarregando modelo...")
            save_status("error", "Processo interrompido")
            sys.exit(0)
            
    except Exception as e:
        error_msg = f"❌ Erro ao carregar modelo: {e}"
        print(error_msg)
        save_status("error", str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

