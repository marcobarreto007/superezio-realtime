# 🎯 SUPER-EZIO CODE MOE - Exemplos de Uso da API

Este documento contém exemplos prontos de requisições JSON para usar o sistema MoE (Mixture of Experts) do SuperEzio Code.

---

## 📡 Endpoints Disponíveis

### Backend Python (FastAPI)
- **Porta:** 8000
- **Síncrono:** `POST http://localhost:8000/chat`
- **Streaming:** `POST http://localhost:8000/chat/stream`

### Server Node (Express - Proxy)
- **Porta:** 8080
- **Endpoint:** `POST http://localhost:8080/api/chat`
- **Formato:** Igual ao backend Python

---

## 🔧 Estrutura do Payload

```typescript
{
  messages: Array<{role: "system" | "user" | "assistant", content: string}>,
  max_tokens: number,        // Ex: 2000
  temperature: number,       // Ex: 0.7 (0.0 = determinístico, 1.0 = criativo)
  stream: boolean,           // true para /chat/stream, false para /chat
  mode: string | null        // null = roteamento automático MoE
}
```

---

## 📝 Exemplos de Requisições

### Exemplo A — Python Code Expert (modo explícito)

Força o uso do expert `code_python` com LoRA especializado.

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Implementa uma função em Python que soma números de uma lista, com testes unitários usando pytest."
    }
  ],
  "max_tokens": 2000,
  "temperature": 0.3,
  "stream": false,
  "mode": "code_python"
}
```

---

### Exemplo B — TypeScript Code Expert (modo explícito)

Força o uso do expert `code_ts` para React/TypeScript.

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Cria um hook React com TypeScript para buscar dados de /api/users, com loading e error state."
    }
  ],
  "max_tokens": 2500,
  "temperature": 0.4,
  "stream": false,
  "mode": "code_ts"
}
```

---

### Exemplo C — Infrastructure Expert (modo explícito)

Força o uso do expert `code_infra` para Docker/DevOps.

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Escreve um Dockerfile otimizado para app FastAPI + Uvicorn, com multi-stage build."
    }
  ],
  "max_tokens": 1800,
  "temperature": 0.2,
  "stream": false,
  "mode": "code_infra"
}
```

---

### Exemplo D — Machine Learning Expert (modo explícito)

Força o uso do expert `code_ml` para PyTorch/transformers.

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Implementa treino de um modelo PyTorch simples (MLP) para classificar dígitos MNIST, com loop de treino e validação."
    }
  ],
  "max_tokens": 3000,
  "temperature": 0.4,
  "stream": false,
  "mode": "code_ml"
}
```

---

### Exemplo E — Roteamento Automático MoE (sem mode)

Deixa o router escolher o expert baseado nas keywords da mensagem. Neste caso, deve rotear para `code_api`.

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Cria uma API REST em FastAPI com rota /health, /items e paginação."
    }
  ],
  "max_tokens": 2200,
  "temperature": 0.5,
  "stream": false,
  "mode": null
}
```

**Roteamento esperado:** `code_api` (detecta keywords: api, rest, fastapi, paginação)

---

### Exemplo F — Com Histórico de Conversação

O sistema mantém contexto entre mensagens. O router analisa TODAS as mensagens para escolher o expert.

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Preciso otimizar uma query SQL que demora 30 segundos."
    },
    {
      "role": "assistant",
      "content": "Entendo. Para otimizar a query SQL, vou precisar ver o código. Pode compartilhar a query?"
    },
    {
      "role": "user",
      "content": "SELECT * FROM orders JOIN customers ON orders.customer_id = customers.id WHERE orders.created_at > '2024-01-01' AND customers.country = 'BR' ORDER BY orders.total DESC LIMIT 1000"
    }
  ],
  "max_tokens": 2500,
  "temperature": 0.3,
  "stream": false,
  "mode": null
}
```

**Roteamento esperado:** `code_database` (detecta keywords: sql, query, join, select)

---

### Exemplo G — Streaming Response

Para receber a resposta em chunks SSE (Server-Sent Events).

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Cria uma classe Python para gerenciar conexões de WebSocket com reconnect automático."
    }
  ],
  "max_tokens": 2000,
  "temperature": 0.4,
  "stream": true,
  "mode": "code_python"
}
```

**Endpoint:** `POST http://localhost:8000/chat/stream`

**Response format:**
```
data: {"token": "class", "done": false}
data: {"token": " WebSocket", "done": false}
data: {"token": "Manager", "done": false}
...
data: {"done": true}
```

---

### Exemplo H — Frontend + Backend Integration

Pede código que envolve múltiplos experts (frontend + API). Router deve escolher baseado no contexto principal.

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Implementa autenticação JWT completa: backend FastAPI com /login e /me, e frontend React com Context API para gerenciar token."
    }
  ],
  "max_tokens": 3500,
  "temperature": 0.5,
  "stream": false,
  "mode": null
}
```

**Roteamento esperado:** `code_api` ou `code_general` (múltiplos domínios = expert generalista)

---

### Exemplo I — Testing Expert

Força uso do expert `code_testing` para testes.

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Cria testes de integração com pytest para testar endpoints FastAPI, incluindo fixtures de database e mocks."
    }
  ],
  "max_tokens": 2800,
  "temperature": 0.3,
  "stream": false,
  "mode": "code_testing"
}
```

