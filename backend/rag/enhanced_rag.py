"""
Enhanced RAG - Técnicas Avançadas (2024-2025)
Implementa técnicas identificadas na pesquisa sem quebrar RAG existente

Features:
- Adaptive Retrieval
- Query Rewriting
- Advanced Reranking
- Contextual Compression
- Hybrid Search Melhorado
- Metadata Filtering
"""
from typing import List, Dict, Optional, Tuple, Set
import re
from dataclasses import dataclass
from collections import Counter


@dataclass
class EnhancedRAGChunk:
    """Chunk com metadados avançados"""
    content: str
    score: float
    source: Optional[str] = None
    domain: Optional[str] = None
    metadata: Dict = None
    position: int = 0  # Posição no documento original


class EnhancedRAG:
    """
    RAG Avançado com técnicas de 2024-2025
    Pode ser usado opcionalmente sem quebrar RAG existente
    """
    
    def __init__(self):
        self.query_complexity_cache: Dict[str, str] = {}  # "simple" | "medium" | "complex"
    
    def detect_query_complexity(self, query: str) -> str:
        """
        Detecta complexidade da query para Adaptive Retrieval
        Returns: "simple", "medium", "complex"
        """
        if query in self.query_complexity_cache:
            return self.query_complexity_cache[query]
        
        query_lower = query.lower()
        
        # Indicadores de complexidade
        complex_indicators = [
            "como funciona", "explique", "qual a diferença", "compare",
            "por que", "porque", "quais são", "quais sao",
            "relação entre", "relacao entre", "depende de"
        ]
        
        simple_indicators = [
            "quem é", "quem e", "o que é", "o que e",
            "onde", "quando", "qual"
        ]
        
        # Contar palavras
        word_count = len(query.split())
        
        # Verificar indicadores
        has_complex = any(ind in query_lower for ind in complex_indicators)
        has_simple = any(ind in query_lower for ind in simple_indicators)
        
        # Determinar complexidade
        if has_complex or word_count > 15:
            complexity = "complex"
        elif has_simple and word_count < 8:
            complexity = "simple"
        else:
            complexity = "medium"
        
        self.query_complexity_cache[query] = complexity
        return complexity
    
    def adaptive_retrieval_top_k(self, query: str, default_k: int = 6) -> int:
        """
        Adaptive Retrieval: Ajusta top_k baseado na complexidade
        """
        complexity = self.detect_query_complexity(query)
        
        if complexity == "simple":
            return max(3, default_k // 2)  # Menos chunks para queries simples
        elif complexity == "complex":
            return default_k * 2  # Mais chunks para queries complexas
        else:
            return default_k  # Padrão para médias
    
    def rewrite_query(self, query: str, context: Optional[List[str]] = None) -> List[str]:
        """
        Query Rewriting: Reescreve query para melhor recuperação
        """
        rewritten = [query]  # Query original sempre incluída
        
        # 1. Decomposição: Dividir queries com múltiplas partes
        if " e " in query.lower() or " e " in query:
            parts = re.split(r'\s+e\s+', query, flags=re.IGNORECASE)
            if len(parts) > 1:
                rewritten.extend([p.strip() for p in parts if p.strip()])
        
        # 2. Expansão: Adicionar sinônimos e variações
        expansions = {
            "como": ["de que forma", "qual a maneira", "de que modo"],
            "criar": ["fazer", "desenvolver", "construir", "gerar"],
            "problema": ["erro", "bug", "issue", "falha"],
            "funciona": ["opera", "executa", "roda", "processa"],
            "usar": ["utilizar", "aplicar", "empregar"],
            "melhor": ["otimizar", "melhorar", "aperfeiçoar"],
        }
        
        words = query.lower().split()
        for word in words:
            if word in expansions:
                for synonym in expansions[word][:2]:  # Limitar a 2 sinônimos por palavra
                    expanded = query.replace(word, synonym)
                    if expanded not in rewritten:
                        rewritten.append(expanded)
        
        # 3. Clarificação: Substituir pronomes por contexto
        if context:
            # Substituir "isso", "ele", "ela" por termos do contexto
            context_words = set()
            for ctx in context[:3]:  # Usar apenas 3 primeiros contextos
                context_words.update(ctx.lower().split()[:5])  # Primeiras 5 palavras
            
            for pronoun in ["isso", "ele", "ela", "eles", "elas", "este", "esta"]:
                if pronoun in query.lower():
                    for word in context_words:
                        if len(word) > 4:  # Apenas palavras significativas
                            clarified = query.replace(pronoun, word, 1)
                            if clarified not in rewritten:
                                rewritten.append(clarified)
                            break
        
        # Limitar a 5 queries reescritas
        return rewritten[:5]
    
    def advanced_rerank(
        self,
        chunks: List[EnhancedRAGChunk],
        query: str,
        top_k: int = 5
    ) -> List[EnhancedRAGChunk]:
        """
        Advanced Reranking: Cross-encoder-like scoring
        Combina múltiplos sinais de relevância
        """
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        scored_chunks = []
        
        for chunk in chunks:
            content_lower = chunk.content.lower()
            content_words = set(re.findall(r'\w+', content_lower))
            
            # 1. Keyword Matching Score (BM25-like)
            common_words = query_words.intersection(content_words)
            keyword_score = len(common_words) / max(len(query_words), 1)
            
            # 2. Phrase Matching Score (mais importante)
            phrase_score = 0.0
            query_phrases = []
            words_list = query_lower.split()
            for i in range(len(words_list) - 1):
                phrase = f"{words_list[i]} {words_list[i+1]}"
                query_phrases.append(phrase)
            
            for phrase in query_phrases:
                if phrase in content_lower:
                    phrase_score += 0.3
            
            phrase_score = min(phrase_score, 1.0)
            
            # 3. Position Score (chunks no início são mais relevantes)
            position_score = 1.0 / (1.0 + chunk.position * 0.1)
            
            # 4. Length Score (chunks muito curtos ou muito longos são menos relevantes)
            content_length = len(chunk.content)
            ideal_length = 200  # Tamanho ideal de chunk
            length_score = 1.0 - abs(content_length - ideal_length) / (ideal_length * 2)
            length_score = max(0.0, min(1.0, length_score))
            
            # 5. Domain Score (se domain match)
            domain_score = 1.0 if chunk.domain else 0.8
            
            # Score combinado (pesos otimizados)
            combined_score = (
                keyword_score * 0.25 +
                phrase_score * 0.35 +
                chunk.score * 0.20 +
                position_score * 0.10 +
                length_score * 0.05 +
                domain_score * 0.05
            )
            
            scored_chunks.append(EnhancedRAGChunk(
                content=chunk.content,
                score=combined_score,
                source=chunk.source,
                domain=chunk.domain,
                metadata=chunk.metadata,
                position=chunk.position
            ))
        
        # Ordenar por score e retornar top_k
        scored_chunks.sort(key=lambda x: x.score, reverse=True)
        return scored_chunks[:top_k]
    
    def compress_context(
        self,
        chunks: List[EnhancedRAGChunk],
        max_tokens: int = 1000,
        preserve_important: bool = True
    ) -> str:
        """
        Contextual Compression: Remove redundâncias mantendo informação relevante
        """
        if not chunks:
            return ""
        
        # Estimar tokens (aproximação: 4 chars = 1 token)
        max_chars = max_tokens * 4
        
        # Se preserve_important, priorizar chunks com maior score
        if preserve_important:
            chunks = sorted(chunks, key=lambda x: x.score, reverse=True)
        
        compressed_parts = []
        current_length = 0
        seen_content = set()  # Evitar duplicatas
        
        for chunk in chunks:
            # Verificar se conteúdo já foi incluído (deduplicação)
            content_hash = hash(chunk.content[:100])
            if content_hash in seen_content:
                continue
            
            chunk_text = chunk.content.strip()
            chunk_length = len(chunk_text)
            
            # Remover redundâncias dentro do chunk
            if preserve_important:
                # Manter apenas sentenças mais relevantes
                sentences = re.split(r'[.!?]\s+', chunk_text)
                important_sentences = []
                for sent in sentences:
                    # Score da sentença baseado em palavras-chave
                    sent_lower = sent.lower()
                    keyword_count = sum(1 for word in sent_lower.split() if len(word) > 4)
                    if keyword_count > 2:  # Sentença com pelo menos 3 palavras significativas
                        important_sentences.append(sent)
                
                chunk_text = '. '.join(important_sentences[:3])  # Máximo 3 sentenças
                chunk_length = len(chunk_text)
            
            if current_length + chunk_length <= max_chars:
                compressed_parts.append(chunk_text)
                seen_content.add(content_hash)
                current_length += chunk_length
            else:
                # Truncar último chunk se necessário
                remaining = max_chars - current_length
                if remaining > 100:  # Só adicionar se sobrar espaço significativo
                    compressed_parts.append(chunk_text[:remaining] + "...")
                break
        
        return "\n\n".join(compressed_parts)
    
    def filter_by_metadata(
        self,
        chunks: List[EnhancedRAGChunk],
        domain: Optional[str] = None,
        min_score: float = 0.0
    ) -> List[EnhancedRAGChunk]:
        """
        Metadata Filtering: Filtra chunks por domínio e score mínimo
        """
        filtered = chunks
        
        # Filtrar por domínio
        if domain:
            filtered = [c for c in filtered if c.domain == domain]
        
        # Filtrar por score mínimo
        filtered = [c for c in filtered if c.score >= min_score]
        
        return filtered
    
    def hybrid_search_enhanced(
        self,
        query: str,
        chunks: List[EnhancedRAGChunk],
        top_k: int = 5,
        domain: Optional[str] = None
    ) -> List[EnhancedRAGChunk]:
        """
        Hybrid Search Melhorado: Combina múltiplas estratégias
        """
        # 1. Query Rewriting
        rewritten_queries = self.rewrite_query(query)
        
        # 2. Buscar chunks para cada query reescrita
        all_chunks = []
        for rewritten_query in rewritten_queries:
            # Buscar chunks que correspondem à query reescrita
            query_words = set(re.findall(r'\w+', rewritten_query.lower()))
            for chunk in chunks:
                content_words = set(re.findall(r'\w+', chunk.content.lower()))
                overlap = len(query_words.intersection(content_words))
                if overlap > 0:
                    # Ajustar score baseado no overlap
                    adjusted_chunk = EnhancedRAGChunk(
                        content=chunk.content,
                        score=chunk.score + (overlap / max(len(query_words), 1)) * 0.1,
                        source=chunk.source,
                        domain=chunk.domain,
                        metadata=chunk.metadata,
                        position=chunk.position
                    )
                    all_chunks.append(adjusted_chunk)
        
        # 3. Metadata Filtering
        if domain:
            all_chunks = self.filter_by_metadata(all_chunks, domain=domain)
        
        # 4. Advanced Reranking
        reranked = self.advanced_rerank(all_chunks, query, top_k=top_k * 2)
        
        # 5. Deduplicação final
        seen_content = set()
        unique_chunks = []
        for chunk in reranked:
            content_hash = hash(chunk.content[:150])  # Hash dos primeiros 150 chars
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_chunks.append(chunk)
                if len(unique_chunks) >= top_k:
                    break
        
        return unique_chunks
    
    def process_query(
        self,
        query: str,
        chunks: List[EnhancedRAGChunk],
        domain: Optional[str] = None,
        max_tokens: int = 1000
    ) -> Tuple[str, List[EnhancedRAGChunk]]:
        """
        Pipeline completo: Processa query com todas as técnicas
        """
        # 1. Adaptive Retrieval: Determinar top_k
        adaptive_top_k = self.adaptive_retrieval_top_k(query)
        
        # 2. Hybrid Search Enhanced
        retrieved_chunks = self.hybrid_search_enhanced(
            query,
            chunks,
            top_k=adaptive_top_k,
            domain=domain
        )
        
        # 3. Contextual Compression
        compressed_context = self.compress_context(
            retrieved_chunks,
            max_tokens=max_tokens,
            preserve_important=True
        )
        
        return compressed_context, retrieved_chunks


# Instância global (opcional - pode ser desabilitado)
enhanced_rag = EnhancedRAG()

