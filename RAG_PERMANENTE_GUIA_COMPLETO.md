# 🧠 SISTEMA RAG COM PERSISTÊNCIA PERMANENTE

## ✅ O QUE FOI IMPLEMENTADO

Sistema completo de armazenamento RAG (Retrieval-Augmented Generation) com **persistência permanente em disco**.

### Funcionalidades

1. **Armazenamento PERMANENTE** 💾
   - Informações salvas em `data/rag_memory.json`
   - Persistem entre reinicializações
   - Nunca são perdidas

2. **Busca Semântica** 🔍
   - Busca por palavras-chave
   - Cálculo de relevância
   - Filtro por tags

3. **Sistema de Tags** 🏷️
   - Organização por categorias
   - Busca eficiente
   - Metadados customizados

4. **API REST Completa** 🌐
   - Adicionar informações
   - Buscar
   - Atualizar
   - Remover
   - Importar/Exportar

---

## 📁 ARQUIVOS CRIADOS

### 1. `src/services/persistentRAG.ts`
**Serviço principal de persistência**

```typescript
// Singleton global
import { persistentRAG } from './src/services/persistentRAG.js';

// Adicionar informação
const id = persistentRAG.addMemory(
  'Rapha estuda na UdeM',
  ['familia', 'rapha', 'educacao'],
  { pessoa: 'Rapha' }
);

// Buscar
const results = persistentRAG.search('universidade Rapha', 5);

// Criar contexto RAG
const context = persistentRAG.buildRagContext('Quem é o Rapha?', 3);
```

### 2. `server/ragRoutes.ts`
**API REST para gerenciar memória**

Endpoints disponíveis (todos em `/api/rag`):
- `POST /add` - Adicionar informação
- `GET /search?query=...` - Buscar
- `GET /context?query=...` - Obter contexto formatado
- `GET /:id` - Buscar por ID
- `GET /tags/:tags` - Buscar por tags
- `PUT /:id` - Atualizar
- `DELETE /:id` - Remover
- `GET /` - Listar todas
- `GET /stats/summary` - Estatísticas
- `POST /import` - Importar JSON
- `GET /export/all` - Exportar tudo

### 3. `test_persistent_rag.ts`
**Teste demonstrativo completo**

---

## 🚀 COMO USAR

### 1. Via TypeScript (Interno)

```typescript
import { persistentRAG } from './src/services/persistentRAG.js';

// ADICIONAR
const id = persistentRAG.addMemory(
  'Marco é empresário especialista em CRA',
  ['familia', 'marco', 'profissional']
);

// BUSCAR
const results = persistentRAG.search('Marco trabalho', 10);
console.log(`${results.length} resultados encontrados`);

// CONTEXTO RAG
const context = persistentRAG.buildRagContext('O que o Marco faz?', 5);
// Retorna string formatada para injetar no prompt do modelo
```

### 2. Via API REST

#### Adicionar Informação
```bash
curl -X POST http://localhost:8080/api/rag/add \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Rapha é FÃ FANÁTICO dos Edmonton Oilers",
    "tags": ["rapha", "hobbies", "esportes"],
    "metadata": { "pessoa": "Rapha" }
  }'
```

**Resposta:**
```json
{
  "success": true,
  "id": "mem_1731456789_abc123xyz",
  "message": "Informação armazenada PERMANENTEMENTE"
}
```

#### Buscar Informações
```bash
curl "http://localhost:8080/api/rag/search?query=Rapha%20universidade&limit=5"
```

**Resposta:**
```json
{
  "success": true,
  "query": "Rapha universidade",
  "results": [
    {
      "id": "mem_...",
      "content": "Rapha estuda na UdeM...",
      "timestamp": 1731456789000,
      "tags": ["familia", "rapha", "educacao"],
      "relevance": 0.85
    }
  ],
  "total": 1
}
```

#### Obter Contexto RAG Formatado
```bash
curl "http://localhost:8080/api/rag/context?query=Quem%20é%20o%20Rapha&limit=3"
```

**Resposta:**
```json
{
  "success": true,
  "query": "Quem é o Rapha",
  "context": "[RAG CONTEXT - Informações Relevantes]\n\n[1] (Relevância: 100%)\nRapha BARRETO é filho do Marco...\n\n[FIM DO CONTEXTO RAG]",
  "hasContext": true
}
```

#### Listar Todas as Entradas
```bash
curl "http://localhost:8080/api/rag/"
```

