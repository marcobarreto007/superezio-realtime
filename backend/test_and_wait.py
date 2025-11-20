"""
Script que aguarda servidor estar pronto e executa testes
"""
import requests
import time
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"
MAX_WAIT = 120  # 2 minutos máximo


def wait_for_server():
    """Aguarda servidor estar pronto"""
    print("⏳ Aguardando servidor estar pronto...")
    print(f"   URL: {BASE_URL}")
    print(f"   Timeout máximo: {MAX_WAIT}s\n")
    
    start_time = time.time()
    attempt = 0
    
    while time.time() - start_time < MAX_WAIT:
        attempt += 1
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                elapsed = time.time() - start_time
                print(f"✅ Servidor está pronto! (após {elapsed:.1f}s, {attempt} tentativas)\n")
                return True
        except:
            if attempt % 10 == 0:
                elapsed = time.time() - start_time
                print(f"   Tentativa {attempt}... ({elapsed:.1f}s)")
            time.sleep(1)
    
    print(f"❌ Servidor não respondeu após {MAX_WAIT}s")
    return False


if __name__ == "__main__":
    if wait_for_server():
        print("🚀 Executando testes...\n")
        # Importar e executar testes
        sys.path.insert(0, str(Path(__file__).parent))
        from test_system_completo import run_all_tests
        run_all_tests()
    else:
        print("\n💡 Dica: Inicie o servidor com:")
        print("   .\\start_backend_python.bat")
        sys.exit(1)

