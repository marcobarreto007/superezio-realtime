"""
Teste do fluxo RAG via API HTTP
Verifica se o backend injeta corretamente o contexto RAG no prompt
"""
import requests
import json

print("=" * 80)
print("🧪 TESTE RAG VIA API HTTP")
print("=" * 80)

# Teste 1: Sem RAG (controle)
print("\n🔵 TESTE 1: Pergunta SEM RAG context")
payload1 = {
    "messages": [
        {"role": "user", "content": "Qual universidade o Rapha estuda?"}
    ],
    "max_tokens": 100,
    "temperature": 0.3
}

try:
    response1 = requests.post(
        "http://localhost:8000/chat",
        json=payload1,
        timeout=30
    )
    result1 = response1.json()
    print(f"📝 Resposta: {result1.get('content', 'Erro')[:200]}")
except Exception as e:
    print(f"❌ Erro: {e}")

# Teste 2: Com RAG
print("\n🟢 TESTE 2: Pergunta COM RAG context")
payload2 = {
    "messages": [
        {
            "role": "user", 
            "content": "Qual universidade o Rapha estuda?",
            "rag_context": "INFORMAÇÃO RELEVANTE: Rapha BARRETO está na UdeM (Université de Montréal), fazendo Ciências Políticas→Direito. Notas sempre A/A+!"
        }
    ],
    "max_tokens": 100,
    "temperature": 0.3
}

try:
    response2 = requests.post(
        "http://localhost:8000/chat",
        json=payload2,
        timeout=30
    )
    result2 = response2.json()
    print(f"📝 Resposta: {result2.get('content', 'Erro')[:200]}")
except Exception as e:
    print(f"❌ Erro: {e}")

# Teste 3: RAG com múltiplas informações
print("\n🟣 TESTE 3: RAG com contexto COMPLEXO")
payload3 = {
    "messages": [
        {
            "role": "user",
            "content": "Me fale sobre o Rapha",
            "rag_context": """INFORMAÇÕES SOBRE RAPHA BARRETO:
- Filho do Marco
- Universitário na UdeM (Université de Montréal)
- Curso: Ciências Políticas → Direito
- Notas: SEMPRE A/A+
- FÃ FANÁTICO dos Edmonton Oilers 🏒
- Ama sushi
- Joga League of Legends
- Curte MMA e boxe
- Conservador mas ANTI-TRUMP"""
        }
    ],
    "max_tokens": 200,
    "temperature": 0.3
}

try:
    response3 = requests.post(
        "http://localhost:8000/chat",
        json=payload3,
        timeout=30
    )
    result3 = response3.json()
    print(f"📝 Resposta: {result3.get('content', 'Erro')[:400]}")
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n" + "=" * 80)
print("✅ TESTE RAG COMPLETO!")
print("=" * 80)
