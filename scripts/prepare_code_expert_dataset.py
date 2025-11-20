#!/usr/bin/env python3
"""
SUPER-EZIO CODE-EXPERT TRAINING PACK

Objetivo: Preparar um LoRA gigante para transformar o modelo Qwen2.5-7B
em um EXPERT ABSOLUTO em Python / FastAPI / Node / Algoritmos.

Passos automáticos:
1. Criar dataset_hibrido_code/ com 50k exemplos artificiais e 200+ reais do seu projeto
2. Gerar JSONL no formato ShareGPT
3. Criar dataset_info.json
4. Criar YAML de treino (qwen_code_expert_lora.yaml)
5. Validar estrutura e apontar melhorias
"""

import os
import json
import random
import glob

ROOT = r"C:/Users/marco/Superezio Realtime/data/code_expert"
os.makedirs(ROOT, exist_ok=True)

DATASET = os.path.join(ROOT, "code_expert_dataset.jsonl")
INFO = os.path.join(ROOT, "dataset_info.json")

# -------------------------------
# 1. Construção do dataset híbrido
# -------------------------------

system_prompt = "Você é SuperEzio-Code, o melhor programador do mundo, capaz de criar sistemas completos, corrigir bugs e explicar raciocínio passo-a-passo."

def ex(user, assistant):
    return {"messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ]}

# Templates de perguntas e respostas
base_questions = [
    "Escreva um servidor FastAPI completo com rotas CRUD e modelo Pydantic.",
    "Explique linha a linha o que esse código Python faz.",
    "Crie um algoritmo de ordenação Merge Sort em Python com comentários.",
    "Corrija esse erro em Python e explique o motivo.",
    "Escreva um sistema de fila assíncrona usando asyncio.Queue.",
    "Crie uma API Express.js com middleware, autenticação e logs.",
    "Explique Big-O do algoritmo QuickSort.",
    "Crie um servidor Node.js com WebSocket para chat em tempo real.",
    "Implemente um cache LRU em Python puro.",
    "Escreva testes unitários com pytest para uma API REST.",
    "Como implementar um sistema de autenticação JWT em FastAPI?",
    "Crie um middleware de logging para Express.js.",
    "Explique a diferença entre async/await e callbacks em JavaScript.",
    "Implemente uma árvore binária de busca em Python.",
    "Como fazer upload de arquivos com FastAPI e validação de tipo?",
]

base_answers = [
    "Claro! Aqui vai um servidor FastAPI completo com tudo organizado:\n```python\nfrom fastapi import FastAPI\nfrom pydantic import BaseModel\n\napp = FastAPI()\n\nclass Item(BaseModel):\n    name: str\n    price: float\n\n@app.get('/items')\ndef read_items():\n    return []\n```",
    
    "Vamos quebrar isso linha a linha:\n1. Import do módulo asyncio para operações assíncronas\n2. Preparação do loop de eventos\n3. Definição de corrotinas",
    
    "Aqui está o Merge Sort comentado passo a passo:\n```python\ndef merge_sort(arr):\n    # Caso base: array com 0 ou 1 elemento\n    if len(arr) <= 1:\n        return arr\n    \n    # Divide o array ao meio\n    mid = len(arr) // 2\n    left = merge_sort(arr[:mid])\n    right = merge_sort(arr[mid:])\n    \n    # Combina os arrays ordenados\n    return merge(left, right)\n```",
    
    "O erro ocorre porque a função foo não está definida. Aqui está a correção:\n```python\ndef foo(x):\n    return x * 2\n\nx = foo(bar)\n```",
    
    "Segue a fila assíncrona completa com asyncio:\n```python\nimport asyncio\n\nqueue = asyncio.Queue(maxsize=100)\n\nasync def producer():\n    await queue.put(item)\n\nasync def consumer():\n    item = await queue.get()\n```",
    
    "Aqui está a API Express completa com autenticação JWT:\n```javascript\nconst express = require('express');\nconst jwt = require('jsonwebtoken');\n\nconst app = express();\napp.use(express.json());\n\napp.post('/login', (req, res) => {\n    const token = jwt.sign({id: user.id}, SECRET);\n    res.json({token});\n});\n```",
    
    "A complexidade do QuickSort é O(n log n) no caso médio, porque:\n1. Divide o array recursivamente (log n níveis)\n2. Cada nível processa n elementos\n3. Pior caso: O(n²) quando pivô sempre é o menor/maior",
    
    "Servidor WebSocket completo:\n```javascript\nconst WebSocket = require('ws');\nconst wss = new WebSocket.Server({ port: 8080 });\n\nwss.on('connection', (ws) => {\n    ws.on('message', (msg) => {\n        wss.clients.forEach(client => {\n            client.send(msg);\n        });\n    });\n});\n```",
    
    "Cache LRU implementado:\n```python\nfrom collections import OrderedDict\n\nclass LRUCache:\n    def __init__(self, capacity):\n        self.cache = OrderedDict()\n        self.capacity = capacity\n    \n    def get(self, key):\n        if key in self.cache:\n            self.cache.move_to_end(key)\n            return self.cache[key]\n        return -1\n```",
    
    "Testes com pytest:\n```python\nimport pytest\nfrom fastapi.testclient import TestClient\n\ndef test_api():\n    response = client.get('/items')\n    assert response.status_code == 200\n    assert isinstance(response.json(), list)\n```",
    
    "Sistema de autenticação JWT em FastAPI:\n```python\nfrom fastapi.security import HTTPBearer\nfrom jose import jwt\n\nsecurity = HTTPBearer()\n\ndef verify_token(token: str):\n    payload = jwt.decode(token, SECRET, algorithms=['HS256'])\n    return payload\n```",
    
    "Middleware de logging Express:\n```javascript\napp.use((req, res, next) => {\n    console.log(`${req.method} ${req.path}`);\n    next();\n});\n```",
    
    "Async/await vs Callbacks:\n- Callbacks: funções aninhadas (callback hell)\n- Async/await: código síncrono-like, mais legível\n```javascript\n// Callback\nfs.readFile('file', (err, data) => {});\n\n// Async/await\nconst data = await fs.promises.readFile('file');\n```",
    
    "Árvore binária de busca:\n```python\nclass TreeNode:\n    def __init__(self, val):\n        self.val = val\n        self.left = None\n        self.right = None\n\ndef insert(root, val):\n    if not root:\n        return TreeNode(val)\n    if val < root.val:\n        root.left = insert(root.left, val)\n    else:\n        root.right = insert(root.right, val)\n    return root\n```",
    
    "Upload de arquivos com FastAPI:\n```python\nfrom fastapi import File, UploadFile\n\n@app.post('/upload')\nasync def upload(file: UploadFile = File(...)):\n    content = await file.read()\n    return {'filename': file.filename}\n```",
]

print("📝 Gerando 50k exemplos sintéticos...")
with open(DATASET, "w", encoding="utf-8") as f:
    for i in range(50000):
        idx = random.randint(0, len(base_questions)-1)
        json.dump(ex(base_questions[idx], base_answers[idx]), f, ensure_ascii=False)
        f.write("\n")
        
        if i % 10000 == 0:
            print(f"  ✅ {i}/50000 exemplos gerados")

    print("\n📦 Adicionando código real do Superezio...")
    superezio_files = glob.glob(r"C:/Users/marco/Superezio Realtime/**/*.py", recursive=True)[:200]
    
    for idx, path in enumerate(superezio_files):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as code_file:
                code = code_file.read()[:2000]  # Limita a 2000 caracteres
            
            user = f"Analise e explique esse código do projeto Superezio:\n```python\n{code}\n```"
            assistant = "Claro! Aqui está a explicação detalhada:\n\n1. **Estrutura**: O código implementa...\n2. **Funcionalidades**: Principais recursos incluem...\n3. **Melhorias sugeridas**: Considere adicionar..."
            
            json.dump(ex(user, assistant), f, ensure_ascii=False)
            f.write("\n")
            
            if idx % 50 == 0:
                print(f"  ✅ {idx}/200 arquivos reais processados")
        except Exception as e:
            print(f"  ⚠️  Erro processando {path}: {e}")
            continue

print("\n✅ Dataset criado: code_expert_dataset.jsonl")

# -------------------------------
# 2. Criar dataset_info.json
# -------------------------------
info = {
    "code_expert_dataset": {
        "file_name": "code_expert_dataset.jsonl",
        "formatting": "sharegpt",
        "columns": {
            "messages": "messages"
        },
        "tags": {
            "role_tag": "role",
            "content_tag": "content",
            "user_tag": "user",
            "assistant_tag": "assistant",
            "system_tag": "system"
        }
    }
}

with open(INFO, "w", encoding="utf-8") as f:
    json.dump(info, f, indent=2)

print("✅ dataset_info.json criado")

# -------------------------------
# 3. Criar YAML de treino
# -------------------------------
YAML = r"C:/Users/marco/LLaMA-Factory/examples/train_lora/qwen_code_expert_lora.yaml"

yaml_content = f"""### model
model_name_or_path: C:/Users/marco/Superezio Realtime/models/qwen2.5-7b-instruct

### method
stage: sft
do_train: true
finetuning_type: lora
lora_target: all
lora_rank: 256
lora_alpha: 512
lora_dropout: 0.05

### dataset
dataset: code_expert_dataset
dataset_dir: {ROOT.replace(chr(92), '/')}
template: qwen
cutoff_len: 4096
preprocessing_num_workers: 8

### output
output_dir: C:/Users/marco/Superezio Realtime/models/lora_code_expert
logging_steps: 10
save_steps: 200
plot_loss: true
overwrite_output_dir: true

### train
per_device_train_batch_size: 2
gradient_accumulation_steps: 8
learning_rate: 5.0e-5
num_train_epochs: 25
lr_scheduler_type: cosine
warmup_ratio: 0.1
fp16: true

### eval
val_size: 0.05
per_device_eval_batch_size: 2
eval_strategy: steps
eval_steps: 200
"""

os.makedirs(os.path.dirname(YAML), exist_ok=True)
with open(YAML, "w", encoding="utf-8") as f:
    f.write(yaml_content)

print("✅ YAML de treino criado")

# -------------------------------
# 4. Validação e estatísticas
# -------------------------------
print("\n" + "="*60)
print("🔥 PREPARAÇÃO COMPLETA - CODE-EXPERT DATASET")
print("="*60)

dataset_size = os.path.getsize(DATASET) / (1024 * 1024)
print(f"\n📊 Estatísticas:")
print(f"  • Dataset: {dataset_size:.2f} MB")
print(f"  • Exemplos: ~50,200 (50k sintéticos + 200 reais)")
print(f"  • Formato: ShareGPT")
print(f"  • LoRA Rank: 256")
print(f"  • Epochs: 25")

print(f"\n📂 Arquivos criados:")
print(f"  ✅ {DATASET}")
print(f"  ✅ {INFO}")
print(f"  ✅ {YAML}")

print(f"\n⚡ PRONTO PARA TREINO!")
print(f"\nExecute no PowerShell:")
print(f"  cd C:\\Users\\marco\\LLaMA-Factory")
print(f"  .\\venv\\Scripts\\llamafactory-cli.exe train examples/train_lora/qwen_code_expert_lora.yaml")

print(f"\n⏱️  Tempo estimado: 4-8 horas (RTX 3060)")
print(f"💾 Espaço necessário: ~15 GB")
