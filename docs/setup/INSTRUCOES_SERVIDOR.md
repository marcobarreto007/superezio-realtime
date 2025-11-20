# 🚀 Como Rodar o SuperEzio Completo

## ⚠️ IMPORTANTE

O SuperEzio precisa de **2 servidores rodando**:

1. **Vite** (frontend) - porta 3000
2. **Express** (API do agente) - porta 8080

---

## 🎯 OPÇÃO 1: Rodar Tudo de Uma Vez (RECOMENDADO)

```bash
npm run dev:full
```

Isso roda ambos os servidores simultaneamente.

---

## 🎯 OPÇÃO 2: Rodar Separadamente

### Terminal 1 - API do Agente:
```bash
npm run serve
```
Roda na porta **8080**

### Terminal 2 - Frontend:
```bash
npm run dev
```
Roda na porta **3000**

---

## ✅ VERIFICAÇÃO

Após iniciar, verifique:

1. **API do Agente:**
   ```
   http://localhost:8080/api/agent/tools
   ```
   Deve retornar lista de tools

2. **Frontend:**
   ```
   http://localhost:3000
   ```
   Deve abrir a interface do SuperEzio

---

## 🔧 CONFIGURAÇÃO

O Vite está configurado para fazer proxy:
- `/api/*` → `http://localhost:8080/api/*`
- `/ollama/*` → `http://localhost:11434/*`

Isso permite que o frontend acesse a API mesmo rodando em portas diferentes.

---

## 🐛 TROUBLESHOOTING

**Erro: "Cannot connect to API"**
- Verifique se `server.mjs` está rodando na porta 8080
- Verifique se não há outro processo usando a porta 8080

**Erro: "Port 3000 already in use"**
- Pare outros processos Node.js
- Ou mude a porta no `vite.config.ts`

**API não responde:**
- Verifique logs do `server.mjs`
- Teste diretamente: `curl http://localhost:8080/api/agent/tools`

---

*Criado em 2025-11-12*

