import express, { Request, Response, NextFunction } from 'express';
import path from 'path';
import { createProxyMiddleware } from 'http-proxy-middleware';
import compression from 'compression';
import agentRoutes from './server/agentRoutes.js';

// CORS com origens específicas (segurança melhorada - remove wildcard)
// Permite apenas Frontend local (Vite dev:3000, Vite preview:5173)
function cors(req: Request, res: Response, next: NextFunction) {
  const allowedOrigins = [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173'
  ];

  const origin = req.headers.origin;
  if (origin && allowedOrigins.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Access-Control-Allow-Credentials', 'true');
  }

  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
}

const app = express();
const PORT = process.env.PORT || 8080;

app.disable('x-powered-by');
app.use(compression());
app.use(cors);

// JSON parser only for routes that are not proxied
app.use('/api/agent', express.json());
app.use('/api/agent', express.urlencoded({ extended: true }));

// Agent API (filesystem, tools, etc.)
app.use('/api/agent', agentRoutes);

// Logging middleware for /api/hf before the proxy
app.use('/api/hf', (req: Request, res: Response, next: NextFunction) => {
  const startTime = Date.now();
  console.log(`\n[Express] ${new Date().toISOString()} - ${req.method} ${req.url}`);
  
  const timeoutWarning = setInterval(() => {
    const elapsed = Date.now() - startTime;
    if (elapsed > 60000 && !res.headersSent) {
      console.log(`[Express] ⚠️  Requisição ainda processando após ${Math.floor(elapsed/1000)}s...`);
    }
  }, 30000);

  res.on('finish', () => {
    clearInterval(timeoutWarning);
    const elapsed = Date.now() - startTime;
    console.log(`[Express] ✅ Resposta enviada em ${elapsed}ms - Status: ${res.statusCode}`);
  });

  res.on('close', () => {
    clearInterval(timeoutWarning);
  });
  
  next();
});

// Proxy for Python FastAPI (Hugging Face inference)
app.use(
  '/api/hf',
  createProxyMiddleware({
    target: 'http://localhost:8000',
    changeOrigin: true,
    pathRewrite: { '^/api/hf': '' },
    timeout: 300000, // 5 minutes
    proxyTimeout: 300000,
    on: {
      proxyReq: (proxyReq, req, res) => {
        const targetPath = req.url?.replace('/api/hf', '') || '';
        const expressReq = req as Request;
        console.log(`[Express Proxy] Proxying ${req.method} ${req.url} -> http://localhost:8000${targetPath}`);
        if (expressReq.body) {
          const bodyData = JSON.stringify(expressReq.body);
          proxyReq.setHeader('Content-Type', 'application/json');
          proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
          proxyReq.write(bodyData);
        }
      },
      proxyRes: (proxyRes, req, res) => {
        console.log(`[Express Proxy] ✅ Resposta recebida: ${proxyRes.statusCode} ${proxyRes.statusMessage} para ${req.url}`);
      },
      error: (err, req, res) => {
        console.error(`[Express Proxy] ❌ Erro ao fazer proxy para ${req.url}:`, err);
        const expressRes = res as Response;
        if (!expressRes.headersSent) {
          expressRes.status(500).json({ error: `Erro no proxy: ${err.message}` });
        }
      },
    },
  })
);

// Static files from Vite build
const distDir = path.resolve(process.cwd(), 'dist');
app.use(express.static(distDir));

// SPA fallback
app.get('*', (_req: Request, res: Response) => {
  res.sendFile(path.join(distDir, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`🚀 Servidor Node.js rodando em http://localhost:${PORT}`);
  console.log(`   -> Proxy /api/hf para http://localhost:8000 (Python Backend)`);
  console.log(`   -> Rotas /api/agent para ferramentas do agente`);
  console.log(`   -> Servindo frontend de ${distDir}`);
});