#### Buscar por Tags
```bash
curl "http://localhost:8080/api/rag/tags/rapha,hobbies"
```

#### Atualizar Entrada
```bash
curl -X PUT http://localhost:8080/api/rag/mem_1731456789_abc123xyz \
  -H "Content-Type: application/json" \
  -d '{
    "content": "CONTEÚDO ATUALIZADO",
    "tags": ["nova", "tag"]
  }'
```

#### Remover Entrada
```bash
curl -X DELETE http://localhost:8080/api/rag/mem_1731456789_abc123xyz
```

#### Estatísticas
```bash
curl "http://localhost:8080/api/rag/stats/summary"
```

**Resposta:**
```json
{
  "success": true,
  "stats": {
    "totalEntries": 25,
    "totalTags": 12,
    "oldestEntry": 1731456789000,
    "newestEntry": 1731456999000
  }
}
```

#### Exportar Tudo
```bash
curl "http://localhost:8080/api/rag/export/all" -o rag_backup.json
```

#### Importar de JSON
```bash
curl -X POST http://localhost:8080/api/rag/import \
  -H "Content-Type: application/json" \
  -d @rag_backup.json
```

---

## 🔄 INTEGRAÇÃO COM O MODELO

### Fluxo Completo RAG

```typescript
// 1. Usuário faz pergunta
const userQuestion = "Qual universidade o Rapha estuda?";

// 2. Buscar contexto relevante
const ragContext = persistentRAG.buildRagContext(userQuestion, 5);

// 3. Enviar para o modelo com contexto
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [
      {
        role: 'user',
        content: userQuestion,
        rag_context: ragContext  // ← CONTEXTO INJETADO AQUI
      }
    ]
  })
});

// 4. Modelo responde usando o contexto RAG
const result = await response.json();
console.log(result.content);
// "Rapha estuda na Université de Montréal (UdeM)..."
```

---

## 🧪 TESTAR O SISTEMA

### 1. Rodar teste demonstrativo

```bash
# Compilar TypeScript
npx tsc test_persistent_rag.ts --module es2022 --moduleResolution node --target es2022

# Executar teste
node test_persistent_rag.js
```

### 2. Verificar arquivo persistente

```bash
# Windows
type data\rag_memory.json

# Linux/Mac
cat data/rag_memory.json
```

### 3. Testar API (servidor deve estar rodando)

```bash
# Iniciar servidor
npx tsx server.ts

# Em outro terminal, testar endpoints
curl "http://localhost:8080/api/rag/stats/summary"
```

---

## 📊 ESTRUTURA DOS DADOS

### Formato de Entrada no Disco

**Arquivo:** `data/rag_memory.json`

```json
[
  {
    "id": "mem_1731456789_abc123xyz",
    "content": "Rapha BARRETO é filho do Marco. Universitário na UdeM...",
    "timestamp": 1731456789000,
    "tags": ["familia", "rapha", "educacao"],
    "metadata": {
      "pessoa": "Rapha",
      "categoria": "perfil"
    }
  },
  {
    "id": "mem_1731456790_def456uvw",
    "content": "Marco BARRETO é o pai do Rapha. Empresário...",
    "timestamp": 1731456790000,
    "tags": ["familia", "marco", "profissional"],
    "metadata": {
      "pessoa": "Marco",
      "categoria": "perfil"
    }
  }
]
```

### Interface TypeScript

```typescript
interface PermanentMemoryEntry {
  id: string;              // Único identificador
  content: string;         // Conteúdo da informação
  timestamp: number;       // Unix timestamp (ms)
  tags: string[];          // Tags para categorização
  metadata?: Record<string, any>;  // Metadados customizados
}

interface SearchResult extends PermanentMemoryEntry {
  relevance: number;       // Score de relevância (0-1)
}
```

---

## ⚙️ CONFIGURAÇÃO

### Capacidade de Armazenamento

Atualmente **ilimitado** - todas as entradas são mantidas.

Se quiser limitar:

```typescript
// Em persistentRAG.ts
private readonly MAX_ENTRIES = 1000;  // Máximo de entradas

addMemory(...) {
  // Adicionar lógica de limpeza
  if (this.memory.size >= this.MAX_ENTRIES) {
    // Remover as mais antigas
    const entries = Array.from(this.memory.entries());
    entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
    const toRemove = entries.slice(0, 100);  // Remover 100 mais antigas
    toRemove.forEach(([id]) => this.memory.delete(id));
  }
  
  // ... resto do código
}
```

