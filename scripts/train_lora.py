"""
LoRA Training Script - SuperEzio Mega Unified Adapter
Treina adaptador LoRA unificado com personalidade + contabilidade + ferramentas

OTIMIZAÇÕES 2025:
- QLoRA (4-bit) para RTX 3060 12GB
- Rank configurável via CLI (recomendado: 128 para mega dataset)
- Target modules otimizados para arquitetura Qwen
- Hyperparâmetros configuráveis via argumentos CLI
"""
import os
import sys
import torch
import argparse
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

# Parse CLI arguments
parser = argparse.ArgumentParser(description="Train SuperEzio LoRA adapter")
parser.add_argument("--data", type=str, help="Path to training dataset (JSONL)")
parser.add_argument("--output", type=str, help="Output directory for LoRA adapter")
parser.add_argument("--rank", type=int, default=16, help="LoRA rank (default: 16)")
parser.add_argument("--alpha", type=int, help="LoRA alpha (default: 2*rank)")
parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs (default: 5)")
parser.add_argument("--batch-size", type=int, default=1, help="Per-device batch size (default: 1)")
parser.add_argument("--gradient-steps", type=int, default=8, help="Gradient accumulation steps (default: 8)")
parser.add_argument("--dropout", type=float, default=0.15, help="LoRA dropout (default: 0.15)")
parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate (default: 2e-4)")
args = parser.parse_args()

