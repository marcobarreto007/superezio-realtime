# 🚀 Como Iniciar os Servidores do SuperEzio

**IMPORTANTE:** O SuperEzio precisa de **3 servidores** rodando simultaneamente!

---

## 📋 OS 3 SERVIDORES NECESSÁRIOS

1. **Python FastAPI** (porta 8000) - Inferência do modelo Hugging Face
2. **Express Backend** (porta 8080) - Proxy e API do agente
3. **Vite Frontend** (porta 3000) - Interface React

---

## ✅ OPÇÃO 1: Script Automático (RECOMENDADO)

### **Windows:**
```bash
start_all.bat
```

Isso abre **3 janelas** automaticamente:
- ✅ Python Backend
- ✅ Express Backend  
- ✅ Vite Frontend

---

## ✅ OPÇÃO 2: NPM Scripts

### **Iniciar tudo de uma vez:**
```bash
npm run dev:all
```

Isso inicia os 3 servidores em paralelo usando `concurrently`.

---

## ✅ OPÇÃO 3: Manual (3 Terminais)

### **Terminal 1: Python FastAPI**
```bash
cd backend
venv\Scripts\activate
python api.py
```
**Ou:**
```bash
start_backend_python.bat
```

**Aguardar:** Modelo carrega em 1-2 minutos  
**Verificar:** http://localhost:8000/health

---

### **Terminal 2: Express Backend**
```bash
npm run serve
```

**Verificar:** http://localhost:8080

---

### **Terminal 3: Vite Frontend**
```bash
npm run dev
```

**Acessar:** http://localhost:3000

---

## 🔍 VERIFICAÇÃO

### **1. Verificar se todos estão rodando:**
```bash
# Python
curl http://localhost:8000/health

# Express
curl http://localhost:8080

# Vite
curl http://localhost:3000
```

### **2. Verificar processos:**
```bash
netstat -ano | findstr ":8000"
netstat -ano | findstr ":8080"
netstat -ano | findstr ":3000"
```

---

## ⚠️ PROBLEMAS COMUNS

### **Erro: "Port 8000 already in use"**
```bash
# Matar processo
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### **Erro: "Modelo não encontrado"**
```bash
# Verificar
Test-Path "models\qwen2.5-7b-instruct\config.json"

# Se não existir, baixar:
python scripts\download_model.py
```

### **Erro: "CUDA não disponível"**
```bash
# Verificar
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 📊 ORDEM DE INICIALIZAÇÃO

1. **Primeiro:** Python FastAPI (carrega modelo)
2. **Segundo:** Express Backend (faz proxy)
3. **Terceiro:** Vite Frontend (interface)

---

## ✅ CHECKLIST

- [ ] Modelo baixado (`models/qwen2.5-7b-instruct/`)
- [ ] Python FastAPI rodando (porta 8000)
- [ ] Express Backend rodando (porta 8080)
- [ ] Vite Frontend rodando (porta 3000)
- [ ] Todos os endpoints respondendo

---

**Status:** ✅ Documentação completa  
**Próximo:** Executar `start_all.bat` ou `npm run dev:all`

