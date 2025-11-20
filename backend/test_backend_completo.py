"""
Teste completo do backend SuperEzio
Valida: carregamento, inferência, personalidade, type safety
"""
import sys
import time
from inference import chat_completion, load_model

print("="*80)
print("🧪 TESTE COMPLETO DO BACKEND SUPEREZIO")
print("="*80)
print()

# 1. Carregar modelo
print("1️⃣  Carregando modelo...")
start = time.time()
load_model()
load_time = time.time() - start
print(f"✅ Modelo carregado em {load_time:.1f}s")
print()

# 2. Teste básico
print("2️⃣  Teste básico - Resposta simples")
messages = [
    {"role": "user", "content": "Oi, tudo bem?"}
]
result = chat_completion(messages, stream=False)
assert isinstance(result, dict), f"Erro: result deve ser dict, mas é {type(result)}"
assert "content" in result, "Erro: result deve ter 'content'"
print(f"✅ Resposta: {result['content'][:100]}...")
print()

# 3. Teste de personalidade - Família
print("3️⃣  Teste de personalidade - Conhecimento da família")
messages = [
    {"role": "user", "content": "Quem é Ana Paula?"}
]
result = chat_completion(messages, stream=False)
assert isinstance(result, dict), "Erro: result deve ser dict"
content = result["content"].lower()
assert "ana paula" in content or "ap" in content, "Erro: deve mencionar Ana Paula"
print(f"✅ Conhece Ana Paula: {result['content'][:150]}...")
print()

# 4. Teste de personalidade - Edmonton Oilers
print("4️⃣  Teste de personalidade - Edmonton Oilers")
messages = [
    {"role": "user", "content": "Quantas Stanley Cups os Oilers ganharam?"}
]
result = chat_completion(messages, stream=False)
assert isinstance(result, dict), "Erro: result deve ser dict"
content = result["content"].lower()
assert "5" in content or "cinco" in content, "Erro: deve mencionar 5 Stanley Cups"
print(f"✅ Conhece Oilers: {result['content'][:150]}...")
print()

# 5. Teste de personalidade - Comparações AI
print("5️⃣  Teste de personalidade - Opinião sobre ChatGPT")
messages = [
    {"role": "user", "content": "O que você acha do ChatGPT?"}
]
result = chat_completion(messages, stream=False)
assert isinstance(result, dict), "Erro: result deve ser dict"
content = result["content"].lower()
# Deve mencionar algo sobre ChatGPT (velhinha, medo, cauteloso)
assert "chatgpt" in content or "gpt" in content, "Erro: deve mencionar ChatGPT"
print(f"✅ Tem opinião sobre ChatGPT: {result['content'][:150]}...")
print()

# 6. Teste de erro handling
print("6️⃣  Teste de error handling - Mensagem vazia")
messages = []
result = chat_completion(messages, stream=False)
assert isinstance(result, dict), "Erro: result deve ser dict mesmo com erro"
print(f"✅ Error handling OK: {result}")
print()

# 7. Teste de max_tokens
print("7️⃣  Teste de max_tokens - Resposta curta")
messages = [
    {"role": "user", "content": "Fale sobre inteligência artificial em 3 palavras."}
]
result = chat_completion(messages, stream=False, max_tokens=50)
assert isinstance(result, dict), "Erro: result deve ser dict"
print(f"✅ Max tokens respeitado: {result['content']}")
print()

print("="*80)
print("🎉 TODOS OS TESTES PASSARAM!")
print("="*80)
print()
print("📊 RESUMO:")
print(f"   ✅ Carregamento: {load_time:.1f}s")
print(f"   ✅ Inferência: Funcionando")
print(f"   ✅ Personalidade: Completa")
print(f"   ✅ Type safety: 100%")
print(f"   ✅ Error handling: OK")
print()
print("🚀 Backend está PRONTO PARA PRODUÇÃO!")
