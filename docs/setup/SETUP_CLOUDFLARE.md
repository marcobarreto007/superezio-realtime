# 🚀 Setup Cloudflare Tunnel - SuperEzio

## **O Que Vai Acontecer:**

```
Frontend (cPanel) → https://teudominio.com
Backend (Tua RTX 3060) → https://api.teudominio.com → Cloudflare Tunnel → localhost:8000
```

---

## **PASSO 1: Instalar Cloudflared**

### Windows:
```bash
winget install Cloudflare.cloudflared
```

### Verificar instalação:
```bash
cloudflared --version
```

---

## **PASSO 2: Login Cloudflare**

```bash
cloudflared tunnel login
```

Isso vai:
1. Abrir browser automaticamente
2. Pedir pra logar no Cloudflare (já tá logado)
3. Escolher domínio (escolhe o teu)
4. Autorizar cloudflared

**Resultado:** Certificado salvo em `C:\Users\marco\.cloudflared\cert.pem`

---

## **PASSO 3: Criar Tunnel**

```bash
cloudflared tunnel create superezio
```

**Output esperado:**
```
Created tunnel superezio with id abc-123-def-456-789
Tunnel credentials written to C:\Users\marco\.cloudflared\abc-123-def-456-789.json
```

**🔴 IMPORTANTE:** Copia esse ID! Vai precisar dele.

---

## **PASSO 4: Configurar DNS**

Substitui `teudominio.com` pelo teu domínio real:

```bash
cloudflared tunnel route dns superezio api.teudominio.com
```

**Exemplo prático:**
```bash
# Se teu domínio é "barreto.tech"
cloudflared tunnel route dns superezio api.barreto.tech
```

**O que isso faz:**
- Cria registro CNAME no Cloudflare automaticamente
- `api.teudominio.com` → `abc-123.cfargotunnel.com`
- Ativa proxy Cloudflare (DDoS protection)

**Verificar no Dashboard Cloudflare:**
1. Vai em **DNS** → **Records**
2. Deve ter um registro CNAME:
   ```
   Tipo: CNAME
   Nome: api
   Conteúdo: abc-123-def-456.cfargotunnel.com
   Proxy: ON (nuvem laranja 🟧)
   ```

---

## **PASSO 5: Editar Config File**

Abre `cloudflared-config.yml` e atualiza 2 coisas:

```yaml
tunnel: superezio
credentials-file: C:\Users\marco\.cloudflared\SEU_TUNNEL_ID_AQUI.json  # ← Muda isso

ingress:
  - hostname: api.teudominio.com  # ← Muda isso pro teu domínio
    service: http://localhost:8000
    originRequest:
      noTLSVerify: true
  - service: http_status:404

logDirectory: C:\Users\marco\Superezio Realtime\logs
```

**Exemplo preenchido:**
```yaml
tunnel: superezio
credentials-file: C:\Users\marco\.cloudflared\abc-123-def-456-789.json
ingress:
  - hostname: api.barreto.tech
    service: http://localhost:8000
    originRequest:
      noTLSVerify: true
  - service: http_status:404
```

---

## **PASSO 6: Testar Tunnel**

### Testar manualmente:

```bash
# Terminal 1: Backend
cd backend
python api.py

# Terminal 2: Tunnel
cloudflared tunnel --config cloudflared-config.yml run
```

### Ou usar script automático:

```bash
start_backend_tunnel.bat
```

**Output esperado:**
```
[OK] Backend rodando em http://localhost:8000
[OK] Cloudflare Tunnel conectado
[OK] https://api.teudominio.com → localhost:8000
```

---

## **PASSO 7: Configurar Frontend**

Edita `.env.production`:

```bash
# .env.production
VITE_API_URL=https://api.teudominio.com
```

**Exemplo:**
```bash
VITE_API_URL=https://api.barreto.tech
```

Build:
```bash
npm run build
```

Upload `dist/` pro cPanel.

---

## **PASSO 8: Testar End-to-End**

1. Abre `https://teudominio.com` (frontend no cPanel)
2. Envia mensagem no chat
3. Abre DevTools (F12) → Console
4. Deve aparecer:
   ```
   🚀 [APIClient] Inicializado
   📍 [APIClient] Base URL: https://api.teudominio.com/api/hf
   📤 [APIClient] Iniciando streaming
   ```

---

## **Troubleshooting**

### **Erro: "tunnel credentials file not found"**
→ Edita `cloudflared-config.yml` com o ID correto do tunnel

### **Erro: "no such tunnel"**
→ Roda `cloudflared tunnel list` pra ver o nome correto

### **Erro: "origin returned 502"**
→ Backend não tá rodando. Inicia `python backend/api.py`

### **Ver logs do tunnel:**
```bash
cloudflared tunnel --loglevel debug --config cloudflared-config.yml run
```

### **Listar tunnels existentes:**
```bash
cloudflared tunnel list
```

### **Deletar tunnel (se errou):**
```bash
cloudflared tunnel delete superezio
```

---

## **Rodar Automático no Boot (Opcional)**

### Criar serviço Windows:

```bash
cloudflared service install cloudflared-config.yml
```

Isso faz o tunnel iniciar automaticamente com Windows.

---

## **Checklist Final**

- [ ] cloudflared instalado (`winget install Cloudflare.cloudflared`)
- [ ] Login feito (`cloudflared tunnel login`)
- [ ] Tunnel criado (`cloudflared tunnel create superezio`)
- [ ] DNS configurado (`cloudflared tunnel route dns superezio api.teudominio.com`)
- [ ] `cloudflared-config.yml` editado (tunnel ID + domínio)
- [ ] Backend rodando (`python backend/api.py`)
- [ ] Tunnel rodando (`cloudflared tunnel run`)
- [ ] `.env.production` configurado com domínio
- [ ] Frontend buildado e no cPanel
- [ ] Testado no browser (F12 console)

---

## **Performance Esperada**

**Latência:**
- User → Cloudflare CDN: ~10-30ms
- Cloudflare → Tua máquina: ~20-50ms
- Backend processing: ~500-2000ms (LLM)

**Total:** 1-2.5 segundos por resposta

**Vantagens Cloudflare:**
- ✅ DDoS protection
- ✅ Web Application Firewall (WAF)
- ✅ HTTPS automático
- ✅ Cache inteligente
- ✅ Não expõe teu IP
- ✅ Funciona atrás de qualquer firewall

---

**Qualquer dúvida, me avisa!**
