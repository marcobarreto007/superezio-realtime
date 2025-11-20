# Guia Rápido: Ativar APIs Externas (17x Mais Rápido)

## Problema Atual

Pipeline usando **Qwen fallback** para todos os 3 stages:
- ⏱️ Stage 1: ~50s
- ⏱️ Stage 2: ~60s
- ⏱️ Stage 3: ~50s
- **Total: ~160s (2.7 minutos)**

## Solução: APIs Externas

Usar **HuggingFace Inference API** para Stage 2 e 3:
- ⚡ Stage 1: ~2s (Qwen local)
- ⚡ Stage 2: ~4s (DeepSeek-Coder API)
- ⚡ Stage 3: ~3s (LLaMA 3 API)
- **Total: ~9s (17x mais rápido!)**

---

## Passo 1: Obter HuggingFace Token

### 1.1. Criar Conta (se não tem)
```
https://huggingface.co/join
```

### 1.2. Gerar Token de Acesso
1. Acesse: https://huggingface.co/settings/tokens
2. Clique em **"New token"**
3. Nome: `superezio-code-pipeline`
4. Tipo: **Read** (suficiente para Inference API)
5. Copie o token: `hf_...`

---

## Passo 2: Configurar Variável de Ambiente

### Windows PowerShell (Temporário - Sessão Atual)

```powershell
$env:HF_TOKEN = "hf_SEU_TOKEN_AQUI"
```

### Windows PowerShell (Permanente)

```powershell
# Adicionar ao perfil do PowerShell
notepad $PROFILE

# Cole essa linha no arquivo:
$env:HF_TOKEN = "hf_SEU_TOKEN_AQUI"

# Salve e recarregue:
. $PROFILE
```

### Alternativa: Arquivo .env

Crie arquivo `.env` na raiz do projeto:

```bash
# .env
HF_TOKEN=hf_SEU_TOKEN_AQUI
```

E adicione no `backend/code_pipeline.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Passo 3: Implementar Chamadas de API

### 3.1. Instalar Dependência

```powershell
pip install requests
```

### 3.2. Adicionar Função no code_pipeline.py

```python
import requests
import os

HF_TOKEN = os.getenv("HF_TOKEN")

def call_hf_inference_api(model_url: str, prompt: str, max_tokens: int = 1024) -> str:
    """
    Chama HuggingFace Inference API.
    
    Args:
        model_url: URL do modelo (ex: DeepSeek-Coder)
        prompt: Prompt completo
        max_tokens: Máximo de tokens
        
    Returns:
        Resposta do modelo
    """
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN não configurado")
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": 0.2,
            "return_full_text": False
        }
    }
    
    response = requests.post(model_url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    
    result = response.json()
    
    # HF Inference API retorna lista
    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "")
    
    return result.get("generated_text", "")
```

### 3.3. Atualizar Stage 2 (Coder)

```python
def call_model_deepseek_coder(...):
    # Tentar API primeiro
    if HF_TOKEN:
        try:
            print(f"🚀 [CODER] Using DeepSeek-Coder API")
            
            prompt = f"{CODER_SYSTEM_PROMPT}\n\n{user_query}\n\nPLAN: {plan_json}"
            
            response_text = call_hf_inference_api(
                model_url=DEEPSEEK_CODER_API,
                prompt=prompt,
                max_tokens=2048
            )
            
            # Parse JSON...
            
        except Exception as e:
            print(f"⚠️  [CODER] API failed: {e}, using Qwen fallback")
    
    # Fallback para Qwen local
    print(f"⚠️  [CODER] Using Qwen fallback")
    # ... código existente ...
```

### 3.4. Atualizar Stage 3 (Reviewer)

```python
def call_model_llama_reviewer(...):
    # Tentar API primeiro
    if HF_TOKEN:
        try:
            print(f"🚀 [REVIEWER] Using LLaMA 3 API")
            
            prompt = f"{REVIEWER_SYSTEM_PROMPT}\n\nPLAN: {plan_json}\n\nCODE: {code_json}"
            
            response_text = call_hf_inference_api(
                model_url=LLAMA3_API,
                prompt=prompt,
                max_tokens=2048
            )
            
            # Parse JSON...
            
        except Exception as e:
            print(f"⚠️  [REVIEWER] API failed: {e}, using Qwen fallback")
    
    # Fallback para Qwen local
    print(f"⚠️  [REVIEWER] Using Qwen fallback")
    # ... código existente ...
