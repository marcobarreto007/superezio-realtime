"""
LoRA Training Script - SuperEzio Personality Adapter
Treina adaptador LoRA customizado para personalidade SuperEzio

OTIMIZAÇÕES 2025:
- QLoRA (4-bit) para RTX 3060 12GB
- Rank adaptativo baseado em Qwen2.5
- Target modules otimizados para arquitetura Qwen
- Hyperparâmetros testados e validados
"""
import os
import sys
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import (
    get_peft_model,
    prepare_model_for_kbit_training,
    LoraConfig,
)
from trl import SFTTrainer  # type: ignore
from datasets import load_dataset
from pathlib import Path
import time

print("="*80)
print("🚀 SUPEREZIO LoRA TRAINING v2.0 - OTIMIZADO 2025")
print("="*80)
print(f"⏰ Início: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Configurações
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.resolve()
MODEL_PATH = PROJECT_ROOT / "models" / "qwen2.5-7b-instruct"
DEFAULT_DATASET = PROJECT_ROOT / "data" / "superezio_identity_balanced.jsonl"  # � 21 exemplos PERSONALIDADE
PERSONA_DATASET = PROJECT_ROOT / "data" / "persona_superezio_full.jsonl"  # 🎭 110 exemplos personalidade
CRA_DATASET = PROJECT_ROOT / "data" / "cra_training.jsonl"  # 🇨🇦 172 exemplos contabilidade
LEGACY_DATASET = PROJECT_ROOT / "data" / "persona_superezio.jsonl"

env_dataset = os.getenv("PERSONA_DATA_PATH")
if env_dataset:
    DATA_PATH = Path(env_dataset).expanduser().resolve()
elif DEFAULT_DATASET.exists():
    DATA_PATH = DEFAULT_DATASET
else:
    DATA_PATH = LEGACY_DATASET

OUTPUT_DIR = PROJECT_ROOT / "models" / "lora_personality_v2"  # � RETREINAMENTO ANTI-OVERFIT
LOG_DIR = PROJECT_ROOT / "logs" / "training"

print(f"📁 Modelo base: {MODEL_PATH}")
dataset_source = "env:PERSONA_DATA_PATH" if env_dataset else ("combined" if DATA_PATH == DEFAULT_DATASET else "legacy")
print(f"📄 Dataset: {DATA_PATH} ({dataset_source})")
print(f"💾 Output: {OUTPUT_DIR}")
print(f"📊 Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
if torch.cuda.is_available():
    print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
    print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
print()

# Verificações
if not MODEL_PATH.exists():
    print(f"❌ Modelo não encontrado: {MODEL_PATH}")
    sys.exit(1)

if not DATA_PATH.exists():
    print(f"❌ Dataset não encontrado: {DATA_PATH}")
    sys.exit(1)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Quantização QLoRA (4-bit) - Otimizada para treino eficiente
print("🔧 Configurando QLoRA (4-bit quantization)...")
print("   • Tipo: NF4 (Normal Float 4-bit)")
print("   • Double quantization: Ativado")
print("   • Compute dtype: BFloat16")
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,  # BFloat16 melhor que Float16
    bnb_4bit_use_double_quant=True,
)
print("✅ Configuração QLoRA pronta")
print()

# 3. Carregar modelo com quantização
print("\n📦 Carregando modelo base...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    quantization_config=bnb_config,  # Usar bnb_config definido acima
    device_map={"": 0},  # Forçar tudo na GPU 0
    trust_remote_code=True,
    dtype=torch.bfloat16,  # ✅ CORRIGIDO: dtype ao invés de torch_dtype
    low_cpu_mem_usage=True,
)

tokenizer = AutoTokenizer.from_pretrained(
    str(MODEL_PATH),
    trust_remote_code=True,
    local_files_only=True
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.pad_token_id = tokenizer.eos_token_id

model.config.pad_token_id = tokenizer.pad_token_id
print("✅ Modelo carregado")

# Preparar para treino LoRA
print("🔧 Preparando modelo para treino LoRA...")
model.gradient_checkpointing_enable()  # Economizar VRAM
model = prepare_model_for_kbit_training(model)
print("✅ Modelo preparado para QLoRA")
print()

# Configuração LoRA OTIMIZADA para Qwen2.5-7B
# ANTI-OVERFIT: Mais dropout, menos rank para datasets pequenos
print("⚡ Configurando LoRA adapter...")
print("   📊 Parâmetros otimizados para Qwen2.5:")
print("   • Rank (r): 16 (reduzido para evitar overfit)")
print("   • Alpha: 32 (2×rank)")
print("   • Target modules: Query, Key, Value, Output, MLP")
print("   • Dropout: 0.15 (ALTO para prevenir memorização)")

lora_config = LoraConfig(
    r=16,                          # Rank 16 - menor para datasets pequenos
    lora_alpha=32,                 # Alpha = 2*r (recomendado)
    target_modules=[               # Todos os módulos críticos do Qwen2.5
        "q_proj",                  # Query projection
        "k_proj",                  # Key projection
        "v_proj",                  # Value projection  
        "o_proj",                  # Output projection
        "gate_proj",               # MLP gate
        "up_proj",                 # MLP up
        "down_proj",               # MLP down
    ],
    lora_dropout=0.15,             # Dropout ALTO para prevenir overfit
    bias="none",                   # Sem bias adicional
    task_type="CAUSAL_LM",
    inference_mode=False,
    modules_to_save=None,          # Não salvar outros módulos
)

model = get_peft_model(model, lora_config)

# Mostrar estatísticas de parâmetros
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
total_params = sum(p.numel() for p in model.parameters())
print()
print("📊 Estatísticas do modelo:")
print(f"   Total de parâmetros: {total_params:,}")
print(f"   Parâmetros treináveis: {trainable_params:,}")
print(f"   Porcentagem treinável: {100 * trainable_params / total_params:.2f}%")
print()
model.print_trainable_parameters()

# Carregar dataset
print("📚 Carregando dataset...")
dataset = load_dataset("json", data_files=str(DATA_PATH), split="train")

# Type guard: garantir que é Dataset (não DatasetDict)
from datasets import Dataset
if not isinstance(dataset, Dataset):
    print(f"❌ Erro: Dataset inválido (tipo: {type(dataset)})")
    sys.exit(1)

print(f"✅ {len(dataset)} exemplos carregados")
print()

# Função de formatação para treino
def format_instruction(sample):
    """Formata conversas no formato do modelo"""
    messages = sample["messages"]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False
    )
    return {"text": text}

# Aplicar formatação
dataset = dataset.map(format_instruction)

# Argumentos de treino OTIMIZADOS
print("🎯 Configurando hyperparâmetros de treino...")
print("   🔄 Épocas: 5 (REDUZIDO para evitar overfit)")
print("   📦 Batch size: 1 (ESTÁVEL - evita travamento)")
print("   📈 Learning rate: 2e-4 (padrão QLoRA)")
print("   📉 Scheduler: Cosine com warmup")
print("   💾 Checkpoint: A cada época")

training_args = TrainingArguments(
    output_dir=str(OUTPUT_DIR),
    num_train_epochs=5,                    # 5 épocas (anti-overfit)
    per_device_train_batch_size=1,         # Batch=1 ESTÁVEL
    gradient_accumulation_steps=8,         # Simula batch=8 (1x8)
    learning_rate=2e-4,                    # Learning rate padrão QLoRA
    lr_scheduler_type="cosine",            # Cosine decay (suave)
    warmup_ratio=0.03,                     # 3% warmup
    logging_steps=1,                       # Log cada step
    logging_dir=str(LOG_DIR),
    save_strategy="epoch",                 # Salvar a cada época
    save_total_limit=2,                    # Manter últimos 2 checkpoints
    bf16=torch.cuda.is_bf16_supported(),   # BFloat16 se disponível
    fp16=not torch.cuda.is_bf16_supported(), # Float16 como fallback
    optim="paged_adamw_8bit",              # Otimizador 8-bit (economiza VRAM)
    gradient_checkpointing=True,           # Economiza VRAM
    max_grad_norm=0.3,                     # Gradient clipping (previne explosão)
    weight_decay=0.001,                    # Regularização
    report_to="none",                      # Sem integração wandb/tensorboard
    dataloader_num_workers=0,              # Windows: 0 workers
    remove_unused_columns=True,
    run_name=f"lora_superezio_{time.strftime('%Y%m%d_%H%M%S')}",
)
print("✅ Configuração de treino pronta")
print()

# Trainer com SFT (Supervised Fine-Tuning)
print("🏋️ Criando trainer...")
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    processing_class=tokenizer,
)
print("✅ Trainer configurado")
print()

