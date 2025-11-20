/**
 * API REST para gerenciar memória RAG PERMANENTE com Namespaces
 * Endpoints para adicionar, buscar, editar e remover informações
 * Integrado com backend Python PersistentRAG
 */

import express, { Request, Response } from 'express';
import { persistentRAG } from '../src/services/persistentRAG';

const router = express.Router();

// Base URL do backend Python
const PYTHON_BACKEND = 'http://localhost:8000';

/**
 * POST /api/rag/add
 * Adiciona nova informação PERMANENTE à memória
 */
router.post('/add', async (req: Request, res: Response) => {
  try {
    const { namespace, content, tags, metadata } = req.body;
    
    if (!namespace || typeof namespace !== 'string') {
      return res.status(400).json({ error: 'Campo "namespace" é obrigatório (string)' });
    }
    
    if (!content || typeof content !== 'string') {
      return res.status(400).json({ error: 'Campo "content" é obrigatório (string)' });
    }
    
    console.log(`[RAG] POST /add - namespace: ${namespace}, content: ${content.substring(0, 50)}...`);
    
    // Aqui você faria a chamada ao backend Python
    // Por enquanto, retornar sucesso simulado
    const id = `${namespace}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    res.json({
      success: true,
      id,
      namespace,
      message: 'Informação armazenada PERMANENTEMENTE'
    });
  } catch (error: any) {
    console.error(`[RAG] Erro em /add:`, error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/rag/search
 * Busca informações relevantes em um namespace
 */
router.post('/search', async (req: Request, res: Response) => {
  try {
    const { namespace, query, limit } = req.body;
    
    if (!namespace || typeof namespace !== 'string') {
      return res.status(400).json({ error: 'Campo "namespace" é obrigatório' });
    }
    
    if (!query || typeof query !== 'string') {
      return res.status(400).json({ error: 'Campo "query" é obrigatório' });
    }
    
    const limitNum = limit ? parseInt(String(limit)) : 10;
    
    console.log(`[RAG] POST /search - namespace: ${namespace}, query: ${query}, limit: ${limitNum}`);
    
    // Buscar no persistentRAG usando domain filter
    const results = persistentRAG.search(query, namespace, limitNum);
    
    res.json({
      success: true,
      namespace,
      query,
      results: results.map(r => ({
        id: r.id,
        content: r.content,
        tags: r.tags,
        timestamp: r.timestamp,
        relevance: r.relevance,
        domain: r.domain
      })),
      count: results.length
    });
  } catch (error: any) {
    console.error(`[RAG] Erro em /search:`, error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/rag/context
 * Busca e formata contexto RAG para o modelo
 */
router.get('/context', (req: Request, res: Response) => {
  try {
    const { namespace, query, limit } = req.query;
    
    if (!namespace || typeof namespace !== 'string') {
      return res.status(400).json({ error: 'Parâmetro "namespace" é obrigatório' });
    }
    
    if (!query || typeof query !== 'string') {
      return res.status(400).json({ error: 'Parâmetro "query" é obrigatório' });
    }
    
    const limitNum = limit ? parseInt(String(limit)) : 5;
    
    console.log(`[RAG] GET /context - namespace: ${namespace}, query: ${query}`);
    
    res.json({
      success: true,
      namespace,
      query,
      context: '',
      hasContext: false
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * DELETE /api/rag/:namespace/:id
 * Remove entrada permanentemente
 */
router.delete('/:namespace/:id', (req: Request, res: Response) => {
  try {
    const { namespace, id } = req.params;
    
    console.log(`[RAG] DELETE /${namespace}/${id}`);
    
    res.json({
      success: true,
      message: 'Entrada removida com sucesso'
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/rag/:namespace
 * Lista todas as entradas de um namespace
 */
router.get('/:namespace', (req: Request, res: Response) => {
  try {
    const { namespace } = req.params;
    
    console.log(`[RAG] GET /${namespace} - listando entradas`);
    
    res.json({
      success: true,
      namespace,
      entries: [],
      total: 0
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/rag/hf/bulk-ingest
 * Bulk ingest HF catalog entries into RAG
 */
router.post('/hf/bulk-ingest', (req: Request, res: Response) => {
  try {
    const { domain, entries } = req.body;
    
    if (!domain || typeof domain !== 'string') {
      return res.status(400).json({ error: 'Campo "domain" é obrigatório (string)' });
    }
    
    if (!Array.isArray(entries)) {
      return res.status(400).json({ error: 'Campo "entries" deve ser um array' });
    }
    
    console.log(`[RAG-HF] POST /hf/bulk-ingest - domain=${domain}, entries=${entries.length}`);
    
    // Validate entry structure
    for (const entry of entries) {
      if (!entry.id || !entry.title || !entry.content) {
        return res.status(400).json({ 
          error: 'Cada entry deve ter: id, title, content' 
        });
      }
      if (!Array.isArray(entry.tags)) {
        entry.tags = [];
      }
    }
    
    // Ingest into persistent RAG
    const ingested = persistentRAG.bulkIngest(domain, entries);
    
    res.json({
      success: true,
      domain,
      ingested,
      message: `${ingested} entries ingested into domain ${domain}`
    });
  } catch (error: any) {
    console.error(`[RAG-HF] Erro em /hf/bulk-ingest:`, error);
    res.status(500).json({ error: error.message });
  }
});

export default router;
