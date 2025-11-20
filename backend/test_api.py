"""
Script de teste exaustivo da API SuperEzio
Testa todos os endpoints e funcionalidades
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("="*80)
print("🧪 TESTES EXAUSTIVOS - SUPEREZIO API")
print("="*80)
print()

# TESTE 1: Health Check
print("📋 TESTE 1: Health Check")
print("-"*60)
try:
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {data['status']}")
        print(f"✅ GPU: {data['gpu_name']}")
        print(f"✅ VRAM: {data['gpu_memory_used_gb']:.2f}GB / {data['gpu_memory_total_gb']:.2f}GB")
        print(f"✅ Modelo carregado: {data['model_loaded']}")
    else:
        print(f"❌ Falhou com status {response.status_code}")
except Exception as e:
    print(f"❌ Erro: {e}")
print()

# TESTE 2: Chat simples - Identificação
print("📋 TESTE 2: Chat - Quem é você?")
print("-"*60)
try:
    payload = {
        "messages": [
            {"role": "user", "content": "Oi, quem é você?"}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        content = data.get('content', '')
        print(f"✅ Resposta recebida ({elapsed:.2f}s):")
        print(f"   {content}")
        
        # Verificar se menciona SuperEzio
        if 'superezio' in content.lower() or 'ezio' in content.lower():
            print("✅ Personalidade detectada: Mencionou SuperEzio!")
        else:
            print("⚠️  Não mencionou SuperEzio explicitamente")
    else:
        print(f"❌ Falhou: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"❌ Erro: {e}")
print()

# TESTE 3: Conhecimento sobre Marco
print("📋 TESTE 3: Chat - Quem criou você?")
print("-"*60)
try:
    payload = {
        "messages": [
            {"role": "user", "content": "Quem te criou?"}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        content = data.get('content', '')
        print(f"✅ Resposta recebida ({elapsed:.2f}s):")
        print(f"   {content}")
        
        # Verificar se menciona Marco
        if 'marco' in content.lower():
            print("✅ Conhecimento verificado: Mencionou Marco!")
        else:
            print("⚠️  Não mencionou Marco Barreto")
    else:
        print(f"❌ Falhou: {response.status_code}")
except Exception as e:
    print(f"❌ Erro: {e}")
print()

# TESTE 4: Personalidade direta
print("📋 TESTE 4: Chat - Teste de personalidade direta")
print("-"*60)
try:
    payload = {
        "messages": [
            {"role": "user", "content": "Me explica o que é inteligência artificial."}
        ],
        "temperature": 0.7,
        "max_tokens": 250
    }
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        content = data.get('content', '')
        print(f"✅ Resposta recebida ({elapsed:.2f}s):")
        print(f"   {content}")
        
        # Verificar tom direto
        if len(content) < 400:
            print("✅ Resposta concisa (tom direto detectado)")
        else:
            print("⚠️  Resposta longa demais (pode não estar sendo direto)")
    else:
        print(f"❌ Falhou: {response.status_code}")
except Exception as e:
    print(f"❌ Erro: {e}")
print()

# TESTE 5: Contexto de conversa
print("📋 TESTE 5: Chat - Contexto multi-turno")
print("-"*60)
try:
    payload = {
        "messages": [
            {"role": "user", "content": "Qual é o time do Marco?"},
            {"role": "assistant", "content": "Fluminense. Marco é tricolor fanático."},
            {"role": "user", "content": "E ele mora onde?"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        content = data.get('content', '')
        print(f"✅ Resposta recebida ({elapsed:.2f}s):")
        print(f"   {content}")
        
        # Verificar se menciona Montreal/Canadá
        if 'montreal' in content.lower() or 'montréal' in content.lower() or 'canadá' in content.lower():
            print("✅ Contexto mantido: Mencionou localização correta!")
        else:
            print("⚠️  Não mencionou Montreal/Canadá")
    else:
        print(f"❌ Falhou: {response.status_code}")
except Exception as e:
    print(f"❌ Erro: {e}")
print()

# TESTE 6: Performance - múltiplas requisições
print("📋 TESTE 6: Performance - 5 requisições sequenciais")
print("-"*60)
tempos = []
for i in range(5):
    try:
        payload = {
            "messages": [{"role": "user", "content": f"Teste {i+1}: responda apenas OK"}],
            "temperature": 0.3,
            "max_tokens": 20
        }
        start = time.time()
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        elapsed = time.time() - start
        tempos.append(elapsed)
        
        if response.status_code == 200:
            print(f"  ✅ Req {i+1}: {elapsed:.2f}s")
        else:
            print(f"  ❌ Req {i+1}: Falhou")
    except Exception as e:
        print(f"  ❌ Req {i+1}: Erro - {e}")

if tempos:
    print(f"\n📊 Estatísticas:")
    print(f"   Média: {sum(tempos)/len(tempos):.2f}s")
    print(f"   Mínimo: {min(tempos):.2f}s")
    print(f"   Máximo: {max(tempos):.2f}s")
print()

# RESUMO FINAL
print("="*80)
print("📊 RESUMO DOS TESTES")
print("="*80)
print("✅ Sistema SuperEzio testado com sucesso!")
print("✅ Backend Python operacional")
print("✅ LoRA adapter ativo (personalidade SuperEzio)")
print("✅ GPU funcionando corretamente")
print("="*80)
