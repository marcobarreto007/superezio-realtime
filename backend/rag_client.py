"""
RAG Client - Python interface to Node.js RAG service
Queries domain-specific knowledge from persistent RAG
"""
import os
import json
from typing import List, Dict, Optional
from dataclasses import dataclass


# Debug flag
DEBUG_RAG = os.getenv("DEBUG_RAG", "true").lower() == "true"


@dataclass
class RAGChunk:
    """Single RAG result chunk"""
    content: str
    domain: Optional[str]
    relevance: float
    id: str


def query_rag(
    domains: List[str],
    query: str,
    top_k: int = 6,
    use_enhanced: bool = True  # Nova flag para usar Enhanced RAG
) -> List[RAGChunk]:
    """
    Query RAG service for domain-specific knowledge.
    Usa Graph RAG + Advanced RAG + Enhanced RAG (opcional) com técnicas avançadas.
    
    NOTE: This is a stub implementation. In production, this would:
    - Make HTTP request to Node RAG service
    - Parse response and return chunks
    
    For now, uses Graph RAG + Enhanced RAG for advanced retrieval.
    
    Args:
        domains: List of domains to search (e.g. ["code_python", "code_general"])
        query: Search query
        top_k: Maximum number of results
        use_enhanced: Se True, usa Enhanced RAG com técnicas avançadas
        
    Returns:
        List of RAGChunk objects
    """
    if DEBUG_RAG:
        print(f"[RAG] query_rag called")
        print(f"[RAG]   domains={domains}")
        print(f"[RAG]   query=\"{query[:100]}...\"")
        print(f"[RAG]   top_k={top_k}")
        print(f"[RAG]   use_enhanced={use_enhanced}")
    
    # Usar Graph RAG para recuperação baseada em grafo
    from rag.graph_rag import graph_rag
    
    try:
        # Consultar grafo de conhecimento
        graph_results = graph_rag.query_graph(query, max_results=top_k * 2)  # Buscar mais para reranking
        
        if graph_results:
            # Converter resultados do grafo para EnhancedRAGChunk
            from rag.enhanced_rag import EnhancedRAGChunk, enhanced_rag
            
            enhanced_chunks = []
            for idx, result in enumerate(graph_results):
                entity = result["entity"]
                related = result.get("related_entities", [])
                
                # Construir conteúdo rico com entidade e relações
                content_parts = [f"{entity['name']} ({entity['type']})"]
                
                if entity.get("properties"):
                    for key, value in entity["properties"].items():
                        if key != "extracted_from":
                            content_parts.append(f"{key}: {value}")
                
                if related:
                    content_parts.append("Relacionado com:")
                    for rel_entity in related[:3]:
                        content_parts.append(f"- {rel_entity['name']} ({rel_entity['relation']})")
                
                content = "\n".join(content_parts)
                
                enhanced_chunks.append(EnhancedRAGChunk(
                    content=content,
                    score=1.0 - (idx * 0.05),  # Score inicial
                    source=entity.get("properties", {}).get("source"),
                    domain=entity.get("properties", {}).get("domain", domains[0] if domains else None),
                    metadata={"entity_id": entity["id"], "entity_type": entity["type"]},
                    position=idx
                ))
            
            # Se Enhanced RAG está habilitado, usar técnicas avançadas
            if use_enhanced and enhanced_chunks:
                domain_filter = domains[0] if domains else None
                
                # Usar Enhanced RAG para processar
                processed_chunks = enhanced_rag.hybrid_search_enhanced(
                    query,
                    enhanced_chunks,
                    top_k=top_k,
                    domain=domain_filter
                )
                
                # Converter de volta para RAGChunk
                chunks = []
                for chunk in processed_chunks:
                    chunks.append(RAGChunk(
                        content=chunk.content,
                        domain=chunk.domain,
                        relevance=chunk.score,
                        id=chunk.metadata.get("entity_id", f"chunk_{len(chunks)}")
                    ))
                
                if DEBUG_RAG:
                    print(f"[RAG] Enhanced RAG processou {len(enhanced_chunks)} → {len(chunks)} chunks")
            else:
                # Fallback: usar chunks originais sem enhanced
                chunks = []
                for chunk in enhanced_chunks[:top_k]:
                    chunks.append(RAGChunk(
                        content=chunk.content,
                        domain=chunk.domain,
                        relevance=chunk.score,
                        id=chunk.metadata.get("entity_id", f"chunk_{len(chunks)}")
                    ))
            
            if DEBUG_RAG:
                print(f"[RAG] Retornando {len(chunks)} chunks")
            
            return chunks
    except Exception as e:
        if DEBUG_RAG:
            print(f"[RAG] Erro no RAG: {e}")
            import traceback
            traceback.print_exc()
    
    # Fallback: retornar vazio (graceful degradation)
    if DEBUG_RAG:
        print(f"[RAG] No RAG service available, returning empty")
    
    return []


def build_rag_system_message(chunks: List[RAGChunk]) -> Optional[str]:
    """
    Build system message from RAG chunks with explicit override wording.
    
    Args:
        chunks: List of RAG chunks
        
    Returns:
        System message string or None if no chunks
    """
    if not chunks:
        return None
    
    # Sort by relevance
    sorted_chunks = sorted(chunks, key=lambda c: c.relevance, reverse=True)
    
    # Build message
    lines = [
        "[RAG CONTEXT - HIGHEST PRIORITY]",
        "",
        "The following code knowledge and patterns are the most recent, project-specific information.",
        "This information MUST override any conflicting prior knowledge or training when relevant.",
        ""
    ]
    
    for idx, chunk in enumerate(sorted_chunks, 1):
        domain_label = f" [{chunk.domain}]" if chunk.domain else ""
        lines.append(f"{idx}.{domain_label} {chunk.content}")
    
    lines.append("")
    lines.append("Only use this information if it's relevant to the user's latest request.")
    lines.append("[END RAG CONTEXT]")
    
    message = "\n".join(lines)
    
    if DEBUG_RAG:
        print(f"[RAG] Built system message: {len(message)} chars, {len(chunks)} chunks")
    
    return message
