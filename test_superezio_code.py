"""
Teste rapido da persona SuperEzio-Code (sem emojis)
"""
import sys
sys.path.append('backend')

from inference import chat_completion

print("=" * 70)
print("TESTE SUPEREZIO-CODE PERSONA")
print("=" * 70)
print()

# Teste 1: Identidade tecnica
print("TESTE 1: Quem e voce e o que voce sabe fazer com codigo?")
print()

messages = [
    {"role": "user", "content": "Quem é você e o que você sabe fazer com código?"}
]

response = chat_completion(messages, [])

print()
print("=" * 70)
print("RESPOSTA:")
print("=" * 70)
print(response['content'])
print()
print("=" * 70)
print(f"Expert usado: {response.get('expert_id', 'N/A')}")
print(f"LoRA: {response.get('lora_adapter', 'N/A')}")
print(f"Tempo: {response.get('generation_time', 0):.2f}s")
print("=" * 70)
print()
