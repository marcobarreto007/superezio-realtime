import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { createProxyMiddleware } from 'http-proxy-middleware';
import compression from 'compression';

// Basic CORS for browser calls from remote origins
function cors(req, res, next) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 8080;
const OLLAMA_TARGET = process.env.OLLAMA_BASE_URL || 'http://127.0.0.1:11434';

app.disable('x-powered-by');
app.use(compression());
app.use(cors);

// Proxy for Ollama API (keeps same path under /api/*)
app.use(
  '/ollama',
  createProxyMiddleware({
    target: OLLAMA_TARGET,
    changeOrigin: true,
    pathRewrite: { '^/ollama': '' },
    ws: true,
    onProxyReq: (proxyReq) => {
      // Ensure JSON default
      if (!proxyReq.getHeader('content-type')) {
        proxyReq.setHeader('content-type', 'application/json');
      }
    },
  })
);

// Static files from Vite build
const distDir = path.resolve(__dirname, 'dist');
app.use(express.static(distDir));

// SPA fallback
app.get('*', (_req, res) => {
  res.sendFile(path.join(distDir, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Proxying /ollama -> ${OLLAMA_TARGET}`);
});
