"""
Converte persona_familia_mega_v2.jsonl para formato compatível com LLaMA-Factory
Formato: cada linha vira um objeto com instruction/input/output (Alpaca style)
"""
import json

input_file = "C:/Users/marco/Superezio Realtime/data/persona_familia_mega_v2.jsonl"
output_file = "C:/Users/marco/Superezio Realtime/data/familia_alpaca.json"

conversations = []

with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            data = json.loads(line)
            messages = data['messages']
            
            # Encontrar system, user e assistant
            system_msg = ""
            user_msg = ""
            assistant_msg = ""
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_msg = msg['content']
                elif msg['role'] == 'user':
                    user_msg = msg['content']
                elif msg['role'] == 'assistant':
                    assistant_msg = msg['content']
            
            # Formato Alpaca para LLaMA-Factory
            conversations.append({
                "instruction": user_msg,
                "input": system_msg,  # System prompt como contexto
                "output": assistant_msg
            })

# Salvar como JSON array
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(conversations, f, ensure_ascii=False, indent=2)

print(f"✅ Convertido {len(conversations)} conversas")
print(f"📁 Salvo em: {output_file}")