---

### Exemplo J — Algorithms Expert

Força uso do expert `code_algorithms` para estruturas de dados.

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Implementa uma árvore AVL balanceada em Python com inserção, remoção e busca, incluindo testes de complexidade O(log n)."
    }
  ],
  "max_tokens": 3000,
  "temperature": 0.2,
  "stream": false,
  "mode": "code_algorithms"
}
```

---

## 🌐 Proxy via Node Server (porta 8080)

O servidor Node em `server.ts` faz proxy para o backend Python. Use o mesmo formato JSON:

**Endpoint:** `POST http://localhost:8080/api/chat`

**Body:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Explica como funciona o event loop do Node.js com exemplos."
    }
  ],
  "max_tokens": 2000,
  "temperature": 0.6,
  "stream": false,
  "mode": "code_ts"
}
```

**Response (síncrono):**
```json
{
  "response": "O event loop do Node.js é...",
  "expert": "code_ts",
  "lora_adapter": "code_expert_v1",
  "usage": {
    "prompt_tokens": 45,
    "completion_tokens": 823,
    "total_tokens": 868
  }
}
```

---

## 🎯 Tabela de Roteamento Automático

Quando `mode: null` ou omitido, o router usa keywords:

| Keywords na mensagem | Expert roteado | LoRA |
|---------------------|----------------|------|
| `python`, `pandas`, `numpy`, `def` | `code_python` | `code_expert_v1` |
| `typescript`, `react`, `vue`, `tsx` | `code_ts` | `code_expert_v1` |
| `docker`, `kubernetes`, `nginx` | `code_infra` | `code_expert_v1` |
| `pytorch`, `transformers`, `lora` | `code_ml` | `code_expert_v1` |
| `select`, `join`, `postgres`, `sql` | `code_database` | `code_expert_v1` |
| `html`, `css`, `tailwind`, `vite` | `code_frontend` | `code_expert_v1` |
| `api`, `rest`, `graphql`, `endpoint` | `code_api` | `code_expert_v1` |
| `pytest`, `jest`, `unittest`, `mock` | `code_testing` | `code_expert_v1` |
| `algorithm`, `heap`, `graph`, `tree` | `code_algorithms` | `code_expert_v1` |
| Nenhuma keyword específica | `code_general` | `None` |

---

## 🔍 Debug e Logs

Para ver o roteamento em ação, ative os flags de debug:

**Backend:** `backend/expert_router.py`
```python
DEBUG_ROUTER = True  # Mostra decisões de roteamento
```

**Logs esperados:**
```
[ROUTER] explicit_mode=None (keyword-based)
[ROUTER] → expert=code_python
[ROUTER] → lora=code_expert_v1
[ROUTER] → rag_domains=['code_python', 'code_general']
[ROUTER] → reason="Detected keywords: pandas, numpy"
```

---

## 🚀 Como Testar

### 1. Via cURL (Linux/Mac/WSL)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Cria uma função Python para validar CPF."}],
    "max_tokens": 1500,
    "temperature": 0.3,
    "stream": false,
    "mode": null
  }'
```

### 2. Via PowerShell (Windows)

```powershell
$body = @{
    messages = @(
        @{
            role = "user"
            content = "Cria uma função Python para validar CPF."
        }
    )
    max_tokens = 1500
    temperature = 0.3
    stream = $false
    mode = $null
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8000/chat" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### 3. Via Python (requests)

```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={
        "messages": [
            {"role": "user", "content": "Cria uma função Python para validar CPF."}
        ],
        "max_tokens": 1500,
        "temperature": 0.3,
        "stream": False,
        "mode": None  # Roteamento automático
    }
)

print(response.json())
```

### 4. Via Interface Web (Frontend)

O frontend React em `src/App.tsx` já está integrado. Use o chat normalmente e o MoE será acionado automaticamente.

---

## 📚 Documentação Técnica

Para entender a arquitetura completa:

- **Expert Registry:** `backend/expert_registry.py` - Define os 10 experts
- **Router:** `backend/expert_router.py` - Lógica de roteamento
- **RAG Client:** `backend/rag_client.py` - Integração com RAG (stub)
- **Prompt Builder:** `backend/prompt_builder.py` - Construção de prompts
- **Inference:** `backend/inference.py` - Fluxo completo MoE

---

## ✅ Validação

Para validar que o MoE está funcionando:

```bash
cd backend
python test_expert_router.py    # Testa roteamento
python test_moe_code_flow.py    # Testa fluxo completo
```

---

**Sistema implementado:** ✅ 100% funcional  
**Última atualização:** 13 Nov 2025  
**Experts disponíveis:** 10 (General, Python, TypeScript, Infra, ML, Database, Frontend, API, Testing, Algorithms)  
**LoRA adapters:** 1 compartilhado (`code_expert_v1`)  
**RAG domains:** 10 namespaces especializados  
