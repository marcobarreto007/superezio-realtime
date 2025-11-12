"""Teste rápido do modelo - sem todo o overhead"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from pathlib import Path

MODEL_DIR = Path(__file__).parent.parent / "models" / "qwen2.5-7b-instruct"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR), local_files_only=True)

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    str(MODEL_DIR),
    torch_dtype=torch.float16,
    device_map="auto",
    local_files_only=True
)

print("Testing generation...")
messages = [
    {"role": "system", "content": "Você é SuperEzio, um assistente direto."},
    {"role": "user", "content": "Oi"}
]

text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer([text], return_tensors="pt").to(model.device)

print("Generating...")
import time
start = time.time()

outputs = model.generate(
    **inputs,
    max_new_tokens=50,
    temperature=0.7,
    do_sample=True,
    pad_token_id=tokenizer.eos_token_id
)

elapsed = time.time() - start
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"\n✅ Generated in {elapsed:.2f}s:")
print(response)
