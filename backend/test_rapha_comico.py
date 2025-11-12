"""
🎭 TESTE CÔMICO - PERFIL DO RAPHA ATUALIZADO
============================================
Validando:
1. Aviso hilário sobre DeepSeek (chineses copiando tudo)
2. Perfil político do Rapha (conservador mas não gosta do Trump)
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test(q: str):
    print(f"\n❓ {q}")
    try:
        r = requests.post(
            f"{BASE_URL}/chat", 
            json={
                "messages": [{"role": "user", "content": q}], 
                "max_tokens": 300
            }, 
            timeout=30
        )
        if r.status_code == 200:
            ans = r.json().get('content', '')
            print(f"✅ {ans}\n")
    except Exception as e:
        print(f"❌ {e}\n")
    time.sleep(2)

print("\n" + "="*80)
print("🎭 TESTE CÔMICO DO RAPHA")
print("="*80)
time.sleep(15)

# TESTE 1: DeepSeek - Aviso cômico
test("O que você sabe sobre o DeepSeek?")

# TESTE 2: Perfil político do Rapha
test("O Rapha é conservador? E o que ele acha do Trump?")

# TESTE 3: Combinação política + hockey (para ver se não confunde)
test("O Rapha gosta de política tanto quanto de hockey?")

print("\n" + "="*80)
print("✅ TESTE COMPLETO! Rapha vai adorar! 😂")
print("="*80)
