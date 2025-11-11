<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://ai.studio/apps/drive/1fuoayGBD22BfX6hsa41qD-ILAqNmNEcr

## Run Locally

**Prerequisites:**  Node.js


1. Install dependencies:
   `npm install`
2. Choose provider in [.env.local](.env.local):
   - For Gemini (cloud): set `MODEL_PROVIDER=gemini` and `GEMINI_API_KEY=...`
   - For Ollama (local): set `MODEL_PROVIDER=ollama`, optionally `OLLAMA_MODEL=qwen2.5:7b-instruct` and `OLLAMA_BASE_URL=http://localhost:11434`
3. Dev (hot reload):
   `npm run dev`

4. Production preview (build + server com proxy /ollama):
   - `npm run build`
   - `npm start`
   - Acesse `http://localhost:8080` (proxy ativo em `/ollama`).

## Deploy (uma VM simples)
1) Instale Node 18+ e Ollama na mesma VM.
2) Configure envs (ex.: `.env` do shell ou serviço systemd):
   - `PORT=8080`
   - `MODEL_PROVIDER=ollama`
   - `OLLAMA_BASE_URL=http://127.0.0.1:11434`
   - `OLLAMA_MODEL=qwen2.5:7b-instruct`
   - `EMBEDDING_MODEL=nomic-embed-text:latest`
3) Build estático: `npm ci && npm run build`.
4) Rode o server: `npm start` (serve `dist/` e proxy `/ollama`).
5) (Opcional) Coloque Nginx na frente com TLS e reverse-proxy para `http://127.0.0.1:8080`.

### Trecho Nginx (opcional)
```
server {
  listen 80;
  server_name app.seudominio.com;

  location / {
    proxy_pass http://127.0.0.1:8080;
  }
}

server {
  listen 80;
  server_name api.seudominio.com;

  location /ollama/ {
    proxy_pass http://127.0.0.1:11434/;
    proxy_set_header Host $host;
  }
}
```
