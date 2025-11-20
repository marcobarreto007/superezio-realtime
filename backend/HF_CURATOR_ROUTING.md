# HF Curator Routing - Implementação Completa

## Resumo das Mudanças

### 1. Expert Registry (`backend/expert_registry.py`)
- **Expandido keywords do `code_hf_curator`** para 40+ termos
- Cobertura completa:
  - HuggingFace Hub: "huggingface", "hf hub", "hf token", "hf cache"
  - Modelos específicos: "starcoder", "codellama", "qwen2.5", "llama", "mistral", "wizardcoder", "deepseek"
  - Artefatos: "checkpoint", "weights", "safetensors", "gguf"
  - Seleção de modelos: "escolher modelo", "qual modelo usar", "best model", "compare models"
  - Português + Inglês

### 2. Expert Router (`backend/expert_router.py`)
- **Adicionada lista `HF_TRIGGERS`** no topo do arquivo (40+ gatilhos)
- **Nova prioridade de roteamento:**
  1. `explicit_mode` (ABSOLUTA - não pode ser sobrescrita)
  2. **HF Override** (novo) - detecta HF_TRIGGERS e força `code_hf_curator`
  3. Keyword-based routing (fallback)

- **Novo método `_extract_user_text()`**: Concatena todas as mensagens do usuário para detecção
- **Logs claros**: `[ROUTER] HF override: trigger='starcoder' → expert=code_hf_curator`

### 3. Testes (`backend/tests/test_expert_router_hf_curator.py`)
- **8 casos de teste:**
  - ✅ Query básica HF
  - ✅ BigCode/The Stack
  - ✅ Query Python normal (NÃO deve ir pra HF)
  - ✅ Explicit mode override
  - ✅ Comparação de modelos
  - ✅ Keywords Qwen/LLaMA
  - ✅ Seleção de modelos
  - ✅ Weights/checkpoints

- **Todos passaram: 8/8** ✅

## Critérios de Aceitação - STATUS

✅ **Queries HF vão para code_hf_curator:**
- "huggingface", "the stack", "starcoder", "codellama", "qwen2.5" → `code_hf_curator`

✅ **Queries normais NÃO vão para code_hf_curator:**
- "código Python com asyncio" → `code_python` ou `code_api`

✅ **explicit_mode tem prioridade absoluta:**
- `mode=code_python` + "huggingface" → `code_python` (explicit_mode ganha)

✅ **Logs claros:**
```
[ROUTER] HF override: trigger='starcoder' → expert=code_hf_curator
[ROUTER] → expert=code_hf_curator
[ROUTER] → lora=None
[ROUTER] → rag_domains=['hf_models_code', 'hf_datasets_code']
```

## Exemplos de Roteamento

### Vão para code_hf_curator ✅
- "Qual o melhor modelo de código no HuggingFace?"
- "Compare CodeLlama vs StarCoder"
- "Quero baixar o modelo bigcode/the-stack"
- "Me recomende um modelo open-source para Python"
- "Como usar Qwen2.5 para code generation?"
- "Onde encontro os weights do modelo?"
- "Converter safetensors para GGUF"

### NÃO vão para code_hf_curator ✅
- "Me mostra código Python com asyncio" → `code_python` ou `code_api`
- "Criar árvore binária em TypeScript" → `code_algorithms`
- "Como fazer deploy no Docker?" → `code_infra`

### Explicit Mode Override ✅
```python
route(messages, explicit_mode="code_python")  # Sempre vai pra code_python
```

## Arquivos Modificados

1. `backend/expert_registry.py` - Expandido keywords do code_hf_curator
2. `backend/expert_router.py` - Adicionado HF_TRIGGERS + lógica de override
3. `backend/tests/test_expert_router_hf_curator.py` - Criado (8 testes)

## Como Usar

### Roteamento Automático
```python
from expert_router import ExpertRouter

router = ExpertRouter()
messages = [{"role": "user", "content": "Qual modelo usar do HuggingFace?"}]
decision = router.route(messages)

print(decision.expert_id)  # → "code_hf_curator"
print(decision.rag_domains)  # → ["hf_models_code", "hf_datasets_code"]
```

### Forçar Expert Específico
```python
# Força code_python mesmo com keywords HF
decision = router.route(messages, explicit_mode="code_python")
print(decision.expert_id)  # → "code_python"
```

## Integração com RAG

O `code_hf_curator` usa RAG domains:
- `hf_models_code`: 22 modelos do HuggingFace
- `hf_datasets_code`: 15 datasets de código

Quando roteado para `code_hf_curator`, o sistema:
1. Busca nos RAG domains relevantes
2. Injeta contexto HF na resposta
3. Responde com conhecimento atualizado sobre modelos/datasets

## Próximos Passos

1. ✅ Testes passando (8/8)
2. ✅ Roteamento funcionando
3. ⏭️ Testar via backend Python (api.py)
4. ⏭️ Fazer query via /api/agent/chat
5. ⏭️ Verificar RAG context no response

## Logs de Exemplo

```
[ROUTER] HF override: trigger='huggingface' → expert=code_hf_curator
[ROUTER] → expert=code_hf_curator
[ROUTER] → lora=None
[ROUTER] → rag_domains=['hf_models_code', 'hf_datasets_code']
[ROUTER] → reason="HF override detected (trigger: 'huggingface')"
```

## Regra de Override (Comentário no Código)

```python
# Regra de override HF:
# Se a query mencionar explicitamente HuggingFace / modelos open-source / Qwen / LLaMA etc,
# o expert code_hf_curator é escolhido antes de qualquer outro, exceto quando explicit_mode é forçado.
```
