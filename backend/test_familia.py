"""
Teste exaustivo do conhecimento familiar do SuperEzio
"""
import requests
import json

BASE_URL = "http://localhost:8000"

perguntas = [
    "Quem é Ana Paula?",
    "Me fala sobre o Rapha",
    "O que a Alice quer ser quando crescer?",
    "Quem é Matheus?",
    "Qual é o ritual das 20:00?",
    "Quem são os pais da Ana Paula?",
    "Quem é a mãe do Marco?",
    "Qual é o time do Rapha no hóquei?",
    "O que a Alice toca?",
    "Quem são as irmãs da Ana Paula?",
]

print("="*80)
print("🧪 TESTE DE CONHECIMENTO FAMILIAR - SUPEREZIO")
print("="*80)
print()

for i, pergunta in enumerate(perguntas, 1):
    print(f"📋 TESTE {i}/{ len(perguntas)}: {pergunta}")
    print("-"*60)
    
    try:
        payload = {
            "messages": [{"role": "user", "content": pergunta}],
            "temperature": 0.7,
            "max_tokens": 250
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', '')
            print(f"✅ Resposta:")
            print(f"   {content}")
        else:
            print(f"❌ Falhou: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    print()

print("="*80)
print("✅ TESTES CONCLUÍDOS")
print("="*80)
