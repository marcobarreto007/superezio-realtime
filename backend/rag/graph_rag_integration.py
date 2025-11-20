"""
Graph RAG Integration
Integra Graph RAG no fluxo principal de inferência
"""
from typing import List, Dict, Optional
from rag.graph_rag import graph_rag, GraphRAG
from rag_client import RAGChunk


def enhance_with_graph_rag(
    query: str,
    domains: List[str],
    existing_chunks: List[RAGChunk] = None
) -> List[RAGChunk]:
    """
    Enriquece resultados RAG com Graph RAG
    Combina busca vetorial tradicional com navegação em grafo
    """
    # Consultar Graph RAG
    graph_results = graph_rag.query_graph(query, max_results=5)
    
    if not graph_results:
        return existing_chunks or []
    
    # Converter resultados do grafo para RAGChunk
    graph_chunks = []
    for result in graph_results:
        entity = result["entity"]
        related = result.get("related_entities", [])
        
        # Construir conteúdo rico
        content_parts = [
            f"**{entity['name']}** ({entity['type']})"
        ]
        
        # Propriedades
        if entity.get("properties"):
            for key, value in entity["properties"].items():
                if key not in ["extracted_from", "domain"]:
                    content_parts.append(f"- {key}: {value}")
        
        # Relações
        if related:
            content_parts.append("\nRelacionado:")
            for rel_entity in related[:3]:
                content_parts.append(
                    f"  • {rel_entity['name']} via {rel_entity['relation']}"
                )
        
        content = "\n".join(content_parts)
        
        graph_chunks.append(RAGChunk(
            content=content,
            domain=entity.get("properties", {}).get("domain") or (domains[0] if domains else None),
            relevance=0.9,  # Alta relevância para Graph RAG
            id=f"graph_{entity['id']}"
        ))
    
    # Combinar com chunks existentes
    if existing_chunks:
        # Graph RAG tem prioridade (relevância mais alta)
        combined = graph_chunks + existing_chunks
        # Ordenar por relevância
        combined.sort(key=lambda x: x.relevance, reverse=True)
        return combined[:len(existing_chunks) + len(graph_chunks)]
    
    return graph_chunks


def build_graph_rag_context(query: str) -> Optional[str]:
    """
    Constrói contexto usando Graph RAG
    """
    try:
        context = graph_rag.build_context_from_graph(query, max_entities=3)
        return context if context else None
    except Exception as e:
        print(f"[Graph RAG] Erro ao construir contexto: {e}")
        return None


def ingest_to_graph(text: str, domain: Optional[str] = None) -> None:
    """
    Ingere texto no grafo de conhecimento
    """
    try:
        graph_rag.ingest_text(text, domain=domain)
    except Exception as e:
        print(f"[Graph RAG] Erro ao ingerir texto: {e}")