print("="*80)
print("🚀 SUPEREZIO LoRA TRAINING v3.0 - MEGA UNIFIED 2025")
print("="*80)
print(f"⏰ Início: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Configurações
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.resolve()
MODEL_PATH = PROJECT_ROOT / "models" / "qwen2.5-7b-instruct"

# Default paths (usados se não fornecer via CLI)
DEFAULT_DATASET = PROJECT_ROOT / "data" / "superezio_identity_balanced.jsonl"
PERSONA_DATASET = PROJECT_ROOT / "data" / "persona_superezio_full.jsonl"
CRA_DATASET = PROJECT_ROOT / "data" / "cra_training.jsonl"
LEGACY_DATASET = PROJECT_ROOT / "data" / "persona_superezio.jsonl"

# Usar argumentos CLI se fornecidos, senão fallback
if args.data:
    DATA_PATH = Path(args.data).resolve()
else:
    env_dataset = os.getenv("PERSONA_DATA_PATH")
    if env_dataset:
        DATA_PATH = Path(env_dataset).expanduser().resolve()
    elif DEFAULT_DATASET.exists():
        DATA_PATH = DEFAULT_DATASET
    else:
        DATA_PATH = LEGACY_DATASET

if args.output:
    OUTPUT_DIR = Path(args.output).resolve()
else:
    OUTPUT_DIR = PROJECT_ROOT / "models" / "lora_personality_v2"

LOG_DIR = PROJECT_ROOT / "logs" / "training"

# Calcular alpha automaticamente se não fornecido
LORA_RANK = args.rank
LORA_ALPHA = args.alpha if args.alpha else (LORA_RANK * 2)
LORA_DROPOUT = args.dropout
NUM_EPOCHS = args.epochs
BATCH_SIZE = args.batch_size
GRADIENT_STEPS = args.gradient_steps
LEARNING_RATE = args.lr

print(f"📁 Modelo base: {MODEL_PATH}")
print(f"📄 Dataset: {DATA_PATH}")
print(f"💾 Output: {OUTPUT_DIR}")
print(f"📊 Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
if torch.cuda.is_available():
    print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
    print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
print()
print("⚙️  Hyperparâmetros:")
print(f"   • LoRA Rank: {LORA_RANK}")
print(f"   • LoRA Alpha: {LORA_ALPHA}")
print(f"   • LoRA Dropout: {LORA_DROPOUT}")
print(f"   • Épocas: {NUM_EPOCHS}")
print(f"   • Batch Size: {BATCH_SIZE}")
print(f"   • Gradient Accumulation: {GRADIENT_STEPS} (effective batch: {BATCH_SIZE * GRADIENT_STEPS})")
print(f"   • Learning Rate: {LEARNING_RATE}")
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
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)
print("✅ Configuração QLoRA pronta")
print()

# Carregar modelo com quantização
print("\n📦 Carregando modelo base...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    quantization_config=bnb_config,
    device_map={"": 0},
    trust_remote_code=True,
    dtype=torch.bfloat16,
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
model.gradient_checkpointing_enable()
model = prepare_model_for_kbit_training(model)
print("✅ Modelo preparado para QLoRA")
print()

# Configuração LoRA com parâmetros CLI
print("⚡ Configurando LoRA adapter...")
print(f"   📊 Rank: {LORA_RANK} (Alpha: {LORA_ALPHA}, Dropout: {LORA_DROPOUT})")
print("   🎯 Target modules: Query, Key, Value, Output, MLP")

lora_config = LoraConfig(
    r=LORA_RANK,
    lora_alpha=LORA_ALPHA,
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type="CAUSAL_LM",
    inference_mode=False,
    modules_to_save=None,
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

# Type guard
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

# Argumentos de treino com valores CLI
print("🎯 Configurando training arguments...")
training_args = TrainingArguments(
    output_dir=str(OUTPUT_DIR),
    num_train_epochs=NUM_EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRADIENT_STEPS,
    learning_rate=LEARNING_RATE,
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,
    logging_steps=1,
    logging_dir=str(LOG_DIR),
    save_strategy="no",
    save_total_limit=1,
    bf16=torch.cuda.is_bf16_supported(),
    fp16=not torch.cuda.is_bf16_supported(),
    optim="paged_adamw_8bit",
    gradient_checkpointing=True,
    max_grad_norm=0.3,
    weight_decay=0.001,
    report_to="none",
    dataloader_num_workers=0,
    remove_unused_columns=True,
    run_name=f"lora_superezio_{time.strftime('%Y%m%d_%H%M%S')}",
)
print("✅ Configuração de treino pronta")
print()

# Trainer com SFT
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
total_steps = len(dataset) // (BATCH_SIZE * GRADIENT_STEPS)
estimated_time_per_step = 5  # segundos por step (estimativa conservadora)
estimated_total_minutes = (total_steps * NUM_EPOCHS * estimated_time_per_step) / 60
print(f"📦 Steps por época: {total_steps}")
print(f"📦 Steps totais: {total_steps * NUM_EPOCHS}")
print(f"⏱️  Tempo estimado: ~{estimated_total_minutes:.1f} minutos ({estimated_total_minutes/60:.1f} horas)")
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
    print(f"⏱️  Tempo total: {training_time/60:.1f} minutos ({training_time/3600:.2f} horas)")
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
    "target_modules": list(lora_config.target_modules) if isinstance(lora_config.target_modules, set) else lora_config.target_modules,
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
print(f"⏱️  Tempo total: {(time.time() - start_time)/60:.1f} minutos ({(time.time() - start_time)/3600:.2f} horas)")
print(f"🔢 Parâmetros treináveis: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")
print()
print("="*80)
print("🎉 SUPEREZIO MEGA LoRA PRONTO!")
print("="*80)
print()
print("📝 PRÓXIMOS PASSOS:")
print()
print("   1️⃣  Atualizar backend/inference.py para usar novo LoRA:")
print(f"      LORA_MEGA_DIR = PROJECT_ROOT / 'models' / '{OUTPUT_DIR.name}'")
print()
print("   2️⃣  Remover SYSTEM_PROMPT do inference.py")
print("      (Todo prompt agora está no LoRA!)")
print()
print("   3️⃣  Reinicie o backend Python:")
print("      cd backend")
print("      python api.py")
print()
print("="*80)
print(f"⏰ Fim: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
