# ✅ Correção: Erro device_map com accelerate

**Erro:** `ValueError: The model has been loaded with accelerate and therefore cannot be moved to a specific device.`  
**Status:** ✅ CORRIGIDO

---

## 🐛 PROBLEMA

Quando usamos `device_map="auto"` no `from_pretrained()`, o modelo é carregado com `accelerate`, que gerencia automaticamente o dispositivo. Tentar passar `device=0` no pipeline causa erro.

---

## ✅ SOLUÇÃO APLICADA

### **1. Removido parâmetro `device` do pipeline:**
```python
# ANTES (causava erro):
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0 if DEVICE == "cuda" else -1,  # ❌ ERRO quando device_map="auto"
)

# DEPOIS (corrigido):
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    # device não é necessário quando device_map="auto" foi usado ✅
)
```

### **2. Corrigido `torch_dtype` para `dtype`:**
```python
# ANTES (deprecated):
torch_dtype=torch.float16

# DEPOIS:
dtype=torch.float16
```

### **3. Atualizado FastAPI para usar `lifespan`:**
```python
# ANTES (deprecated):
@app.on_event("startup")
async def startup():
    ...

# DEPOIS:
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    ...
    yield
    # Shutdown
    ...

app = FastAPI(..., lifespan=lifespan)
```

---

## 📝 ARQUIVOS MODIFICADOS

1. ✅ `backend/inference.py` - Removido `device` do pipeline, corrigido `dtype`
2. ✅ `backend/api.py` - Atualizado para usar `lifespan` ao invés de `@app.on_event`

---

## ✅ VERIFICAÇÃO

O servidor deve iniciar sem erros:
```bash
cd backend
set PYTHONIOENCODING=utf-8
venv\Scripts\activate
python api.py
```

**Resultado esperado:**
- ✅ Modelo carrega na GPU
- ✅ Pipeline criado sem erros
- ✅ Servidor inicia na porta 8000

---

**Status:** ✅ Correção aplicada  
**Próximo:** Testar servidor iniciando corretamente