### Localização do Arquivo

Padrão: `data/rag_memory.json` (relativo ao diretório do projeto)

Para mudar:

```typescript
// Em persistentRAG.ts constructor
this.memoryFilePath = join(process.cwd(), 'data', 'rag_memory.json');
// Mudar para:
this.memoryFilePath = 'C:/caminho/customizado/memoria.json';
```

---

## 🔐 SEGURANÇA E BACKUP

### Backup Automático

```bash
# Criar backup diário (adicionar ao cron/task scheduler)
curl "http://localhost:8080/api/rag/export/all" -o "backup_$(date +%Y%m%d).json"
```

### Restauração

```bash
# Restaurar de backup
curl -X POST http://localhost:8080/api/rag/import \
  -H "Content-Type: application/json" \
  -d @backup_20251112.json
```

### Limpeza de Dados Antigos

```typescript
// Script de limpeza
const entries = persistentRAG.listAll();
const oneYearAgo = Date.now() - (365 * 24 * 60 * 60 * 1000);

entries.forEach(entry => {
  if (entry.timestamp < oneYearAgo) {
    persistentRAG.remove(entry.id);
  }
});
```

---

## 📈 EXEMPLOS DE USO

### Caso 1: Perfil de Família

```typescript
// Adicionar informações sobre cada membro
persistentRAG.addMemory(
  'Rapha: filho, 21 anos, UdeM, Direito, Edmonton Oilers fan',
  ['familia', 'rapha']
);

persistentRAG.addMemory(
  'Marco: pai, empresário, CRA expert, Montreal',
  ['familia', 'marco']
);

// Buscar quando necessário
const context = persistentRAG.buildRagContext('Fale sobre a família', 5);
```

### Caso 2: Base de Conhecimento de CRA

```typescript
// Adicionar regras e informações sobre CRA
persistentRAG.addMemory(
  'CRA: Canada Revenue Agency. Prazo T1: 30 de abril. T4 enviado por empregadores.',
  ['cra', 'impostos', 'prazos']
);

persistentRAG.addMemory(
  'RRSP: Registered Retirement Savings Plan. Limite 18% do salário.',
  ['cra', 'aposentadoria', 'rrsp']
);

// Buscar informações específicas
const info = persistentRAG.search('prazo declaração imposto', 5, ['cra']);
```

### Caso 3: Histórico de Conversas

```typescript
// Salvar pontos importantes de conversas
persistentRAG.addMemory(
  'Rapha mencionou interesse em fazer estágio na PwC no verão de 2025',
  ['rapha', 'carreira', 'planos'],
  { data: '2024-11-12', contexto: 'conversa sobre futuro' }
);

// Recuperar em conversas futuras
const memories = persistentRAG.search('Rapha estágio trabalho', 10);
```

---

## ✅ PRÓXIMOS PASSOS (Opcional)

### 1. Embeddings Vetoriais (Busca Mais Inteligente)

```bash
npm install @xenova/transformers
```

```typescript
// Usar modelos de embedding para busca semântica real
import { pipeline } from '@xenova/transformers';

const embedder = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');

// Gerar embedding ao adicionar
const embedding = await embedder(content);
entry.embedding = Array.from(embedding.data);

// Busca por similaridade de cosseno
```

### 2. ChromaDB (Banco Vetorial)

```bash
npm install chromadb
```

```typescript
// Usar ChromaDB para busca vetorial eficiente
import { ChromaClient } from 'chromadb';
```

### 3. Interface Web para Gerenciar Memórias

Criar componente React:
- Listar todas as memórias
- Adicionar nova
- Editar existente
- Buscar e filtrar
- Visualizar estatísticas

---

## 🎯 RESUMO

✅ **Sistema RAG permanente implementado**
- Armazenamento em `data/rag_memory.json`
- API REST completa em `/api/rag`
- Busca por palavras-chave e tags
- Integração com backend de inferência
- Exportação e importação de dados
- Testes demonstrativos incluídos

🔄 **Fluxo de uso:**
1. Adicionar informações via API ou código
2. Informações salvas PERMANENTEMENTE no disco
3. Buscar contexto relevante para cada pergunta
4. Injetar contexto no prompt do modelo
5. Modelo responde usando informações armazenadas

💾 **Persistência garantida:**
- Arquivo JSON no disco
- Carregamento automático no startup
- Salvamento imediato após cada modificação
- Nunca perde dados entre reinicializações

🚀 **Pronto para uso em produção!**
