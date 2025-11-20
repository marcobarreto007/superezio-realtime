# 📊 Guia de Logs e Tempos - SuperEzio

## ⏱️ Tempos Esperados

### **Carregamento Inicial do Modelo**
- **Model Loader**: 60-90 segundos (primeira vez)
- **FastAPI**: 60-90 segundos (carrega modelo no seu processo)

### **Geração de Resposta (Inferência)**
- **Resposta curta** (< 100 tokens): 5-15 segundos
- **Resposta média** (100-500 tokens): 15-30 segundos
- **Resposta longa** (500-1000 tokens): 30-60 segundos
- **Timeout máximo**: 120 segundos (2 minutos)

## 🔍 Onde Ver os Logs

### **1. Frontend (Console do Navegador)**
Abra DevTools (F12) → Console

**Logs esperados:**
```
[HF Client] Enviando mensagem para /api/hf/chat...
[HF Client] Mensagens: 2 mensagens na conversa
[HF Client] Última mensagem: Oi, como você está?...
[HF Client] Resposta recebida em 12.3s
```

**Se houver erro:**
```
[HF Client] Erro após 5.2s: Failed to fetch
Error communicating with Hugging Face backend: ...
```

### **2. Python FastAPI (Janela do PowerShell)**
Procure pela janela "SuperEzio Python Backend"

**Logs esperados:**
```
============================================================
🔵 [REQ #1234] Nova requisição recebida em 22:30:15
📊 [REQ #1234] Max tokens: 1024, Temperature: 0.2
📝 [REQ #1234] Mensagens: 2 mensagens na conversa
💬 [REQ #1234] Última mensagem: Oi, como você está?
⏳ [REQ #1234] Iniciando inferência...
✅ [REQ #1234] Inferência concluída em 12.34s
✅ [REQ #1234] Resposta gerada: 245 caracteres
⚡ [REQ #1234] Performance: 19.8 chars/s
⏱️  [REQ #1234] Tempo total: 12.45s
============================================================
```

**Se houver erro:**
```
❌ [REQ #1234] Erro no chat após 5.2s: ...
```

### **3. Express Backend (Janela do PowerShell)**
Procure pela janela "SuperEzio Express"

**Logs esperados:**
```
Server running on http://localhost:8080
Proxying /api/hf -> http://localhost:8000 (Python FastAPI - Hugging Face)
Proxying /api/agent -> Agent Tools (filesystem, etc)
```

## 🚨 Problemas Comuns

### **"SuperEzio está digitando..." por mais de 2 minutos**
**Causa**: Timeout ou servidor travado

**Solução**:
1. Verifique o console do navegador (F12) → veja se há erro
2. Verifique a janela do Python FastAPI → veja se há erro
3. Se não houver logs, o servidor pode estar travado
4. Reinicie: `kill_all_servers.bat` → `start_all_ordered.bat`

### **Erro: "Failed to fetch"**
**Causa**: Servidor não está respondendo

**Solução**:
1. Verifique se Python FastAPI está rodando (porta 8000)
2. Verifique se Express está rodando (porta 8080)
3. Teste: `curl http://localhost:8000/health`

### **Erro: "Timeout: O servidor demorou mais de 120 segundos"**
**Causa**: Modelo está processando resposta muito longa ou travado

**Solução**:
1. Verifique a janela do Python FastAPI → veja se está processando
2. Se não houver logs, o modelo pode estar travado
3. Reinicie o Python FastAPI

### **Nenhum log aparece**
**Causa**: Requisição não está chegando ao servidor

**Solução**:
1. Verifique o Network tab no DevTools (F12)
2. Veja se a requisição para `/api/hf/chat` está sendo feita
3. Verifique se há erro de CORS ou conexão

## 📈 Performance Esperada

### **RTX 3060 12GB (seu hardware)**
- **Modelo**: Qwen2.5-7B-Instruct
- **VRAM usada**: ~3.6 GB
- **Velocidade**: 15-25 caracteres/segundo
- **Latência**: 5-30 segundos (depende do tamanho da resposta)

### **Otimizações Aplicadas**
- ✅ `max_tokens: 1024` (reduzido de 2048)
- ✅ `temperature: 0.2` (mais determinístico)
- ✅ `device_map="auto"` (otimização GPU)
- ✅ `dtype=torch.float16` (half precision)

## 🔧 Debug Rápido

### **Verificar se tudo está rodando:**
```powershell
# Verificar portas
netstat -ano | findstr ":8000 :8080 :3000" | findstr "LISTENING"

# Verificar processos
Get-Process | Where-Object {$_.ProcessName -match 'python|node'}
```

### **Testar API diretamente:**
```powershell
# Testar Python FastAPI
curl http://localhost:8000/health

# Testar Express
curl http://localhost:8080
```

### **Ver logs em tempo real:**
1. Abra as janelas do PowerShell (Model Loader, FastAPI, Express, Vite)
2. Mantenha-as visíveis
3. Envie uma mensagem no chat
4. Observe os logs aparecerem em tempo real

## 📝 Checklist de Verificação

Quando "SuperEzio está digitando...":

- [ ] Console do navegador mostra `[HF Client] Enviando mensagem...`
- [ ] Python FastAPI mostra `🔵 [REQ #...] Nova requisição recebida`
- [ ] Python FastAPI mostra `⏳ [REQ #...] Iniciando inferência...`
- [ ] Aguardar 5-60 segundos (depende do tamanho da resposta)
- [ ] Python FastAPI mostra `✅ [REQ #...] Inferência concluída`
- [ ] Console do navegador mostra `[HF Client] Resposta recebida em X.Xs`
- [ ] Mensagem aparece no chat

Se algum passo falhar, veja os logs para identificar onde está o problema.

---

*Última atualização: 2025-01-XX*

