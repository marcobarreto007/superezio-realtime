#!/usr/bin/env python3
"""
TREINO DIRETO CODE-EXPERT - GPU FORÇADA
Sem LLaMA-Factory, usando PEFT + transformers puro
"""

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset
import os

print("🔥 TREINO CODE-EXPERT GPU")
print("=" * 60)

# Forçar CUDA
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"🖥️  Device: {device}")
print(f"📊 CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"💻 GPU: {torch.cuda.get_device_name(0)}")
    print(f"🎯 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

# Configurações
MODEL_PATH = r"C:/Users/marco/Superezio Realtime/models/qwen2.5-7b-instruct"
DATASET_FILE = r"C:/Users/marco/Superezio Realtime/data/code_expert/code_expert_dataset.jsonl"
OUTPUT_DIR = r"C:/Users/marco/Superezio Realtime/models/lora_code_expert"

print(f"\n📦 Carregando modelo {MODEL_PATH}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

# Carregar modelo DIRETO na GPU
print(f"🚀 Carregando modelo na GPU...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    device_map="cuda:0",  # FORÇAR GPU
    trust_remote_code=True
)

print(f"✅ Modelo carregado em: {model.device}")

# Configuração LoRA
print(f"\n🎯 Configurando LoRA Rank 256...")
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=256,
    lora_alpha=512,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    bias="none"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Carregar dataset
print(f"\n📊 Carregando dataset {DATASET_FILE}")
dataset = load_dataset("json", data_files=DATASET_FILE, split="train")
print(f"✅ {len(dataset)} exemplos carregados")

# Tokenizar dataset
def tokenize_function(examples):
    # Formato ShareGPT: extrair mensagens e formatar
    texts = []
    for messages in examples["messages"]:
        # Construir texto completo
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )
        texts.append(text)
    
    return tokenizer(
        texts,
        truncation=True,
        max_length=4096,
        padding=False
    )

print(f"\n🔄 Tokenizando dataset...")
tokenized_dataset = dataset.map(
    tokenize_function,
    batched=True,
    remove_columns=dataset.column_names,
    desc="Tokenizing"
)

# Split train/eval
train_test_split = tokenized_dataset.train_test_split(test_size=0.05)
train_dataset = train_test_split["train"]
eval_dataset = train_test_split["test"]

print(f"✅ Train: {len(train_dataset)} | Eval: {len(eval_dataset)}")

# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# Training arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=25,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=5e-5,
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,
    logging_steps=10,
    save_steps=200,
    eval_steps=200,
    evaluation_strategy="steps",
    save_total_limit=3,
    fp16=True,
    gradient_checkpointing=True,
    optim="adamw_torch",
    report_to="none",
    remove_unused_columns=False,
)

# Trainer
print(f"\n🎯 Iniciando treino...")
print(f"   • Epochs: 25")
print(f"   • Batch size: 2")
print(f"   • Gradient accumulation: 8")
print(f"   • Effective batch: 16")
print(f"   • Learning rate: 5e-5")
print(f"   • LoRA Rank: 256")

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=data_collator,
)

# TREINAR
print(f"\n🔥 INICIANDO TREINO NA GPU!")
print("=" * 60)
trainer.train()

# Salvar modelo final
print(f"\n💾 Salvando modelo final em {OUTPUT_DIR}")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"\n✅ TREINO COMPLETO!")
print(f"📂 Modelo salvo em: {OUTPUT_DIR}")
