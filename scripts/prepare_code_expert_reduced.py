"""
Dataset Code Expert REDUZIDO para RTX 3060
Gera ~1000 exemplos high-quality mantendo RTX 3060 feliz

Estratégia:
- 200 exemplos REAIS do projeto (100%)
- 800 exemplos SINTÉTICOS (top quality)
Total: 1000 exemplos (20x menor que 50k)
"""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CODE_EXPERT_DIR = PROJECT_ROOT / "data" / "code_expert"
REAL_FILES = CODE_EXPERT_DIR / "code_expert_dataset.jsonl"
OUTPUT = PROJECT_ROOT / "data" / "code_expert_reduced.jsonl"

def extract_reduced_dataset():
    """Extrai 1000 melhores exemplos"""
    print("📚 Carregando dataset original (50k)...")
    
    real_examples = []
    synthetic_examples = []
    
    with open(REAL_FILES, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            
            try:
                example = json.loads(line)
                # Identificar exemplos reais vs sintéticos
                # Reais têm system content mais específico do projeto
                system = example["messages"][0]["content"]
                
                if "FastAPI" in system or "TypeScript" in system or "MongoDB" in system:
                    # Provavelmente real do projeto
                    real_examples.append(example)
                else:
                    # Sintético genérico
                    synthetic_examples.append(example)
                    
            except json.JSONDecodeError as e:
                print(f"⚠️  Linha {line_num}: JSON inválido - {e}")
                continue
    
    print(f"✅ {len(real_examples)} exemplos reais")
    print(f"✅ {len(synthetic_examples)} exemplos sintéticos")
    
    # Estratégia: Priorizar REAIS (mais valiosos)
    # Pegar 200 reais + 800 sintéticos = 1000 total
    
    # Se tiver menos de 200 reais, complementar com sintéticos
    if len(real_examples) < 200:
        selected_real = real_examples
        needed_synthetic = 1000 - len(real_examples)
        selected_synthetic = synthetic_examples[:needed_synthetic]
    else:
        selected_real = real_examples[:200]
        selected_synthetic = synthetic_examples[:800]
    
    final_dataset = selected_real + selected_synthetic
    
    print(f"\n📊 Dataset reduzido:")
    print(f"   • Exemplos reais: {len(selected_real)}")
    print(f"   • Exemplos sintéticos: {len(selected_synthetic)}")
    print(f"   • TOTAL: {len(final_dataset)}")
    print(f"   • Redução: {50200 / len(final_dataset):.1f}x menor")
    
    # Salvar
    print(f"\n💾 Salvando em: {OUTPUT}")
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for example in final_dataset:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
    
    # Stats
    file_size = OUTPUT.stat().st_size
    print(f"✅ Salvo! Tamanho: {file_size / 1024:.1f} KB")
    print(f"   (Original: 28.12 MB → Reduzido: {file_size / 1024 / 1024:.2f} MB)")
    print(f"   Compressão: {28.12 / (file_size / 1024 / 1024):.1f}x")
    
    return len(final_dataset)

if __name__ == "__main__":
    print("="*80)
    print("🔧 CODE EXPERT - DATASET REDUZIDO (1000 exemplos)")
    print("="*80)
    print()
    
    if not REAL_FILES.exists():
        print(f"❌ Dataset original não encontrado: {REAL_FILES}")
        exit(1)
    
    total = extract_reduced_dataset()
    
    print()
    print("="*80)
    print("✅ DATASET REDUZIDO PRONTO!")
    print("="*80)
    print()
    print("📝 PRÓXIMO PASSO:")
    print()
    print("   Treinar com train_lora.py (MESMO script que funcionou):")
    print()
    print("   cd scripts")
    print(f'   python train_lora.py \\')
    print(f'       --data "../data/code_expert_reduced.jsonl" \\')
    print(f'       --output "../models/lora_code_expert_v1" \\')
    print(f'       --rank 128 \\')
    print(f'       --alpha 256 \\')
    print(f'       --epochs 10 \\')
    print(f'       --batch-size 4 \\')
    print(f'       --gradient-steps 2 \\')
    print(f'       --lr 5e-4')
    print()
    print(f"   Tempo estimado: ~{total // 8 * 5 / 60:.1f} min (~{total // 8} steps × 5s)")
    print()
