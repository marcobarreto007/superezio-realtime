"""
Teste Simplificado - Validação Final
======================================
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test(q: str):
    print(f"\n❓ {q}")
    try:
        r = requests.post(f"{BASE_URL}/chat", json={"messages": [{"role": "user", "content": q}], "max_tokens": 200}, timeout=30)
        if r.status_code == 200:
            print(f"✅ {r.json().get('content', '')}\n")
    except Exception as e:
        print(f"❌ {e}\n")
    time.sleep(2)

print("\n🧪 VALIDAÇÃO FINAL\n")
time.sleep(15)

test("Ana Paula é a mais velha das irmãs?")
test("Quantas Stanley Cups os Oilers ganharam?")
test("O que você acha do ChatGPT?")

print("\n✅ FIM")
