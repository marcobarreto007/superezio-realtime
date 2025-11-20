# 🚀 Como Usar o Backend Python (Hugging Face)

**Status:** ✅ Implementação completa

---

## 📋 PRÉ-REQUISITOS

- ✅ Python 3.12+ instalado
- ✅ CUDA instalado (para GPU)
- ✅ Modelo Qwen2.5-7B baixado (14.2 GB)
- ✅ Ambiente virtual criado (`backend/venv/`)

---

## 🚀 INICIAR SERVIDOR

### **Opção 1: Script Batch (Windows)**
```bash
cd backend
start.bat
```

### **Opção 2: Manual**
```bash
cd backend
venv\Scripts\activate
python api.py
```

**Servidor roda em:** `http://localhost:8000`

---

## ✅ VERIFICAÇÃO

### **1. Verificar Saúde:**
```bash
curl http://localhost:8000/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "gpu_available": true,
  "gpu_name": "NVIDIA GeForce RTX 3060",
  "gpu_memory_total_gb": 12.0,
  "gpu_memory_used_gb": 5.5,
  "model_loaded": true
}
```

### **2. Testar Chat:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "Você é SuperEzio."},
      {"role": "user", "content": "Oi!"}
    ],
    "temperature": 0.2,
    "max_tokens": 512
  }'
```

---

## 🔗 INTEGRAÇÃO COM EXPRESS

O Express (`server.mjs`) já está configurado para fazer proxy:

**Frontend → Express → FastAPI**

```
http://localhost:3000/api/hf/chat
  → http://localhost:8080/api/hf/chat (Express)
    → http://localhost:8000/chat (FastAPI)
```

---

## 📊 ENDPOINTS DISPONÍVEIS

### **GET /** - Informações do servidor
```json
{
  "status": "online",
  "model": "Qwen2.5-7B-Instruct",
  "device": "cuda",
  "gpu_memory_used_gb": 5.5
}
```

### **GET /health** - Status de saúde
```json
{
  "status": "healthy",
  "gpu_available": true,
  "model_loaded": true
}
```

### **POST /chat** - Chat completion
```json
{
  "messages": [
    {"role": "user", "content": "Olá!"}
  ],
  "temperature": 0.2,
  "max_tokens": 2048,
  "tools": [...] (opcional)
}
```

---

## 🐛 TROUBLESHOOTING

### **Erro: "Modelo não encontrado"**
```bash
# Verificar se modelo existe
Test-Path "models\qwen2.5-7b-instruct\config.json"

# Se não existir, baixar:
python scripts/download_model.py
```

### **Erro: "CUDA não disponível"**
```bash
# Verificar CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Se False, reinstalar PyTorch com CUDA:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### **Erro: "Port 8000 already in use"**
```bash
# Matar processo na porta 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## ✅ CHECKLIST DE TESTE

- [ ] Servidor Python inicia sem erros
- [ ] Modelo carrega na GPU
- [ ] Endpoint `/health` responde
- [ ] Endpoint `/chat` funciona
- [ ] Express faz proxy corretamente
- [ ] Frontend consegue chamar `/api/hf/chat`

---

**Status:** ✅ Pronto para uso  
**Próximo:** Testar integração completa

