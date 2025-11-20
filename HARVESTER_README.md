# HuggingFace Knowledge Harvester

Sistema de colheita de conhecimento do HuggingFace para alimentar o RAG do SuperEzio.

## 🎯 Objetivo

"Vampirizar" o HuggingFace Hub para baixar modelos, datasets e metadados que alimentarão o sistema RAG de 10TB do SuperEzio.

## 🏗️ Arquitetura

```
backend/
├── hf_client.py       # Cliente HuggingFace (API wrapper)
├── hf_harvester.py    # CLI para colheita de conhecimento
└── .env               # Configuração (token, paths)

data/
├── hf_catalog/        # Catálogos JSON para RAG
├── hf_cache/          # Cache de datasets
└── rag_cache/         # Cache do sistema RAG

models/
└── hf_models/         # Modelos baixados do HF

scripts/
└── hf_harvester.bat   # Launcher Windows
```

## 🔑 Configuração

### 1. Token HuggingFace

Obtenha seu token em: https://huggingface.co/settings/tokens

**Permissões necessárias:** `read`

### 2. Arquivo .env

```bash
# Copie .env.example para .env
cp .env.example .env

# Edite .env e adicione seu token
HF_TOKEN=hf_seu_token_aqui
```

**⚠️ NUNCA commite o arquivo .env no git!**

### 3. Dependências

```bash
pip install huggingface_hub python-dotenv
```

## 🚀 Uso

### Windows (PowerShell/CMD)

```bash
# Modo interativo (menu)
scripts\hf_harvester.bat

# Ou diretamente com Python
cd backend
python hf_harvester.py
```

### Modo Interativo

Menu com opções:
1. 🔍 Buscar Modelos
2. 📊 Buscar Datasets
3. ⬇️ Download Modelo
4. ⬇️ Download Dataset
5. 🌊 Colheita em Batch (Código)
6. 🚪 Sair

### Modo CLI (comandos diretos)

```bash
# Buscar modelos
python hf_harvester.py search-models --query "python code" --tags code,python --limit 50

# Buscar datasets
python hf_harvester.py search-datasets --query "code" --limit 30

# Download modelo específico
python hf_harvester.py download-model --id "Qwen/Qwen2.5-7B-Instruct"

# Download dataset específico
python hf_harvester.py download-dataset --id "bigcode/the-stack"

# Colheita em batch (pré-configurada para código)
python hf_harvester.py batch-harvest
```

## 📦 Funcionalidades

### hf_client.py (Cliente HF)

**Métodos principais:**
- `login()` - Valida token HF
- `search_models()` - Busca modelos (query, tags, limit, sort)
- `search_datasets()` - Busca datasets
- `get_model_info()` - Info detalhada do modelo
- `get_dataset_info()` - Info detalhada do dataset
- `download_model()` - Download completo do modelo
- `download_dataset()` - Download completo do dataset
- `save_catalog()` - Salva catálogo JSON para RAG

**Exemplo de uso:**
```python
from hf_client import HuggingFaceClient

# Criar cliente (token de HF_TOKEN env var)
client = HuggingFaceClient()

# Validar login
if client.login():
    # Buscar modelos de código
    models = client.search_models(
        query="python code",
        tags=["code"],
        limit=50,
        sort="downloads"
    )
    
    # Salvar catálogo
    client.save_catalog("models", models, "code_models.json")
    
    # Download modelo
    client.download_model("Qwen/Qwen2.5-7B-Instruct")
```

### hf_harvester.py (CLI)

**Características:**
- Menu interativo colorido (ANSI)
- Modos: interativo e CLI direto
- Busca com filtros (tags, limit, sort)
- Download com opções (allow/ignore patterns)
- Batch harvest pré-configurado para código
- Salva metadados JSON para RAG

**Batch Harvest:**
Queries pré-configuradas:
- Python code (50 resultados)
- TypeScript (30)
- JavaScript (30)
- Docker (20)
- Machine Learning (30)

Total: ~160 modelos + ~160 datasets

## 📊 Catálogos JSON

