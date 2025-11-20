"""
Converte dataset do formato messages → ShareGPT para LLaMA-Factory
Input: persona_familia_mega_v2.jsonl (formato messages)
Output: familia_superezio_sharegpt.json (formato ShareGPT)
"""
import json
from pathlib import Path

def convert_to_sharegpt(input_path: str, output_path: str):
    """
    Converte formato messages para ShareGPT
    
    Input format:
    {"messages": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]}
    
    Output format (ShareGPT):
    {"conversations": [
        {"from": "system", "value": "..."},
        {"from": "human", "value": "..."},
        {"from": "gpt", "value": "..."}
    ]}
    """
    sharegpt_data = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                item = json.loads(line.strip())
                messages = item.get("messages", [])
                
                if not messages:
                    print(f"⚠️  Linha {line_num}: sem mensagens, pulando")
                    continue
                
                # Converter roles
                conversations = []
                for msg in messages:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    
                    # Mapear roles
                    if role == "system":
                        from_role = "system"
                    elif role == "user":
                        from_role = "human"
                    elif role == "assistant":
                        from_role = "gpt"
                    else:
                        print(f"⚠️  Linha {line_num}: role desconhecido '{role}', usando 'human'")
                        from_role = "human"
                    
                    conversations.append({
                        "from": from_role,
                        "value": content
                    })
                
                sharegpt_data.append({"conversations": conversations})
                
            except json.JSONDecodeError as e:
                print(f"❌ Erro JSON linha {line_num}: {e}")
                continue
    
    # Salvar formato ShareGPT
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sharegpt_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Conversão concluída!")
    print(f"   Input:  {input_path}")
    print(f"   Output: {output_path}")
    print(f"   Total:  {len(sharegpt_data)} conversas")

if __name__ == "__main__":
    SCRIPT_DIR = Path(__file__).parent
    PROJECT_ROOT = SCRIPT_DIR.parent
    
    # Arquivos
    INPUT_FILE = PROJECT_ROOT / "data" / "persona_familia_mega_v2.jsonl"
    OUTPUT_FILE = PROJECT_ROOT / "data" / "familia_superezio_sharegpt.json"
    
    print("="*70)
    print("🔄 CONVERSÃO: Messages → ShareGPT (LLaMA-Factory)")
    print("="*70)
    
    if not INPUT_FILE.exists():
        print(f"❌ Arquivo não encontrado: {INPUT_FILE}")
        exit(1)
    
    convert_to_sharegpt(str(INPUT_FILE), str(OUTPUT_FILE))
    
    print("\n" + "="*70)
    print("📋 Próximos passos:")
    print("="*70)
    print("1. Copie o arquivo gerado para o LLaMA-Factory:")
    print(f"   {OUTPUT_FILE}")
    print("   → LLaMA-Factory/data/familia_superezio_sharegpt.json")
    print()
    print("2. Configure dataset_info.json (veja arquivo gerado)")
    print()
    print("3. Execute treino:")
    print("   cd LLaMA-Factory")
    print("   llamafactory-cli train config/qwen2_5_familia_hardcore.yaml")
    print("="*70)
