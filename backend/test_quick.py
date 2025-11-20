"""
Teste Rápido - Valida funcionalidades básicas
Útil para verificar se sistema está funcionando
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_quick():
    """Teste rápido de funcionalidades básicas"""
    print("="*60)
    print("🧪 TESTE RÁPIDO - SuperEzio v2.1.0")
    print("="*60)
    print()
    
    # 1. Health Check
    print("1️⃣  Testando Health Check...")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            print("   ✅ Health check OK")
        else:
            print(f"   ❌ Status: {r.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        print("   💡 Certifique-se de que o servidor está rodando")
        return
    
    # 2. Métricas
    print("\n2️⃣  Testando Métricas...")
    try:
        r = requests.get(f"{BASE_URL}/metrics", timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"   ✅ Métricas disponíveis")
            print(f"   📊 Contadores: {len(data.get('counters', {}))}")
            print(f"   📊 Histogramas: {len(data.get('histograms', {}))}")
        else:
            print(f"   ⚠️  Status: {r.status_code}")
    except Exception as e:
        print(f"   ⚠️  Erro: {e}")
    
    # 3. Chat básico
    print("\n3️⃣  Testando Chat Básico...")
    try:
        payload = {
            "messages": [{"role": "user", "content": "Olá! Diga apenas 'OK'"}],
            "max_tokens": 50
        }
        r = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        if r.status_code == 200:
            data = r.json()
            content = data.get("content", "")
            print(f"   ✅ Chat funcionando")
            print(f"   💬 Resposta: {content[:100]}...")
        else:
            print(f"   ❌ Status: {r.status_code}")
            print(f"   Resposta: {r.text[:200]}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. RAG Injection
    print("\n4️⃣  Testando RAG Injection...")
    try:
        rag_info = "Código de teste: TEST-123-ABC"
        payload = {
            "messages": [{
                "role": "user",
                "content": "Qual é o código de teste?",
                "ragContext": [rag_info]
            }],
            "max_tokens": 100
        }
        r = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        if r.status_code == 200:
            data = r.json()
            content = data.get("content", "").lower()
            if "test-123" in content or "test-123-abc" in content:
                print("   ✅ RAG foi injetado e usado")
            else:
                print("   ⚠️  RAG injetado mas não detectado na resposta")
                print(f"   Resposta: {content[:150]}")
        else:
            print(f"   ❌ Status: {r.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "="*60)
    print("✅ Teste rápido concluído!")
    print("="*60)


if __name__ == "__main__":
    test_quick()
