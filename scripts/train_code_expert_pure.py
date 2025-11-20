#!/usr/bin/env python3
"""
TREINO DIRETO CODE-EXPERT - PYTORCH PURO COM CUDA FORÇADA
"""

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType
from torch.utils.data import DataLoader, Dataset
import json
from tqdm import tqdm
import os

print("🔥 TREINO CODE-EXPERT - PYTORCH PURO")
print("=" * 60)

# Verificar CUDA
if not torch.cuda.is_available():
    print("❌ CUDA não disponível!")
    exit(1)

device = torch.device("cuda:0")
print(f"✅ Device: {device}")
print(f"💻 GPU: {torch.cuda.get_device_name(0)}")
print(f"🎯 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB\n")

# Configurações
MODEL_PATH = r"C:/Users/marco/Superezio Realtime/models/qwen2.5-7b-instruct"
DATASET_FILE = r"C:/Users/marco/Superezio Realtime/data/code_expert/code_expert_dataset.jsonl"
OUTPUT_DIR = r"C:/Users/marco/Superezio Realtime/models/lora_code_expert"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Hiperparâmetros (ULTRA-OTIMIZADO PARA RTX 3060 12GB)
EPOCHS = 5  # Reduzido ainda mais
BATCH_SIZE = 1
GRAD_ACCUM = 32  # Aumentado para compensar
LR = 5e-5
MAX_LENGTH = 1024  # Reduzido para 1024
LORA_RANK = 64  # Reduzido para 64

print(f"📦 Carregando modelo...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True,
    load_in_8bit=True,  # Quantização 8-bit para economizar VRAM
)

print(f"✅ Modelo carregado em 8-bit: {next(model.parameters()).device}\n")

# Habilitar gradient checkpointing ANTES do LoRA
model.gradient_checkpointing_enable()

# LoRA Config (OTIMIZADO PARA 12GB VRAM)
print(f"🎯 Aplicando LoRA Rank {LORA_RANK}...")
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=LORA_RANK,
    lora_alpha=LORA_RANK * 2,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    bias="none"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Preparar modelo para treinamento com 8-bit
from peft import prepare_model_for_kbit_training
model = prepare_model_for_kbit_training(model)

# Dataset
class CodeExpertDataset(Dataset):
    def __init__(self, file_path, tokenizer, max_length):
        self.data = []
        print(f"\n📊 Carregando dataset...")
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                self.data.append(json.loads(line))
        print(f"✅ {len(self.data)} exemplos carregados")
        
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        messages = item["messages"]
        
        # Formatar chat
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )
        
        # Tokenizar
        encoded = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        input_ids = encoded["input_ids"].squeeze()
        attention_mask = encoded["attention_mask"].squeeze()
        
        # Labels = input_ids (causal LM)
        labels = input_ids.clone()
        labels[labels == self.tokenizer.pad_token_id] = -100
        
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels
        }

dataset = CodeExpertDataset(DATASET_FILE, tokenizer, MAX_LENGTH)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

# Optimizer
optimizer = torch.optim.AdamW(model.parameters(), lr=LR)

# Treino
print(f"\n🔥 INICIANDO TREINO")
print(f"   • Epochs: {EPOCHS}")
print(f"   • Batch size: {BATCH_SIZE}")
print(f"   • Gradient accumulation: {GRAD_ACCUM}")
print(f"   • Effective batch: {BATCH_SIZE * GRAD_ACCUM}")
print(f"   • Learning rate: {LR}")
print(f"   • Total steps: {len(dataloader) * EPOCHS // GRAD_ACCUM}")
print("=" * 60 + "\n")

model.train()
global_step = 0

for epoch in range(EPOCHS):
    epoch_loss = 0
    optimizer.zero_grad()
    
    pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{EPOCHS}")
    
    for step, batch in enumerate(pbar):
        # Mover para GPU
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        
        # Forward
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )
        
        loss = outputs.loss / GRAD_ACCUM
        epoch_loss += loss.item()
        
        # Backward
        loss.backward()
        
        # Gradient accumulation
        if (step + 1) % GRAD_ACCUM == 0:
            optimizer.step()
            optimizer.zero_grad()
            global_step += 1
            
            pbar.set_postfix({
                "loss": f"{loss.item() * GRAD_ACCUM:.4f}",
                "step": global_step
            })
        
        # Salvar checkpoint
        if global_step > 0 and global_step % 200 == 0:
            checkpoint_dir = f"{OUTPUT_DIR}/checkpoint-{global_step}"
            print(f"\n💾 Salvando checkpoint {global_step}...")
            model.save_pretrained(checkpoint_dir)
            tokenizer.save_pretrained(checkpoint_dir)
    
    avg_loss = epoch_loss / len(dataloader)
    print(f"\n📊 Epoch {epoch+1} | Loss: {avg_loss:.4f}")

# Salvar modelo final
print(f"\n💾 Salvando modelo final...")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"\n✅ TREINO COMPLETO!")
print(f"📂 Modelo salvo em: {OUTPUT_DIR}")