Estrutura do catálogo:
```json
{
  "type": "models",
  "created_at": "2025-01-31T10:30:00",
  "count": 50,
  "items": [
    {
      "id": "Qwen/Qwen2.5-7B-Instruct",
      "author": "Qwen",
      "downloads": 1234567,
      "likes": 890,
      "tags": ["text-generation", "pytorch", "code"],
      "pipeline_tag": "text-generation",
      "library_name": "transformers",
      "created_at": "2024-01-01T00:00:00",
      "last_modified": "2024-12-31T00:00:00"
    }
  ]
}
```

**Uso no RAG:**
- IDs para download sob demanda
- Metadados para busca semântica
- Tags para categorização
- Stats (downloads/likes) para ranking

## 🔒 Segurança

### ✅ BOAS PRÁTICAS:
- Token em variável de ambiente (`HF_TOKEN`)
- Arquivo `.env` no `.gitignore`
- `.env.example` sem token real
- Validação de token no login

### ❌ NUNCA FAÇA:
- Hardcode de tokens no código
- Commit de `.env` no git
- Share de tokens em público
- Tokens em logs/prints

## 📁 Estrutura de Dados

### Após Colheita em Batch:

```
data/hf_catalog/
├── batch_code_models.json      # ~160 modelos de código
├── batch_code_datasets.json    # ~160 datasets de código
├── models_catalog_*.json       # Buscas individuais
└── datasets_catalog_*.json

data/hf_cache/
└── <dataset_id>/               # Datasets baixados
    ├── *.parquet
    ├── *.json
    └── hf_metadata.json

models/hf_models/
└── <model_id>/                 # Modelos baixados
    ├── *.safetensors
    ├── config.json
    ├── tokenizer.json
    └── hf_metadata.json
```

## 🎯 Roadmap

### ✅ FASE 1: Infrastructure (COMPLETO)
- [x] Cliente HuggingFace
- [x] CLI Harvester
- [x] Batch harvest
- [x] Catálogos JSON
- [x] Segurança (token via .env)

### ⚠️ FASE 2: RAG Integration (PRÓXIMO)
- [ ] Loader de catálogos JSON
- [ ] Índice vetorial (embeddings)
- [ ] Busca semântica
- [ ] Cache inteligente
- [ ] Download sob demanda

### ⚠️ FASE 3: Optimization
- [ ] Incremental updates
- [ ] Deduplicação
- [ ] Compressão
- [ ] Sharding (10TB)

## 🧛 Vampirização em Ação

```bash
# 1. Configurar token
echo "HF_TOKEN=hf_seu_token_aqui" > backend/.env

# 2. Executar batch harvest
scripts\hf_harvester.bat

# 3. Escolher opção 5 (Colheita em Batch)

# 4. Aguardar colheita (~5-10 min)

# 5. Verificar resultados
dir data\hf_catalog\
# batch_code_models.json     (modelos)
# batch_code_datasets.json   (datasets)
```

## 📝 Notas

- **Performance:** Batch harvest leva ~5-10 minutos (depende de rede)
- **Storage:** Catálogos JSON são leves (~100KB cada)
- **Modelos:** Downloads grandes (GBs), configurar filters quando possível
- **Datasets:** Alguns datasets são ENORMES (100GB+), usar filtros!
- **Rate Limits:** HF tem rate limits, batch harvest respeita limites

## 🐛 Troubleshooting

### Token inválido
```
❌ Erro ao validar token HuggingFace
```
**Solução:** Verificar token em https://huggingface.co/settings/tokens

### Dependências faltando
```
ModuleNotFoundError: No module named 'huggingface_hub'
```
**Solução:** `pip install huggingface_hub python-dotenv`

### .env não encontrado
```
ERRO: Arquivo .env nao encontrado!
```
**Solução:** Copiar `.env.example` para `.env` e adicionar token

### Download muito lento
**Solução:** Usar filtros `allow_patterns` para baixar apenas arquivos necessários

### Disco cheio
**Solução:** Modelos/datasets ocupam MUITO espaço, verificar antes de baixar

## 🤝 Contribuição

Este módulo faz parte do SuperEzio Realtime. Para contribuir:
1. Testar harvester com diferentes queries
2. Adicionar novas queries pré-configuradas em batch_harvest
3. Otimizar filtros para downloads
4. Melhorar catálogos JSON para RAG

---

**Autor:** Marco Barreto  
**Projeto:** SuperEzio Realtime  
**Arquitetura:** 1 LoRA (personalidade) + System Prompts (roles) + RAG (conhecimento 10TB)