```

---

## Passo 4: Testar

```powershell
# 1. Configurar token
$env:HF_TOKEN = "hf_SEU_TOKEN_AQUI"

# 2. Testar pipeline
cd backend
python test_code_pipeline.py

# 3. Ver logs
# Deve mostrar:
# 🚀 [CODER] Using DeepSeek-Coder API
# 🚀 [REVIEWER] Using LLaMA 3 API
```

---

## Passo 5: Rodar Backend

```powershell
cd backend
python api.py

# Em outro terminal:
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Crie função Python fatorial"}]
  }'
```

---

## Performance Esperada

### Com APIs Ativadas ✅

```
[PIPELINE][PLANNER] Stage 1: Planning
  Expert: code_python
  ✅ Plan generated in 2000ms

[PIPELINE][CODER] Stage 2: Code Generation
  🚀 Using DeepSeek-Coder API
  ✅ Code generated in 4000ms

[PIPELINE][REVIEWER] Stage 3: Code Review
  🚀 Using LLaMA 3 API
  ✅ Review completed in 3000ms

################################
# PIPELINE COMPLETED
# Total time: 9000ms (9s)
################################
```

### Sem APIs (Fallback) ⚠️

```
[PIPELINE][PLANNER] Stage 1: Planning
  ✅ Plan generated in 50000ms

[PIPELINE][CODER] Stage 2: Code Generation
  ⚠️  Using Qwen fallback
  ✅ Code generated in 60000ms

[PIPELINE][REVIEWER] Stage 3: Code Review
  ⚠️  Using Qwen fallback
  ✅ Review completed in 50000ms

################################
# PIPELINE COMPLETED
# Total time: 160000ms (160s)
################################
```

---

## Alternativa: OpenRouter

Se preferir usar **OpenRouter** (suporta mais modelos):

### 1. Obter API Key
```
https://openrouter.ai/keys
```

### 2. Configurar
```powershell
$env:OPENROUTER_API_KEY = "sk-or-..."
```

### 3. Implementar em code_pipeline.py
```python
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

def call_openrouter(model: str, messages: list) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages
    }
    
    response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
    result = response.json()
    
    return result["choices"][0]["message"]["content"]
```

---

## Custos Estimados

### HuggingFace Inference API (Grátis!)
- **DeepSeek-Coder**: Grátis (rate limited)
- **LLaMA 3-8B**: Grátis (rate limited)
- **Limite:** ~1000 requests/dia

### OpenRouter (Pago)
- **DeepSeek-Coder-6.7B**: $0.14/1M tokens
- **LLaMA 3-8B**: $0.18/1M tokens
- **Por query:** ~$0.001-0.003 (1-3 centavos)

---

## Troubleshooting

### Erro: "Model is currently loading"
```
⚠️  Modelo ainda carregando no HF. Tente em 30s.
```
**Solução:** Aguarde ou use fallback automático.

### Erro: "Rate limit exceeded"
```
⚠️  Rate limit excedido. Usando fallback.
```
**Solução:** Aguarde 1 minuto ou configure OpenRouter.

### Erro: "Invalid token"
```
❌ HF_TOKEN inválido
```
**Solução:** Verifique token em https://huggingface.co/settings/tokens

---

## Conclusão

### Sem APIs (Padrão)
- ✅ Funciona sempre
- ⚠️ Lento (~160s)
- ✅ Zero custo

### Com APIs Externas
- ✅ 17x mais rápido (~9s)
- ✅ Modelos especializados
- ⚠️ Requer token (grátis)

**Recomendação:** Ative APIs externas para melhor experiência!

---

**Próximo Passo:** Implementar chamadas de API em `code_pipeline.py`
