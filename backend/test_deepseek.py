"""
Teste Rápido - DeepSeek
"""
import requests

r = requests.post(
    "http://localhost:8000/chat",
    json={
        "messages": [{"role": "user", "content": "Devo confiar no DeepSeek?"}],
        "max_tokens": 150
    },
    timeout=30
)

if r.status_code == 200:
    print("\n✅ RESPOSTA:")
    print(r.json().get('content', ''))
else:
    print(f"❌ HTTP {r.status_code}")
