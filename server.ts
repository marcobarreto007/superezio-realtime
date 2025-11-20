import express, { Request, Response, NextFunction } from 'express';
import path from 'path';
import { createProxyMiddleware } from 'http-proxy-middleware';
import compression from 'compression';
import fileUpload from 'express-fileupload';
import agentRoutes from './server/agentRoutes.js';
import ragRoutes from './server/ragRoutes.js';

// CORS configuration
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
app.use(fileUpload()); // Add file upload middleware

// Parsers for non-proxied routes
app.use('/api/agent', express.json());
app.use('/api/agent', express.urlencoded({ extended: true }));
app.use('/api/rag', express.json());
app.use('/api/rag', express.urlencoded({ extended: true }));

// Agent and RAG routes
app.use('/api/agent', agentRoutes);
app.use('/api/rag', ragRoutes);

// Proxy for Python FastAPI
app.use(
  '/api/hf',
  createProxyMiddleware({
    target: 'http://localhost:8000',
    changeOrigin: true,
    pathRewrite: { '^/api/hf': '' },
    timeout: 300000,
    proxyTimeout: 300000,
    on: {
      proxyReq: (proxyReq, req, res) => {
        const expressReq = req as Request;
        console.log(`[Express Proxy] Proxying ${req.method} ${req.url} -> http://localhost:8000${req.url.replace('/api/hf', '')}`);
        
        // Handle multipart/form-data for vision endpoint
        if (req.headers['content-type']?.includes('multipart/form-data')) {
            // express-fileupload handles the parsing, but for proxying,
            // we let http-proxy-middleware forward the raw request body.
            // No need to re-serialize, just let it stream.
            return;
        }

        // Handle standard JSON requests
        if (expressReq.body && Object.keys(expressReq.body).length > 0) {
          const bodyData = JSON.stringify(expressReq.body);
          proxyReq.setHeader('Content-Type', 'application/json');
          proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
          proxyReq.write(bodyData);
        }
      },
      proxyRes: (proxyRes, req, res) => {
        console.log(`[Express Proxy] ✅ Response: ${proxyRes.statusCode} for ${req.url}`);
      },
      error: (err, req, res) => {
        console.error(`[Express Proxy] ❌ Error for ${req.url}:`, err);
        if (!res.headersSent) {
          res.status(500).json({ error: `Proxy error: ${err.message}` });
        }
      },
    },
  })
);

// Static files and SPA fallback
const distDir = path.resolve(process.cwd(), 'dist');
app.use(express.static(distDir));
app.get('*', (_req: Request, res: Response) => {
  res.sendFile(path.join(distDir, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`🚀 Servidor Node.js rodando em http://localhost:${PORT}`);
});
