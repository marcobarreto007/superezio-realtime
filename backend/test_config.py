# -*- coding: utf-8 -*-
"""
Testes básicos para configuração do backend Python
Testes que NÃO carregam o modelo (rápidos)
"""
import sys
import os
from pathlib import Path

# Adicionar backend ao path
BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))

def test_imports():
    """Testa se todos os imports necessários funcionam"""
    try:
        import torch
        import transformers
        import fastapi
        import uvicorn
        from peft import PeftModel
        print("✅ Todos os imports funcionando")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar: {e}")
        return False

def test_torch_cuda():
    """Testa se CUDA está disponível"""
    import torch
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        device_name = torch.cuda.get_device_name(0)
        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"✅ CUDA disponível: {device_name} ({total_memory:.1f} GB)")
    else:
        print("⚠️  CUDA não disponível - rodará em CPU")
    return True

def test_model_path():
    """Testa se o caminho do modelo está correto"""
    from inference import LOCAL_MODEL_DIR, LORA_ADAPTER_DIR

    if LOCAL_MODEL_DIR.exists():
        print(f"✅ Modelo encontrado: {LOCAL_MODEL_DIR}")
        # Verificar arquivos críticos
        config_file = LOCAL_MODEL_DIR / "config.json"
        if config_file.exists():
            print(f"✅ config.json encontrado")
        else:
            print(f"⚠️  config.json NÃO encontrado")
    else:
        print(f"❌ Modelo NÃO encontrado: {LOCAL_MODEL_DIR}")
        return False

    # LoRA é opcional
    if LORA_ADAPTER_DIR.exists():
        print(f"✅ Adaptador LoRA encontrado: {LORA_ADAPTER_DIR}")
    else:
        print(f"ℹ️  Adaptador LoRA não encontrado (opcional)")

    return True

def test_api_endpoints():
    """Testa se os endpoints da API estão definidos"""
    try:
        from api import app
        routes = [route.path for route in app.routes]

        expected_routes = ["/", "/health", "/chat", "/chat/stream"]
        for route in expected_routes:
            if route in routes:
                print(f"✅ Endpoint '{route}' definido")
            else:
                print(f"❌ Endpoint '{route}' NÃO encontrado")
                return False

        return True
    except Exception as e:
        print(f"❌ Erro ao verificar endpoints: {e}")
        return False

def run_all_tests():
    """Executa todos os testes"""
    print("="*60)
    print("🧪 TESTES DE CONFIGURAÇÃO BACKEND")
    print("="*60)

    tests = [
        ("Imports", test_imports),
        ("CUDA/GPU", test_torch_cuda),
        ("Caminho do Modelo", test_model_path),
        ("Endpoints da API", test_api_endpoints),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n📋 Teste: {name}")
        print("-"*60)
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Exceção no teste '{name}': {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\nTotal: {passed}/{total} testes passaram")
    print("="*60)

    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
