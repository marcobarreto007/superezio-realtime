"""
Teste Simples - Verificar LoRA sem importar inference completo
"""
import os
import sys
from pathlib import Path
import torch

# Configuração
BACKEND_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = BACKEND_DIR.parent.resolve()
LOCAL_MODEL_DIR = PROJECT_ROOT / "models" / "qwen2.5-7b-instruct"
LORA_ADAPTER_DIR = PROJECT_ROOT / "models" / "lora_superezio"

print("="*60)
print("🧪 TESTE SIMPLES - VERIFICAÇÃO LoRA")
print("="*60)

# Teste 1: Verificar diretórios
print("\n📁 TESTE 1: VERIFICAR DIRETÓRIOS")
print("-"*60)

model_exists = LOCAL_MODEL_DIR.exists()
lora_exists = LORA_ADAPTER_DIR.exists()

print(f"Modelo base: {LOCAL_MODEL_DIR}")
print(f"  Status: {'✅ EXISTE' if model_exists else '❌ NÃO ENCONTRADO'}")

print(f"\nAdaptador LoRA: {LORA_ADAPTER_DIR}")
print(f"  Status: {'✅ EXISTE' if lora_exists else '❌ NÃO ENCONTRADO'}")

if lora_exists:
    lora_files = list(LORA_ADAPTER_DIR.glob("*"))
    print(f"\n  📄 Arquivos no diretório LoRA ({len(lora_files)}):")
    for f in sorted(lora_files)[:10]:
        size = f.stat().st_size if f.is_file() else 0
        size_mb = size / (1024*1024)
        print(f"     - {f.name} ({size_mb:.2f} MB)")
    
    # Verificar arquivos importantes
    adapter_config = LORA_ADAPTER_DIR / "adapter_config.json"
    adapter_model = LORA_ADAPTER_DIR / "adapter_model.safetensors"
    
    print(f"\n  🔍 Arquivos críticos:")
    print(f"     adapter_config.json: {'✅' if adapter_config.exists() else '❌'}")
    print(f"     adapter_model.safetensors: {'✅' if adapter_model.exists() else '❌'}")

# Teste 2: Carregar e verificar modelo
if model_exists:
    print("\n\n🤖 TESTE 2: CARREGAR MODELO")
    print("-"*60)
    
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft.peft_model import PeftModel
        
        print("✅ Imports bem-sucedidos")
        
        # Configuração de quantização
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        
        print("\n⏳ Carregando modelo base (4-bit)...")
        base_model = AutoModelForCausalLM.from_pretrained(
            str(LOCAL_MODEL_DIR),
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            local_files_only=True,
        )
        print("✅ Modelo base carregado")
        
        # Verificar tipo
        print(f"\n   Tipo: {type(base_model).__name__}")
        print(f"   Módulo: {type(base_model).__module__}")
        
        # Tentar carregar LoRA
        if lora_exists:
            print("\n⏳ Carregando adaptador LoRA...")
            try:
                model = PeftModel.from_pretrained(
                    base_model, 
                    str(LORA_ADAPTER_DIR),
                    is_trainable=False
                )
                print("✅ Adaptador LoRA carregado!")
                
                print(f"\n   Tipo após LoRA: {type(model).__name__}")
                print(f"   Módulo: {type(model).__module__}")
                
                # Verificar se é PeftModel
                is_peft = "PeftModel" in type(model).__name__
                print(f"\n   {'✅' if is_peft else '❌'} É PeftModel: {is_peft}")
                
                # Verificar configuração PEFT
                if hasattr(model, 'peft_config'):
                    print(f"   ✅ Tem peft_config")
                    print(f"   Adaptadores: {list(model.peft_config.keys())}")
                
                if hasattr(model, 'active_adapter'):
                    print(f"   ✅ Adaptador ativo: {model.active_adapter}")
                
                # Contar parâmetros
                total_params = sum(p.numel() for p in model.parameters())
                trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
                
                print(f"\n   📊 Parâmetros:")
                print(f"      Total: {total_params:,}")
                print(f"      Treináveis: {trainable_params:,}")
                print(f"      Proporção: {trainable_params/total_params*100:.4f}%")
                
                # Procurar módulos LoRA
                lora_modules = []
                for name, module in model.named_modules():
                    if 'lora' in name.lower():
                        lora_modules.append(name)
                
                if lora_modules:
                    print(f"\n   ✅ Módulos LoRA encontrados: {len(lora_modules)}")
                    print(f"      Exemplos:")
                    for name in lora_modules[:3]:
                        print(f"      - {name}")
                else:
                    print(f"\n   ⚠️  Nenhum módulo 'lora' encontrado nos nomes")
                
                # TESTE DE INFERÊNCIA
                print("\n\n💬 TESTE 3: INFERÊNCIA COM LoRA")
                print("-"*60)
                
                tokenizer = AutoTokenizer.from_pretrained(
                    str(LOCAL_MODEL_DIR),
                    trust_remote_code=True,
                    local_files_only=True,
                )
                tokenizer.pad_token = tokenizer.eos_token
                
                # Prompt de teste
                test_prompt = "Quem é você?"
                
                print(f"Pergunta: {test_prompt}")
                print("\n⏳ Gerando resposta...")
                
                inputs = tokenizer(test_prompt, return_tensors="pt").to(model.device)
                
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=100,
                    temperature=0.1,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                )
                
                response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                response_only = response[len(test_prompt):].strip()
                
                print(f"\n💬 Resposta:\n{response_only}")
                
                # Verificar se menciona SuperEzio
                has_superezio = 'superezio' in response_only.lower()
                print(f"\n{'✅' if has_superezio else '⚠️'} Menciona 'SuperEzio': {has_superezio}")
                
            except Exception as e:
                print(f"❌ Erro ao carregar LoRA: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("\n⚠️  Adaptador LoRA não encontrado - usando apenas modelo base")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()

# Resumo
print("\n\n" + "="*60)
print("📋 RESUMO")
print("="*60)
print(f"\n1. Modelo base existe: {'✅' if model_exists else '❌'}")
print(f"2. Adaptador LoRA existe: {'✅' if lora_exists else '❌'}")

if model_exists and lora_exists:
    print("\n✅ Ambos estão presentes - execute o servidor para testar!")
elif not lora_exists:
    print("\n⚠️  Adaptador LoRA não encontrado")
    print("   Execute: python scripts/train_lora.py")
else:
    print("\n⚠️  Revise os erros acima")

print("\n" + "="*60)
