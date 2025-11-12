// Rotas da API para o Agente SuperEzio
// Endpoints para operações de sistema

import express, { Request, Response } from 'express';
import { executeTool, AVAILABLE_TOOLS } from './agentTools.js';

const router = express.Router();

// Listar tools disponíveis
router.get('/tools', (req: Request, res: Response) => {
  res.json({ tools: AVAILABLE_TOOLS });
});

// Executar uma tool
router.post('/tools/execute', async (req: Request, res: Response) => {
  const { toolName, parameters, confirmed } = req.body;

  if (!toolName) {
    return res.status(400).json({ error: 'toolName é obrigatório' });
  }

  const result = await executeTool(toolName, parameters || {}, confirmed === true);
  
  if (result.requiresConfirmation) {
    return res.status(202).json({ 
      ...result,
      message: 'Esta ação requer confirmação. Envie novamente com confirmed: true'
    });
  }
  
  if (result.error) {
    return res.status(400).json(result);
  }

  res.json(result);
});

// Buscar arquivos
router.get('/files/search', async (req: Request, res: Response) => {
  const { path: searchPath, pattern } = req.query;
  
  if (!searchPath || !pattern) {
    return res.status(400).json({ error: 'path e pattern são obrigatórios' });
  }

  const result = await executeTool('search_files', {
    searchPath: String(searchPath),
    pattern: String(pattern),
  }, true);

  res.json(result);
});

// Ler arquivo
router.get('/files/read', async (req: Request, res: Response) => {
  const { path: filePath } = req.query;
  
  if (!filePath) {
    return res.status(400).json({ error: 'path é obrigatório' });
  }

  const result = await executeTool('read_file', {
    filePath: String(filePath),
  }, true);

  if (result.error) {
    return res.status(500).json(result);
  }

  res.json(result);
});

// Listar diretório
router.get('/files/list', async (req: Request, res: Response) => {
  const { path: dirPath } = req.query;
  
  if (!dirPath) {
    return res.status(400).json({ error: 'path é obrigatório' });
  }

  const result = await executeTool('list_directory', {
    dirPath: String(dirPath),
  }, true);

  res.json(result);
});

// Email endpoints
router.get('/emails/read', async (req: Request, res: Response) => {
  const { limit, folder } = req.query;
  
  const result = await executeTool('read_emails', {
    limit: limit ? parseInt(String(limit)) : 10,
    folder: folder || 'INBOX',
  }, true);

  res.json(result);
});

router.get('/emails/search', async (req: Request, res: Response) => {
  const { query, limit } = req.query;
  
  if (!query) {
    return res.status(400).json({ error: 'query é obrigatório' });
  }

  const result = await executeTool('search_emails', {
    query: String(query),
    limit: limit ? parseInt(String(limit)) : 10,
  }, true);

  res.json(result);
});

router.get('/emails/unread', async (req: Request, res: Response) => {
  const result = await executeTool('get_unread_count', {}, true);
  res.json(result);
});

export default router;
