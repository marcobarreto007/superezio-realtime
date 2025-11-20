# 🔬 Pesquisa: Novas Técnicas de RAG (2024-2025)

## Técnicas Identificadas para Melhorar RAG

### 1. **Adaptive Retrieval** 🎯
**Conceito**: Ajusta dinamicamente o número de chunks recuperados baseado na complexidade da query.

**Implementação Sugerida**:
- Query simples → top_k=3
- Query complexa → top_k=10
- Query com múltiplas partes → top_k=15

**Benefício**: Reduz ruído em queries simples, aumenta recall em queries complexas.

---

### 2. **Query Rewriting** ✍️
**Conceito**: Reescreve a query do usuário para melhorar recuperação antes de buscar.

**Técnicas**:
- **Decomposição**: "Como funciona X e Y?" → ["Como funciona X?", "Como funciona Y?"]
- **Expansão**: "criar API" → "criar API REST FastAPI Python"
- **Clarificação**: "isso" → substituir por contexto anterior

**Benefício**: Melhora precisão da busca em 20-30%.

---

### 3. **Reranking Avançado** 📊
**Conceito**: Usa modelo de reranking dedicado para ordenar resultados.

**Técnicas**:
- **Cross-encoder**: Modelo que compara query + chunk simultaneamente
- **Multi-stage**: Primeiro BM25/keyword, depois rerank semântico
- **Diversity**: Garantir diversidade nos resultados (não só top score)

**Benefício**: Melhora precisão em 15-25%.

---

### 4. **Contextual Compression** 🗜️
**Conceito**: Comprime contexto mantendo apenas informação relevante.

**Técnicas**:
- **Extractive**: Extrai apenas sentenças relevantes
- **Abstractive**: Resume chunks mantendo informação chave
- **Selective**: Remove redundâncias e informações não relacionadas

**Benefício**: Reduz tokens em 40-60% mantendo qualidade.

---

### 5. **Hybrid Search Melhorado** 🔍
**Conceito**: Combina busca vetorial + keyword + grafo de forma inteligente.

**Técnicas**:
- **Reciprocal Rank Fusion**: Combina rankings de diferentes métodos
- **Weighted Fusion**: Pesos dinâmicos baseados no tipo de query
- **Graph + Vector**: Usa Graph RAG + busca vetorial simultaneamente

**Benefício**: Melhora recall em 30-40%.

---

### 6. **Self-RAG** 🤖
**Conceito**: Modelo decide quando buscar, o que buscar e como usar.

**Técnicas**:
- **Retrieval Decision**: Modelo decide se precisa buscar
- **Passage Selection**: Modelo escolhe quais chunks usar
- **Generation with Retrieval**: Gera resposta usando chunks selecionados

**Benefício**: Reduz buscas desnecessárias, melhora uso de contexto.

---

### 7. **Iterative Retrieval** 🔄
**Conceito**: Busca iterativa refinando query baseado em resultados anteriores.

**Técnicas**:
- **Query Expansion Iterativo**: Expande query baseado em chunks encontrados
- **Multi-turn Retrieval**: Busca em múltiplas rodadas refinando
- **Feedback Loop**: Usa chunks recuperados para melhorar próxima busca

**Benefício**: Melhora recall em queries complexas.

---

### 8. **Metadata Filtering** 🏷️
**Conceito**: Usa metadados para filtrar antes de buscar semanticamente.

**Técnicas**:
- **Domain Filtering**: Filtra por domínio (code_python, familia, etc.)
- **Date Filtering**: Prioriza conteúdo recente
- **Source Filtering**: Filtra por fonte confiável

**Benefício**: Reduz ruído, melhora precisão.

---

## 🎯 Prioridades para Implementação

### **Fase 1: Quick Wins** (Implementar Agora)
1. ✅ **Adaptive Retrieval** - Fácil, impacto alto
2. ✅ **Query Rewriting** - Melhora imediata
3. ✅ **Metadata Filtering** - Já temos domínios

### **Fase 2: Médio Prazo** (Próximas Semanas)
4. ✅ **Reranking Avançado** - Melhora precisão
5. ✅ **Contextual Compression** - Reduz tokens
6. ✅ **Hybrid Search Melhorado** - Melhora recall

### **Fase 3: Longo Prazo** (Futuro)
7. ⏳ **Self-RAG** - Complexo, requer treinamento
8. ⏳ **Iterative Retrieval** - Pode ser lento

---

## 📚 Referências

- **Adaptive Retrieval**: "Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity" (2024)
- **Query Rewriting**: "Query2doc: Query Expansion with Large Language Models" (2024)
- **Reranking**: "In-Context Reranking with Large Language Models" (2024)
- **Self-RAG**: "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection" (2024)
- **Graph RAG**: Microsoft GraphRAG, LangChain Graph Retrieval

---

## 💡 Implementação Sugerida

Criar módulo `backend/rag/enhanced_rag.py` com:
- Adaptive retrieval
- Query rewriting
- Advanced reranking
- Contextual compression
- Hybrid search melhorado

**Sem quebrar RAG existente** - adicionar como camada opcional que pode ser ativada.

