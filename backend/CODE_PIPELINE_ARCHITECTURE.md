# Code Pipeline - Arquitetura de 3 Modelos

## Visão Geral

O **Code Pipeline** é uma arquitetura sofisticada de 3 estágios que orquestra múltiplos modelos para gerar código de alta qualidade.

### Conceito

```
User Query → ROUTER → Code Expert? 
                           ↓
                    ┌──────────────┐
                    │  PLANNER     │ (Qwen local + RAG + SuperEzio)
                    │  Stage 1     │
                    └──────┬───────┘
                           ↓ (plan.json)
                    ┌──────────────┐
                    │  CODER       │ (DeepSeek-Coder ou Qwen)
                    │  Stage 2     │
                    └──────┬───────┘
                           ↓ (code.json)
                    ┌──────────────┐
                    │  REVIEWER    │ (LLaMA 3 ou Qwen)
                    │  Stage 3     │
                    └──────┬───────┘
                           ↓ (final_answer.md)
                    📝 User Response
```

---

## Arquitetura Detalhada

### Stage 1: PLANNER (Qwen2.5-7B Local)

**Responsabilidades:**
- Entender pedido do usuário em profundidade
- Analisar contexto RAG disponível
- Identificar constraints (Windows, Python 3.11, etc.)
- Gerar plano estruturado em JSON
- Sugerir API design se aplicável

**Modelo:** Qwen2.5-7B-Instruct (local, 4-bit)  
**Persona:** SuperEzio-Code Planner  
**Temperature:** 0.3 (determinístico)  
**Max Tokens:** 1024

**Saída JSON:**
```json
{
  "stage": "planner",
  "expert": "code_python",
  "goal": "Criar API REST para gerenciar usuários",
  "context_used": ["FastAPI patterns", "SQLAlchemy ORM"],
  "constraints": ["Windows PowerShell", "Python 3.11", "FastAPI"],
  "api_design": {
    "endpoints": ["/users", "/users/{id}"],
    "classes": ["User", "UserService"],
    "functions": ["create_user", "get_user"]
  },
  "reasoning": "FastAPI é ideal para APIs REST modernas"
}
```

---

### Stage 2: CODER (DeepSeek-Coder ou Fallback)

**Responsabilidades:**
- Receber plano do Stage 1
- Gerar código completo e funcional
- Criar arquivos necessários
- Sugerir comandos para executar
- Considerar edge cases e error handling

**Modelo Preferido:** DeepSeek-Coder-6.7B-Instruct (HF Inference API)  
**Fallback:** Qwen2.5-7B local  
**Persona:** DeepSeek-Code Executor  
**Temperature:** 0.2 (baixa para código)  
**Max Tokens:** 2048

**Saída JSON:**
```json
{
  "stage": "coder",
  "expert": "code_python",
  "files_to_create": [
    {
      "path": "backend/service.py",
      "language": "python",
      "content": "from fastapi import FastAPI\n..."
    }
  ],
  "files_to_update": [],
  "cmd_instructions": [
    "pip install fastapi uvicorn",
    "python backend/service.py"
  ],
  "notes": "Código usa type hints e async/await"
}
```

---

### Stage 3: REVIEWER (LLaMA 3 ou Fallback)

**Responsabilidades:**
- Revisar código do Stage 2
- Identificar bugs, vulnerabilidades, problemas
- Verificar se atende plano original
- Sugerir patches se necessário
- Gerar resposta final em Markdown

**Modelo Preferido:** LLaMA-3-8B-Instruct (HF Inference API)  
**Fallback:** Qwen2.5-7B local  
**Persona:** LLaMA-3 Reviewer  
**Temperature:** 0.4 (criativo para explicações)  
**Max Tokens:** 2048

**Saída JSON:**
```json
{
  "stage": "review",
  "expert": "code_python",
  "status": "ok",
  "issues": [],
  "suggested_patches": [],
  "final_answer_markdown": "# API REST com FastAPI\n\n..."
}
```

---

## Experts de Código

Todos os seguintes experts usam o pipeline automaticamente:

1. **code_python** - Python, FastAPI, Django, pandas, PyTorch
2. **code_ts** - TypeScript, React, Next.js, Node.js
3. **code_js** - JavaScript puro
4. **code_infra** - Docker, Kubernetes, CI/CD
5. **code_ml** - Machine Learning, LoRA, transformers
6. **code_database** - SQL, PostgreSQL, MongoDB
7. **code_frontend** - React, Vue, CSS, Tailwind
8. **code_api** - REST APIs, GraphQL, OpenAPI
9. **code_testing** - pytest, Jest, TDD
10. **code_algorithms** - Data structures, complexidade
11. **code_hf_curator** - HuggingFace models e datasets
12. **code_general** - Programação geral

