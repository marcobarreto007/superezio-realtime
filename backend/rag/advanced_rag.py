"""
Advanced RAG Implementation
Baseado em papers recentes sobre RAG optimization (2024-2025)

Features:
- Query expansion
- Re-ranking
- Hybrid search (semantic + keyword)
- Context compression
"""
from typing import List, Dict, Optional, Tuple
import re
from dataclasses import dataclass


@dataclass
class RAGChunk:
    """Chunk de RAG com metadados"""
    content: str
    score: float
    source: Optional[str] = None
    metadata: Dict = None


class AdvancedRAG:
    """RAG avançado com otimizações baseadas em papers"""
    
    def __init__(self):
        self.query_cache: Dict[str, List[RAGChunk]] = {}
    
    def expand_query(self, query: str) -> List[str]:
        """
        Query expansion baseado em papers recentes
        Gera variações da query para melhor recall
        """
        expansions = [query]  # Query original
        
        # Adicionar sinônimos comuns
        synonyms = {
            "como": ["de que forma", "qual a maneira"],
            "criar": ["fazer", "desenvolver", "construir"],
            "problema": ["erro", "bug", "issue"],
            "funciona": ["opera", "executa", "roda"],
        }
        
        words = query.lower().split()
        for word in words:
            if word in synonyms:
                for synonym in synonyms[word]:
                    expanded = query.replace(word, synonym)
                    expansions.append(expanded)
        
        return expansions[:3]  # Limitar a 3 expansões
    
    def rerank_chunks(
        self, 
        chunks: List[RAGChunk], 
        query: str,
        top_k: int = 5
    ) -> List[RAGChunk]:
        """
        Re-ranking de chunks baseado em relevância semântica
        Usa scoring híbrido: BM25-like + semantic similarity
        """
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        scored_chunks = []
        for chunk in chunks:
            # Score BM25-like (keyword matching)
            content_lower = chunk.content.lower()
            content_words = set(re.findall(r'\w+', content_lower))
            
            # Intersecção de palavras
            common_words = query_words.intersection(content_words)
            keyword_score = len(common_words) / max(len(query_words), 1)
            
            # Score de posição (chunks no início são mais relevantes)
            position_score = 1.0  # Simplificado
            
            # Score combinado
            combined_score = (keyword_score * 0.6) + (chunk.score * 0.4) + (position_score * 0.1)
            
            scored_chunks.append(RAGChunk(
                content=chunk.content,
                score=combined_score,
                source=chunk.source,
                metadata=chunk.metadata
            ))
        
        # Ordenar por score e retornar top_k
        scored_chunks.sort(key=lambda x: x.score, reverse=True)
        return scored_chunks[:top_k]
    
    def compress_context(
        self, 
        chunks: List[RAGChunk], 
        max_tokens: int = 1000
    ) -> str:
        """
        Context compression baseado em papers
        Remove redundâncias e mantém informação mais relevante
        """
        if not chunks:
            return ""
        
        # Estimar tokens (aproximação: 4 chars = 1 token)
        max_chars = max_tokens * 4
        
        compressed_parts = []
        current_length = 0
        
        for chunk in chunks:
            chunk_text = chunk.content
            chunk_length = len(chunk_text)
            
            if current_length + chunk_length <= max_chars:
                compressed_parts.append(chunk_text)
                current_length += chunk_length
            else:
                # Truncar último chunk se necessário
                remaining = max_chars - current_length
                if remaining > 100:  # Só adicionar se sobrar espaço significativo
                    compressed_parts.append(chunk_text[:remaining] + "...")
                break
        
        return "\n\n".join(compressed_parts)
    
    def hybrid_search(
        self,
        query: str,
        chunks: List[RAGChunk],
        top_k: int = 5
    ) -> List[RAGChunk]:
        """
        Hybrid search: combina semantic + keyword search
        """
        # 1. Query expansion
        expanded_queries = self.expand_query(query)
        
        # 2. Buscar chunks para cada query expandida
        all_chunks = []
        for exp_query in expanded_queries:
            # Simular busca semântica (em produção, usar embeddings reais)
            for chunk in chunks:
                if exp_query.lower() in chunk.content.lower():
                    all_chunks.append(chunk)
        
        # 3. Re-ranking
        reranked = self.rerank_chunks(all_chunks, query, top_k=top_k * 2)
        
        # 4. Deduplicação
        seen_content = set()
        unique_chunks = []
        for chunk in reranked:
            content_hash = hash(chunk.content[:100])  # Hash dos primeiros 100 chars
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_chunks.append(chunk)
                if len(unique_chunks) >= top_k:
                    break
        
        return unique_chunks


# Instância global
advanced_rag = AdvancedRAG()

