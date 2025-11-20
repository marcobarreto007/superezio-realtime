"""
Teste: SuperEzio conhece as ferramentas e cria arquivo
"""
import sys
sys.path.append('backend')

from inference import chat_completion

print("=" * 70)
print("TESTE: FERRAMENTAS E CRIACAO DE ARQUIVO")
print("=" * 70)
print()

# Teste 1: Quais ferramentas tem acesso?
print("TESTE 1: Quais ferramentas voce tem acesso?")
print("-" * 70)

messages1 = [
    {"role": "user", "content": "Quais ferramentas você tem acesso? Liste todas."}
]

response1 = chat_completion(messages1, [])

print()
print("RESPOSTA:")
print("=" * 70)
print(response1['content'])
print("=" * 70)
print()

# Teste 2: Criar arquivo na área de trabalho
print()
print("TESTE 2: Criar arquivo na area de trabalho")
print("-" * 70)

messages2 = [
    {"role": "user", "content": "Crie um arquivo chamado 'teste_superezio.txt' na minha área de trabalho com o texto 'SuperEzio funcionando! Data: 13/11/2025'"}
]

response2 = chat_completion(messages2, [])

print()
print("RESPOSTA:")
print("=" * 70)
print(response2['content'])
print("=" * 70)
print()