---

## Integração com Sistema Existente

### Fluxo Completo

```python
# 1. User faz request para /api/chat
POST /api/chat
{
  "messages": [{"role": "user", "content": "Crie uma API REST Python"}],
  "model": "Qwen2.5-7B-Instruct"
}

# 2. api.py → inference.py → chat_completion()

# 3. MoE Router decide expert
router.route(messages) → "code_python"

# 4. Detecta code expert
is_code_expert("code_python") → True

# 5. Executa pipeline
run_code_pipeline(messages, "code_python", rag_context)

# 6. Pipeline retorna resultado final
{
  "content": "# API REST com FastAPI\n\n...",
  "expert": "code_python",
  "pipeline_stages": {...},
  "pipeline_duration_ms": 8500
}

# 7. api.py retorna para cliente
{
  "id": "chatcmpl-...",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "# API REST com FastAPI\n\n..."
    }
  }]
}
```

### Código de Integração (inference.py)

```python
from code_pipeline import run_code_pipeline, is_code_expert

def chat_completion(messages, tools, temperature, max_tokens, stream, mode):
    # ... existing MoE routing ...
    
    # CODE PIPELINE CHECK
    if is_code_expert(decision.expert_id):
        print(f"🚀 [MOE] Code expert detected → Using 3-stage pipeline")
        pipeline_result = run_code_pipeline(
            messages=messages,
            expert_id=decision.expert_id,
            rag_context=rag_system_message
        )
        
        return {
            "content": pipeline_result["content"],
            "expert": pipeline_result["expert"],
            "pipeline_stages": pipeline_result.get("pipeline_stages", {}),
            "pipeline_duration_ms": pipeline_result.get("pipeline_duration_ms", 0),
            "lora_adapter": decision.lora_adapter,
            "rag_domains": decision.rag_domains
        }
    
    # ... continue with standard flow for non-code experts ...
```

---

## Vantagens do Pipeline

### 1. Especialização de Tarefas
- **Planner:** Foco em arquitetura e design
- **Coder:** Foco em implementação
- **Reviewer:** Foco em qualidade e correção

### 2. Qualidade do Código
- Revisão automática em 3 camadas
- Detecção de bugs antes de entregar ao usuário
- Sugestão de melhorias e patches

### 3. Context Awareness
- RAG integration no Stage 1
- Plano guia o Coder no Stage 2
- Reviewer valida contra plano original

### 4. Flexibilidade
- Fallback para Qwen local se APIs externas falham
- Pode usar modelos diferentes por stage
- Logs detalhados para debug

### 5. Escalabilidade
- Fácil adicionar novos experts
- Pode substituir modelos por stage
- Pipeline isolado do resto do sistema

---

## Configuração

### Variáveis de Ambiente

```bash
# HuggingFace Inference API (para Stage 2 e 3)
export HF_TOKEN="hf_..."

# OpenRouter API (alternativa)
export OPENROUTER_API_KEY="sk-or-..."
```

### Fallback Automático

Se as APIs não estiverem configuradas, o sistema usa **Qwen local** para todos os 3 estágios:

```
Stage 1: Qwen local (sempre)
Stage 2: DeepSeek API → Qwen local (fallback)
Stage 3: LLaMA 3 API → Qwen local (fallback)
```

---

## Performance

### Timing Esperado

```
Stage 1 (Planner):  1-3 segundos
Stage 2 (Coder):    3-6 segundos
Stage 3 (Reviewer): 2-4 segundos
Total:              6-13 segundos
```

### Otimizações Futuras

1. **Cache de Planos:** Planos similares podem ser reutilizados
2. **Paralelização:** Stage 2 e 3 podem rodar em paralelo para review parcial
3. **Streaming:** Retornar Stage 2 enquanto Stage 3 processa
4. **Batch Processing:** Processar múltiplos arquivos em paralelo

---

## Testes

### Executar Test Suite

```powershell
cd backend
python test_code_pipeline.py
```

### Testes Incluídos

1. ✅ **Expert Detection:** Valida is_code_expert()
2. ✅ **Python Pipeline:** Testa code_python end-to-end
3. ✅ **TypeScript Pipeline:** Testa code_ts
4. ✅ **Infrastructure Pipeline:** Testa code_infra
5. ✅ **RAG Context:** Testa pipeline com RAG injection

---

## Debug

### Logs Detalhados

O pipeline gera logs estruturados:

