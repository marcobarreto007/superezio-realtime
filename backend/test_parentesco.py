"""
Teste específico: Matheus é irmão de quem?
"""
import requests

BASE_URL = "http://localhost:8000"

perguntas = [
    "Matheus é irmão de quem? Do Marco ou da Ana Paula?",
    "Quem são os irmãos da Ana Paula?",
    "O Marco tem irmãos?",
]

print("="*80)
print("🧪 TESTE ESPECÍFICO - PARENTESCO DO MATHEUS")
print("="*80)
print()

for i, pergunta in enumerate(perguntas, 1):
    print(f"📋 TESTE {i}: {pergunta}")
    print("-"*60)
    
    try:
        payload = {
            "messages": [{"role": "user", "content": pergunta}],
            "temperature": 0.3,
            "max_tokens": 150
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', '')
            print(f"✅ Resposta:")
            print(f"   {content}")
        else:
            print(f"❌ Falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    print()

print("="*80)
