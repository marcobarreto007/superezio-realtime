# 🚀 Deploy SuperEzio - Frontend no cPanel + Backend Local

## **Arquitetura**

```
cPanel (public_html/)
└── Frontend React (dist/) → HTTPS público

Tua Máquina (RTX 3060)
└── Backend Python + GPU → Exposto via Ngrok/IP
```

---

## **PARTE 1: Expor Backend (Tua Máquina)**

### **Opção A: Ngrok (MAIS FÁCIL)**

1. Baixa Ngrok: https://ngrok.com/download
2. Cria conta grátis (free tier)
3. Roda backend:
   ```bash
   cd backend
   python api.py
   ```
4. Em outro terminal:
   ```bash
   ngrok http 8000
   ```
5. Copia a URL (ex: `https://abc123.ngrok.io`)

**Pros:** Setup em 2 min, HTTPS grátis, funciona atrás de firewall
**Cons:** URL muda se reiniciar (free tier), latência +50ms

### **Opção B: IP Fixo + Roteador**

1. Pega teu IP público: https://whatismyipaddress.com
2. No roteador, faz port forwarding:
   - Porta externa: `8000`
   - IP interno: `192.168.X.X` (teu PC)
   - Porta interna: `8000`
3. Backend fica em: `http://TEU_IP:8000`

**Pros:** Sem middleman, latência baixa
**Cons:** IP pode mudar, precisa config roteador, sem HTTPS (precisa Cloudflare)

---

## **PARTE 2: Configurar Frontend**

### **1. Editar `.env.production`**

```bash
# .env.production
VITE_API_URL=https://abc123.ngrok.io
# OU
VITE_API_URL=http://SEU_IP:8000
```

### **2. Build do Frontend**

```bash
npm run build
```

Isso gera pasta `dist/` com:
- `index.html`
- `assets/` (JS, CSS, imagens)

---

## **PARTE 3: Upload no cPanel**

### **Método A: File Manager (GUI)**

1. No cPanel → File Manager
2. Vai em `public_html/` (ou `public_html/superezio/`)
3. Deleta conteúdo antigo (se houver)
4. Upload tudo de `dist/`:
   - `index.html`
   - `assets/` (pasta inteira)

### **Método B: Git no cPanel (RECOMENDADO)**

1. No cPanel → Git Version Control → Create
   - **Clone URL:** `https://github.com/marcobarreto007/superezio-realtime.git`
   - **Repository Path:** `/home/SEU_USER/superezio-realtime`
   - **Branch:** `main`

2. SSH no cPanel (ou Terminal):
   ```bash
   cd ~/superezio-realtime
   git pull
   npm install
   npm run build

   # Copiar dist/ pro public_html
   rm -rf ~/public_html/superezio/*
   cp -r dist/* ~/public_html/superezio/
   ```

3. Criar script `deploy.sh`:
   ```bash
   #!/bin/bash
   cd ~/superezio-realtime
   git pull
   npm run build
   rm -rf ~/public_html/superezio/*
   cp -r dist/* ~/public_html/superezio/
   echo "✅ Deploy completo!"
   ```

   Próximos deploys:
   ```bash
   bash ~/superezio-realtime/deploy.sh
   ```

---

## **PARTE 4: CORS no Backend**

Teu backend precisa aceitar requests do domínio do cPanel.

Edita `backend/api.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://teudominio.com",  # Domínio do cPanel
        "http://localhost:3000",   # Dev local
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## **PARTE 5: Testar**

1. Abre `https://teudominio.com/superezio` no browser
2. Abre DevTools (F12) → Console
3. Envia mensagem no chat
4. Deve aparecer logs tipo:
   ```
   🚀 [APIClient] Inicializado
   📍 [APIClient] Base URL: https://abc123.ngrok.io/api/hf
   📤 [APIClient] Iniciando streaming
   ```

---

## **Troubleshooting**

### **Erro: CORS blocked**
→ Verifica CORS no `backend/api.py` (Parte 4)

### **Erro: Failed to fetch**
→ Backend não tá rodando ou URL errada no `.env.production`

### **Build com URL errada**
→ Edita `.env.production`, deleta `dist/`, roda `npm run build` de novo

### **Ngrok parou**
→ URL muda se reiniciar. Pega nova URL, atualiza `.env.production`, rebuild, re-upload

---

## **Checklist Final**

- [ ] Backend rodando na tua máquina (`python backend/api.py`)
- [ ] Ngrok expondo porta 8000 (ou port forward configurado)
- [ ] `.env.production` com URL correta
- [ ] `npm run build` sem erros
- [ ] CORS configurado no backend
- [ ] `dist/` upado no `public_html/` do cPanel
- [ ] Testado no browser (F12 console sem erros)

---

## **Performance**

**Latência esperada:**
- Frontend (cPanel) → User: ~50ms (CDN)
- User → Backend (Ngrok): ~100-200ms (Ngrok overhead)
- User → Backend (IP direto): ~30-80ms (depende do ISP)
- Geração LLM: ~500-2000ms (depende do modelo)

**Total:** 1-3 segundos por resposta

---

**Quando terminar deploy, avisa que eu verifico se tá tudo ok!**