```
================================================================================
[PIPELINE][PLANNER] Stage 1: Planning
  Expert: code_python
  RAG Context: Yes
================================================================================

✅ [PLANNER] Plan generated in 1850ms
   Goal: Criar API REST para gerenciar usuários
   Constraints: 3

================================================================================
[PIPELINE][CODER] Stage 2: Code Generation
  Expert: code_python
  Plan: Criar API REST para gerenciar usuários...
================================================================================

✅ [CODER] Code generated in 4200ms
   Files: 2, Commands: 3

================================================================================
[PIPELINE][REVIEWER] Stage 3: Code Review
  Expert: code_python
================================================================================

✅ [REVIEWER] Review completed in 3100ms
   Status: ok, Issues: 0

################################################################################
# PIPELINE COMPLETED
# Total time: 9150ms
#   Stage 1 (Planner):  1850ms
#   Stage 2 (Coder):    4200ms
#   Stage 3 (Reviewer): 3100ms
################################################################################
```

### Desabilitar Debug

```python
# code_pipeline.py
DEBUG_PIPELINE = False
```

---

## Exemplos de Uso

### Exemplo 1: API REST Python

**Input:**
```
Crie uma API REST em Python com FastAPI para gerenciar usuários
```

**Pipeline Flow:**
1. Planner: Identifica FastAPI, SQLAlchemy, CRUD operations
2. Coder: Gera main.py, models.py, schemas.py
3. Reviewer: Valida código, adiciona error handling

**Output:**
```markdown
# API REST com FastAPI

Criei uma API completa com 3 arquivos:

## 1. models.py
```python
from sqlalchemy import Column, Integer, String
...
```

## 2. schemas.py
```python
from pydantic import BaseModel
...
```

## 3. main.py
```python
from fastapi import FastAPI
...
```

## Como Executar

```powershell
pip install fastapi uvicorn sqlalchemy
uvicorn main:app --reload
```

Acesse: http://localhost:8000/docs
```

---

### Exemplo 2: React Component

**Input:**
```
Crie um componente React TypeScript com lista de usuários e paginação
```

**Pipeline Flow:**
1. Planner: Identifica React, TypeScript, hooks, state management
2. Coder: Gera UserList.tsx com useState, useEffect
3. Reviewer: Adiciona loading state, error handling

**Output:**
```markdown
# Componente UserList

```typescript
import React, { useState, useEffect } from 'react';

interface User {
  id: number;
  name: string;
  email: string;
}

export const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  
  // ... código completo ...
};
```

## Como Usar

```powershell
npm install react
# Importe em App.tsx: import { UserList } from './UserList';
```
```

---

## Roadmap

### Fase 1: MVP (ATUAL) ✅
- [x] Pipeline de 3 estágios
- [x] Integração com MoE Router
- [x] Fallback para Qwen local
- [x] Logs detalhados
- [x] Test suite

### Fase 2: APIs Externas
- [ ] Integração com DeepSeek-Coder API
- [ ] Integração com LLaMA 3 API
- [ ] Retry logic e rate limiting
- [ ] Cache de respostas

### Fase 3: Otimizações
- [ ] Streaming de Stage 2 enquanto Stage 3 processa
- [ ] Paralelização de tasks
- [ ] Cache de planos similares
- [ ] Batch processing

### Fase 4: Melhorias
- [ ] Tool calling integration
- [ ] File creation automática
- [ ] Git commit suggestions
- [ ] Interactive refinement

---

## FAQ

### Q: Por que 3 modelos e não 1?

**A:** Especialização de tarefas. Cada modelo foca em uma coisa:
- Qwen: Planejamento e contexto
- DeepSeek: Geração de código (especialista)
- LLaMA: Revisão e explicação

### Q: E se as APIs falharem?

**A:** Fallback automático para Qwen local. O sistema sempre funciona.

### Q: Posso desabilitar o pipeline?

**A:** Sim. Comente a linha em `inference.py`:
```python
# if is_code_expert(decision.expert_id):
#     pipeline_result = run_code_pipeline(...)
```

### Q: Como adicionar um novo expert de código?

**A:** 
1. Adicione em `expert_registry.py` com ID começando com `code_`
2. Adicione keywords relevantes
3. Pipeline detecta automaticamente

### Q: Qual o custo de usar APIs externas?

**A:** 
- DeepSeek-Coder: ~$0.14/1M tokens
- LLaMA 3-8B: ~$0.18/1M tokens
- Por query: ~$0.001-0.003 (1-3 cents)

---

## Conclusão

O **Code Pipeline** é uma arquitetura robusta que combina:
- ✅ Planejamento inteligente (Qwen + RAG + SuperEzio)
- ✅ Código especializado (DeepSeek-Coder)
- ✅ Revisão de qualidade (LLaMA 3)
- ✅ Fallback automático
- ✅ Integração transparente

**Resultado:** Código de alta qualidade, revisado e explicado, em português coloquial.

---

**Autor:** Marco Barreto  
**Projeto:** Superezio Realtime  
**Data:** 2025-01-13  
**Versão:** 1.0.0
