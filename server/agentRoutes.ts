// Rotas da API para o Agente SuperEzio
// Endpoints para operações de sistema

import express from 'express';
import { executeTool, AVAILABLE_TOOLS, ToolExecution } from './agentTools.js';

const router = express.Router();

// Listar tools disponíveis
router.get('/tools', (req, res) => {
  res.json({ tools: AVAILABLE_TOOLS });
});

// Executar uma tool
router.post('/tools/execute', async (req, res) => {
  const { toolName, parameters, confirmed } = req.body;

  if (!toolName) {
    return res.status(400).json({ error: 'toolName é obrigatório' });
  }

  const result = await executeTool(toolName, parameters || {}, confirmed === true);
  
  if (result.error && result.error.includes('Confirmação necessária')) {
    return res.status(202).json({ 
      ...result,
      requiresConfirmation: true,
      message: 'Esta ação requer confirmação. Envie novamente com confirmed: true'
    });
  }

  res.json(result);
});

// Buscar arquivos
router.get('/files/search', async (req, res) => {
  const { path: searchPath, pattern } = req.query;
  
  if (!searchPath || !pattern) {
    return res.status(400).json({ error: 'path e pattern são obrigatórios' });
  }

  const result = await executeTool('search_files', {
    searchPath: searchPath as string,
    pattern: pattern as string,
  }, true);

  res.json(result);
});

// Ler arquivo
router.get('/files/read', async (req, res) => {
  const { path: filePath } = req.query;
  
  if (!filePath) {
    return res.status(400).json({ error: 'path é obrigatório' });
  }

  const result = await executeTool('read_file', {
    filePath: filePath as string,
  }, true);

  if (result.error) {
    return res.status(500).json(result);
  }

  res.json(result);
});

// Listar diretório
router.get('/files/list', async (req, res) => {
  const { path: dirPath } = req.query;
  
  if (!dirPath) {
    return res.status(400).json({ error: 'path é obrigatório' });
  }

  const result = await executeTool('list_directory', {
    dirPath: dirPath as string,
  }, true);

  res.json(result);
});

export default router;