# TREINAR!
print("="*80)
print("🚀 INICIANDO TREINAMENTO...")
print("="*80)
print(f"⏰ Horário: {time.strftime('%H:%M:%S')}")
print(f"📊 Total de exemplos: {len(dataset)}")
print(f"📦 Steps por época: {len(dataset) // (training_args.per_device_train_batch_size * training_args.gradient_accumulation_steps)}")
print(f"⏱️  Tempo estimado: ~15-30 minutos (RTX 3060)")
print("="*80)
print()

start_time = time.time()

try:
    trainer.train()
    training_time = time.time() - start_time
    
    print()
    print("="*80)
    print("✅ TREINO COMPLETO!")
    print("="*80)
    print(f"⏱️  Tempo total: {training_time/60:.1f} minutos")
    print()
    
except KeyboardInterrupt:
    print("\n⚠️  Treino interrompido pelo usuário")
    print("💾 Salvando progresso atual...")
except Exception as e:
    print(f"\n❌ Erro durante treino: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Salvar adapter final
print("💾 Salvando LoRA adapter...")
model.save_pretrained(str(OUTPUT_DIR))
tokenizer.save_pretrained(str(OUTPUT_DIR))

# Salvar configuração adicional
import json
config_info = {
    "model_base": "Qwen/Qwen2.5-7B-Instruct",
    "lora_rank": lora_config.r,
    "lora_alpha": lora_config.lora_alpha,
    "target_modules": list(lora_config.target_modules) if isinstance(lora_config.target_modules, set) else lora_config.target_modules,  # Converter set para list
    "training_time": f"{(time.time() - start_time)/60:.1f} min",
    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
    "num_epochs": training_args.num_train_epochs,
    "dataset_size": len(dataset),
}

with open(OUTPUT_DIR / "training_info.json", "w", encoding="utf-8") as f:
    json.dump(config_info, f, indent=2, ensure_ascii=False)

print("✅ LoRA adapter salvo com sucesso!")
print()

# Estatísticas finais
adapter_size = sum(f.stat().st_size for f in OUTPUT_DIR.glob("**/*") if f.is_file())
print("="*80)
print("📊 ESTATÍSTICAS FINAIS")
print("="*80)
print(f"📁 Localização: {OUTPUT_DIR}")
print(f"💾 Tamanho do adapter: {adapter_size / (1024**2):.1f} MB")
print(f"⏱️  Tempo total: {(time.time() - start_time)/60:.1f} minutos")
print(f"� Parâmetros treináveis: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")
print()
print("="*80)
print("🎉 SUPEREZIO PERSONALIZADO PRONTO!")
print("="*80)
print()
print("📝 PRÓXIMOS PASSOS:")
print()
print("   1️⃣  Reinicie o backend Python:")
print("      cd backend")
print("      venv\\Scripts\\python.exe api.py")
print()
print("   2️⃣  O adapter será carregado automaticamente")
print("      Você verá: '🚀 ADAPTADOR LoRA ENCONTRADO!'")
print()
print("   3️⃣  Teste a personalidade:")
print("      Pergunte: 'Quem é você?'")
print("      Resposta esperada: Menção a 'SuperEzio'")
print()
print("="*80)
print(f"⏰ Fim: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
