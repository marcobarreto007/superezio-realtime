"""
Teste de correção: Matheus é irmão da Ana Paula, não do Marco
"""
import requests

BASE_URL = "http://localhost:8000"

print("="*80)
print("🧪 TESTE DE CORREÇÃO - MATHEUS")
print("="*80)
print()

pergunta = "Quem é Matheus?"
print(f"📋 Pergunta: {pergunta}")
print("-"*60)

try:
    payload = {
        "messages": [{"role": "user", "content": pergunta}],
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        content = data.get('content', '')
        print(f"✅ Resposta:")
        print(f"   {content}")
        print()
        
        # Verificar correção
        if 'irmão da ana paula' in content.lower() or 'irmão da ap' in content.lower():
            print("✅ CORRETO: Identificou como irmão da Ana Paula!")
        elif 'irmão do marco' in content.lower():
            print("❌ ERRO: Ainda diz que é irmão do Marco!")
        else:
            print("⚠️  Não especificou claramente de quem é irmão")
    else:
        print(f"❌ Falhou: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"❌ Erro: {e}")

print()
print("="*80)
print("INSTRUÇÕES:")
print("Se aparecer erro de conexão, reinicie o backend:")
print("  cd c:\\Users\\marco\\Superezio Realtime")
print("  start_backend_persistent.bat")
print("="*80)
